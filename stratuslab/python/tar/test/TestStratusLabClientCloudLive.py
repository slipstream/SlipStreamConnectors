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


if __name__ == '__main__':
    unittest.main()
