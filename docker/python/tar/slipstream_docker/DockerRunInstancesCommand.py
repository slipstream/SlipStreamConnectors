#!/usr/bin/env python
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

from slipstream.command.CloudClientCommand import main
from slipstream.command.RunInstancesCommand import RunInstancesCommand
from slipstream_docker.DockerCommand import DockerCommand
from slipstream.NodeDecorator import NodeDecorator
from slipstream.NodeInstance import NodeInstance
from slipstream_docker.DockerClientCloud import DockerClientCloud


class DockerRunInstances(RunInstancesCommand, DockerCommand):
    NETWORK_PORTS_MAPPINGS_KEY = DockerClientCloud.NETWORK_PORTS_MAPPINGS_KEY
    MOUNTS_KEY = DockerClientCloud.MOUNTS_KEY
    RESTART_POLICY_KEY = DockerClientCloud.RESTART_POLICY_KEY
    ENV_KEY = DockerClientCloud.ENV_KEY
    WORKING_DIR_KEY = DockerClientCloud.WORKING_DIR_KEY
    COMMAND_KEY = DockerClientCloud.COMMAND_KEY
    ARGS_KEY = DockerClientCloud.ARGS_KEY
    CPU_RATIO_KEY = DockerClientCloud.CPU_RATIO_KEY
    MEMORY_KEY = DockerClientCloud.MEMORY_KEY

    def __init__(self):
        super(DockerRunInstances, self).__init__()

    def set_cloud_specific_options(self, parser):
        DockerCommand.set_cloud_specific_options(self, parser)

        self.parser.add_option('--' + self.NETWORK_PORTS_MAPPINGS_KEY, action='append',
                               dest=self.NETWORK_PORTS_MAPPINGS_KEY,
                               help='Publish a service port(s) to the host. '
                                    'Format is <PROTOCOL>:<PUBLISHED_PORT>:<TARGET_PORT>. '
                                    'This option can be used multiple times. If PUBLISHED_PORT is omitted, '
                                    'a random port will be assigned (e.g. tcp:20000:22 or for dynamic port tcp::22).'
                                    'You can also specify a range of ports '
                                    '(e.g. tcp:62000-62005:6000-6005 or tcp::6000-6005 for dynamic ports).')

        self.parser.add_option('--' + self.MOUNTS_KEY, action='append',
                               dest=self.MOUNTS_KEY,
                               help='Consists of multiple key-value pairs, separated by commas and each consisting of '
                                    'a <key>=<value> tuple. This option can be used multiple times. '
                                    'Format is '
                                    'type=[volume,bind,tmpfs],src=<VOLUME-NAME>,dst=<CONTAINER-PATH>,[readonly] '
                                    '(e.g. type=volume,src=nginx-vol,dst=/usr/share/nginx/html,readonly).')

        self.parser.add_option('--' + self.RESTART_POLICY_KEY, default='none', dest=self.RESTART_POLICY_KEY,
                               help='Restart when condition is met ("none"|"on-failure"|"any"). Default: "none"')

        self.parser.add_option('--' + self.ENV_KEY, dest=self.ENV_KEY, action='append',
                               help='Set environment variables. This option can be used multiple times. '
                                    '(e.g. VAR=value)')

        self.parser.add_option('--' + self.WORKING_DIR_KEY, dest=self.WORKING_DIR_KEY,
                               help='The working directory for commands to run in.')

        self.parser.add_option('--' + self.COMMAND_KEY, dest=self.COMMAND_KEY,
                               help='The command to be run in the image.')

        self.parser.add_option('--' + self.ARGS_KEY, dest=self.ARGS_KEY, action='append',
                               help='Arguments to the command.')

        self.parser.add_option('--' + self.CPU_RATIO_KEY, dest=self.CPU_RATIO_KEY,
                               help='CPU ratio limit and reserved in float. Max is 1.0')

        self.parser.add_option('--' + self.MEMORY_KEY, dest=self.MEMORY_KEY,
                               help='Memory limit and reserved in GB. Float value.')

    def _set_command_specific_options(self, parser):
        super(DockerRunInstances, self)._set_command_specific_options(parser)
        parser.remove_option('--' + self.PLATFORM_KEY)
        parser.remove_option('--' + self.EXTRA_DISK_VOLATILE)
        parser.remove_option('--' + self.LOGIN_USER_KEY)
        parser.remove_option('--' + self.LOGIN_PASS_KEY)
        parser.remove_option('--' + self.NETWORK_TYPE)
        parser.remove_option('--' + NodeDecorator.NATIVE_CONTEXTUALIZATION_KEY)

    def _get_command_specific_user_cloud_params(self):
        return {}

    def _get_node_instance(self):
        runtime_parameters = {
            NodeDecorator.NODE_INSTANCE_NAME_KEY: self.get_node_instance_name(),
            'cloudservice': self._cloud_instance_name,
            'image.id': self.get_option(self.IMAGE_ID_KEY)}

        return NodeInstance(runtime_parameters)

    def get_cloud_specific_node_inst_cloud_params(self):
        node_params = DockerCommand.get_cloud_specific_node_inst_cloud_params(self)
        return node_params

    def _get_command_specific_node_inst_cloud_params(self):
        return {self.NETWORK_PORTS_MAPPINGS_KEY: self.get_option(self.NETWORK_PORTS_MAPPINGS_KEY),
                self.MOUNTS_KEY: self.get_option(self.MOUNTS_KEY),
                self.RESTART_POLICY_KEY: self.get_option(self.RESTART_POLICY_KEY),
                self.ENV_KEY: self.get_option(self.ENV_KEY),
                self.WORKING_DIR_KEY: self.get_option(self.WORKING_DIR_KEY),
                self.COMMAND_KEY: self.get_option(self.COMMAND_KEY),
                self.ARGS_KEY: self.get_option(self.ARGS_KEY),
                self.CPU_RATIO_KEY: self.get_option(self.CPU_RATIO_KEY),
                self.MEMORY_KEY: self.get_option(self.MEMORY_KEY)}

    def get_cloud_specific_mandatory_options(self):
        return DockerCommand.get_cloud_specific_mandatory_options(self)

    def _get_command_mandatory_options(self):
        return [self.IMAGE_ID_KEY]


if __name__ == "__main__":
    main(DockerRunInstances)
