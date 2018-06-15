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

from slipstream.command.RunInstancesCommand import RunInstancesCommand
from slipstream.UserInfo import UserInfo
from slipstream_openstack.OpenStackCommand import OpenStackCommand
from slipstream_openstack.OpenStackClientCloud import FLOATING_IPS_KEY, REUSE_FLOATING_IPS_KEY


class OpenStackRunInstances(RunInstancesCommand, OpenStackCommand):

    INSTANCE_TYPE_KEY = 'instance-type'
    SECURITY_GROUPS_KEY = 'security-groups'
    NETWORK_PUBLIC_KEY = 'network-public'
    NETWORK_PRIVATE_KEY = 'network-private'
    USE_FLOATING_IP = 'use-floating-ips'
    REUSE_FLOATING_IP = 'reuse-floating-ips'

    def __init__(self):
        super(OpenStackRunInstances, self).__init__()

    def set_cloud_specific_options(self, parser):
        OpenStackCommand.set_cloud_specific_options(self, parser)

        self.parser.add_option('--' + self.INSTANCE_TYPE_KEY, dest=self.INSTANCE_TYPE_KEY,
                               help='Instance Type (Flavor)',
                               default=None, metavar='TYPE')

        self.parser.add_option('--' + self.SECURITY_GROUPS_KEY, dest=self.SECURITY_GROUPS_KEY,
                               help='Comma separated list of security groups',
                               default='', metavar='SECGROUPS')

        self.parser.add_option('--' + self.NETWORK_PUBLIC_KEY, dest=self.NETWORK_PUBLIC_KEY,
                               help='Mapping for Public network (default: "")',
                               default='', metavar='NAME')

        self.parser.add_option('--' + self.NETWORK_PRIVATE_KEY, dest=self.NETWORK_PRIVATE_KEY,
                               help='Mapping for Private network (default: "")',
                               default='', metavar='NAME')

        self.parser.add_option('--' + self.USE_FLOATING_IP, dest=self.USE_FLOATING_IP,
                               help='Use Floating IPs for the public network. '
                                    'Use --' + self.NETWORK_PUBLIC_KEY + 'to define the ip-pool',
                               action='store_true', default=False)

        self.parser.add_option('--' + self.REUSE_FLOATING_IP, dest=self.REUSE_FLOATING_IP,
                               help='Do not allocate new Floating IPs. '
                                    'Reuse already allocated and unused Floating IPs',
                               action='store_true', default=False)

    def get_cloud_specific_user_cloud_params(self):
        user_params = OpenStackCommand.get_cloud_specific_user_cloud_params(self)
        user_params[UserInfo.NETWORK_PUBLIC_KEY] = self.get_option(self.NETWORK_PUBLIC_KEY)
        user_params[UserInfo.NETWORK_PRIVATE_KEY] = self.get_option(self.NETWORK_PRIVATE_KEY)
        user_params[FLOATING_IPS_KEY]= self.get_option(self.USE_FLOATING_IP)
        user_params[REUSE_FLOATING_IPS_KEY]= self.get_option(self.REUSE_FLOATING_IP)
        return user_params

    def get_cloud_specific_node_inst_cloud_params(self):
        return {'security.groups': self.get_option(self.SECURITY_GROUPS_KEY),
                'instance.type': self.get_option(self.INSTANCE_TYPE_KEY)}

    def get_cloud_specific_mandatory_options(self):
        return OpenStackCommand.get_cloud_specific_mandatory_options(self) + \
               [self.INSTANCE_TYPE_KEY,
                self.SECURITY_GROUPS_KEY]
