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

from slipstream_openstack.OpenStackClientCloud import \
    OpenStackClientCloud
from slipstream.ConfigHolder import ConfigHolder
from slipstream.SlipStreamHttpClient import UserInfo
from slipstream.NodeDecorator import (NodeDecorator, RUN_CATEGORY_IMAGE,
                                      RUN_CATEGORY_DEPLOYMENT, KEY_RUN_CATEGORY)
from slipstream import util
from slipstream.NodeInstance import NodeInstance

CONFIG_FILE = os.path.join(os.path.dirname(__file__),
                           'pyunit.credentials.properties')
# Example configuration file.
"""
[Test]
openstack.location = LVS
openstack.username = konstan@sixsq.com
openstack.password = xxx
openstack.imageid =  d02ee717-33f7-478b-ba14-02196978fea8
openstack.ssh.username = ubuntu
openstack.ssh.password = yyy
"""  # pylint: disable=pointless-string-statement


def publish_vm_info(self, vm, node_instance):
    # pylint: disable=unused-argument, protected-access
    print '%s, %s' % (self._vm_get_id(vm), self._vm_get_ip(vm))


class TestOpenStackClientCloudLive(unittest.TestCase):

    connector_instance_name = 'openstack'

    def constructKey(self, name):
        return self.connector_instance_name + '.' + name

    def setUp(self):
        os.environ['SLIPSTREAM_CONNECTOR_INSTANCE'] = self.connector_instance_name
        os.environ['SLIPSTREAM_BOOTSTRAP_BIN'] = 'http://example.com/bootstrap'
        os.environ['SLIPSTREAM_DIID'] = '00000000-0000-0000-0000-000000000000'

        if not os.path.exists(CONFIG_FILE):
            raise Exception('Configuration file %s not found.' % CONFIG_FILE)

        self.ch = ConfigHolder(configFile=CONFIG_FILE, context={'foo': 'bar'})
        self.ch.set(KEY_RUN_CATEGORY, '')

        OpenStackClientCloud._publish_vm_info = publish_vm_info  # pylint: disable=protected-access
        self.client = OpenStackClientCloud(self.ch)

        self.user_info = UserInfo(self.connector_instance_name)
        self.user_info['General.ssh.public.key'] = self.ch.config['General.ssh.public.key']
        self.user_info[self.constructKey('endpoint')] = self.ch.config['openstack.endpoint']
        self.user_info[self.constructKey('tenant.name')] = self.ch.config['openstack.tenant.name']
        self.user_info[self.constructKey('username')] = self.ch.config['openstack.username']
        self.user_info[self.constructKey('password')] = self.ch.config['openstack.password']

        self.user_info[self.constructKey('service.type')] = self.ch.config['openstack.service.type']
        self.user_info[self.constructKey('service.name')] = self.ch.config['openstack.service.name']
        self.user_info[self.constructKey('service.region')] = self.ch.config['openstack.service.region']
        self.user_info[self.constructKey('network.private')] = self.ch.config['openstack.network.private']

        security_groups = self.ch.config['openstack.security.groups']
        image_id = self.ch.config['openstack.imageid']
        instance_type = self.ch.config.get('openstack.intance.type', 'm1.tiny')
        network_type = self.ch.config['openstack.network.type']
        node_name = 'test_node'

        self.multiplicity = 2

        self.node_instances = {}
        for i in range(1, self.multiplicity + 1):
            node_instance_name = node_name + '.' + str(i)
            self.node_instances[node_instance_name] = NodeInstance({
                NodeDecorator.NODE_NAME_KEY: node_name,
                NodeDecorator.NODE_INSTANCE_NAME_KEY: node_instance_name,
                'cloudservice': self.connector_instance_name,
                # 'index': i,
                'image.platform': 'Ubuntu',
                'image.imageId': image_id,
                'image.id': image_id,
                self.constructKey('instance.type'): instance_type,
                self.constructKey('security.groups'): security_groups,
                'network': network_type
            })

        self.node_instance = NodeInstance({
            NodeDecorator.NODE_NAME_KEY: NodeDecorator.MACHINE_NAME,
            NodeDecorator.NODE_INSTANCE_NAME_KEY: NodeDecorator.MACHINE_NAME,
            'cloudservice': self.connector_instance_name,
            'image.platform': 'Ubuntu',
            'image.imageId': image_id,
            'image.id': image_id,
            self.constructKey('instance.type'): instance_type,
            self.constructKey('security.groups'): security_groups,
            'network': network_type,
            'image.prerecipe':
"""#!/bin/sh
set -e
set -x

ls -l /tmp
dpkg -l | egrep "nano|lvm" || true
""",
                'image.packages': ['lvm2', 'nano'],
                'image.recipe':
"""#!/bin/sh
set -e
set -x

dpkg -l | egrep "nano|lvm" || true
lvs
"""
        })

    def tearDown(self):
        os.environ.pop('SLIPSTREAM_CONNECTOR_INSTANCE')
        os.environ.pop('SLIPSTREAM_BOOTSTRAP_BIN')
        self.client = None
        self.ch = None

    def xtest_1_startStopImages(self):
        self.client.run_category = RUN_CATEGORY_DEPLOYMENT

        self.client.start_nodes_and_clients(self.user_info, self.node_instances)

        util.printAndFlush('Instances started')

        vms = self.client.get_vms()
        assert len(vms) == self.multiplicity

        self.client.stop_deployment()

    def xtest_2_buildImage(self):
        self.client.run_category = RUN_CATEGORY_IMAGE

        self.client.start_nodes_and_clients(self.user_info, {NodeDecorator.MACHINE_NAME: self.node_instance})
        instances_details = self.client.get_vms_details()

        assert instances_details
        assert instances_details[0][NodeDecorator.MACHINE_NAME]

        new_id = self.client.build_image(self.user_info, self.node_instance)
        assert new_id

    def xtest_3_list_instances(self):
        self.client._initialization(self.user_info)
        assert isinstance(self.client.list_instances(), list)


if __name__ == '__main__':
    unittest.main()
