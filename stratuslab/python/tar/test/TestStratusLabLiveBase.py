"""
 SlipStream Client
 =====
 Copyright (C) 2014 SixSq Sarl (sixsq.com)
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

from slipstream_stratuslab.StratusLabClientCloud import StratusLabClientCloud
from slipstream.ConfigHolder import ConfigHolder
from slipstream.SlipStreamHttpClient import UserInfo
from slipstream.NodeInstance import NodeInstance
from slipstream.NodeDecorator import NodeDecorator

CONFIG_FILE = os.path.join(os.path.dirname(__file__),
                           'pyunit.credentials.properties')
# Example configuration file.
"""
[Test]
stratuslab.username = konstan@sixsq.com
stratuslab.password = xxx
stratuslab.imageid =  HZTKYZgX7XzSokCHMB60lS0wsiv
"""  # pylint: disable=pointless-string-statement


class TestStratusLabLiveBase(unittest.TestCase):

    def setUp(self):

        os.environ['SLIPSTREAM_CONNECTOR_INSTANCE'] = 'stratuslab'
        os.environ['SLIPSTREAM_BOOTSTRAP_BIN'] = 'http://example.com/bootstrap'
        os.environ['SLIPSTREAM_DIID'] = '00000000-0000-0000-0000-00%s' % int(time.time())

        config_file = self._get_config_file()
        if not os.path.exists(config_file):
            raise Exception('Configuration file %s not found.' % config_file)

        self.ch = ConfigHolder(configFile=config_file, context={'foo': 'bar'})
        self.ch.set('verboseLevel', int(self.ch.config['General.verbosity']))

        os.environ['SLIPSTREAM_PDISK_ENDPOINT'] = self.ch.config['SLIPSTREAM_PDISK_ENDPOINT']

        self.client = StratusLabClientCloud(self.ch)
        self.client._publish_vm_info = Mock()

        self.user_info = UserInfo('stratuslab')
        self.user_info['stratuslab.endpoint'] = self.ch.config['stratuslab.endpoint']
        self.user_info['stratuslab.ip.type'] = self.ch.config['stratuslab.ip.type']
        self.user_info['stratuslab.marketplace.endpoint'] = self.ch.config['stratuslab.marketplace.endpoint']
        self.user_info['stratuslab.password'] = self.ch.config['stratuslab.password']
        self.user_info['General.ssh.public.key'] = self.ch.config['General.ssh.public.key']
        self.user_info['stratuslab.username'] = self.ch.config['stratuslab.username']
        self.user_info['User.firstName'] = 'Foo'
        self.user_info['User.lastName'] = 'Bar'
        self.user_info['User.email'] = 'dont@bother.me'

        extra_disk_volatile = self.ch.config['stratuslab.extra.disk.volatile']
        image_id = self.ch.config['stratuslab.imageid']
        self.multiplicity = int(self.ch.config.get('stratuslab.multiplicity', 2))
        self.max_iaas_workers = self.ch.config.get('stratuslab.max.iaas.workers', 10)

        self.node_name = 'test_node'
        self.node_instances = {}
        for i in range(1, self.multiplicity + 1):
            node_instance_name = self.node_name + '.' + str(i)
            self.node_instances[node_instance_name] = NodeInstance({
                NodeDecorator.NODE_NAME_KEY: self.node_name,
                NodeDecorator.NODE_INSTANCE_NAME_KEY: node_instance_name,
                'cloudservice': 'stratuslab',
                'extra.disk.volatile': extra_disk_volatile,
                'image.resourceUri': '',
                'image.platform': 'Ubuntu',
                'image.imageId': image_id,
                'image.id': image_id,
                'stratuslab.instance.type': 'm1.small',
                'stratuslab.disks,bus.type': 'virtio',
                'stratuslab.cpu': '',
                'stratuslab.ram': '',
                'network': 'public'
            })

        self.node_instance = NodeInstance({
            NodeDecorator.NODE_NAME_KEY: NodeDecorator.MACHINE_NAME,
            NodeDecorator.NODE_INSTANCE_NAME_KEY: NodeDecorator.MACHINE_NAME,
            'cloudservice': 'stratuslab',
            'extra.disk.volatile': extra_disk_volatile,
            'image.resourceUri': '',
            'image.platform': 'Ubuntu',
            'image.imageId': image_id,
            'image.id': image_id,
            'stratuslab.instance.type': 'm1.small',
            'stratuslab.disks,bus.type': 'virtio',
            'stratuslab.cpu': '',
            'stratuslab.ram': '',
            'network': 'public',
            'image.prerecipe':
"""#!/bin/sh
set -e
set -x

ls -l /tmp
dpkg -l | egrep "nano|lvm" || true
""",
            'image.packages' : ['lvm2', 'nano'],
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

    def _get_config_file(self):
        return CONFIG_FILE
