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

import time

import slipstream.util as util
import slipstream.exceptions.Exceptions as Exceptions

from slipstream.util import override
from slipstream.cloudconnectors.BaseCloudConnector import BaseCloudConnector
from slipstream.utils.ssh import generate_keypair

import xmlrpclib
import urllib
import re
import base64
try:
    import xml.etree.cElementTree as eTree  # c-version first
except ImportError:
    try:
        import xml.etree.ElementTree as eTree  # python version
    except ImportError:
        eTree = None
        raise Exception('failed to import ElementTree')


def getConnector(config_holder):
    return getConnectorClass()(config_holder)


def getConnectorClass():
    return OpenNebulaClientCloud


def searchInObjectList(list_, property_name, property_value):
    for element in list_:
        if isinstance(element, dict):
            if element.get(property_name) == property_value:
                return element
        else:
            if getattr(element, property_name) == property_value:
                return element
    return None


class OpenNebulaClientCloud(BaseCloudConnector):

    VM_STATE = [
        'Init',       # 0
        'Pending',    # 1
        'Hold',       # 2
        'Running',    # 3
        'Stopped',    # 4
        'Suspended',  # 5
        'Done',       # 6
        '_',          # 7
        'Poweroff',   # 8
        'Undeployed'  # 0
        ]

    def _resize(self, node_instance):
        raise Exceptions.ExecutionException("%s doesn't implement resize feature." %
                                            self.__class__.__name__)

    def _detach_disk(self, node_instance):
        raise Exceptions.ExecutionException("%s doesn't implement detach disk feature." %
                                            self.__class__.__name__)

    def _attach_disk(self, node_instance):
        raise Exceptions.ExecutionException("%s doesn't implement attach disk feature." %
                                            self.__class__.__name__)

    cloudName = 'opennebula'

    def __init__(self, config_holder):

        super(OpenNebulaClientCloud, self).__init__(config_holder)

        self._set_capabilities(contextualization=True,
                               direct_ip_assignment=True,
                               orchestrator_can_kill_itself_or_its_vapp=True)
        self.user_info = None

    def _rpc_execute(self, command, *args):
        remote_function = getattr(self.driver, command)
        success, output_or_error_msg, err_code = \
            remote_function(self._create_session_string(), *args)
        if not success:
            raise Exceptions.ExecutionException(output_or_error_msg)
        return output_or_error_msg

    @override
    def _initialization(self, user_info):
        util.printStep('Initialize the OpenNebula connector.')
        self.user_info = user_info

        if self.is_build_image():
            self.tmp_private_key, self.tmp_public_key = generate_keypair()
            self.user_info.set_private_key(self.tmp_private_key)

        self.driver = self._create_rpc_connection()

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

    @override
    def _start_image(self, user_info, node_instance, vm_name):
        return self._start_image_on_opennebula(user_info, node_instance, vm_name)

    def _start_image_on_opennebula(self, user_info, node_instance, vm_name):
        instance_name = 'NAME = %s' % self.format_instance_name(vm_name)

        selected_instance_type = node_instance.get_instance_type()
        if selected_instance_type == 'micro':
            instance_type = 'INSTANCE_TYPE = %s' % selected_instance_type
            cpu = 'VCPU = 1'
            ram = 'MEMORY = 512'
        elif selected_instance_type == 'small':
            instance_type = 'INSTANCE_TYPE = %s' % selected_instance_type
            cpu = 'VCPU = 2'
            ram = 'MEMORY = 1024'
        elif selected_instance_type == 'medium':
            instance_type = 'INSTANCE_TYPE = %s' % selected_instance_type
            cpu = 'VCPU = 4'
            ram = 'MEMORY = 2048'
        elif selected_instance_type == 'large':
            instance_type = 'INSTANCE_TYPE = %s' % selected_instance_type
            cpu = 'VCPU = 8'
            ram = 'MEMORY = 4096'
        else:
            raise Exceptions.ParameterNotFoundException(
                "Couldn't find the specified instance type: %s" % selected_instance_type)

        vm_ram_gbytes = node_instance.get_ram() or None
        if vm_ram_gbytes:
            ram = 'MEMORY = %d' % int(float(vm_ram_gbytes) * 1024)

        vm_cpu = node_instance.get_cpu() or None
        if vm_cpu:
            cpu = 'VCPU = %d' % int(vm_cpu)

        # add real CPU ratio
        cpu = " ".join(['CPU = 0.5', cpu])

        disk = 'DISK = [ IMAGE_ID  = %d ]' % int(node_instance.get_image_id())

        # extract mappings for Public and Private networks from the connector instance
        network_type = node_instance.get_network_type()
        network_id = None
        if network_type == 'Public':
            network_id = int(user_info.get_public_network_name())
        elif network_type == 'Private':
            network_id = int(user_info.get_private_network_name())
        nic = 'NIC = [ NETWORK_ID = %d ]' % network_id

        if self.is_build_image():
            public_key = self.tmp_public_key
            contextualization_script = ''
        else:
            public_key = self.user_info.get_public_keys()
            contextualization_script = self._get_bootstrap_script(node_instance)

        context = 'CONTEXT = [ NETWORK = "YES", SSH_PUBLIC_KEY = "' + public_key \
                  + '", START_SCRIPT_BASE64 = "%s"]' % base64.b64encode(contextualization_script)
        template = ' '.join([instance_name, instance_type, cpu, ram, disk, nic, context])
        vm_id = self._rpc_execute('one.vm.allocate', template, False)
        vm = self._rpc_execute('one.vm.info', vm_id)
        return eTree.fromstring(vm)

    @override
    def list_instances(self):
        vms = eTree.fromstring(self._rpc_execute('one.vmpool.info', -3, -1, -1, -1))
        return vms.findall('VM')

    @override
    def _stop_deployment(self):
        for _, vm in self.get_vms().items():
            self._rpc_execute('one.vm.action', 'delete', int(vm.findtext('ID')))

    @override
    def _stop_vms_by_ids(self, ids):
        for _id in map(int, ids):
            self._rpc_execute('one.vm.action', 'delete', _id)

    @override
    def _build_image(self, user_info, node_instance):
        return self._build_image_on_opennebula(user_info, node_instance)

    def _build_image_on_opennebula(self, user_info, node_instance):
        listener = self._get_listener()
        machine_name = node_instance.get_name()
        vm = self._get_vm(machine_name)
        ip_address = self._vm_get_ip(vm)
        vm_id = int(self._vm_get_id(vm))
        self._wait_instance_in_state(vm_id, 'Running', time_out=300)
        self._build_image_increment(user_info, node_instance, ip_address)
        util.printStep('Creation of the new Image.')
        self._rpc_execute('one.vm.action', 'poweroff', vm_id)
        self._wait_instance_in_state(vm_id, 'Poweroff', time_out=300)
        listener.write_for(machine_name, 'Saving the image')
        new_image_name = node_instance.get_image_short_name() + time.strftime("_%Y%m%d-%H%M%S")
        new_image_id = int(self._rpc_execute(
            'one.vm.disksaveas', vm_id, 0, new_image_name, '', -1))
        self._wait_image_creation_completed(new_image_id)
        listener.write_for(machine_name, 'Image saved !')
        self._rpc_execute('one.vm.action', 'resume', vm_id)
        self._wait_instance_in_state(vm_id, 'Running', time_out=300)
        return str(new_image_id)

    def _wait_instance_in_state(self, vm_id, state, time_out):
        time_stop = time.time() + time_out

        current_state = None
        while current_state != self.VM_STATE.index(state):
            if time.time() > time_stop:
                raise Exceptions.ExecutionException(
                    'Timed out while waiting for instance "%s" enter in %s state'
                    % vm_id, state)
            time.sleep(3)
            vm = self._rpc_execute('one.vm.info', vm_id)
            current_state = int(eTree.fromstring(vm).findtext('STATE'))

    def _wait_image_creation_completed(self, new_image_id):
        time_wait = 600
        time_stop = time.time() + time_wait

        image_state = None
        ready_code = 1
        while image_state != ready_code:
            if time.time() > time_stop:
                raise Exceptions.ExecutionException(
                    'Timed out while waiting for image "%s" to be created' % new_image_id)
            time.sleep(3)
            image = self._rpc_execute('one.image.info', new_image_id)
            image_state = int(eTree.fromstring(image).findtext('STATE'))

    def _create_session_string(self):
        quoted_username = urllib.quote(self.user_info.get_cloud_username(), '')
        quoted_password = urllib.quote(self.user_info.get_cloud_password(), '')
        return '%s:%s' % (quoted_username, quoted_password)

    def _create_rpc_connection(self):
        protocol_separator = '://'
        parts = self.user_info.get_cloud_endpoint().split(protocol_separator)
        url = parts[0] + protocol_separator + self._create_session_string() \
            + "@" + ''.join(parts[1:])
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
