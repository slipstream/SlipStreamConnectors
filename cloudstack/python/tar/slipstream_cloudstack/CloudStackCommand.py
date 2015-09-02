"""
 SlipStream Client
 =====
 Copyright (C) 2013 SixSq Sarl (sixsq.com)
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
from slipstream_cloudstack.CloudStackClientCloud import CloudStackClientCloud


class CloudStackCommand(CloudClientCommand):

    ENDPOINT_KEY = 'endpoint'
    ZONE_KEY = 'zone'

    def __init__(self):
        super(CloudStackCommand, self).__init__()

    def get_connector_class(self):
        return CloudStackClientCloud

    def set_cloud_specific_options(self, parser):
        self.parser.add_option('--' + self.ENDPOINT_KEY, dest=self.ENDPOINT_KEY,
                               help='Endpoint', default='', metavar='ENDPOINT')

        self.parser.add_option('--' + self.ZONE_KEY, dest=self.ZONE_KEY,
                               help='Zone', default='', metavar='ZONE')

    def get_cloud_specific_user_cloud_params(self):
        return {self.ENDPOINT_KEY: self.get_option(self.ENDPOINT_KEY),
                self.ZONE_KEY: self.get_option(self.ZONE_KEY)}

    def get_cloud_specific_mandatory_options(self):
        return [self.ZONE_KEY,
                self.ENDPOINT_KEY]
