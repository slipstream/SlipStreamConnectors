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

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from slipstream.command.CloudClientCommand import main
from slipstream.command.DescribeInstancesCommand import DescribeInstancesCommand
from slipstream_opennebula.OpenNebulaCommand import OpenNebulaCommand
from slipstream_opennebula.OpenNebulaClientCloud import OpenNebulaClientCloud


class OpenNebulaDescribeInstances(DescribeInstancesCommand, OpenNebulaCommand):

    VM_LCM_STATE = [
        'Lcm init',                         # 0
        'Prolog',                           # 1
        'Boot',                             # 2
        'Running',                          # 3
        'Migrate',                          # 4
        'Save stop',                        # 5
        'Save suspend',                     # 6
        'Save migrate',                     # 7
        'Prolog migrate',                   # 8
        'Prolog resume',                    # 9
        'Epilog stop',                      # 10
        'Epilog',                           # 11
        'Shutdown',                         # 12
        '//Cancel',                         # 13
        '//Failure',                        # 14
        'Cleanup resubmit',                 # 15
        'Unknown',                          # 16
        'Hotplug',                          # 17
        'Shutdown poweroff',                # 18
        'Boot unknown',                     # 19
        'Boot poweroff',                    # 20
        'Boot suspended',                   # 21
        'Boot stopped',                     # 22
        'Cleanup delete',                   # 23
        'Hotplug snapshot',                 # 24
        'Hotplug nic',                      # 25
        'Hotplug saveas',                   # 26
        'Hotplug saveas poweroff',          # 27
        'Hotplug saveas suspended',         # 28
        'Shutdown undeploy',                # 29
        'Epilog undeploy',                  # 30
        'Prolog undeploy',                  # 31
        'Boot undeploy',                    # 32
        'Hotplug prolog poweroff',          # 33
        'Hotplug epilog poweroff',          # 34
        'Boot migrate',                     # 35
        'Boot failure',                     # 36
        'Boot migrate failure',             # 37
        'Prolog migrate failure',           # 38
        'Prolog failure',                   # 39
        'Epilog failure',                   # 40
        'Epilog stop failure',              # 41
        'Epilog undeploy failure',          # 42
        'Prolog migrate poweroff',          # 43
        'Prolog migrate poweroff failure',  # 44
        'Prolog migrate suspend',           # 45
        'Prolog migrate suspend failure',   # 46
        'Boot undeploy failure',            # 47
        'Boot stopped failure',             # 48
        'Prolog resume failure',            # 49
        'Prolog undeploy failure',          # 50
        'Disk snapshot poweroff',           # 51
        'Disk snapshot revert poweroff',    # 52
        'Disk snapshot delete poweroff',    # 53
        'Disk snapshot suspended',          # 54
        'Disk snapshot revert suspended',   # 55
        'Disk snapshot delete suspended',   # 56
        'Disk snapshot',                    # 57
        'Disk snapshot revert',             # 58
        'Disk snapshot delete',             # 59
        'Prolog migrate unknown',           # 60
        'Prolog migrate unknown failure'    # 61
    ]

    def _vm_get_state(self, cc, vm):
        vm_state = int(vm.findtext('STATE'))
        if vm_state == OpenNebulaClientCloud.VM_STATE.index('Active'):
            return self.VM_LCM_STATE[int(vm.findtext('LCM_STATE'))]
        return OpenNebulaClientCloud.VM_STATE[vm_state]

    def _vm_get_id(self, cc, vm):
        return vm.findtext('ID')

    def __init__(self):
        super(OpenNebulaDescribeInstances, self).__init__()


if __name__ == "__main__":
    main(OpenNebulaDescribeInstances)
