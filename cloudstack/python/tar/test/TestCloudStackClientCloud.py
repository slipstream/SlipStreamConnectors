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
import unittest
from mock import Mock
from slipstream.ConfigHolder import ConfigHolder
from slipstream_cloudstack.CloudStackClientCloud import CloudStackClientCloud


class TestCloudStackClientCloud(unittest.TestCase):

    connector_instance_name = 'cloudstack'

    def setUp(self):
        os.environ['SLIPSTREAM_CONNECTOR_INSTANCE'] = self.connector_instance_name

    def tearDown(self):
        pass

    def test_init(self):
        CloudStackClientCloud(ConfigHolder(context={'foo': 'bar'}))

    def test_vm_get_id_ip(self):
        cs = CloudStackClientCloud(ConfigHolder(context={'foo': 'bar'}))

        assert 1 == cs._vm_get_id(dict(id=1))
        obj = Mock()
        obj.id = 1
        assert 1 == cs._vm_get_id(obj)

        assert '1.2.3.4' == cs._vm_get_ip(dict(ip='1.2.3.4'))
        obj = Mock()
        obj.ip = '1.2.3.4'
        assert '1.2.3.4' == cs._vm_get_ip(obj)


if __name__ == '__main__':
    unittest.main()
