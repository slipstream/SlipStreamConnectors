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


class DockerRunInstances(RunInstancesCommand, DockerCommand):

    NETWORK_PUBLIC_KEY = 'network-public'
    NETWORK_PRIVATE_KEY = 'network-private'
    CPU_KEY = 'cpu'
    RAM_KEY = 'ram'
    CUSTOM_VM_TEMPLATE_KEY = 'custom-vm-template'
    NETWORK_SPECIFIC_NAME_KEY = 'network-specific-name'
    CONTEXTUALIZATION_TYPE_KEY = 'contextualization-type'

    REQUEST_BODY = "instance-namespace"


    def __init__(self):
        super(DockerRunInstances, self).__init__()

    def set_cloud_specific_options(self, parser):
        DockerCommand.set_cloud_specific_options(self, parser)

        self.parser.add_option('--' + self.INSTANCES_NAMESPACE, dest=self.INSTANCES_NAMESPACE,
                          help='Namespace where the instances are',
                          default=[], metavar='NAMESPACE')

    def get_cloud_specific_mandatory_options(self):
        # return KubernetesCommand.get_cloud_specific_mandatory_options(self).append(self.INSTANCES_NAMESPACE)
        return DockerCommand.get_cloud_specific_mandatory_options(self)


if __name__ == "__main__":
    main(DockerRunInstances)
