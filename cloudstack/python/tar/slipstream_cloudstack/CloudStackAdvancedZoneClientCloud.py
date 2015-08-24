"""
 SlipStream Client
 =====
 Copyright (C) 2013 SixSq Sarl (sixsq.com)
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

import slipstream.exceptions.Exceptions as Exceptions

from slipstream.util import override
from slipstream_cloudstack.CloudStackClientCloud import CloudStackClientCloud

import libcloud.security


def getConnector(configHolder):
    return getConnectorClass()(configHolder)


def getConnectorClass():
    return CloudStackAdvancedZoneClientCloud


class CloudStackAdvancedZoneClientCloud(CloudStackClientCloud):

    cloudName = 'cloudstack'

    def __init__(self, configHolder):
        libcloud.security.VERIFY_SSL_CERT = False

        super(CloudStackAdvancedZoneClientCloud, self).__init__(configHolder)

        self._reset_capabilities()
        self._set_capabilities(contextualization=False,
                               generate_password=True,
                               direct_ip_assignment=True,
                               orchestrator_can_kill_itself_or_its_vapp=True)

    @override
    def _initialization(self, user_info):
        super(CloudStackAdvancedZoneClientCloud, self)._initialization(user_info) # pylint: disable=protected-access
        self.networks = self._thread_local.driver.ex_list_networks() # pylint: disable=attribute-defined-outside-init

    @override
    def _start_image_on_cloudstack(self, user_info, node_instance, vm_name):
        image_id = node_instance.get_image_id()
        instance_name = self.format_instance_name(vm_name)
        instance_type = node_instance.get_instance_type()
        ip_type = node_instance.get_network_type()

        keypair = None
        contextualization_script = None
        if not node_instance.is_windows():
            keypair = user_info.get_keypair_name()
            contextualization_script = self.is_build_image() and '' or self._get_bootstrap_script(node_instance)

        security_groups = node_instance.get_security_groups()
        security_groups = (len(security_groups) > 0) and security_groups or None

        _networks = node_instance.get_networks()
        try:
            networks = [[i for i in self.networks if i.name == x.strip()][0] for x in _networks if x]
        except IndexError:
            raise Exceptions.ParameterNotFoundException(
                "Couldn't find one or more of the specified networks: %s" % _networks)

        try:
            size = [i for i in self.sizes if i.name == instance_type][0]
        except IndexError:
            raise Exceptions.ParameterNotFoundException(
                "Couldn't find the specified instance type: %s" % instance_type)
        try:
            image = [i for i in self.images if i.id == image_id][0]
        except IndexError:
            raise Exceptions.ParameterNotFoundException(
                "Couldn't find the specified image: %s" % image_id)

        if node_instance.is_windows():
            instance = self._thread_local.driver.create_node(
                name=instance_name,
                size=size,
                image=image,
                ex_security_groups=security_groups,
                networks=networks)
        else:
            instance = self._thread_local.driver.create_node(
                name=instance_name,
                size=size,
                image=image,
                ex_keyname=keypair,
                ex_userdata=contextualization_script,
                ex_security_groups=security_groups,
                networks=networks)

        ip = self._get_instance_ip_address(instance, ip_type)
        if not ip:
            raise Exceptions.ExecutionException("Couldn't find a '%s' IP" % ip_type)

        vm = dict(instance=instance,
                  ip=ip,
                  id=instance.id)
        return vm
