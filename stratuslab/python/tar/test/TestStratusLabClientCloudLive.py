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

from slipstream import util
from slipstream.NodeDecorator import NodeDecorator, RUN_CATEGORY_IMAGE

from TestStratusLabLiveBase import TestStratusLabLiveBase


class TestStratusLabClientCloudLive(TestStratusLabLiveBase):

    def xtest_1_start_stop_images(self):

        self.client._get_max_workers = Mock(return_value=self.max_iaas_workers)

        try:
            self.client.start_nodes_and_clients(self.user_info, self.node_instances)

            util.printAndFlush('Instances started\n')

            vms = self.client.get_vms()
            assert len(vms) == int(self.multiplicity)
        finally:
            self.client.stop_deployment()

    def xtest_2_build_image(self):

        self.client.run_category = RUN_CATEGORY_IMAGE
        self.client._prepare_machine_for_build_image = Mock()

        self.client.start_nodes_and_clients(
            self.user_info, {NodeDecorator.MACHINE_NAME: self.node_instance})
        instances_details = self.client.get_vms_details()

        assert instances_details
        assert instances_details[0][NodeDecorator.MACHINE_NAME]

        new_id = self.client.build_image(self.user_info, self.node_instance)
        # StratusLab doesn't provide us with image ID
        assert new_id == ''

if __name__ == '__main__':
    unittest.main()
