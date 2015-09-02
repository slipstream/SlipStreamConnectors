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

import os

import slipstream.util as util

from slipstream.util import override, ENV_NODE_INSTANCE_NAME
from slipstream.NodeInstance import NodeInstance
from slipstream.cloudconnectors.BaseCloudConnector import BaseCloudConnector
from slipstream.exceptions.Exceptions import ExecutionException


def getConnector(configHolder):
    return getConnectorClass()(configHolder)


def getConnectorClass():
    return PhysicalHostClientCloud


class PhysicalHostClientCloud(BaseCloudConnector):
    cloudName = 'physicalhost'

    def __init__(self, configHolder):
        super(PhysicalHostClientCloud, self).__init__(configHolder)

        self._set_capabilities(contextualization=True,
                               direct_ip_assignment=True,
                               orchestrator_can_kill_itself_or_its_vapp=True)

    @override
    def _initialization(self, user_info):
        # pylint: disable=attribute-defined-outside-init
#        for node_info in nodes_info:
#            if node_info['multiplicity'] > 1:
#                raise Exceptions.ExecutionException('Multiplicity not yet supported by this connector.')

        # TODO: username, password and private_key should be taken from Image Info
        self.username = user_info.get_cloud_username()
        self.password = user_info.get_cloud_password()
        self.private_key = user_info.get_private_key()

        # TODO: check if this is needed. The orchestrator should be handled server side.
        node_instance = NodeInstance({'name': 'orchestrator-physicalhost',
                                      'loginUser': self.username,
                                      'cloudservice': self.cloudName,
                                      self.cloudName + '.login.password': self.password})

        vm = {'username': self.username,
              'password': self.password,
              'private_key': self.private_key,
              'host': os.environ['PHYSICALHOST_ORCHESTRATOR_HOST'],
              'id': os.environ['PHYSICALHOST_ORCHESTRATOR_HOST'],
              'ip': os.environ['PHYSICALHOST_ORCHESTRATOR_HOST']}

        super(PhysicalHostClientCloud, self).__add_vm(vm, node_instance)  # pylint: disable=protected-access

    @override
    def _start_image(self, user_info, node_instance, vm_name):
        host = node_instance.get_image_id()
        username = self.username

        command = self._build_contextualization_script(node_instance, username)

        self._run_script_with_private_key(host, self.username, command, self.password, self.private_key)

        vm = {'username': self.username,
              'private_key': self.private_key,
              'password': self.password,
              'host': host,
              'id': host,
              'ip': host}
        return vm

    @override
    def _vm_get_ip(self, host):
        return host['ip']

    @override
    def _vm_get_id(self, host):
        return host['id']

    @override
    def _stop_deployment(self):
        for nodename, node in self.get_vms().items():
            if not nodename == 'orchestrator-physicalhost':
                self.__stop_image(node['username'], node['private_key'], node['password'], node['host'])

    @override
    def _stop_vms_by_ids(self, ids):
        util.printAndFlush("Stop ids: %s" % ids)
        for _, node in self.get_vms().items():
            util.printAndFlush("   Node: %s" % node['host'])
            if node['host'] in ids:
                self.__stop_image(node['username'], node['private_key'], node['password'], node['host'])

    def _build_contextualization_script(self, node_instance, username):
        sudo = self._get_sudo(username)
        node_instance_name = node_instance.get_name()

        userData = "echo '(" + sudo + " bash -c '\\''sleep 5; "
        for (k, v) in os.environ.items():
            if k.startswith('SLIPSTREAM_') or k.startswith('PHYSICALHOST_'):
                userData += 'export ' + k + '="' + v + '"' + "; "
        userData += 'export ' + ENV_NODE_INSTANCE_NAME + '="' + node_instance_name + '"' + "; "
        userData += self._build_slipstream_bootstrap_command(node_instance_name)
        userData += "'\\'') > /dev/null 2>&1 &' | at now"
        return userData

    def __stop_image(self, username, privateKey, password, host):
        sudo = self._get_sudo(username)

        command = sudo + " bash -c '"
        # command = "echo '(sudo bash -c '\\''"
        # command += 'kill -9 `ps -Af | grep python | grep slipstream | grep -v grep | awk "{print $2}"`; ';
        command += "rm -R /tmp/slipstream*; rm /tmp/tmp*; rm -R /opt/slipstream; rm -R /opt/paramiko; "
        command += "'"
        # command += "'\\'') > /dev/null 2>&1 &' | at now"

        self._run_script_with_private_key(host, username, command, password, privateKey)

    def _get_sudo(self, username):
        if username == 'root':
            return ''
        else:
            return 'sudo'

    def _run_script_with_private_key(self, host, username, command, password, privateKey):
        sshPrivateKeyFile = None
        if privateKey:
            sshPrivateKeyFile = util.file_put_content_in_temp_file(privateKey)
        try:
            self._run_script(host, username, command, password, sshPrivateKeyFile)
        finally:
            try:
                os.unlink(sshPrivateKeyFile)
            except:
                pass

    def _build_image(self, user_info, node_instance):
        raise ExecutionException("%s doesn't implement build image feature." %
                                 self.__class__.__name__)
