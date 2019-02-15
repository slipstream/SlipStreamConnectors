"""
 SlipStream Client
 =====
 Copyright (C) 2018 SixSq Sarl (sixsq.com)
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
from slipstream_docker.DockerClientCloud import DockerClientCloud
from slipstream.UserInfo import UserInfo


class DockerCommand(CloudClientCommand):
    CERT_KEY = DockerClientCloud.CERT_KEY
    KEY_KEY = DockerClientCloud.KEY_KEY

    def __init__(self):
        super(DockerCommand, self).__init__()

    def get_connector_class(self):
        return DockerClientCloud

    def set_cloud_specific_options(self, parser):
        parser.add_option('--' + UserInfo.CLOUD_ENDPOINT_KEY, dest=UserInfo.CLOUD_ENDPOINT_KEY,
                          help='Docker remote API endpoint (e.g. https://myswarm.com:2376/v1.35)',
                          default='', metavar='ENDPOINT')

    def _set_common_options(self, parser):
        parser.add_option('--' + self.CERT_KEY, dest=self.CERT_KEY,
                          help='Client certificate for the cluster', metavar='cert',
                          default='')
        parser.add_option('--' + self.KEY_KEY, dest=self.KEY_KEY,
                          help='Key to authenticate with the cluster', metavar='key',
                          default='')

    def get_cloud_specific_user_cloud_params(self):
        return {UserInfo.CLOUD_ENDPOINT_KEY: self.get_option(UserInfo.CLOUD_ENDPOINT_KEY)}

    def _get_common_user_cloud_params(self):
        return {self.CERT_KEY: self.get_option(self.CERT_KEY),
                self.KEY_KEY: self.get_option(self.KEY_KEY),
                UserInfo.CLOUD_ENDPOINT_KEY: self.get_option(UserInfo.CLOUD_ENDPOINT_KEY)}

    def get_cloud_specific_node_inst_cloud_params(self):
        return {UserInfo.CLOUD_ENDPOINT_KEY: self.get_option(UserInfo.CLOUD_ENDPOINT_KEY)}

    def _get_common_mandatory_options(self):
        return [UserInfo.CLOUD_ENDPOINT_KEY]

    def get_cloud_specific_mandatory_options(self):
        return [UserInfo.CLOUD_ENDPOINT_KEY]
