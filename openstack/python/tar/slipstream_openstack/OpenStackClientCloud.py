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

from libcloud.compute.types import Provider
from libcloud.compute.types import NodeState
from libcloud.compute.providers import get_driver
import libcloud.security

import slipstream.util as util
import slipstream.exceptions.Exceptions as Exceptions

from slipstream.util import override
from slipstream.NodeDecorator import NodeDecorator
from slipstream.cloudconnectors.BaseCloudConnector import BaseCloudConnector

def getConnector(configHolder):
    return getConnectorClass()(configHolder)


def getConnectorClass():
    return OpenStackClientCloud


def searchInObjectList(list_, propertyName, propertyValue):
    for element in list_:
        if isinstance(element, dict):
            if element.get(propertyName) == propertyValue:
                return element
        else:
            if getattr(element, propertyName) == propertyValue:
                return element
    return None


class OpenStackClientCloud(BaseCloudConnector):
    cloudName = 'openstack'

    def __init__(self, configHolder):
        libcloud.security.VERIFY_SSL_CERT = False

        super(OpenStackClientCloud, self).__init__(configHolder)

        self._set_capabilities(contextualization=True,
                               orchestrator_can_kill_itself_or_its_vapp=True)

        self.flavors = []
        self.images = []
        self.networks = []
        self.security_groups = []
        self.tempPrivateKey = None

    @override
    def _initialization(self, user_info):
        util.printStep('Initialize the OpenStack connector.')
        self._thread_local.driver = self._get_driver(user_info)
        self.flavors = self._thread_local.driver.list_sizes()
        self.images = self._thread_local.driver.list_images()
        self.networks = self._thread_local.driver.ex_list_networks()
        self.security_groups = self._thread_local.driver.ex_list_security_groups()

        if self.is_deployment():
            self._import_keypair(user_info)
        elif self.is_build_image():
            self._create_keypair_and_set_on_user_info(user_info)

    @override
    def _finalization(self, user_info):
        try:
            kp_name = user_info.get_keypair_name()
            self._delete_keypair(kp_name)
        # pylint: disable=W0703
        except Exception:
            pass

    def _build_image(self, user_info, node_instance):
        return self._build_image_on_openstack(user_info, node_instance)

    def _build_image_on_openstack(self, user_info, node_instance):
        self._thread_local.driver = self._get_driver(user_info)
        listener = self._get_listener()

        if not user_info.get_private_key() and self.tempPrivateKey:
            user_info.set_private_key(self.tempPrivateKey)
        machine_name = node_instance.get_name()

        vm = self._get_vm(machine_name)

        util.printAndFlush("\n  node_instance: %s \n" % str(node_instance))
        util.printAndFlush("\n  VM: %s \n" % str(vm))

        ip_address = self._vm_get_ip(vm)
        vm_id = self._vm_get_id(vm)
        instance = vm['instance']

        self._wait_instance_in_running_state(vm_id)

        self._build_image_increment(user_info, node_instance, ip_address)

        util.printStep('Creation of the new Image.')
        listener.write_for(machine_name, 'Saving the image')
        newImg = self._thread_local.driver.ex_save_image(instance,
                                                         node_instance.get_image_short_name(),
                                                         metadata=None)

        self._wait_image_creation_completed(newImg.id)
        listener.write_for(machine_name, 'Image saved !')

        return newImg.id

    @override
    def _start_image(self, user_info, node_instance, vm_name):
        self._thread_local.driver = self._get_driver(user_info)
        return self._start_image_on_openstack(user_info, node_instance, vm_name)

    def _start_image_on_openstack(self, user_info, node_instance, vm_name):
        image_id = node_instance.get_image_id()
        instance_type = node_instance.get_instance_type()
        keypair = user_info.get_keypair_name()
        security_groups = self._get_security_groups_for_node_instance(node_instance)
        flavor = searchInObjectList(self.flavors, 'name', instance_type)
        image = searchInObjectList(self.images, 'id', image_id)
        contextualization_script = self.is_build_image() and '' or self._get_bootstrap_script(node_instance)

        if flavor is None:
            raise Exceptions.ParameterNotFoundException("Couldn't find the specified flavor: %s" % instance_type)
        if image is None:
            raise Exceptions.ParameterNotFoundException("Couldn't find the specified image: %s" % image_id)

        # extract mappings for Public and Private networks from the connector instance
        network = None
        network_type = node_instance.get_network_type()
        if network_type == 'Public':
            network_name = user_info.get_public_network_name()
            network = searchInObjectList(self.networks, 'name', network_name)
        elif network_type == 'Private':
            network_name = user_info.get_private_network_name()
            network = searchInObjectList(self.networks, 'name', network_name)

        kwargs = {"name": vm_name,
                  "size": flavor,
                  "image": image,
                  "ex_keyname": keypair,
                  "ex_userdata": contextualization_script,
                  "ex_security_groups": security_groups}

        if network is not None:
            kwargs["networks"] = [network]

        instance = self._thread_local.driver.create_node(**kwargs)

        vm = dict(networkType=node_instance.get_network_type(),
                  instance=instance,
                  ip='',
                  id=instance.id)
        return vm

    @override
    def list_instances(self):
        return self._thread_local.driver.list_nodes()

    def _get_security_groups_for_node_instance(self, node_instance):
        security_groups = []
        security_groups_not_found = []

        for sg_name in node_instance.get_security_groups():
            if not sg_name:
                continue
            sgs = [sg for sg in self.security_groups if sg.name == sg_name.strip()]

            if len(sgs) < 1:
                security_groups_not_found.append(sg_name)
            else:
                security_groups.append(sgs[0])

        if security_groups_not_found:
            raise Exceptions.ParameterNotFoundException("Couldn't find the following security groups: %s"
                                                        % ', '.join(security_groups_not_found))

        return security_groups

    @override
    def _create_allow_all_security_group(self):
        sg_name = NodeDecorator.SECURITY_GROUP_ALLOW_ALL_NAME
        sg_desc = NodeDecorator.SECURITY_GROUP_ALLOW_ALL_DESCRIPTION
        driver = self._thread_local.driver

        if any([sg.name == sg_name for sg in self.security_groups]):
            return

        sg = driver.ex_create_security_group(sg_name, sg_desc)
        driver.ex_create_security_group_rule(sg, 'tcp', 1, 65535, cidr='0.0.0.0/0')
        driver.ex_create_security_group_rule(sg, 'udp', 1, 65535, cidr='0.0.0.0/0')
        driver.ex_create_security_group_rule(sg, 'icmp', -1, -1, cidr='0.0.0.0/0')

        # Update the cached list of available security groups
        self.security_groups = driver.ex_list_security_groups()

    @override
    def _stop_deployment(self):
        for _, vm in self.get_vms().items():
            vm['instance'].destroy()

    @override
    def _stop_vms_by_ids(self, ids):
        for node in self._thread_local.driver.list_nodes():
            if node.id in ids:
                node.destroy()

    def _get_driver(self, user_info):
        driverOpenStack = get_driver(Provider.OPENSTACK)
        isHttps = user_info.get_cloud_endpoint().lower().startswith('https://')

        return driverOpenStack(user_info.get_cloud_username(),
                               user_info.get_cloud_password(),
                               secure=isHttps,
                               ex_tenant_name=user_info.get_cloud('tenant.name'),
                               ex_force_auth_url=user_info.get_cloud_endpoint(),
                               ex_force_auth_version='2.0_password',
                               ex_force_service_type=user_info.get_cloud('service.type'),
                               ex_force_service_name=user_info.get_cloud('service.name'),
                               ex_force_service_region=user_info.get_cloud('service.region'))

    @override
    def _vm_get_ip(self, vm):
        return vm['ip']

    @override
    def _vm_get_id(self, vm):
        return vm['id']

    def _get_vm_size(self, vm_instance):
        try:
            size = [i for i in self.flavors if i.id == vm_instance.extra.get('flavorId')][0]
        except IndexError:
            return None
        else:
            return size

    @override
    def _vm_get_ip_from_list_instances(self, vm_instance):
        return self._get_instance_ip_address(vm_instance)

    @override
    def _vm_get_cpu(self, vm_instance):
        size = self._get_vm_size(vm_instance)
        if size:
            return size.vcpus

    @override
    def _vm_get_ram(self, vm_instance):
        size = self._get_vm_size(vm_instance)
        if size:
            return size.ram

    @override
    def _vm_get_root_disk(self, vm_instance):
        size = self._get_vm_size(vm_instance)
        if size:
            return size.disk

    @override
    def _vm_get_instance_type(self, vm_instance):
        size = self._get_vm_size(vm_instance)
        if size:
            return size.name

    def _get_instance_ip_address(self, instance, ip_type='', strict=True):
        if ip_type.lower() == 'private':
            return (len(instance.private_ips) != 0) and instance.private_ips[0] or (len(instance.public_ips) != 0 and not strict) and instance.public_ips[0] or ''
        elif ip_type.lower() == 'public':
            return (len(instance.public_ips) != 0) and instance.public_ips[0] or (len(instance.private_ips) != 0 and not strict) and instance.private_ips[0] or ''
        else:
            return (len(instance.public_ips) != 0) and instance.public_ips[0] or (len(instance.private_ips) != 0) and instance.private_ips[0] or ''

    @override
    def _wait_and_get_instance_ip_address(self, vm):
        timeWait = 300
        timeStop = time.time() + timeWait

        while time.time() < timeStop:
            time.sleep(1)

            ipType = vm['networkType']
            vmId = vm['id']

            instances = self._thread_local.driver.list_nodes()
            instance = searchInObjectList(instances, 'id', vmId)
            ip = self._get_instance_ip_address(instance, ipType or '')
            if ip:
                vm['ip'] = ip
                return vm

        try:
            ip = self._get_instance_ip_address(instance, ipType or '', False)
        # pylint: disable=W0703
        except Exception:
            pass

        if ip:
            vm['ip'] = ip
            return vm

        raise Exceptions.ExecutionException(
            'Timed out while waiting for IPs to be assigned to instances: %s' % vmId)

    def _wait_instance_in_running_state(self, instanceId):
        timeWait = 300
        timeStop = time.time() + timeWait

        state = ''
        while state != NodeState.RUNNING:
            if time.time() > timeStop:
                raise Exceptions.ExecutionException(
                    'Timed out while waiting for instance "%s" enter in running state'
                    % instanceId)
            time.sleep(1)
            node = self._thread_local.driver.list_nodes()
            state = searchInObjectList(node, 'id', instanceId).state

    def _wait_image_creation_completed(self, imageId):
        timeWait = 600
        timeStop = time.time() + timeWait

        imgState = None
        while imgState == None:
            if time.time() > timeStop:
                raise Exceptions.ExecutionException(
                    'Timed out while waiting for image "%s" to be created' % imageId)
            time.sleep(1)
            images = self._thread_local.driver.list_images()
            imgState = searchInObjectList(images, 'id', imageId)

    def _import_keypair(self, user_info):
        kp_name = 'ss-key-%i' % int(time.time())
        public_key = user_info.get_public_keys()
        try:
            kp = self._thread_local.driver.ex_import_keypair_from_string(kp_name, public_key)
        except Exception as ex:
            raise Exceptions.ExecutionException('Cannot import the public key. Reason: %s' % ex)
        kp_name = kp.name
        user_info.set_keypair_name(kp_name)
        return kp_name

    def _create_keypair_and_set_on_user_info(self, user_info):
        kp_name = 'ss-build-image-%i' % int(time.time())
        kp = self._thread_local.driver.ex_create_keypair(kp_name)
        user_info.set_private_key(kp.private_key)
        user_info.set_keypair_name(kp.name)
        self.tempPrivateKey = kp.private_key
        return kp.name

    def _delete_keypair(self, kp_name):
        kp = searchInObjectList(self._thread_local.driver.list_key_pairs(), 'name', kp_name)
        self._thread_local.driver.delete_key_pair(kp)

