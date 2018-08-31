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

import re
import time

from .LibcloudCloudstackPatch import patch_libcloud
patch_libcloud()

import os

from urlparse import urlparse
from threading import RLock

from slipstream.UserInfo import UserInfo
from slipstream.ConfigHolder import ConfigHolder

from slipstream.cloudconnectors.BaseCloudConnector import BaseCloudConnector
from slipstream.utils.tasksrunner import TasksRunner
from slipstream.NodeDecorator import NodeDecorator
from slipstream.util import override
import slipstream.util as util
import slipstream.exceptions.Exceptions as Exceptions

from libcloud.compute.base import KeyPair
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

import libcloud.security


def getConnector(configHolder):
    return getConnectorClass()(configHolder)


def getConnectorClass():
    return CloudStackClientCloud


def instantiate_from_cimi(cimi_connector, cimi_cloud_credential):
    user_info = UserInfo(cimi_connector['instanceName'])

    cloud_params = {
        UserInfo.CLOUD_USERNAME_KEY: cimi_cloud_credential['key'],
        UserInfo.CLOUD_PASSWORD_KEY: cimi_cloud_credential['secret'],
        'endpoint': cimi_connector.get('endpoint'),
        'zone': cimi_connector.get('zone'),
    }
    user_info.set_cloud_params(cloud_params)

    config_holder = ConfigHolder(options={'verboseLevel': 0, 'retry': False})

    os.environ['SLIPSTREAM_CONNECTOR_INSTANCE'] = cimi_connector['instanceName']

    connector_instance = CloudStackClientCloud(config_holder)

    connector_instance._initialization(user_info)

    return connector_instance

STATE_MAP = {0: 'Running',
             1: 'Rebooting',
             2: 'Terminated',
             3: 'Pending',
             4: 'Unknown',
             5: 'Stopped'}

class CloudStackClientCloud(BaseCloudConnector):

    cloudName = 'cloudstack'

    def __init__(self, configHolder):
        libcloud.security.VERIFY_SSL_CERT = False

        super(CloudStackClientCloud, self).__init__(configHolder)

        self._set_capabilities(contextualization=True,
                               generate_password=True,
                               direct_ip_assignment=True,
                               orchestrator_can_kill_itself_or_its_vapp=True)

        self._zone = None
        self._zones = None
        self._sizes = None
        self._images = None
        self._volumes = None
        self._lock_zone = RLock()
        self._lock_zones = RLock()
        self._lock_sizes = RLock()
        self._lock_images = RLock()
        self._lock_volumes = RLock()
        self._lock_libcloud_driver = RLock()

    @property
    def libcloud_driver(self):
        with self._lock_libcloud_driver:
            if not hasattr(self._thread_local, '_libcloud_driver'):
                util.printDetail('Initializing libcloud driver')
                self._thread_local._libcloud_driver = self._get_driver(self.user_info)
            return self._thread_local._libcloud_driver

    @property
    def zones(self):
        if self._zones is None:
            with self._lock_zones:
                if self._zones is None:
                    util.printDetail('Getting zones')
                    self._zones = self.libcloud_driver.list_locations()
        return self._zones

    @property
    def zone(self):
        if self._zone is None:
            with self._lock_zone:
                if self._zone is None:
                    util.printDetail('Getting zone')
                    self._zone = self._get_zone(self.user_info)
        return self._zone

    @property
    def sizes(self):
        if self._sizes is None:
            with self._lock_sizes:
                if self._sizes is None:
                    util.printDetail('Getting sizes')
                    self._sizes = self.libcloud_driver.list_sizes(location=self.zone)
        return self._sizes

    @property
    def images(self):
        if self._images is None:
            with self._lock_images:
                if self._images is None:
                    util.printDetail('Getting images')
                    self._images = self.libcloud_driver.list_images(location=self.zone)
        return self._images

    @property
    def volumes(self):
        if self._volumes is None:
            with self._lock_volumes:
                if self._volumes is None:
                    util.printDetail('Getting volumes')
                    self._volumes = self.libcloud_driver.list_volumes()
        return self._volumes

    @override
    def _initialization(self, user_info):
        util.printStep('Initialize the CloudStack connector.')

        self.user_info = user_info

        if self.is_build_image():
            raise NotImplementedError('The run category "%s" is not yet implemented' % self.run_category)

    @override
    def _finalization(self, user_info):
        try:
            kp_name = user_info.get_keypair_name()
            if kp_name:
                self._delete_keypair(kp_name)
        except:  # pylint: disable=bare-except
            pass

    @override
    def _start_image(self, user_info, node_instance, vm_name):
        return self._start_image_on_cloudstack(user_info, node_instance, vm_name)

    def _start_image_on_cloudstack(self, user_info, node_instance, vm_name):
        try:
            kp_name = self._import_keypair(user_info)
            node_instance.set_cloud_node_ssh_keypair_name(kp_name)
        except Exceptions.ExecutionException as e:
            util.printError(e)

        instance_name = self.format_instance_name(vm_name)
        instance_type = node_instance.get_instance_type()
        ip_type = node_instance.get_network_type()

        keypair = None
        contextualization_script = None
        if not node_instance.is_windows():
            keypair = user_info.get_keypair_name()
            contextualization_script = self._get_bootstrap_script_if_not_build_image(node_instance)

        security_groups = node_instance.get_security_groups()
        security_groups = (len(security_groups) > 0) and security_groups or None

        try:
            size = [i for i in self.sizes if i.name == instance_type][0]
        except IndexError:
            raise Exceptions.ParameterNotFoundException("Couldn't find the specified instance type: %s" % instance_type)

        image = self._get_image(node_instance)

        disk_size = node_instance.get_cloud_parameter('disk')

        kwargs = dict(name=instance_name,
                      size=size,
                      image=image,
                      location=self.zone,
                      ex_security_groups=security_groups)

        if disk_size:
            kwargs['ex_rootdisksize'] = disk_size.replace('G', '')

        if not node_instance.is_windows():
            kwargs.update(dict(ex_keyname= keypair,
                               ex_userdata=contextualization_script))

        instance = self.libcloud_driver.create_node(**kwargs)

        ip = self._get_instance_ip_address(instance, ip_type)
        if not ip:
            raise Exceptions.ExecutionException("Couldn't find a '%s' IP" % ip_type)

        vm = dict(instance=instance,
                  ip=ip,
                  id=instance.id)
        return vm

    def _get_zone(self, user_info):
        zone_name = user_info.get_cloud('zone', '')
        try:
            return [i for i in self.zones if i.name.lower() == zone_name.lower()][0]
        except IndexError:
            raise Exceptions.ParameterNotFoundException("Couldn't find the specified zone: %s" % zone_name)

    def _get_image(self, node_instance):
        image_id = node_instance.get_image_id()
        try:
            return [i for i in self.images if i.id == image_id][0]
        except IndexError:
            raise Exceptions.ParameterNotFoundException("Couldn't find the specified image: %s" % image_id)

    @override
    def list_instances(self):
        return self.libcloud_driver.list_nodes(location=self.zone)

    @override
    def _create_allow_all_security_group(self):
        sg_name = NodeDecorator.SECURITY_GROUP_ALLOW_ALL_NAME
        sg_desc = NodeDecorator.SECURITY_GROUP_ALLOW_ALL_DESCRIPTION
        driver = self.libcloud_driver

        if any([sg.get('name') == sg_name for sg in driver.ex_list_security_groups()]):
            return

        sg = driver.ex_create_security_group(sg_name, description=sg_desc)
        driver.ex_authorize_security_group_ingress(sg_name, 'tcp', '0.0.0.0/0', 0, 65535)
        driver.ex_authorize_security_group_ingress(sg_name, 'udp', '0.0.0.0/0', 0, 65535)
        driver.ex_authorize_security_group_ingress(sg_name, 'icmp', '0.0.0.0/0')

    def _stop_instances(self, instances):
        tasksRunnner = TasksRunner(self._stop_instance,
                                   max_workers=self.max_iaas_workers,
                                   verbose=self.verboseLevel)
        for instance in instances:
            tasksRunnner.put_task(instance)

        tasksRunnner.run_tasks()
        tasksRunnner.wait_tasks_processed()

    def _stop_instance(self, instance):
        self.libcloud_driver.destroy_node(instance)

    @override
    def _stop_deployment(self):
        instances = [vm['instance'] for vm in self.get_vms().itervalues()]
        self._stop_instances(instances)

    @override
    def _stop_vms_by_ids(self, ids):
        instances = [i for i in self.list_instances() if i.id in ids]
        self._stop_instances(instances)

    @staticmethod
    def _get_driver(user_info):
        CloudStack = get_driver(Provider.CLOUDSTACK)

        url = urlparse(user_info.get_cloud_endpoint())
        secure = (url.scheme == 'https')

        return CloudStack(user_info.get_cloud_username(),
                          user_info.get_cloud_password(),
                          secure=secure,
                          host=url.hostname,
                          port=url.port,
                          path=url.path)

    @override
    def _vm_get_password(self, vm):
        password = vm['instance'].extra.get('password', None)
        print 'VM Password: ', password
        return password

    @override
    def _vm_get_ip(self, vm):
        return vm['ip']

    @override
    def _vm_get_id(self, vm):
        return vm['id']

    @override
    def _vm_get_state(self, vm_instance):
        return STATE_MAP[vm_instance.state]

    def _get_vm_size(self, vm_instance):
        try:
            size = [i for i in self.sizes if i.id == vm_instance.extra.get('size_id')][0]
        except IndexError:
            return None
        else:
            return size

    @override
    def _vm_get_ip_from_list_instances(self, vm_instance):
        return self._get_instance_ip_address(vm_instance)

    @override
    def _vm_get_id_from_list_instances(self, vm):
        return vm.id

    @override
    def _vm_get_cpu(self, vm_instance):
        size = self._get_vm_size(vm_instance)
        if size and 'cpu' in size.extra:
            return size.extra.get('cpu')

    @override
    def _vm_get_ram(self, vm_instance):
        size = self._get_vm_size(vm_instance)
        if size:
            return size.ram

    @override
    def _vm_get_root_disk(self, vm_instance):
        volume = self._find_root_disk_volume(vm_instance.id)
        return volume.size / float(1024 * 1024 * 1024) if volume else None

    @override
    def _vm_get_instance_type(self, vm_instance):
        return vm_instance.extra.get('size_name')

    @override
    def _list_vm_sizes(self):
        return self.sizes

    @override
    def _size_get_cpu(self, vm_size):
        return vm_size.extra.get('cpu')

    @override
    def _size_get_ram(self, vm_size):
        return vm_size.ram

    @override
    def _size_get_instance_type(self, vm_size):
        return vm_size.name

    def _find_root_disk_volume(self, instance_id):
        for v in self.volumes:
            if v.extra.get('instance_id') == instance_id and v.extra.get('volume_type') == 'ROOT':
                return v

    def _get_instance_ip_address(self, instance, ipType='public'):
        if ipType.lower() == 'private':
            return (len(instance.private_ips) != 0) and instance.private_ips[0] or (len(instance.public_ips) != 0) and instance.public_ips[0] or ''
        else:
            return (len(instance.public_ips) != 0) and instance.public_ips[0] or (len(instance.private_ips) != 0) and instance.private_ips[0] or ''

    def _import_keypair(self, user_info):
        kp_name = 'ss-key-%i' % int(time.time() * 1000000)
        public_key = user_info.get_public_keys()
        try:
            kp = self.libcloud_driver.import_key_pair_from_string(kp_name, public_key)
        except Exception as e:
            user_info.set_keypair_name(None)
            raise Exceptions.ExecutionException('Cannot import the public key. Reason: %s' % e)
        kp_name = kp.name
        user_info.set_keypair_name(kp_name)
        return kp_name

    def _create_keypair_and_set_on_user_info(self, user_info):
        kp_name = 'ss-build-image-%i' % int(time.time())
        kp = self.libcloud_driver.create_key_pair(kp_name)
        user_info.set_private_key(kp.private_key)
        kp_name = kp.name
        user_info.set_keypair_name(kp_name)
        return kp_name

    def _delete_keypair(self, kp_name):
        kp = KeyPair(name=kp_name, public_key=None, fingerprint=None,
                     driver=self.libcloud_driver)
        return self.libcloud_driver.delete_key_pair(kp)

    def format_instance_name(self, name):
        name = self.remove_bad_char_in_instance_name(name)
        return self.truncate_instance_name(name)

    def truncate_instance_name(self, name):
        if len(name) <= 63:
            return name
        else:
            return name[:31] + '-' + name[-31:]

    def remove_bad_char_in_instance_name(self, name):
        try:
            newname = re.sub(r'[^a-zA-Z0-9-]', '', name)
            m = re.search('[a-zA-Z]([a-zA-Z0-9-]*[a-zA-Z0-9]+)?', newname)
            return m.string[m.start():m.end()]
        except:
            raise Exceptions.ExecutionException(
                'Cannot handle the instance name "%s". Instance name can '
                'contain ASCII letters "a" through "z", the digits "0" '
                'through "9", and the hyphen ("-"), must be between 1 and 63 '
                'characters long, and can\'t start or end with "-" '
                'and can\'t start with digit' % name)

    def _build_image(self, user_info, node_instance):
        raise Exceptions.ExecutionException("%s doesn't implement build image feature." %
                                            self.__class__.__name__)
