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

import re
import unittest
from mock import Mock

from slipstream_stratuslab.StratusLabIterClientCloud import StratusLabIterClientCloud
from TestStratusLabLiveBase import TestStratusLabLiveBase

TEST_MANIFEST_FILE = 'N-Bu1h1jt3K8ODnCTw4JiyPaH5k.xml'

# Mock manifest downloader to prevent contacting Marketplace.
# Use local test manifest.
import stratuslab.marketplace.ManifestDownloader
manifest = open(TEST_MANIFEST_FILE).read()
manifest_et = stratuslab.marketplace.ManifestDownloader.ManifestDownloader._parseXml(manifest)
stratuslab.marketplace.ManifestDownloader.ManifestDownloader._download = Mock(return_value=manifest_et)

from stratuslab.vm_manager.Runner import Runner


class TestStratusLabIterClientCloud(TestStratusLabLiveBase):

    def xtest_1_Runner_patched_for_persistent_disk_size(self):
        assert re.search('persistentDiskSize', Runner.PERSISTENT_DISK, re.MULTILINE)

    def xtest_2_Runner_has_extra_disk_definition_with_size(self):
        self.client = StratusLabIterClientCloud(self.ch)
        self.client._initialization(self.user_info)

        ch = self.client.slConfigHolder.deepcopy()
        disk_uuid = '1-2-3-4'
        disk_size = '1234'
        self.node_instance.set_cloud_parameters({'extra_disk_persistent': disk_uuid})
        self.node_instance.set_cloud_parameters({'extra_disk_persistent_size': disk_size})
        self.client._set_extra_disks_on_config_holder(ch, self.node_instance)

        Runner._checkPersistentDiskAvailable = Mock()
        runner = self.client._get_stratuslab_runner(self.node_instance.get_image_id(), ch)
        vm_template = runner._buildVmTemplate(runner.vmTemplateFile)

        disks = re.findall('DISK\s*=\s*\[.*?\]', vm_template, re.MULTILINE | re.DOTALL)
        found = False
        for disk in disks:
            if re.search('source\s*=\s*.*%s' % disk_uuid, disk, re.M | re.I):
                assert None != re.search('size\s*=\s*%s' % disk_size, disk, re.M | re.I)
                found = True
        assert found


if __name__ == '__main__':
    unittest.main()
