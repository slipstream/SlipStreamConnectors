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

import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

from slipstream.command.ServiceOffersCommand import ServiceOffersCommand
from slipstream_opennebula.OpenNebulaCommand import OpenNebulaCommand


class OpenNebulaServiceOffersCommand(OpenNebulaCommand, ServiceOffersCommand):
    CPU_MAX_KEY = 'cpu-max'
    RAM_MAX_KEY = 'ram-max'
    DISK_MAX_KEY = 'disk-max'
    DISK_INTERVAL_KEY = 'disk-interval'
    ENDPOINT = ""

    def __init__(self):
        super(OpenNebulaServiceOffersCommand, self).__init__()

    def _list_vm_sizes(self):
        vm_sizes = []
        for cpu in range(1, self.get_option(self.CPU_MAX_KEY) + 1, 1)[1:]:
            for ram in range(512, (self.get_option(self.RAM_MAX_KEY) * 1024) + 512, 512)[1:]:
                vm_sizes.append({'cpu': cpu, 'ram': ram})
        return vm_sizes

    def _get_cpu(self, vm_size):
        return vm_size['cpu']

    def _get_ram(self, vm_size):
        return vm_size['ram']

    def _get_root_disk_sizes(self, vm_size, os):
        return range(10, self.get_option(self.DISK_MAX_KEY) + self.get_option(self.DISK_INTERVAL_KEY), self.get_option(self.DISK_INTERVAL_KEY))[1:]

    def set_cloud_specific_options(self, parser):
        super(OpenNebulaCommand, self).set_cloud_specific_options(parser)

        parser.add_option('--' + self.CPU_MAX_KEY, dest=self.CPU_MAX_KEY,
                          help='Max number of vCPU available per virtual machine', metavar='NUMBER', type='int')

        parser.add_option('--' + self.RAM_MAX_KEY, dest=self.RAM_MAX_KEY,
                          help='Max number of RAM in GiB available per virtual machine', metavar='NUMBER', type='int')

        parser.add_option('--' + self.DISK_MAX_KEY, dest=self.DISK_MAX_KEY,
                          help='Max number of disk in GiB available per virtual machine', metavar='NUMBER', type='int')

        parser.add_option('--' + self.DISK_INTERVAL_KEY, dest=self.DISK_INTERVAL_KEY, default=10, metavar='NUMBER',
                          type='int', help='Interval of disk space between two service offers in (GiB). Default: 10')

    def get_cloud_specific_mandatory_options(self):
        return [self.CPU_MAX_KEY,
                self.RAM_MAX_KEY,
                self.DISK_MAX_KEY]

    def _get_common_mandatory_options(self):
        return []

    def get_cloud_specific_user_cloud_params(self):
        return {}