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
from slipstream_stratuslab.StratusLabIterClientCloud import StratusLabIterClientCloud
from TestStratusLabLiveBase import TestStratusLabLiveBase


class TestStratusLabIterClientCloudLive(TestStratusLabLiveBase):

    def xtest_1_create_delete_volume(self):
        self.client = StratusLabIterClientCloud(self.ch)
        self.client._set_user_info_on_stratuslab_config_holder(self.user_info)

        size = int(self.node_instance.get_volatile_extra_disk_size())
        uuid = self.client._volume_create(size, 'big disk')
        assert self.client._volume_exists(uuid)
        assert uuid == self.client._volume_delete(uuid)

    def xtest_2_start_stop_images(self):

        self.client = StratusLabIterClientCloud(self.ch)
        self.client._publish_vm_info = Mock()

        self.client._get_max_workers = Mock(return_value=self.max_iaas_workers)

        try:
            self.client.start_nodes_and_clients(self.user_info, self.node_instances)

            util.printAndFlush('Instances started\n')

            vms = self.client.get_vms()
            assert len(vms) == int(self.multiplicity)

            runners = vms.values()
            for runner in runners:
                vm_id = runner.vmIds[0]
                state = self.client._wait_vm_in_state(['Running', ], runner, vm_id,
                                                      counts=50, sleep=6, throw=True)
                assert 'Running' == state
        finally:
            self.client.stop_deployment()

    def xtest_3_start_stop_images_by_ids(self):

        self.client = StratusLabIterClientCloud(self.ch)
        self.client._publish_vm_info = Mock()

        self.client._get_max_workers = Mock(return_value=self.max_iaas_workers)

        vm_ids = []
        try:
            self.client.start_nodes_and_clients(self.user_info, self.node_instances)

            util.printAndFlush('Instances started\n')

            vms = self.client.get_vms()
            assert len(vms) == int(self.multiplicity)

            runners = vms.values()
            for runner in runners:
                vm_id = runner.vmIds[0]
                state = self.client._wait_vm_in_state(['Running', ], runner, vm_id,
                                                      counts=50, sleep=6, throw=True)
                assert 'Running' == state
                vm_ids.append(vm_id)
        finally:
            self.client.stop_vms_by_ids(vm_ids)


if __name__ == '__main__':
    unittest.main()
