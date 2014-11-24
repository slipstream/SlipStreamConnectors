"""
 SlipStream Client
 =====
 Copyright (C) 2014 SixSq Sarl (sixsq.com)
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

import json
import os
import time
from IPy import IP

from slipstream import util
from slipstream.util import override
from slipstream.SlipStreamHttpClient import UserInfo
from slipstream.cloudconnectors.BaseCloudConnector import BaseCloudConnector
from slipstream.exceptions import Exceptions
from .OcciDriver import OcciDriver, VOLATILE_DISK_DEF_BY_ATTRIBUTE, \
    VOLATILE_DISK_NAME_PREFIX


def getConnector(configHolder):
    return OcciClientCloud(configHolder)


class CliCallException(Exception):
    pass


class NoInterfacesAvailable(Exception):
    pass


class NoPublicIpFound(Exception):
    pass


def is_public_ip(ip):
    return (IP(ip).iptype() == 'PUBLIC') and True or False


class OcciClientCloud(BaseCloudConnector):

    cloudName = 'occi'

    WAIT_FOR_IP_SEC = 60 * 2

    @staticmethod
    def _is_public_ip(ip):
        return is_public_ip(ip)

    def __init__(self, config_holder):

        self.wait_for_public_ip = False

        super(OcciClientCloud, self).__init__(config_holder)

        self._set_capabilities(contextualization=True)

        self.user_info = UserInfo(self.get_cloud_service_name())

    @override
    def _initialization(self, user_info):
        endpoint = user_info.get_cloud('endpoint')
        proxy_file = self._get_proxy_file(user_info)
        self.driver = OcciDriver(endpoint, proxy_file)
        self.user_info = user_info

    def _start_image(self, user_info, node_instance, vm_name):
        # In the case of starting from CLI context file can already be provided.
        # The caller is responsible for cleaning up.
        unlink_context_file = False
        context_file = node_instance.get_cloud_parameter('context_file', '')
        if not context_file:
            context = self._get_contextualization(node_instance)
            context_file = util.file_put_content_in_temp_file(context)
            unlink_context_file = True
        try:
            extra_disk_ids = []
            try:
                extra_disk_ids = self._get_extra_disks_ids(node_instance)
                node = self.__start_image(context_file, node_instance,
                                          vm_name, extra_disk_ids)
            except Exception:
                self._delete_disks(extra_disk_ids)
                raise
            return node
        finally:
            if unlink_context_file:
                os.unlink(context_file)

    def _build_image(self, user_info, node_instance):
        raise Exceptions.ExecutionException("%s doesn't implement build image feature." %
                                            self.__class__.__name__)

    def _stop_vms_by_ids(self, vm_ids):
        self._print_detail("Terminate instances by IDs.")
        for vm_id in vm_ids:
            self._print_detail("   terminating '%s'" % vm_id)
            self._stop_instance(vm_id)

    @override
    def _stop_deploymet(self):
        self._print_detail("Terminate all instances.")
        for nodename, node in self.get_vms().items():
            self._print_detail("   terminating [%s, %s]" % (nodename, node))
            self._stop_instance(self._vm_get_id(node))

    def _vm_get_id(self, node):
        return node['id']

    def _vm_get_ip(self, node, public_ip_only=False):
        '''Return the first found public IP of the VM or the first private one.
        Raise NoInterfacesAvailable if no interfaces are set on the VM.
        If public_ip_only is True - return first found public IP or raise
        NoPublicIpFound.
        '''
        netkind = "http://schemas.ogf.org/occi/infrastructure#networkinterface"
        net_ifaces = self._get_links_data_for_kind(node, netkind)
        if not net_ifaces:
            raise NoInterfacesAvailable('No network interfaces found '
                                        'on VM ' + self._vm_get_id(node))
        ips = [self._vm_get_interface_ip(net_iface) for net_iface in net_ifaces]
        for ip in ips:
            if self._is_public_ip(ip):
                return ip
        if public_ip_only:
            raise NoPublicIpFound('No public IP found from %s' % str(ips))
        else:
            return ips[0]

    def _get_proxy_file(self, user_info):
        try:
            # When called from occi-run-instances, VOMS proxy is given as file.
            return user_info.get_cloud('proxy_file')
        except KeyError:
            material = user_info.get_cloud('proxy')
            return util.file_put_content_in_temp_file(material + '\n')

    def __start_image(self, context_file, node_instance, vm_name,
                      extra_disk_ids):
        '''Start image, wait for IP to be set, return OCCI compute node (VM).
        '''
        ostpl = node_instance.get_image_id()
        restpl = node_instance.get_instance_type()
        network_id = self._get_network_id(node_instance)
        instance_name = node_instance.get_name()

        # OCCI doesn't like ':' in the VM names.
        _vm_name = vm_name.replace(':', '_')
        url = self.driver.create_compute(context_file, ostpl, restpl, _vm_name,
                                         extra_disk_ids)
        vm_id = self._get_id_from_uri(url)
        vm = self._describe_instance(vm_id)
        if network_id:
            try:
                self._attach_network_by_id(vm, network_id)
            except Exception:
                self._try_publish_vm_id(instance_name, vm_id)
                raise
        try:
            vm = self._wait_ip_set_on_node(vm, self.wait_for_public_ip)
        except Exception:
            self._try_publish_vm_id(instance_name, vm_id)
            raise
        return vm

    def _try_publish_vm_id(self, instance_name, vm_id):
        try:
            self._publish_vm_id(instance_name, vm_id)
        except Exception as ex:
            self._print_detail("Failed to publish VM id: %s" % str(ex))

    def _delete_disks(self, disk_ids):
        for disk_id in disk_ids:
            self._delete_disk(disk_id)

    def _delete_disk(self, disk_id):
        self.driver.delete_storage(disk_id)

    def _wait_ip_set_on_node(self, node, public_ip=False):
        vm_id = self._vm_get_id(node)
        time_end = time.time() + self.WAIT_FOR_IP_SEC
        while time.time() <= time_end:
            node = self._describe_instance(vm_id)
            try:
                ip = self._vm_get_ip(node, public_ip_only=public_ip)
            except NoInterfacesAvailable:
                pass
            else:
                if ip:
                    return node
            time.sleep(3)
        raise Exceptions.ExecutionException(
            'Timed out after %s sec waiting for IP to be set on VM %s ' % \
            (self.WAIT_FOR_IP_SEC, vm_id))

    def _get_extra_disks_ids(self, node_instance):
        '''Return list of extra disk IDs as defined by user.
        If disk is volatile, the disk size is expected (in GB) from the
        user instead. Then, the disk of the requested size is created and its
        ID is returned.
        '''
        extra_disk_ids = []

        if node_instance.get_volatile_extra_disk_size():
            volatile_disk_id = self._create_volatile_disk(
                node_instance.get_volatile_extra_disk_size())
            extra_disk_ids.append(volatile_disk_id)

        # TODO: enable when providing persistent disk is implemented server side.
#         if node_instance.get_persistent_extra_disk_id():
#             extra_disk_ids.append(node_instance.get_persistent_extra_disk_id())

        return extra_disk_ids

    def _create_volatile_disk(self, size):
        '''Return cloud ID of the created disk.
        '''
        disk_uri = self.driver.create_volatile_storage(size)
        return self._get_id_from_uri(disk_uri)

    def _attach_network_by_id(self, vm, network_id):
        '''Attach started VM to the defined network.
        '''
        self.driver.attach_network(self._vm_get_id(vm), network_id)

    @staticmethod
    def _get_network_id(node_instance):
        try:
            return node_instance.get_cloud_parameter('network.id')
        except Exceptions.ParameterNotFoundException:
            return ''

    def _get_contextualization(self, node_instance):
        '''cloud-init based contextualization.
        '''
        return self._get_cloudinit_multipart(node_instance, self.user_info)

    def _get_cloudinit_multipart(self, node_instance, user_info):
        '''Two parts: embedded bootstrap wrapper script and cloud-init config.
        '''
        bootstrap_script = self._get_bootstrap_script(
            node_instance, pre_bootstrap=self._get_prebootstrap_script())

        data = """Content-Type: multipart/mixed; boundary="%(boundary)s"
MIME-Version: 1.0

--%(boundary)s
Content-Type: text/cloud-config; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Content-Disposition: attachment; filename="userdata.txt"

%(cloud_init_config)s

--%(boundary)s
Content-Type: text/x-shellscript; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Content-Disposition: attachment; filename="run.sh"

%(bootstrap_script)s

--%(boundary)s--
""" % {'cloud_init_config': self._get_cloudinit_config(node_instance, user_info),
       'bootstrap_script': bootstrap_script,
       'boundary': '================4393449873403893838=='}

        return data

    def _get_prebootstrap_script(self):
        """ FIXME: we assume that the target system is RedHat based
        and we will use YUM.
        """
        script = 'yum install -y wget python'
        if self.is_start_orchestrator():
            script += """
cat > /etc/yum.repos.d/egi-rocci.repo <<EOF
[rocci.cli-sl-6-x86_64]
name=Repository for rocci.cli (o/s: sl6 arch: x86_64)
baseurl=http://repository.egi.eu/community/software/rocci.cli/4.2.x/releases/sl/6/x86_64/RPMS/
enabled=1
gpgcheck=0
EOF
yum install -y occi-cli

# To resolve an issue with image os_tpl#02f8cd09-7c79-4b3a-923a-51cd16496a6f
# on https://prisma-cloud.ba.infn.it:8787
rpm -e --nodeps python-crypto || true
rpm -e --nodeps python-paramiko || true
yum install -y gcc python-devel python-pip
pip install paramiko==1.9.0
pip install pycrypto
"""
        return script

    @staticmethod
    def _get_cloudinit_config(node_instance, user_info):
        config = """#cloud-config
users:
 - name: %(username)s
   lock-passwd: true
   ssh-import-id: %(username)s
   ssh-authorized-keys:
    - %(ssh_key)s
""" % {'username': node_instance.get_username('root'),
       'ssh_key': user_info.get_public_keys()}
        return config

    def _get_attached_volatile_disks(self, vm_id):
        '''Return a list of volatile disk IDs linked to the VM.
        '''
        storage_kind = 'http://schemas.ogf.org/occi/infrastructure#storagelink'
        vm = self._get_vm_by_id(vm_id)
        attached_disks = self._get_links_data_for_kind(vm, storage_kind)
        volatile_disk_ids = []
        for disk in attached_disks:
            disk_id = self._get_storage_id_if_volatile(disk)
            if disk_id:
                volatile_disk_ids.append(disk_id)
        return volatile_disk_ids

    def _get_storage_id_if_volatile(self, disk):
        if VOLATILE_DISK_DEF_BY_ATTRIBUTE:
            raise NotImplementedError('Getting disk type by attributes '
                'not available. Unable to determine disk type.')
        else:
            disk_name = disk['attributes']['occi']['core']['title']
            if disk_name.startswith(VOLATILE_DISK_NAME_PREFIX):
                return self._get_id_from_uri(disk['target'])

    def _get_vm_by_id(self, vm_id):
        '''Return VM as dictionary.
        '''
        vms = self._list_instances([vm_id])
        if len(vms) > 0:
            return vms[0]
        else:
            return {}

    @staticmethod
    def _get_links_data_for_kind(resource_dict, kind):
        '''Return list of 'kind's matching 'links' maps.
        '''
        links_data = []
        for link in resource_dict['links']:
            if link['kind'] == kind:
                links_data.append(link)
        return links_data

    @staticmethod
    def _vm_get_interface_ip(net_iface):
        return net_iface['attributes']['occi']['networkinterface']['address']

    @staticmethod
    def _vm_get_state(node):
        return node['attributes']['occi']['compute']['state']

    def _stop_instance(self, vm_id):
        attached_volatile_disks = self._get_attached_volatile_disks(vm_id)
        self._vm_detach_disks(vm_id, attached_volatile_disks)
        self._delete_instance(vm_id)
        self._delete_disks(attached_volatile_disks)

    def _vm_detach_disks(self, vm_id, disk_ids):
        for disk_id in disk_ids:
            self._vm_detach_disk(vm_id, disk_id)

    def _vm_detach_disk(self, vm_id, disk_id):
        self.driver.unlink_disk_from_vm(vm_id, disk_id)

    def _delete_instance(self, vm_id):
        self.driver.delete_compute(vm_id)

    def list_instances(self, vm_ids=[]):
        '''Return list of nodes.
        '''
        if vm_ids:
            return self._list_instances(vm_ids)
        else:
            return self._describe_instances()

    def _list_instances(self, vm_ids_list):
        '''Return list of nodes.
        '''
        instances = []
        for vm_id in vm_ids_list:
            instances.append(self._describe_instance(vm_id))
        return instances

    def _describe_instance(self, vm_id):
        '''Return dict representing node.
        '''
        output = self.driver.describe_compute(vm_id)
        return json.loads(output)[0]

    def _describe_instances(self):
        '''Return list of nodes.
        '''
        output = self.driver.describe_compute()
        return json.loads(output)

    #
    # Helper methods.
    #
    @staticmethod
    def _get_id_from_uri(uri):
        return uri.rsplit('/', 1)[-1]
