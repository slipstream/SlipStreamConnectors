#!/usr/bin/env python
"""
 SlipStream Client
 =====
 Copyright (C) 2013 SixSq Sarl (sixsq.com)
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

import base64
import json
import os
import unittest
import socket
from mock import Mock

from slipstream_stratuslab.StratuslabClientCloud import StratuslabClientCloud
from slipstream.ConfigHolder import ConfigHolder as SlipstreamConfigHolder
from slipstream.exceptions import Exceptions

from stratuslab.ConfigHolder import ConfigHolder as StratusLabConfigHolder
from stratuslab.vm_manager.Runner import Runner
from slipstream.NodeInstance import NodeInstance

# pylint: disable=protected-access


class TestStratusLabClientCloud(unittest.TestCase):

    def setUp(self):
        os.environ['SLIPSTREAM_CONNECTOR_INSTANCE'] = 'stratuslab'

    def tearDown(self):
        os.environ.pop('SLIPSTREAM_CONNECTOR_INSTANCE')

    def test__getCreateImageMessagingMessage(self):

        msg = StratuslabClientCloud._get_create_image_messaging_message('/foo/bar')

        assert {'uri': '/foo/bar', 'imageid': ''} == json.loads(
            base64.b64decode(msg))

    def test_runInstanceMaxAttempts(self):
        # pylint: disable=star-args

        stratuslabClient = StratuslabClientCloud(
            SlipstreamConfigHolder(context={'foo': 'bar'},
                                   config={'foo': 'bar'}))
        stratuslabClient.RUNINSTANCE_RETRY_TIMEOUT = 0
        stratuslabClient._do_run_instance = Mock()
        stratuslabClient._do_run_instance.side_effect = socket.error()

        self.failUnlessRaises(Exceptions.ExecutionException,
                              stratuslabClient._run_instance,
                              *('abc', StratusLabConfigHolder()), max_attempts=5)
        assert stratuslabClient._do_run_instance.call_count == 5
        stratuslabClient._do_run_instance.call_count = 0

        self.failUnlessRaises(Exceptions.ExecutionException,
                              stratuslabClient._run_instance,
                              *('abc', StratusLabConfigHolder()), max_attempts=0)
        assert stratuslabClient._do_run_instance.call_count == 1

    def test_extraDisksOnStratusLabRunner(self):
        stratuslabClient = StratuslabClientCloud(
            SlipstreamConfigHolder(context={'foo': 'bar'},
                                   config={'foo': 'bar'}))
        slch = StratusLabConfigHolder()
        slch.set('username', 'foo')
        slch.set('password', 'bar')
        slch.set('endpoint', 'example.com')
        slch.set('verboseLevel', 0)
        node_instance = NodeInstance({'cloudservice': 'stratuslab',
                                      'extra.disk.volatile': '123',
                                      'stratuslab.extra_disk_persistent': '1-2-3',
                                      'stratuslab.extra_disk_readonly': 'ABC'})
        stratuslabClient._set_extra_disks_on_config_holder(slch, node_instance)
        Runner._checkPersistentDiskAvailable = Mock()
        runner = stratuslabClient._get_stratuslab_runner('abc', slch)
        assert runner.extraDiskSize == int('123') * 1024  # MB
        assert runner.persistentDiskUUID == '1-2-3'
        assert runner.readonlyDiskId == 'ABC'

if __name__ == '__main__':
    unittest.main()
