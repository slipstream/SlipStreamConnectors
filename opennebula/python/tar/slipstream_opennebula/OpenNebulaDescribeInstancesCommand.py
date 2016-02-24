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

    def _vm_get_state(self, cc, vm):
        return OpenNebulaClientCloud.VM_STATE[int(vm.findtext('STATE'))]

    def _vm_get_id(self, cc, vm):
        return vm.findtext('ID')

    def __init__(self):
        super(OpenNebulaDescribeInstances, self).__init__()


if __name__ == "__main__":
    main(OpenNebulaDescribeInstances)
