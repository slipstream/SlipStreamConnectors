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
from slipstream.command.DescribeInstancesCommand import DescribeInstancesCommand
from slipstream_docker.DockerCommand import DockerCommand
from slipstream_docker.DockerClientCluster import DockerClientCluster


class DockerDescribeInstances(DescribeInstancesCommand, DockerCommand):

    # def _vm_get_state(self, cc, vm):
    #     return vm['status']['phase']
    #
    # def _vm_get_id(self, cc, vm):
    #     return vm['metadata']['uid']

    def _print_results(self, cc, vms):
        print "id, name, namespace, node name, image, state, ip, " \
                "port mappings [containerPort:hostPort], restart policy, " \
                "cpu request, ram request, instance-type, creation time, start time"
        for vm in vms:
            print ', '.join([
                cc._vm_get_id(vm),
                cc._vm_get_name(vm),
                cc._vm_get_namespace(vm),
                cc._vm_get_node_name(vm),
                cc._vm_get_image_name(vm),
                cc._vm_get_state(vm) or 'Unknown',
                cc._vm_get_ip(vm),
                cc._vm_get_port_mappings(vm),
                cc._vm_get_restart_policy(vm),
                cc._vm_get_cpu(vm),
                cc._vm_get_ram(vm),
                cc._vm_get_instance_type( vm),
                cc._vm_get_creation_time( vm),
                cc._vm_get_start_time( vm)])

    def __init__(self):
        super(DockerDescribeInstances, self).__init__()


if __name__ == "__main__":
    main(DockerDescribeInstances)
