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
import time
import unittest
from mock import Mock

from slipstream.cloudconnectors.BaseCloudConnector import BaseCloudConnector
from slipstream_cloudstack.CloudStackClientCloud import CloudStackClientCloud
from slipstream.ConfigHolder import ConfigHolder
from slipstream.SlipStreamHttpClient import UserInfo
from slipstream.NodeInstance import NodeInstance
from slipstream.NodeDecorator import RUN_CATEGORY_DEPLOYMENT, KEY_RUN_CATEGORY, NodeDecorator
from slipstream import util

CONFIG_FILE = os.path.join(os.path.dirname(__file__),
                           'pyunit.credentials.properties')

# Example configuration file.
"""
[Test]
General.ssh.public.key = ssh-rsa ....
cloudstack.endpoint = https://api.exoscale.ch/compute
cloudstack.key = xxx
cloudstack.secret = yyy
cloudstack.zone = CH-GV2
cloudstack.template = 8c7e60ae-3a30-4031-a3e6-29832d85d7cb
cloudstack.instance.type = Micro
cloudstack.security.groups = default
cloudstack.max.iaas.workers = 2
"""  # pylint: disable=pointless-string-statement

# pylint: disable=protected-access


class TestCloudStackClientCloud(unittest.TestCase):

    connector_instance_name = 'cloudstack'

    def constructKey(self, name):
        return self.connector_instance_name + '.' + name

    def setUp(self):
        BaseCloudConnector._publish_vm_info = Mock()  # pylint: disable=protected-access

        os.environ['SLIPSTREAM_CONNECTOR_INSTANCE'] = self.connector_instance_name
        os.environ['SLIPSTREAM_BOOTSTRAP_BIN'] = 'http://example.com/bootstrap'
        os.environ['SLIPSTREAM_DIID'] = '00000000-0000-0000-0000-%s' % time.time()

        if not os.path.exists(CONFIG_FILE):
            raise Exception('Configuration file %s not found.' % CONFIG_FILE)

        self.ch = ConfigHolder(configFile=CONFIG_FILE, context={'foo': 'bar'})
        self.ch.set(KEY_RUN_CATEGORY, '')
        self.ch.set('verboseLevel', self.ch.config['General.verbosity'])

        self.client = CloudStackClientCloud(self.ch)

        self.user_info = UserInfo(self.connector_instance_name)
        self.user_info[self.constructKey('endpoint')] = self.ch.config['cloudstack.endpoint']
        self.user_info[self.constructKey('zone')] = self.ch.config['cloudstack.zone']
        self.user_info[self.constructKey('username')] = self.ch.config['cloudstack.key']
        self.user_info[self.constructKey('password')] = self.ch.config['cloudstack.secret']
        security_groups = self.ch.config['cloudstack.security.groups']
        instance_type = self.ch.config['cloudstack.instance.type']
        self.user_info['General.ssh.public.key'] = self.ch.config['General.ssh.public.key']
        image_id = self.ch.config[self.constructKey('template')]

        self.multiplicity = 2
        self.max_iaas_workers = self.ch.config.get('cloudstack.max.iaas.workers',
                                                   str(self.multiplicity))

        self.node_name = 'test_node'
        self.node_instances = {}
        for i in range(1, self.multiplicity + 1):
            node_instance_name = self.node_name + '.' + str(i)
            self.node_instances[node_instance_name] = NodeInstance({
                NodeDecorator.NODE_NAME_KEY: self.node_name,
                NodeDecorator.NODE_INSTANCE_NAME_KEY: node_instance_name,
                'cloudservice': self.connector_instance_name,
                # 'index': i,s
                'image.platform': 'linux',
                'image.imageId': image_id,
                'image.id': image_id,
                self.constructKey('instance.type'): instance_type,
                self.constructKey('security.groups'): security_groups,
                'network': 'private'
            })

    def tearDown(self):
        os.environ.pop('SLIPSTREAM_CONNECTOR_INSTANCE')
        os.environ.pop('SLIPSTREAM_BOOTSTRAP_BIN')
        self.client = None
        self.ch = None

    def xtest_1_startStopImages(self):
        self.client._get_max_workers = Mock(return_value=self.max_iaas_workers)
        self.client.run_category = RUN_CATEGORY_DEPLOYMENT

        try:
            self.client.start_nodes_and_clients(self.user_info, self.node_instances)

            util.printAndFlush('Instances started')

            vms = self.client.get_vms()
            assert len(vms) == self.multiplicity
        finally:
            self.client.stop_deployment()

    def xtest_2_buildImage(self):
        raise NotImplementedError()


if __name__ == '__main__':
    unittest.main()
