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
from slipstream.NodeDecorator import NodeDecorator
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
                               orchestrator_can_kill_itself_or_its_vapp=True)
        self.flavors = []
        self.images = []
        self.tempPrivateKey = None
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
        # self._thread_local.driver = self._get_driver(user_info)
        # self.flavors = self._thread_local.driver.list_sizes()
        # self.images = self._thread_local.driver.list_images()
        #
        # if self.is_deployment():
        #     self._import_keypair(user_info)
        # elif self.is_build_image():
        #     self._create_keypair_and_set_on_user_info(user_info)

    @override
    def _finalization(self, user_info):
        util.printStep('KB: _finalization.')
        # try:
        #     kp_name = user_info.get_keypair_name()
        #     self._delete_keypair(kp_name)
        # # pylint: disable=W0703
        # except Exception:
        #     pass

    def _build_image(self, user_info, node_instance):
        return self._build_image_on_opennebula(user_info, node_instance)

    def _build_image_on_opennebula(self, user_info, node_instance):
        util.printStep('KB: _build_image_on_opennebula.')
        # self._thread_local.driver = self._get_driver(user_info)
        # listener = self._get_listener()
        #
        # if not user_info.get_private_key() and self.tempPrivateKey:
        #     user_info.set_private_key(self.tempPrivateKey)
        # machine_name = node_instance.get_name()
        #
        # vm = self._get_vm(machine_name)
        #
        # util.printAndFlush("\n  node_instance: %s \n" % str(node_instance))
        # util.printAndFlush("\n  VM: %s \n" % str(vm))
        #
        # ip_address = self._vm_get_ip(vm)
        # vm_id = self._vm_get_id(vm)
        # instance = vm['instance']
        #
        # self._wait_instance_in_running_state(vm_id)
        #
        # self._build_image_increment(user_info, node_instance, ip_address)
        #
        # util.printStep('Creation of the new Image.')
        # listener.write_for(machine_name, 'Saving the image')
        # newImg = self._thread_local.driver.ex_save_image(instance,
        #                                                  node_instance.get_image_short_name(),
        #                                                  metadata=None)
        #
        # self._wait_image_creation_completed(newImg.id)
        # listener.write_for(machine_name, 'Image saved !')
        #
        # return newImg.id
        return None

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
        return self._start_image_on_opennebula(node_instance, vm_name)

    def _start_image_on_opennebula(self, node_instance, vm_name):
        util.printStep('KB: _start_image_on_opennebula.')
        image_id = node_instance.get_image_id()
        #instance_type = int(node_instance.get_instance_type())
        contextualization_script = self.is_build_image() and '' or self._get_bootstrap_script(node_instance)
        with open("/tmp/debug", "a") as myfile:
            myfile.write(contextualization_script)
            myfile.write('\n\nbase64\n')
            myfile.write(base64.b64encode(contextualization_script))
        disk = ' DISK = [ IMAGE_ID  = 8, SIZE = 20000 ]'
        nic = ' NIC = [ NETWORK = "public", NETWORK_UNAME="oneadmin" ]'
        context = ' CONTEXT = [ NETWORK = "YES", SSH_PUBLIC_KEY = "' + self.user_info.get_public_keys() + '", START_SCRIPT_BASE64 = "%s"]' % base64.b64encode(contextualization_script)
        template = 'INSTANCE_TYPE = "micro" VCPU = 1 CPU = 0.5 MEMORY = 512 Name = ' + self.format_instance_name(vm_name) + disk + nic + context
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

        #keypair = user_info.get_keypair_name()
        # #security_groups = self._get_security_groups_for_node_instance(node_instance)
        # flavor = searchInObjectList(self.flavors, 'name', instance_type)
        # image = searchInObjectList(self.images, 'id', image_id)
        # contextualization_script = self.is_build_image() and '' or self._get_bootstrap_script(node_instance)
        #
        # if flavor is None:
        #     raise Exceptions.ParameterNotFoundException("Couldn't find the specified flavor: %s" % instance_type)
        # if image is None:
        #     raise Exceptions.ParameterNotFoundException("Couldn't find the specified image: %s" % image_id)
        #
        # # extract mappings for Public and Private networks from the connector instance
        # network = None
        # network_type = node_instance.get_network_type()
        # if network_type == 'Public':
        #     network_name = user_info.get_public_network_name()
        #     network = searchInObjectList(self.networks, 'name', network_name)
        # elif network_type == 'Private':
        #     network_name = user_info.get_private_network_name()
        #     network = searchInObjectList(self.networks, 'name', network_name)
        #
        # kwargs = {"name": vm_name,
        #           "size": flavor,
        #           "image": image,
        #           "ex_keyname": keypair,
        #           "ex_userdata": contextualization_script,
        #           "ex_security_groups": security_groups}
        #
        # if network is not None:
        #     kwargs["networks"] = [network]
        #
        # instance = self._thread_local.driver.create_node(**kwargs)
        #
        #vm = dict(networkType=node_instance.get_network_type(),
        #          instance='test',
        #          ip='',
        #          id=1)
        #return vm
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

    def _import_keypair(self, user_info):
        util.printStep('KB: _import_keypair.')
        # kp_name = 'ss-key-%i' % int(time.time())
        # public_key = user_info.get_public_keys()
        # try:
        #     kp = self._thread_local.driver.ex_import_keypair_from_string(kp_name, public_key)
        # except Exception as ex:
        #     raise Exceptions.ExecutionException('Cannot import the public key. Reason: %s' % ex)
        # kp_name = kp.name
        # user_info.set_keypair_name(kp_name)
        # return kp_name
        return None

    def _create_keypair_and_set_on_user_info(self, user_info):
        util.printStep('KB: _import_keypair.')
        # kp_name = 'ss-build-image-%i' % int(time.time())
        # kp = self._thread_local.driver.ex_create_keypair(kp_name)
        # user_info.set_private_key(kp.private_key)
        # user_info.set_keypair_name(kp.name)
        # self.tempPrivateKey = kp.private_key
        # return kp.name
        return None

    def _delete_keypair(self, kp_name):
        util.printStep('KB: _delete_keypair.')
        #kp = searchInObjectList(self._thread_local.driver.list_key_pairs(), 'name', kp_name)
        #self._thread_local.driver.delete_key_pair(kp)

