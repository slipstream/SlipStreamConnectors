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
import sys

def getConnector(config_holder):
    return getConnectorClass()(config_holder)

def getConnectorClass():
    return DockerClientCluster

class DockerClientCluster(BaseCloudConnector):

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


    @override
    def _start_image(self, user_info, node_instance, vm_name):
        # Adapt naming convention from IaaS model
        try: 
            service = json.loads(node_instance.get_cloud_parameter("service"))
        except ValueError as ve:
            raise ValueError("Requested service is not in JSON format - %s" % ve), None, sys.exc_info()[2]
        except:
            raise

        service_name = service["Name"] if service.has_key("Name") else vm_name

        util.printStep('Deploy service %s to %s' % (service_name, user_info.get_cloud_endpoint()))
        return self._start_container_in_docker(user_info, node_instance, service_name)


    def _start_container_in_docker(self, user_info, node_instance, service_name):
        request_url = "%s/services/create" % (user_info.get_cloud_endpoint())
        service = node_instance.get_cloud_parameter("service")

        try:
            create = requests.post(request_url, data=service, 
                        headers={'Content-Type': 'application/json', 'Accept': 'application/json'})
        except requests.exceptions.ConnectionError as e:
            raise requests.exceptions.ConnectionError("Remote Docker API is not running - %s" % e), None, sys.exc_info()[2]
        except:
            raise

        response_json = json.loads(create.text)

        self.validate_start_image(response_json)

        return response_json

    
    def validate_start_image(self, response):
        """Takes the raw response from _start_container_in_docker
        and checks whether the service creation request was successful or not"""
        if len(response.keys()) == 1 and response.has_key("message"):
            raise Exceptions.ExecutionException(response["message"])


    @override
    def list_instances(self):
        request_url = "%s/services" % (self.user_info.get_cloud_endpoint())
        services_list = requests.get(request_url)

        # return a list of objects instead of plain text
        return json.loads(services_list.text)


    @override
    def _stop_vms_by_ids(self, ids):
        for service_id in ids:
            delete_url = "%s/services/%s" % (self.user_info.get_cloud_endpoint(), service_id)
            delete = requests.delete(delete_url)
            if delete.text:
                self._print_detail(delete.text)


    @override
    def _build_image(self, user_info, node_instance):
        return self._build_container_image(user_info, node_instance)


    def _build_container_image(self, user_info, node_instance):
        #TODO: build docker image and upload to registry
        return None


    def _vm_get_name(self, vm):
        # Return the service name
        return vm["Spec"]["Name"]


    def _vm_get_image_name(self, vm):
        # Return the container image name
        return vm["Spec"]["TaskTemplate"]["ContainerSpec"]["Image"]


    def _vm_get_port_mappings(self, vm):
        # string of hostPort:containerPort mappings
        return "%s:%s" % (vm["Endpoint"]["Ports"][0]["PublishedPort"], 
                        vm["Endpoint"]["Ports"][0]["TargetPort"])


    def _vm_get_restart_policy(self, vm):
        # Return the container restart policy
        return vm["Spec"]["TaskTemplate"]["RestartPolicy"]["Condition"]


    def _vm_get_creation_time(self, vm):
        # Return the container creation time
        return vm['CreatedAt']


    def _vm_get_start_time(self, vm):
        # Return the container creation time
        return vm['UpdatedAt']


    @override
    def _vm_get_ip(self, vm):
        if vm.has_key("Endpoint"):
            return vm["Endpoint"]["VirtualIPs"][0]["Addr"]
        else:
            return vm


    def _vm_get_replicas(self, vm):
        return str(vm["Spec"]["Mode"]["Replicated"]["Replicas"])


    @override
    def _vm_get_id(self, vm):
        return vm["ID"]


    @override
    def _vm_get_ip_from_list_instances(self, vm_instance):
        return self._vm_get_ip(vm_instance)


    @override
    def _vm_get_instance_type(self, vm_instance):
        return "service"
