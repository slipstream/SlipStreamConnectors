#!/usr/bin/env python
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

import unittest
from mock import Mock

from slipstream.NodeDecorator import NodeDecorator, RUN_CATEGORY_IMAGE
from slipstream.exceptions.Exceptions import ExecutionException

from TestStratusLabLiveBase import TestStratusLabLiveBase


class TestStratusLabClientCloudLive(TestStratusLabLiveBase):

    def xtest_1_start_stop_images(self):
        self._start_stop_instances()

    def xtest_2_start_stop_instances_by_ids(self):
        self._start_stop_instances_by_ids()

    def xtest_3_build_image(self):

        self.client.run_category = RUN_CATEGORY_IMAGE
        self.client._prepare_machine_for_build_image = Mock()

        self.client.start_nodes_and_clients(
            self.user_info, {NodeDecorator.MACHINE_NAME: self.node_instance})
        instances_details = self.client.get_vms_details()

        assert instances_details
        assert instances_details[0][NodeDecorator.MACHINE_NAME]

        new_id = self.client.build_image(self.user_info, self.node_instance)
        assert len(new_id) == len(self.node_instance.get_image_id())
        # TODO:
        # + assert that disk is in Markeptlace
        # ? start VM from this new disk
        #   - assert that VM starts
        #   - assert that can connect to the VM
        #   - stop the VM
        # + delete manifest from Marketplace
        # + delete volume from PDisk

    def xtest_4_vm_get_root_disk(self):
        vm = Mock()
        vm.template_disk_0_size = '123'
        assert '123' == self.client._vm_get_root_disk(vm)

        class vm:
            template_disk_source = '%s/%s' % (self.ch.config['stratuslab.marketplace.endpoint'],
                                              self.ch.config['stratuslab.imageid'])

        assert 0 < int(self.client._vm_get_root_disk(vm))

        # Search in PDisk.
        self.client._set_user_info_on_stratuslab_config_holder(self.user_info)

        # Fail to find volume in PDisk.
        class vm:
            template_disk_source = 'pdisk:154.48.152.10:8445:does-not-exist'

        try:
            self.client._vm_get_root_disk(vm)
        except ExecutionException as ex:
            if not str(ex).startswith('Failed to describe'):
                self.fail('Should have failed with "Failed to describe ..."')
        else:
            self.fail('Should have failed to find the volume.')

        # Succeed to find volume in PDisk and get its size.
        # NB! set to the volume uuid that current user has access to.
        test_volume_uuid = '2ed510f5-1ae2-4a27-86a3-e932ea761524'

        class vm:
            template_disk_source = 'pdisk:154.48.152.10:8445:%s' % test_volume_uuid

        assert 6 == int(self.client._vm_get_root_disk(vm))


if __name__ == '__main__':
    unittest.main()
