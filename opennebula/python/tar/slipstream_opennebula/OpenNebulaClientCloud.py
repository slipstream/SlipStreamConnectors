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
import ssl
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
        return 'NAME = {0}'.format(self.format_instance_name(vm_name))

    def _set_disks(self, image_id, disk_size_gb):
        try:
            img_id = int(image_id)
        except:
            raise Exception('Somethiing is wrong with image ID : {0}!'.format(image_id))
        if disk_size_gb == None:
           return 'DISK = [ IMAGE_ID  = {0:d}]'.format(img_id)
        else:
            try:
                disk_size_mb = int(float(disk_size_gb) * 1024)
            except:
                raise Exception('Something is wrong with root disk size : {0}!'.format(disk_size_gb))
            return 'DISK = [ IMAGE_ID  = {0:d}, SIZE={1:d} ]'.format(img_id, disk_size_mb)

    def _set_additionnal_disks(self, disk_size_gb):
        if disk_size_gb is None:
            return ''
        try:
            disk_size_mb = int(float(disk_size_gb) * 1024)
        except:
            raise 'Something wrong with additionnal disk size : {0}!'.format(disk_size_gb)
        return 'DISK = [ FORMAT = "ext4", SIZE="{0:d}", TYPE="fs", IO="native" ]'.format(disk_size_mb)

    def _set_cpu(self, vm_vcpu):
        try:
            number_vcpu = int(vm_vcpu)
        except:
            raise 'Something wrong with CPU size : {0}!'.format(vm_vcpu)
        vcpu = 'VCPU = {0:d}'.format(number_vcpu)
        # add real CPU ratio - quota 2 vms per cpu
        return ' '.join(['CPU = 0.5', vcpu])

    def _set_ram(self, vm_ram_gbytes):
        try:
            ram = int(float(vm_ram_gbytes) * 1024)
        except ValueError:
            raise 'Something wrong with RAM size : {0}!'.format(vm_ram_gbytes)
        return 'MEMORY = {0:d}'.format(ram)

    def _set_nics(self, requested_network_type, public_network_id, private_network_id):
        # extract mappings for Public and Private networks from the connector instance
        if requested_network_type.upper() == 'PUBLIC':
            try:
                network_id = int(public_network_id)
            except ValueError:
                raise 'Something wrong with specified Public Network ID : {0}!'.format(public_network_id)
        elif requested_network_type.upper() == 'PRIVATE':
            try:
                network_id = int(private_network_id)
            except ValueError:
                raise 'Something wrong with specified Private Network ID : {0}!'.format(private_network_id)
        else:
            return ''
        return 'NIC = [ NETWORK_ID = {0:d} ]'.format(network_id)

    def _set_specific_nic(self, network_specific_name):
        network_infos = network_specific_name.split(';')
        if len(network_infos) == 1:
            return 'NIC = [ NETWORK = {0} ]'.format(network_infos[0])
        elif len(network_infos) == 2:
            return 'NIC = [ NETWORK = {0}, NETWORK_UNAME = {1} ]'.format(network_infos[0], network_infos[1])
        else:
            raise 'Something wrong with specified Network name : {0}!'.format(network_specific_name)


    def _set_contextualization(self, contextualization_type, public_ssh_key, contextualization_script):
        if contextualization_type != 'cloud-init':
            return 'CONTEXT = [ NETWORK = "YES", SSH_PUBLIC_KEY = "{0}", ' \
                   'START_SCRIPT_BASE64 = "{1}"]'.format(public_ssh_key, base64.b64encode(contextualization_script))
        else:
            return 'CONTEXT = [ PUBLIC_IP = "$NIC[IP]", SSH_PUBLIC_KEY = "{0}", USERDATA_ENCODING = "base64", ' \
                   'USER_DATA = "{1}"]'.format(public_ssh_key, base64.b64encode(contextualization_script))

    @override
    def _start_image(self, user_info, node_instance, vm_name):
        return self._start_image_on_opennebula(user_info, node_instance, vm_name)

    def _start_image_on_opennebula(self, user_info, node_instance, vm_name):
        instance_name = self._set_instance_name(vm_name)

        ram = self._set_ram(node_instance.get_ram())

        cpu = self._set_cpu(node_instance.get_cpu())

        disks = self._set_disks(node_instance.get_image_id(), node_instance.get_root_disk_size())

        additionnal_disks = self._set_additionnal_disks(node_instance.get_volatile_extra_disk_size())

        try:
            network_specific_name = node_instance.get_cloud_parameter('network.specific.name').strip()
        except:
            network_specific_name = ''

        if network_specific_name:
            nics = self._set_specific_nic(network_specific_name)
        else:
            nics = self._set_nics(node_instance.get_network_type(),
                          user_info.get_public_network_name(),
                          user_info.get_private_network_name())

        if self.is_build_image():
            context = self._set_contextualization(node_instance.get_cloud_parameter('contextualization.type'),
                                                  self.tmp_public_key, '')
        else:
            context = self._set_contextualization(node_instance.get_cloud_parameter('contextualization.type'),
                                                  self.user_info.get_public_keys(),
                                                  self._get_bootstrap_script(node_instance))
        custom_vm_template = node_instance.get_cloud_parameter('custom.vm.template') or ''

        template = ' '.join([instance_name, cpu, ram, disks, additionnal_disks, nics, context, custom_vm_template])
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
        self._wait_vm_in_state(vm_id, 'Active', time_out=300, time_sleep=10)
        self._build_image_increment(user_info, node_instance, ip_address)
        util.printStep('Creation of the new Image.')
        self._rpc_execute('one.vm.action', 'poweroff', vm_id)
        self._wait_vm_in_state(vm_id, 'Poweroff', time_out=300, time_sleep=10)
        listener.write_for(machine_name, 'Saving the image')
        new_image_name = node_instance.get_image_short_name() + time.strftime("_%Y%m%d-%H%M%S")
        new_image_id = int(self._rpc_execute(
            'one.vm.disksaveas', vm_id, 0, new_image_name, '', -1))
        self._wait_image_in_state(new_image_id, 'Ready', time_out=1800, time_sleep=30)
        listener.write_for(machine_name, 'Image saved !')
        self._rpc_execute('one.vm.action', 'resume', vm_id)
        self._wait_vm_in_state(vm_id, 'Active', time_out=300, time_sleep=10)
        return str(new_image_id)

    def _get_vm_state(self, vm_id):
        vm = self._rpc_execute('one.vm.info', vm_id)
        return int(eTree.fromstring(vm).findtext('STATE'))

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
        image = self._rpc_execute('one.image.info', image_id)
        return int(eTree.fromstring(image).findtext('STATE'))

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
        return format(int(vm_instance.findtext('TEMPLATE/DISK/SIZE')) / 1024.0, '.3f')

    @override
    def _vm_get_instance_type(self, vm_instance):
        return vm_instance.findtext('USER_TEMPLATE/INSTANCE_TYPE')
