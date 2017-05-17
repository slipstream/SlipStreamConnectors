#!/usr/bin/env python
"""
 SlipStream Client
 =====
 Copyright (C) 2015 SixSq Sarl (sixsq.com)
 =====
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""

import os
import sys
import unittest
import traceback
from mock import Mock
from pprint import pprint as pp

from slipstream import util
from slipstream.ConfigHolder import ConfigHolder
from slipstream.NodeInstance import NodeInstance
from slipstream.SlipStreamHttpClient import UserInfo
from slipstream.NodeDecorator import KEY_RUN_CATEGORY
from slipstream.NodeDecorator import RUN_CATEGORY_DEPLOYMENT


def publish_vm_info(self, vm, node_instance):
    # pylint: disable=unused-argument, protected-access
    print '%s, %s' % (self._vm_get_id(vm), self._vm_get_ip(vm))


class TestBaseLive(unittest.TestCase):
    cin = ''
    node_instances = {} # of NodeInstance()
    multiplicity = 0
    max_iaas_workers = 1

    def construct_key(self, name):
        return self.cin + '.' + name

    def _conf_val(self, key, default=None):
        conf_key = self.construct_key(key)
        if default:
            return self.ch.config.get(conf_key, default)
        return self.ch.config[conf_key]

    def _build_user_info(self, keys):
        self.user_info = UserInfo(self.cin)
        self.user_info['General.ssh.public.key'] = self.ch.config[
            'General.ssh.public.key']
        for k in keys:
            self.user_info[self.construct_key(k)] = self._conf_val(k)

    def _load_config(self, conf_file):
        if not os.path.exists(conf_file):
            raise Exception('Configuration file %s not found.' % conf_file)

        self.ch = ConfigHolder(configFile=conf_file, context={'foo': 'bar'})
        self.ch.set(KEY_RUN_CATEGORY, '')

    def _build_client(self, testedCls):
        testedCls._publish_vm_info = publish_vm_info  # pylint: disable=protected-access
        self.client = testedCls(self.ch)

    def _get_ex_msg(self, ex):
        if hasattr(ex, 'message'):
            return ex.message
        if hasattr(ex, 'arg'):
            return ex.arg
        return ''

    def _setUp(self, testedCls, conf_file, conf_keys):
        """(Re-)sets the following fields
        self.ch               - ConfigHolder
        self.client           - instance of BaseCloudConnector
        self.user_info        - UserInfo
        self.multiplicity     - int
        self.max_iaas_workers - str
        """
        os.environ['SLIPSTREAM_CONNECTOR_INSTANCE'] = self.cin
        os.environ['SLIPSTREAM_BOOTSTRAP_BIN'] = 'http://example.com/bootstrap'
        os.environ['SLIPSTREAM_DIID'] = '00000000-0000-0000-0000-000000000000'

        self._load_config(conf_file)
        self._build_client(testedCls)
        self._build_user_info(conf_keys)
        pp(self.user_info)

        self.multiplicity = int(self._conf_val('multiplicity', 2))
        self.max_iaas_workers = self._conf_val('max.iaas.workers',
                                               str(self.multiplicity))

    def _test_startStopImages(self):
        "Live test that starts and stops VMs on a cloud."
        self.client._get_max_workers = Mock(return_value=self.max_iaas_workers)
        self.client.run_category = RUN_CATEGORY_DEPLOYMENT

        success = True
        error = ''
        try:
            self.client.start_nodes_and_clients(self.user_info,
                                                self.node_instances)
            vms = self.client.get_vms()
            assert len(vms) == self.multiplicity
            util.printAction('Instances started.')
            pp(vms)
        except Exception as ex:
            success = False
            error = self._get_ex_msg(ex)
            util.printError("Exception caught while starting instances!")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
        finally:
            util.printAction("Stopping deployment.")
            self.client.stop_deployment()
        self.assertEquals(success, True, error)
