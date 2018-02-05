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

import time

import slipstream.util as util
import slipstream.exceptions.Exceptions as Exceptions

from slipstream.util import override
from slipstream.cloudconnectors.BaseCloudConnector import BaseCloudConnector
from slipstream.utils.ssh import generate_keypair

import ssl
import urllib
import re
import base64
import requests
import json

def getConnector(config_holder):
    return getConnectorClass()(config_holder)

def getConnectorClass():
    return DockerClientCluster

class DockerClientCluster(BaseCloudConnector):

    VM_STATE = [
        'Init',       # 0
        'Pending',    # 1
        'Hold',       # 2
        'Active',     # 3
        'Stopped',    # 4
        'Suspended',  # 5
        'Done',       # 6
        '//Failed',   # 7
        'Poweroff',   # 8
        'Undeployed'  # 9
    ]

    IMAGE_STATE = [
        'Init',       # 0
        'Ready',      # 1
        'Used',       # 2
        'Disabled',   # 3
        'Locked',     # 4
        'Error',      # 5
        'Clone',      # 6
        'Delete',     # 7
        'Used_pers'   # 8
    ]

    def _resize(self, node_instance):
        raise Exceptions.ExecutionException('{0} doesn\'t implement resize feature.'.format(self.__class__.__name__))

    def _detach_disk(self, node_instance):
        raise Exceptions.ExecutionException('{0} doesn\'t implement detach disk feature.'.format(self.__class__.__name__))

    def _attach_disk(self, node_instance):
        raise Exceptions.ExecutionException('{0} doesn\'t implement attach disk feature.'.format(self.__class__.__name__))

    cloudName = 'docker'

    def __init__(self, config_holder):

        super(DockerClientCluster, self).__init__(config_holder)

        self._set_capabilities(contextualization=True)
        self.user_info = None

    @override
    def _initialization(self, user_info, **kwargs):
        util.printStep('Initialize the Docker connector.')
        self.user_info = user_info

        # if self.is_build_image():
        #     self.tmp_private_key, self.tmp_public_key = generate_keypair()
        #     self.user_info.set_private_key(self.tmp_private_key)

    def format_instance_name(self, name):
        new_name = self.remove_bad_char_in_instance_name(name)
        return self.truncate_instance_name(new_name)

    @staticmethod
    def truncate_instance_name(name):
        if len(name) <= 128:
            return name
        else:
            return name[:63] + '-' + name[-63:]

    @staticmethod
    def remove_bad_char_in_instance_name(name):
        return re.sub('[^a-zA-Z0-9-]', '', name)

    def _set_instance_name(self, vm_name):
        return self.format_instance_name(vm_name)


    #################### TODO
    def _set_contextualization(self, contextualization_type, public_ssh_key, contextualization_script):
        if contextualization_type != 'cloud-init':
            return 'CONTEXT = [ NETWORK = "YES", SSH_PUBLIC_KEY = "{0}", ' \
                   'START_SCRIPT_BASE64 = "{1}"]'.format(public_ssh_key, base64.b64encode(contextualization_script))
        else:
            return 'CONTEXT = [ PUBLIC_IP = "$NIC[IP]", SSH_PUBLIC_KEY = "{0}", USERDATA_ENCODING = "base64", ' \
                   'USER_DATA = "{1}"]'.format(public_ssh_key, base64.b64encode(contextualization_script))
    ####################

    @override
    def _start_image(self, user_info, node_instance, vm_name):
        # Adapt naming convention from IaaS model
        container_name = vm_name
        return self._start_container_in_docker(user_info, node_instance, container_name)

    def _start_container_in_docker(self, user_info, node_instance, container_name):
        instance_name = self._set_instance_name(container_name)
        instance_type = "service"
        instance_image_id = node_instance.get_image_id()
        #################### TODO
        # BUILD IMG does not apply the same way on containers. tmp key is not needed neither there are any contextualization packages like cloud-init
        # if self.is_build_image():
        #     context = self._set_contextualization(node_instance.get_cloud_parameter('contextualization.type'),
        #                                           self.tmp_public_key, '')
        # else:
        #     context = self._set_contextualization(node_instance.get_cloud_parameter('contextualization.type'),
        #                                           self.user_info.get_public_keys(),
        #                                           self._get_bootstrap_script(node_instance))
        ####################

        # create pod manifest
#         manifest = '''
# {
#     "kind": "%s",
#     "apiVersion": "v1",
#     "metadata":{
#         "name": "%s",
#         "namespace": "default",
#         "labels": {
#             "name": "%s"
#         }
#     },
#     "spec": {
#         "containers": [{
#             "name": "%s",
#             "image": "%s",
#             "ports": [{"containerPort": 80}],
#             "resources": {
#                 "limits": {
#                     "memory": "128Mi",
#                     "cpu": "500m"
#                 }
#             }
#         }]
#     }
# }''' % (instance_type, instance_name, instance_name, instance_name, instance_image_id)

        manifest = '''
{
  "Name": "web",
  "TaskTemplate": {
    "ContainerSpec": {
      "Image": "nginx"
    },
    "LogDriver": {
      "Name": "json-file",
      "Options": {
        "max-file": "3",
        "max-size": "10M"
      }
    },
    "RestartPolicy": {
      "Condition": "on-failure",
      "Delay": 10000000000,
      "MaxAttempts": 10
    }
  },
  "Mode": {
    "Replicated": {
      "Replicas": 1
    }
  },
  "UpdateConfig": {
    "Parallelism": 2,
    "Delay": 1000000000,
    "FailureAction": "pause",
    "Monitor": 15000000000,
    "MaxFailureRatio": 0.15
  },
  "RollbackConfig": {
    "Parallelism": 1,
    "Delay": 1000000000,
    "FailureAction": "pause",
    "Monitor": 15000000000,
    "MaxFailureRatio": 0.15
  },
  "EndpointSpec": {
    "Ports": [
      {
        "Protocol": "tcp",
        "PublishedPort": 8181,
        "TargetPort": 80
      }
    ]
  },
  "Labels": {
    "foo": "bar"
  }
}
'''

        request_url = "%s/services/create" % (self.user_info.get_cloud_endpoint())
        create = requests.post(request_url, data=manifest, headers={'Content-Type': 'application/json'})
        # pod = self._get_pod(instance_name, "defaut")
        return json.loads(create.text)

    @override
    def list_instances(self):
        instance_type = "pods"
        request_url = "%s/%s" % (self.user_info.get_cloud_endpoint(), instance_type)
        pods = requests.get(request_url)

        # returns list([]) of items({})
        return json.loads(pods.text)['items']

    # @override
    # def _stop_deployment(self):
    #     # for _, vm in self.get_vms().items():
    #     #     self._rpc_execute('one.vm.action', 'delete', int(vm.findtext('ID')))

    def _get_pod(self, pod_name, namespace):
        instance_type = "pods"
        request_url = "%s/namespaces/%s/%s/%s" % (self.user_info.get_cloud_endpoint(), \
                                namespace, instance_type, pod_name)
        return request_url

    @override
    def _stop_vms_by_ids(self, ids):
        pass

    def _stop_instances_in_namespace(self, ids, namespace):
        instance_type = "pods"
        for _id in map(str, ids):
            request_url = "%s/namespaces/%s/%s/%s" % (self.user_info.get_cloud_endpoint(), \
                                namespace, instance_type, _id)
            delete = requests.delete(request_url)

    @override
    def _build_image(self, user_info, node_instance):
        return self._build_container_image(user_info, node_instance)

    def _build_container_image(self, user_info, node_instance):
        #TODO: build docker image and upload to registry

        return None
        # listener = self._get_listener()
        # machine_name = node_instance.get_name()
        # vm = self._get_vm(machine_name)
        # ip_address = self._vm_get_ip(vm)
        # vm_id = int(self._vm_get_id(vm))
        # self._wait_vm_in_state(vm_id, 'Active', time_out=300, time_sleep=10)
        # self._build_image_increment(user_info, node_instance, ip_address)
        # util.printStep('Creation of the new Image.')
        # self._rpc_execute('one.vm.action', 'poweroff', vm_id)
        # self._wait_vm_in_state(vm_id, 'Poweroff', time_out=300, time_sleep=10)
        # listener.write_for(machine_name, 'Saving the image')
        # new_image_name = node_instance.get_image_short_name() + time.strftime("_%Y%m%d-%H%M%S")
        # new_image_id = int(self._rpc_execute(
        #     'one.vm.disksaveas', vm_id, 0, new_image_name, '', -1))
        # self._wait_image_in_state(new_image_id, 'Ready', time_out=1800, time_sleep=30)
        # listener.write_for(machine_name, 'Image saved !')
        # self._rpc_execute('one.vm.action', 'resume', vm_id)
        # self._wait_vm_in_state(vm_id, 'Active', time_out=300, time_sleep=10)
        # return str(new_image_id)

    def _get_vm_state(self, vm_id):
        return 'STATE'
        # vm = self._rpc_execute('one.vm.info', vm_id)
        # return int(eTree.fromstring(vm).findtext('STATE'))

    def _wait_vm_in_state(self, vm_id, state, time_out, time_sleep=30):
        time_stop = time.time() + time_out
        current_state = self._get_vm_state(vm_id)
        while current_state != self.VM_STATE.index(state):
            if time.time() > time_stop:
                raise Exceptions.ExecutionException(
                    'Timed out while waiting VM {0} to enter in state {1}'.format(vm_id, state))
            time.sleep(time_sleep)
            current_state = self._get_vm_state(vm_id)
        return current_state

    def _get_image_state(self, image_id):
        return 'IMAGE_STATE'
        # image = self._rpc_execute('one.image.info', image_id)
        # return int(eTree.fromstring(image).findtext('STATE'))

    def _wait_image_in_state(self, image_id, state, time_out, time_sleep=30):
        time_stop = time.time() + time_out
        current_state = self._get_image_state(image_id)
        while current_state != self.IMAGE_STATE.index(state):
            if time.time() > time_stop:
                raise Exceptions.ExecutionException(
                    'Timed out while waiting for image {0} to be in state {1}'.format(image_id, state))
            time.sleep(time_sleep)
            current_state = self._get_image_state(image_id)
        return current_state

    def _wait_image_not_in_state(self, image_id, state, time_out, time_sleep=30):
        time_stop = time.time() + time_out
        current_state = self._get_image_state(image_id)
        while current_state == self.IMAGE_STATE.index(state):
            if time.time() > time_stop:
                raise Exceptions.ExecutionException(
                        'Timed out while waiting for image {0} to be in state {1}'.format(image_id, state))
            time.sleep(time_sleep)
            current_state = self._get_image_state(image_id)
        return current_state

    def _create_session_string(self):
        quoted_username = urllib.quote(self.user_info.get_cloud_username(), '')
        quoted_password = urllib.quote(self.user_info.get_cloud_password(), '')
        return '{0}:{1}'.format(quoted_username, quoted_password)

    def _create_rpc_connection(self):
        protocol_separator = '://'
        parts = self.user_info.get_cloud_endpoint().split(protocol_separator)
        url = parts[0] + protocol_separator + self._create_session_string() \
            + "@" + ''.join(parts[1:])
        no_certif_check = hasattr(ssl, '_create_unverified_context') and ssl._create_unverified_context() or None
        try:
            return xmlrpclib.ServerProxy(url, context=no_certif_check)
        except TypeError:
            return xmlrpclib.ServerProxy(url)

    def _vm_get_name(self, vm):
        # Return the container name
        return vm['spec']['containers'][0]['name']

    def _vm_get_namespace(self, vm):
        return vm['metadata']['namespace']

    def _vm_get_node_name(self, vm):
        # Return the host name
        if "containerStatuses" not in vm['status'].keys():
            return ""
        else:
            return vm['spec']['nodeName']

    def _vm_get_image_name(self, vm):
        # Return the container image name
        return vm['spec']['containers'][0]['image']

    def _vm_get_port_mappings(self, vm):
        # string of hostPort:containerPort mappings
        port_mappings = ""
        if 'ports' in vm['spec']['containers'][0].keys():
            for mapping in vm['spec']['containers'][0]['ports']:
                port_mappings += "%s:%s " % (mapping.get("hostPort", ""), \
                                mapping.get("containerPort", ""))
        return port_mappings

    def _vm_get_restart_policy(self, vm):
        # Return the container restart policy
        return vm['spec']['restartPolicy']

    def _vm_get_creation_time(self, vm):
        # Return the container creation time
        return vm['metadata']['creationTimestamp']

    def _vm_get_start_time(self, vm):
        # Return the container creation time
        if "containerStatuses" not in vm['status'].keys():
            return ""
        else:
            return vm['status']['startTime']

    @override
    def _vm_get_ip(self, vm):
        if "containerStatuses" not in vm['status'].keys():
            return ""
        else:
            return vm['status']['podIP']

    @override
    def _vm_get_cpu(self, vm):
        if bool(vm['spec']['containers'][0]['resources']):
            return vm['spec']['containers'][0]['resources']['requests']['cpu']
        else:
            return "not defined"

    @override
    def _vm_get_ram(self, vm):
        if bool(vm['spec']['containers'][0]['resources']):
            return vm['spec']['containers'][0]['resources']['requests']['memory']
        else:
            return "not defined"

    @override
    def _vm_get_id(self, vm):
        return vm['metadata']['name']

    @override
    def _vm_get_state(self, vm):
        return vm['status']['phase']

    @override
    def _vm_get_ip_from_list_instances(self, vm_instance):
        return self._vm_get_ip(vm_instance)

    @override
    def _vm_get_instance_type(self, vm_instance):
        return "container"
