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

from slipstream.command.CloudClientCommand import CloudClientCommand
from slipstream_openstack.OpenStackClientCloud import OpenStackClientCloud, \
    STATE_MAP


class OpenStackCommand(CloudClientCommand):

    STATE_MAP = STATE_MAP

    DOMAIN_KEY = 'domain'
    REGION_KEY = 'region'
    PROJECT_KEY = 'project'
    ENDPOINT_KEY = 'endpoint'
    SERVICE_TYPE_KEY = 'service-type'
    SERVICE_NAME_KEY = 'service-name'
    IDENTITY_VERSION_KEY = 'identity-version'

    def __init__(self):
        super(OpenStackCommand, self).__init__()

    def get_connector_class(self):
        return OpenStackClientCloud

    def set_cloud_specific_options(self, parser):
        parser.add_option('--' + self.ENDPOINT_KEY, dest=self.ENDPOINT_KEY, help='Identity service (Keystone)',
                          default='', metavar='ENDPOINT')

        parser.add_option('--' + self.REGION_KEY, dest=self.REGION_KEY, help='Region (default: regionOne)',
                          default='regionOne', metavar='REGION')

        parser.add_option('--' + self.DOMAIN_KEY, dest=self.DOMAIN_KEY, help='Domain (Identity v3 only)',
                          default='', metavar='DOMAIN')

        parser.add_option('--' + self.PROJECT_KEY, dest=self.PROJECT_KEY, help='Project (Tenant)',
                          default='', metavar='PROJECT')

        parser.add_option('--' + self.IDENTITY_VERSION_KEY, dest=self.IDENTITY_VERSION_KEY,
                          help='Identity API version (v2|v3)', default='v2', metavar='VERSION')

        parser.add_option('--' + self.SERVICE_TYPE_KEY, dest=self.SERVICE_TYPE_KEY,
                          help='Type-name of the service which provides the instances functionality (default: compute)',
                          default='compute', metavar='TYPE')

        parser.add_option('--' + self.SERVICE_NAME_KEY, dest=self.SERVICE_NAME_KEY,
                          help='Name of the service which provides the instances functionality (optional)',
                          default=None, metavar='NAME')

    def get_cloud_specific_user_cloud_params(self):
        return {'tenant-name': self.get_option(self.PROJECT_KEY),
                'serviceRegion': self.get_option(self.REGION_KEY),
                'domain-name': self.get_option(self.DOMAIN_KEY),
                self.ENDPOINT_KEY: self.get_option(self.ENDPOINT_KEY),
                'serviceType': self.get_option(self.SERVICE_TYPE_KEY),
                'serviceName': self.get_option(self.SERVICE_NAME_KEY),
                'identityVersion': self.get_option(self.IDENTITY_VERSION_KEY)}

    def get_cloud_specific_mandatory_options(self):
        return [self.REGION_KEY,
                self.PROJECT_KEY,
                self.ENDPOINT_KEY,
                self.SERVICE_TYPE_KEY]
