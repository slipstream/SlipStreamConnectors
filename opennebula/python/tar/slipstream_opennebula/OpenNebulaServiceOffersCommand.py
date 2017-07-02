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

import math
from slipstream.command.ServiceOffersCommand import ServiceOffersCommand
from slipstream_opennebula.OpenNebulaCommand import OpenNebulaCommand
from slipstream.util import override


class OpenNebulaServiceOffersCommand(OpenNebulaCommand, ServiceOffersCommand):
    CPU_MAX_KEY = 'cpu-max'
    RAM_MAX_KEY = 'ram-max'
    DISK_MAX_KEY = 'disk-max'
    DISK_INTERVAL_KEY = 'disk-interval'
    ENDPOINT = ""

    def __init__(self):
        super(OpenNebulaServiceOffersCommand, self).__init__()

    def __get_interval(self, interval, max):
        return range(interval, max + interval, interval)

    @staticmethod
    def _get_ram_range(max_ram):
        ram_list = [512]

        exp = 5
        while True:
            last_ram = ram_list[-1]
            next_ram = None

            if last_ram < 1024:
                next_ram = last_ram + 256
            elif last_ram < 6144:
                next_ram = last_ram + 1024
            elif last_ram < 16384:
                next_ram = last_ram + 2048
            else:
                next_ram = 2 ** exp * 1024
                exp += 1

            if next_ram is not None and next_ram <= max_ram:
                ram_list.append(next_ram)
            else:
                break

        return ram_list

    @staticmethod
    def _get_cpu_range(max_cpu):
        base = 2
        return [base ** i for i in range(int(math.log(max_cpu,base))+1)]

    @override
    def _list_vm_sizes(self):
        vm_sizes = []
        for cpu in self._get_cpu_range(self.get_option(self.CPU_MAX_KEY)):
            for ram in self._get_ram_range(self.get_option(self.RAM_MAX_KEY) * 1024):
                vm_sizes.append({'cpu': cpu, 'ram': ram})
        return vm_sizes

    @override
    def _get_cpu(self, vm_size):
        return vm_size['cpu']

    @override
    def _get_ram(self, vm_size):
        return vm_size['ram']

    @override
    def _get_root_disk_sizes(self, vm_size, os):
        return self.__get_interval(self.get_option(self.DISK_INTERVAL_KEY), self.get_option(self.DISK_MAX_KEY))

    @override
    def set_cloud_specific_options(self, parser):
        super(OpenNebulaCommand, self).set_cloud_specific_options(parser)

        parser.add_option('--' + self.CPU_MAX_KEY, dest=self.CPU_MAX_KEY, default=8,
                          help='Max number of vCPU available per virtual machine', metavar='NUMBER', type='int')

        parser.add_option('--' + self.RAM_MAX_KEY, dest=self.RAM_MAX_KEY, default=14,
                          help='Max number of RAM in GiB available per virtual machine', metavar='NUMBER', type='int')

        parser.add_option('--' + self.DISK_MAX_KEY, dest=self.DISK_MAX_KEY, default=200,
                          help='Max number of disk in GiB available per virtual machine', metavar='NUMBER', type='int')

        parser.add_option('--' + self.DISK_INTERVAL_KEY, dest=self.DISK_INTERVAL_KEY, default=10, metavar='NUMBER',
                          type='int', help='Interval of disk space between two service offers in (GiB). Default: 10')

    def get_cloud_specific_mandatory_options(self):
        return []

    def _get_common_mandatory_options(self):
        return []

    def get_cloud_specific_user_cloud_params(self):
        return {}
