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
import os
import requests
from tempfile import NamedTemporaryFile

import slipstream.util as util
import slipstream.exceptions.Exceptions as Exceptions

from slipstream.util import override
from slipstream.cloudconnectors.BaseCloudConnector import BaseCloudConnector
from slipstream.ConfigHolder import ConfigHolder
from slipstream.UserInfo import UserInfo


def getConnector(config_holder):
    return getConnectorClass()(config_holder)


def getConnectorClass():
    return DockerClientCloud


def get_user_info_from_cimi(cimi_connector, cimi_cloud_credential):
    user_info = UserInfo(cimi_connector['instanceName'])

    cloud_params = {
        UserInfo.CLOUD_ENDPOINT_KEY: cimi_connector['endpoint'],
        UserInfo.CLOUD_USERNAME_KEY: cimi_cloud_credential['key'],
        UserInfo.CLOUD_PASSWORD_KEY: cimi_cloud_credential['secret']
    }
    user_info.set_cloud_params(cloud_params)
    return user_info


def instantiate_from_cimi(cimi_connector, cimi_cloud_credential,
                          config_holder=ConfigHolder(options={'verboseLevel': 0, 'retry': False})):
    user_info = get_user_info_from_cimi(cimi_connector, cimi_cloud_credential)

    connector_instance = DockerClientCloud(config_holder)

    connector_instance._initialization(user_info)

    return connector_instance


class DockerClientCloud(BaseCloudConnector):
    # TODO Add support for Centos
    # TODO Fix _vm_get_state
    # TODO find a way to inform user of published port
    CERT_KEY = 'cert'
    KEY_KEY = 'key'
    NETWORK_PORTS_MAPPINGS_KEY = 'publish'
    RESTART_POLICY_KEY = 'restart-policy'
    ENV_KEY = 'env'
    WORKING_DIR_KEY = 'dir'
    COMMAND_KEY = 'cmd'
    ARGS_KEY = 'args'
    CPU_RATIO_KEY = 'cpu-ratio'
    MEMORY_KEY = 'ram'

    def _resize(self, node_instance):
        raise Exceptions.ExecutionException('{0} doesn\'t implement resize feature.'.format(self.__class__.__name__))

    def _detach_disk(self, node_instance):
        raise Exceptions.ExecutionException(
            '{0} doesn\'t implement detach disk feature.'.format(self.__class__.__name__))

    def _attach_disk(self, node_instance):
        raise Exceptions.ExecutionException(
            '{0} doesn\'t implement attach disk feature.'.format(self.__class__.__name__))

    cloudName = 'docker'

    def __init__(self, config_holder):
        super(DockerClientCloud, self).__init__(config_holder)

        self._set_capabilities(contextualization=True, direct_ip_assignment=True)
        self.user_info = None
        self.docker_api = None
        self.cert_file = NamedTemporaryFile(delete=False)
        self.key_file = NamedTemporaryFile(delete=False)

    @override
    def _initialization(self, user_info, **kwargs):
        util.printStep('Initialize the Docker connector.')
        self.user_info = user_info
        cert_string = user_info.get_cloud(self.CERT_KEY).replace("\\n", "\n")
        self.cert_file.write(cert_string)
        self.cert_file.close()
        key_string = user_info.get_cloud(self.KEY_KEY).replace("\\n", "\n")
        self.key_file.write(key_string)
        self.key_file.close()
        self.docker_api = requests.Session()
        self.docker_api.verify = False
        self.docker_api.cert = (self.cert_file.name, self.key_file.name)
        self.docker_api.headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    def _get_full_url(self, action):
        return "{}/{}".format(self.user_info.get_cloud_endpoint(), action)

    @staticmethod
    def validate_start_image(response):
        """Takes the raw response from _start_container_in_docker
        and checks whether the service creation request was successful or not"""
        if len(response.keys()) == 1 and response.has_key("message"):
            raise Exceptions.ExecutionException(response["message"])

    @override
    def _start_image(self, user_info, node_instance, vm_name):
        try:
            vm = self._start_container_in_docker(user_info, node_instance, vm_name)
        finally:
            self.cleanup_secrets()
        return vm

    def _start_container_in_docker(self, user_info, node_instance, service_name):
        service_json = {'Name': service_name,
                        'TaskTemplate': {'ContainerSpec': {'Image': node_instance.get_image_id()},
                                         'Resources': {'Reservations': {},
                                                       'Limits': {}}},
                        'EndpointSpec': {}}

        working_dir = node_instance.get_cloud_parameter(self.WORKING_DIR_KEY)
        if working_dir:
            service_json['TaskTemplate']['ContainerSpec']['Dir'] = working_dir

        env = node_instance.get_cloud_parameter(self.ENV_KEY)
        if env:
            service_json['TaskTemplate']['ContainerSpec']['Env'] = env

        cpu_ratio = node_instance.get_cloud_parameter(self.CPU_RATIO_KEY)
        if cpu_ratio:
            cpu_ratio_nano_secs = int(float(cpu_ratio) * 10 ** 9)
            service_json['TaskTemplate']['Resources']['Limits']['NanoCPUs'] = cpu_ratio_nano_secs
            service_json['TaskTemplate']['Resources']['Reservations']['NanoCPUs'] = cpu_ratio_nano_secs

        ram_giga_bytes = node_instance.get_cloud_parameter(self.MEMORY_KEY)
        if ram_giga_bytes:
            ram_bytes = int(float(ram_giga_bytes) * 1073741824)
            service_json['TaskTemplate']['Resources']['Limits']['MemoryBytes'] = ram_bytes
            service_json['TaskTemplate']['Resources']['Reservations']['MemoryBytes'] = ram_bytes

        restart_policy = node_instance.get_cloud_parameter(self.RESTART_POLICY_KEY)
        if restart_policy:
            service_json['TaskTemplate']['RestartPolicy'] = {'Condition': restart_policy}

        cmd = node_instance.get_cloud_parameter(self.COMMAND_KEY)
        if cmd:
            service_json['TaskTemplate']['ContainerSpec']['command'] = [cmd]

        args = node_instance.get_cloud_parameter(self.ARGS_KEY)
        if args:
            service_json['TaskTemplate']['ContainerSpec']['args'] = args

        ports = []

        if not cmd and not args:
            ports = [{'TargetPort': 22}]
            bootstrap_script = self._get_bootstrap_script(node_instance)
            service_json['TaskTemplate']['ContainerSpec']['command'] = ['/bin/sh']
            service_json['TaskTemplate']['ContainerSpec']['args'] = \
                ['-c',
                 'apt-get update && apt-get install -y wget && apt-get install -y python && ' +
                 'apt-get install -y python-pkg-resources && apt-get install -y openssh-server && ' +
                 'mkdir -p /var/run/sshd && mkdir -p $HOME/.ssh/ && '
                 'echo "{}" > $HOME/.ssh/authorized_keys && '.format(self.user_info.get_public_keys()) +
                 'sed -i "s/PermitRootLogin prohibit-password/PermitRootLogin yes/" /etc/ssh/sshd_config && ' +
                 '/usr/sbin/sshd && ' +
                 ' && '.join(bootstrap_script.splitlines()[1:])]

        publish_ports = node_instance.get_cloud_parameter(self.NETWORK_PORTS_MAPPINGS_KEY)
        if publish_ports:
            for publish_port in publish_ports:
                temp = publish_port.split(':')
                port_mapping = {'TargetPort': int(temp[0])}
                if len(temp) > 1:
                    port_mapping['PublishedPort'] = int(temp[1])
                ports.append(port_mapping)
            service_json['EndpointSpec'] = {'Ports': ports}

        create_response = self.docker_api.post(self._get_full_url("services/create"), json=service_json).json()

        self.validate_start_image(create_response)
        vm_id = create_response['ID']
        vm = self.docker_api.get(self._get_full_url("services/{}".format(vm_id))).json()

        return vm

    def cleanup_secrets(self):
        os.unlink(self.cert_file.name)
        os.unlink(self.key_file.name)

    @override
    def list_instances(self):
        try:
            request_url = self._get_full_url("services")
            services_list = self.docker_api.get(request_url, verify=False).json()
        finally:
            self.cleanup_secrets()
        return services_list

    @override
    def _stop_vms_by_ids(self, ids):
        try:
            for service_id in ids:
                self.docker_api.delete(self._get_full_url("services/{}".format(service_id)))
        finally:
            self.cleanup_secrets()

    @override
    def _vm_get_ip(self, vm):
        virtual_ips = vm.get('Endpoint', {}).get('VirtualIPs', [])
        if len(virtual_ips) > 0:
            return virtual_ips[0]["Addr"].split('/')[0]
        else:
            return None

    @override
    def _vm_get_id(self, vm):
        return vm["ID"]

    @override
    def _vm_get_state(self, vm_instance):
        # FIXME: check link below to implement service state checks
        # https://success.docker.com/article/how-to-determine-if-a-service-was-created-successfully-when-using-the-api
        return 'running'

    @override
    def _vm_get_ip_from_list_instances(self, vm_instance):
        return self._vm_get_ip(vm_instance)
