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
    import xml.etree.cElementTree as eTree  # c-version, faster
except ImportError:
    import xml.etree.ElementTree as eTree  # python version


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
        proxy = self._create_rpc_connection()
        remote_function = getattr(proxy, command)
        success, output_or_error_msg, err_code = \
            remote_function(self._create_session_string(), *args)
        if not success:
            raise Exceptions.ExecutionException(output_or_error_msg)
        return output_or_error_msg

    @override
    def _initialization(self, user_info, **kwargs):
        util.printStep('Initialize the OpenNebula connector.')
        self.user_info = user_info

        if self.is_build_image():
            self.tmp_private_key, self.tmp_public_key = generate_keypair()
            self.user_info.set_private_key(self.tmp_private_key)

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
        return 'NAME = %s' % self.format_instance_name(vm_name)

    def _set_disks(self, image_id):
        return 'DISK = [ IMAGE_ID  = %d ]' % int(image_id)

    def _set_cpu(self, vm_vcpu):
        cpu = 'VCPU = %d' % int(vm_vcpu)
        # add real CPU ratio - quota 2 vms per cpu
        return " ".join(['CPU = 0.5', cpu])

    def _set_ram(self, vm_ram_gbytes):
        return 'MEMORY = %d' % int(float(vm_ram_gbytes) * 1024)

    def _set_nics(self, requested_network_type, public_network_id, private_network_id):
        # extract mappings for Public and Private networks from the connector instance
        if requested_network_type == 'Public':
            network_id = int(public_network_id)
        elif requested_network_type == 'Private':
            network_id = int(private_network_id)
        else:
            return ''
        return 'NIC = [ NETWORK_ID = %d ]' % network_id

    def _set_contextualization(self, public_ssh_key, contextualization_script):
        return 'CONTEXT = [ NETWORK = "YES", SSH_PUBLIC_KEY = "' + public_ssh_key \
               + '", START_SCRIPT_BASE64 = "%s"]' % base64.b64encode(contextualization_script)

    def _set_custom_vm_template(self, custom_vm_template):
        return custom_vm_template


    @override
    def _start_image(self, user_info, node_instance, vm_name):
        return self._start_image_on_opennebula(user_info, node_instance, vm_name)

    def _start_image_on_opennebula(self, user_info, node_instance, vm_name):
        instance_name = self._set_instance_name(vm_name)

        selected_instance_type = node_instance.get_instance_type()
        if selected_instance_type == 'micro':
            vm_cpu = 1
            vm_ram_gbytes = 0.5
        elif selected_instance_type == 'small':
            vm_cpu = 2
            vm_ram_gbytes = 1
        elif selected_instance_type == 'medium':
            vm_cpu = 4
            vm_ram_gbytes = 2
        elif selected_instance_type == 'large':
            vm_cpu = 8
            vm_ram_gbytes = 4
        else:
            raise Exceptions.ParameterNotFoundException(
                "Couldn't find the specified instance type: %s" % selected_instance_type)

        ram = self._set_ram(node_instance.get_ram() or vm_ram_gbytes)

        cpu = self._set_cpu(node_instance.get_cpu() or vm_cpu)

        disks = self._set_disks(node_instance.get_image_id())

        nics = self._set_nics(node_instance.get_network_type(),
                      user_info.get_public_network_name(),
                      user_info.get_private_network_name())

        if self.is_build_image():
            context = self._set_contextualization(self.tmp_public_key, '')
        else:
            context = self._set_contextualization(self.user_info.get_public_keys(),
                                                  self._get_bootstrap_script(node_instance))
        custom_vm_template = self._set_custom_vm_template(node_instance.get_cloud_parameter('custom.vm.template'))

        template = ' '.join([instance_name, cpu, ram, disks, nics, context, custom_vm_template])
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
        self._wait_instance_in_state(vm_id, 'Running', time_out=300, time_sleep=10)
        self._build_image_increment(user_info, node_instance, ip_address)
        util.printStep('Creation of the new Image.')
        self._rpc_execute('one.vm.action', 'poweroff', vm_id)
        self._wait_instance_in_state(vm_id, 'Poweroff', time_out=300, time_sleep=10)
        listener.write_for(machine_name, 'Saving the image')
        new_image_name = node_instance.get_image_short_name() + time.strftime("_%Y%m%d-%H%M%S")
        new_image_id = int(self._rpc_execute(
            'one.vm.disksaveas', vm_id, 0, new_image_name, '', -1))
        self._wait_image_state(new_image_id, 'Ready', time_out=1800, time_sleep=30)
        listener.write_for(machine_name, 'Image saved !')
        self._rpc_execute('one.vm.action', 'resume', vm_id)
        self._wait_instance_in_state(vm_id, 'Running', time_out=300, time_sleep=10)
        return str(new_image_id)

    def _get_vm_state(self, vm_id):
        vm = self._rpc_execute('one.vm.info', vm_id)
        return int(eTree.fromstring(vm).findtext('STATE'))

    def _wait_instance_in_state(self, vm_id, state, time_out, time_sleep=30):
        time_stop = time.time() + time_out
        current_state = self._get_vm_state()
        while current_state != self.VM_STATE.index(state):
            if time.time() > time_stop:
                raise Exceptions.ExecutionException(
                    'Timed out while waiting VM %s to enter in state %s' % (vm_id, state))
            time.sleep(time_sleep)
            current_state = self._get_vm_state()
        return current_state

    def _get_image_state(self, image_id):
        image = self._rpc_execute('one.image.info', image_id)
        return int(eTree.fromstring(image).findtext('STATE'))

    def _wait_image_in_state(self, image_id, state, time_out, time_sleep=30):
        time_stop = time.time() + time_out
        current_state = self._get_image_state(image_id)
        while current_state != self.IMAGE_STATE.index(state):
            if time.time() > time_stop:
                raise Exceptions.ExecutionException(
                    'Timed out while waiting for image %s to be in state %s' % (image_id, state))
            time.sleep(time_sleep)
            current_state = self._get_image_state(image_id)
        return current_state

    def _wait_image_not_in_state(self, image_id, state, time_out, time_sleep=30):
        time_stop = time.time() + time_out
        current_state = self._get_image_state(image_id)
        while current_state == self.IMAGE_STATE.index(state):
            if time.time() > time_stop:
                raise Exceptions.ExecutionException(
                        'Timed out while waiting for image %s to be in state %s' % (image_id, state))
            time.sleep(time_sleep)
            current_state = self._get_image_state(image_id)
        return current_state

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
