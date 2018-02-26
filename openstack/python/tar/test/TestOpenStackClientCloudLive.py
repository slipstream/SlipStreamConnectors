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

from slipstream.NodeDecorator import (NodeDecorator, RUN_CATEGORY_IMAGE)
from slipstream.NodeInstance import NodeInstance
from slipstream.UserInfo import UserInfo
import slipstream.util as util

from slipstream_openstack.OpenStackClientCloud import \
    OpenStackClientCloud, FLOATING_IPS_KEY
from slipstream_openstack.OpenStackClientCloud import searchInObjectList
from slipstream_openstack.TestBaseLive import TestBaseLive

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


class TestOpenStackClientCloudLive(TestBaseLive):
    cin = 'openstack'

    conf_keys = ['endpoint',
                 'tenant-name',
                 'username',
                 'password',
                 'domain-name',
                 'identityVersion',
                 'serviceType',
                 'serviceName',
                 'serviceRegion',
                 'tenant-name',
                 'network.type',
                 FLOATING_IPS_KEY,
                 UserInfo.NETWORK_PUBLIC_KEY,
                 UserInfo.NETWORK_PRIVATE_KEY]

    def _update_user_info(self):
        self.user_info[self.construct_key(FLOATING_IPS_KEY)] = \
            util.str2bool(self.user_info.get_cloud(FLOATING_IPS_KEY, 'false'))

    def setUp(self):
        self._setUp(OpenStackClientCloud, CONFIG_FILE, self.conf_keys)
        self._update_user_info()
        security_groups = self._conf_val('security.groups')
        image_id = self._conf_val('imageid')
        instance_type = self._conf_val('intance.type', 'm1.tiny')
        network_type = self._conf_val('network.type')
        node_name = 'test_node'

        self.node_instances = {}
        for i in range(1, self.multiplicity + 1):
            node_instance_name = node_name + '.' + str(i)
            self.node_instances[node_instance_name] = NodeInstance({
                NodeDecorator.NODE_NAME_KEY: node_name,
                NodeDecorator.NODE_INSTANCE_NAME_KEY: node_instance_name,
                'cloudservice': self.cin,
                'image.platform': 'Ubuntu',
                'image.imageId': image_id,
                'image.id': image_id,
                self.construct_key('instance.type'): instance_type,
                self.construct_key('security.groups'): security_groups,
                'network': network_type
            })

        self.node_instance = NodeInstance({
            NodeDecorator.NODE_NAME_KEY: NodeDecorator.MACHINE_NAME,
            NodeDecorator.NODE_INSTANCE_NAME_KEY: NodeDecorator.MACHINE_NAME,
            'cloudservice': self.cin,
            'image.platform': 'Ubuntu',
            'image.imageId': image_id,
            'image.id': image_id,
            self.construct_key('instance.type'): instance_type,
            self.construct_key('security.groups'): security_groups,
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

        self.node_instance_with_additional_disk = NodeInstance({
            NodeDecorator.NODE_NAME_KEY: NodeDecorator.MACHINE_NAME,
            NodeDecorator.NODE_INSTANCE_NAME_KEY: NodeDecorator.MACHINE_NAME,
            'cloudservice': self.cin,
            'image.platform': 'Ubuntu',
            'image.imageId': image_id,
            'image.id': image_id,
            self.construct_key('instance.type'): instance_type,
            'network': network_type,
            'extra.disk.volatile': '20'
        })

    def tearDown(self):
        os.environ.pop('SLIPSTREAM_CONNECTOR_INSTANCE')
        os.environ.pop('SLIPSTREAM_BOOTSTRAP_BIN')
        self.client = None
        self.ch = None

    def xtest_1_start_stop_images(self):
        self._test_start_stop_images()

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

    def xtest_4_start_image_with_extra_disk(self):
        self.client.run_category = RUN_CATEGORY_IMAGE

        self.client.start_nodes_and_clients(self.user_info,
                                            {NodeDecorator.MACHINE_NAME: self.node_instance_with_additional_disk})

        vm_id = self.client.get_vms()[NodeDecorator.MACHINE_NAME]['id']
        nodes = self.client.list_instances()

        assert searchInObjectList(nodes, 'id', vm_id).extra['volumes_attached']

        self.client.stop_deployment()


if __name__ == '__main__':
    unittest.main()
