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

from slipstream_stratuslab.StratusLabIterClientCloud import StratusLabIterClientCloud
from TestStratusLabLiveBase import TestStratusLabLiveBase


class TestStratusLabIterClientCloudLive(TestStratusLabLiveBase):

    def _get_connector_class(self):
        return StratusLabIterClientCloud

    def xtest_1_create_delete_volume(self):
        self.client._set_user_info_on_stratuslab_config_holder(self.user_info)

        size = int(self.node_instance.get_volatile_extra_disk_size())
        uuid = self.client._volume_create(size, 'big disk')
        assert self.client._volume_exists(uuid)
        assert uuid == self.client._volume_delete(uuid)

    def xtest_2_start_stop_images(self):
        self._start_stop_instances()

    def xtest_3_start_stop_images_by_ids(self):
        self._start_stop_instances_by_ids()

if __name__ == '__main__':
    unittest.main()
