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

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from slipstream.command.CloudClientCommand import main
from slipstream.command.RunInstancesCommand import RunInstancesCommand
from slipstream_docker.DockerCommand import DockerCommand
from slipstream.NodeDecorator import NodeDecorator
from slipstream.NodeInstance import NodeInstance

class DockerRunInstances(RunInstancesCommand, DockerCommand):

    SERVICE_REQUEST = "service"

    def __init__(self):
        super(DockerRunInstances, self).__init__()

    def set_cloud_specific_options(self, parser):
        DockerCommand.set_cloud_specific_options(self, parser)

        self.parser.add_option('--' + self.SERVICE_REQUEST, dest=self.SERVICE_REQUEST,
                          help='Service request to be passed to Docker',
                          default='', metavar='SERVICE-REQUEST')
    
    def _set_command_specific_options(self, parser):
        pass

    def _get_command_specific_user_cloud_params(self):
        # NodeDecorator.NATIVE_CONTEXTUALIZATION_KEY doesn't apply here, and it doesn't even exist anymore
        # so simply force return {} as it line 97 of RunInstancesCommand.py
        return {}

    def _get_node_instance(self):
        # the runtime parameters are not the same as for VMs
        runtime_parameters = {
            NodeDecorator.NODE_INSTANCE_NAME_KEY: self.get_node_instance_name(),
            'cloudservice': self._cloud_instance_name
        }

        return NodeInstance(runtime_parameters)

    def get_cloud_specific_node_inst_cloud_params(self):
        node_params = DockerCommand.get_cloud_specific_node_inst_cloud_params(self)
        node_params[self.SERVICE_REQUEST] = self.get_option(self.SERVICE_REQUEST)
        return node_params

    def _get_command_specific_node_inst_cloud_params(self):
        # LOGIN_PASS_KEY does not apply to the Docker connector
        cloud_params = {}
        return cloud_params

    def get_cloud_specific_mandatory_options(self):
        return DockerCommand.get_cloud_specific_mandatory_options(self)

    def _get_command_mandatory_options(self):
        # Remove USER PASS from mandatory parameters as we might be dealing
        # with a no protected cluster
        return [self.SERVICE_REQUEST]

if __name__ == "__main__":
    main(DockerRunInstances)
