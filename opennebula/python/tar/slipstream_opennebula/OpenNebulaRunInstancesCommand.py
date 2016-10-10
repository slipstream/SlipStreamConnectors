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
from slipstream.command.RunInstancesCommand import RunInstancesCommand
from slipstream_opennebula.OpenNebulaCommand import OpenNebulaCommand


class OpenNebulaRunInstances(RunInstancesCommand, OpenNebulaCommand):

    NETWORK_PUBLIC_KEY = 'network-public'
    NETWORK_PRIVATE_KEY = 'network-private'
    CPU_KEY = 'cpu'
    RAM_KEY = 'ram'
    CUSTOM_VM_TEMPLATE_KEY = 'custom-vm-template'
    NETWORK_SPECIFIC_NAME_KEY = 'network-specific-name'

    def __init__(self):
        super(OpenNebulaRunInstances, self).__init__()

    def set_cloud_specific_options(self, parser):
        OpenNebulaCommand.set_cloud_specific_options(self, parser)

        self.parser.add_option('--' + self.NETWORK_PUBLIC_KEY, dest=self.NETWORK_PUBLIC_KEY,
                               help='Mapping for Public network (default: "")',
                               default='', metavar='ID')

        self.parser.add_option('--' + self.NETWORK_PRIVATE_KEY, dest=self.NETWORK_PRIVATE_KEY,
                               help='Mapping for Private network (default: "")',
                               default='', metavar='ID')

        self.parser.add_option('--' + self.CPU_KEY, dest=self.CPU_KEY,
                               help='Number of CPUs.',
                               default='', metavar='CPU')

        self.parser.add_option('--' + self.RAM_KEY, dest=self.RAM_KEY,
                               help='RAM in GB.',
                               default='', metavar='RAM')

        self.parser.add_option('--' + self.CUSTOM_VM_TEMPLATE_KEY, dest=self.CUSTOM_VM_TEMPLATE_KEY,
                               help='Additional VM template e.g. ' +
                                    '\'GRAPHICS = [ TYPE = VNC, LISTEN = 0.0.0.0, PORT = 5900 ]\'',
                               default='', metavar='CUSTOM_VM_TEMPLATE')

        self.parser.add_option('--' + self.NETWORK_SPECIFIC_NAME_KEY, dest=self.NETWORK_SPECIFIC_NAME_KEY,
                               help='Override network in Cloud configuration section! ' +
                                    'Connect VM network interface on specified virtual network name. ' +
                                    'Format: <NETWORK_NAME> or <NETWORK_NAME;NETWORK_UNAME>',
                               default='', metavar='NETWORK_NAME')

    def get_cloud_specific_user_cloud_params(self):
        user_params = OpenNebulaCommand.get_cloud_specific_user_cloud_params(self)
        user_params['network.public'] = self.get_option(self.NETWORK_PUBLIC_KEY)
        user_params['network.private'] = self.get_option(self.NETWORK_PRIVATE_KEY)
        return user_params

    def get_cloud_specific_node_inst_cloud_params(self):
        return {'cpu': self.get_option(self.CPU_KEY),
                'ram': self.get_option(self.RAM_KEY),
                'custom.vm.template': self.get_option(self.CUSTOM_VM_TEMPLATE_KEY),
                'network.specific.name': self.get_option(self.NETWORK_SPECIFIC_NAME_KEY)}

    def get_cloud_specific_mandatory_options(self):
        return OpenNebulaCommand.get_cloud_specific_mandatory_options(self)


if __name__ == "__main__":
    main(OpenNebulaRunInstances)
