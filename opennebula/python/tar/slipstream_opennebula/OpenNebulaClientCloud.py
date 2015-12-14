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


import slipstream.util as util
import slipstream.exceptions.Exceptions as Exceptions

from slipstream.util import override
from slipstream.cloudconnectors.BaseCloudConnector import BaseCloudConnector

import xmlrpclib
import urllib
from pprint import pprint, pformat
import xml.etree.ElementTree as etree
import re
import base64

def getConnector(configHolder):
    return getConnectorClass()(configHolder)


def getConnectorClass():
    return OpenNebulaClientCloud


def searchInObjectList(list_, propertyName, propertyValue):
    for element in list_:
        if isinstance(element, dict):
            if element.get(propertyName) == propertyValue:
                return element
        else:
            if getattr(element, propertyName) == propertyValue:
                return element
    return None


class OpenNebulaClientCloud(BaseCloudConnector):
    cloudName = 'opennebula'

    def __init__(self, configHolder):

        super(OpenNebulaClientCloud, self).__init__(configHolder)

        self._set_capabilities(contextualization=True,
                               direct_ip_assignment=True,
                               orchestrator_can_kill_itself_or_its_vapp=True)
        self.user_info = None

    def _rpc_execute(self, command, *args):
        remoteFunction = getattr(self.driver, command)
        success, output_or_error_msg, err_code = remoteFunction(self._createSessionString(self.user_info), *args)
        if not success:
            raise Exceptions.ExecutionException(output_or_error_msg)
        return output_or_error_msg

    @override
    def _initialization(self, user_info):
        util.printStep('Initialize the OpenNebula connector.')
        self.driver = self._createRpcConnection(user_info)
        self.user_info = user_info

    def format_instance_name(self, name):
        name = self.remove_bad_char_in_instance_name(name)
        return self.truncate_instance_name(name)

    def truncate_instance_name(self, name):
        if len(name) <= 128:
            return name
        else:
            return name[:63] + '-' + name[-63:]

    def remove_bad_char_in_instance_name(self, name):
        return re.sub('[^a-zA-Z0-9-]', '', name)

    @override
    def _start_image(self, user_info, node_instance, vm_name):
        util.printStep('KB: _start_image.')
        return self._start_image_on_opennebula(user_info, node_instance, vm_name)

    def _start_image_on_opennebula(self, user_info, node_instance, vm_name):
        instance_name = 'NAME = %s' % self.format_instance_name(vm_name)

        selected_instance_type = node_instance.get_instance_type()
        if selected_instance_type == 'micro':
            instance_type = 'INSTANCE_TYPE = %s' % selected_instance_type
            cpu = 'CPU = 0.5'
            ram = 'MEMORY = 512'
        elif selected_instance_type == 'small':
            instance_type = 'INSTANCE_TYPE = %s' % selected_instance_type
            cpu = 'CPU = 1'
            ram = 'MEMORY = 1024'
        elif selected_instance_type == 'large':
            instance_type = 'INSTANCE_TYPE = %s' % selected_instance_type
            cpu = 'CPU = 2'
            ram = 'MEMORY = 2048'
        elif selected_instance_type == 'xlarge':
            instance_type = 'INSTANCE_TYPE = %s' % selected_instance_type
            cpu = 'CPU = 4'
            ram = 'MEMORY = 4096'
        else :
            raise Exceptions.ParameterNotFoundException(
                "Couldn't find the specified instance type: %s" % selected_instance_type)

        disk = 'DISK = [ IMAGE_ID  = %d ]' % int(node_instance.get_image_id())

        # extract mappings for Public and Private networks from the connector instance
        network_type = node_instance.get_network_type()
        if network_type == 'Public':
            network_id = int(user_info.get_public_network_name())
        elif network_type == 'Private':
            network_id = int(user_info.get_private_network_name())
        nic = 'NIC = [ NETWORK_ID = %d ]' % network_id

        contextualization_script = self.is_build_image() and '' or self._get_bootstrap_script(node_instance)
        context = 'CONTEXT = [ NETWORK = "YES", SSH_PUBLIC_KEY = "' + self.user_info.get_public_keys() \
                  + '", START_SCRIPT_BASE64 = "%s"]' % base64.b64encode(contextualization_script)

        template = ' '.join([instance_name, instance_type, cpu, ram, disk, nic, context])
        vm_id = self._rpc_execute('one.vm.allocate', template, False)
        vm = self._rpc_execute('one.vm.info', vm_id)
        #xml = etree.fromstring(vm)
        #pprint('ici:')
        #pprint(xml.find('TEMPLATE/NIC/IP').text)
        #vm = self._get_from_rpc(user_info, 'one.template.instantiate', instance_type, vm_name, False, 'NIC = [ NETWORK = "private" ] DISK = [ IMAGE_ID  = 10 ]')
        #success, vm_id_or_error_msg, error_code = self.driver.one.template.instantiate(self._createSessionString(user_info), instance_type, vm_name, False, "")
        #pprint("vm_id_or_error_msg:")
        #pprint(vm_id_or_error_msg)
        #pprint("success:")
        #pprint(success)
        #pprint("error_code:")
        #pprint(error_code)
        return etree.fromstring(vm)

    def format_instance_name(self, name):
        name = self.remove_bad_char_in_instance_name(name)
        return self.truncate_instance_name(name)

    def truncate_instance_name(self, name):
        if len(name) <= 128:
            return name
        else:
            return name[:63] + '-' + name[-63:]

    def remove_bad_char_in_instance_name(self, name):
        return re.sub('[^a-zA-Z0-9-]', '', name)

    @override
    def list_instances(self):
        vms = etree.fromstring(self._rpc_execute('one.vmpool.info', -3, -1, -1, 3))
        return vms.findall('VM')

    @override
    def _stop_deployment(self):
        util.printStep('KB: _stop_deployment.')
        # for _, vm in self.get_vms().items():
        #     vm['instance'].destroy()

    @override
    def _stop_vms_by_ids(self, ids):
        for _id in map(int, ids):
            self._rpc_execute('one.vm.action', 'delete', _id)

    def _createSessionString(self, user_info):
        quotedUsername = urllib.quote(user_info.get_cloud_username(), '')
        quotedPassword = urllib.quote(user_info.get_cloud_password(), '')
        return '%s:%s' % (quotedUsername, quotedPassword)

    def _createRpcConnection(self, user_info):
        protocolSeparator = '://'
        parts = user_info.get_cloud_endpoint().split(protocolSeparator)
        url = parts[0] + protocolSeparator + self._createSessionString(user_info) + "@" + ''.join(parts[1:])
        return xmlrpclib.ServerProxy(url)

    @override
    def _vm_get_ip(self, vm):
        return vm.findtext('TEMPLATE/NIC/IP')

    @override
    def _vm_get_id(self, vm):
        return vm.findtext('ID')

    @override
    def _vm_get_ip_from_list_instances(self, vm_instance):
        return self._vm_get_ip(vm_instance)

    @override
    def _vm_get_cpu(self, vm_instance):
        return vm_instance.findtext('TEMPLATE/VCPU')

    @override
    def _vm_get_ram(self, vm_instance):
        return vm_instance.findtext('TEMPLATE/MEMORY')

    @override
    def _vm_get_root_disk(self, vm_instance):
        return vm_instance.findtext('TEMPLATE/DISK/SIZE')

    @override
    def _vm_get_instance_type(self, vm_instance):
        return vm_instance.findtext('USER_TEMPLATE/INSTANCE_TYPE')

