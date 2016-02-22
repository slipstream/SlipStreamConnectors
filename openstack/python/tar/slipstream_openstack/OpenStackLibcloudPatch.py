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

from libcloud.compute.base import Node
from libcloud.compute.types import NodeState
from libcloud.utils.networking import is_public_subnet
from libcloud.compute.drivers.openstack import OpenStackComputeConnection, \
                                               OpenStack_1_1_NodeDriver
from libcloud.common.openstack_identity import OpenStackServiceCatalog,\
                                               OpenStackServiceCatalogEntry, \
                                               OpenStackServiceCatalogEntryEndpoint, \
                                               OpenStackIdentityEndpointType


def _parse_service_catalog_auth_v3(self, service_catalog):
    entries = []

    for item in service_catalog:
        service_type = item['type']
        service_name = item.get('name', None)

        entry_endpoints = []
        for endpoint in item['endpoints']:
            region = endpoint.get('region', None)
            url = endpoint['url']
            endpoint_type = endpoint['interface']

            if endpoint_type == 'internal':
                endpoint_type = OpenStackIdentityEndpointType.INTERNAL
            elif endpoint_type == 'public':
                endpoint_type = OpenStackIdentityEndpointType.EXTERNAL
            elif endpoint_type == 'admin':
                endpoint_type = OpenStackIdentityEndpointType.ADMIN

            entry_endpoint = OpenStackServiceCatalogEntryEndpoint(
                region=region, url=url, endpoint_type=endpoint_type)
            entry_endpoints.append(entry_endpoint)

        entry = OpenStackServiceCatalogEntry(service_type=service_type,
                                             endpoints=entry_endpoints,
                                             service_name=service_name)
        entries.append(entry)

    return entries

def _to_node(self, api_node):
    public_networks_labels = ['public', 'internet']

    public_ips, private_ips = [], []

    for label, values in api_node['addresses'].items():
        for value in values:
            ip = value['addr']

            is_public_ip = False

            try:
                public_subnet = is_public_subnet(ip)
            except:
                # IPv6
                public_subnet = False

            # Openstack Icehouse sets 'OS-EXT-IPS:type' to 'floating' for
            # public and 'fixed' for private
            explicit_ip_type = value.get('OS-EXT-IPS:type', None)

            if public_subnet:
                # Check for public subnet
                is_public_ip = True
            elif explicit_ip_type == 'floating':
                is_public_ip = True
            elif explicit_ip_type == 'fixed':
                is_public_ip = False
            elif label in public_networks_labels:
                # Try label next
                is_public_ip = True

            if is_public_ip:
                public_ips.append(ip)
            else:
                private_ips.append(ip)

    # Sometimes 'image' attribute is not present if the node is in an error
    # state
    image = api_node.get('image', None)
    image_id = image.get('id', None) if image else None
    config_drive = api_node.get("config_drive", False)
    volumes_attached = api_node.get('os-extended-volumes:volumes_attached')

    return Node(
        id=api_node['id'],
        name=api_node['name'],
        state=self.NODE_STATE_MAP.get(api_node['status'],
                                      NodeState.UNKNOWN),
        public_ips=public_ips,
        private_ips=private_ips,
        driver=self,
        extra=dict(
            addresses=api_node['addresses'],
            hostId=api_node['hostId'],
            access_ip=api_node.get('accessIPv4'),
            access_ipv6=api_node.get('accessIPv6', None),
            # Docs says "tenantId", but actual is "tenant_id". *sigh*
            # Best handle both.
            tenantId=api_node.get('tenant_id') or api_node['tenantId'],
            userId=api_node.get('user_id', None),
            imageId=image_id,
            flavorId=api_node['flavor']['id'],
            uri=next(link['href'] for link in api_node['links'] if
                     link['rel'] == 'self'),
            metadata=api_node['metadata'],
            password=api_node.get('adminPass', None),
            created=api_node['created'],
            updated=api_node['updated'],
            key_name=api_node.get('key_name', None),
            disk_config=api_node.get('OS-DCF:diskConfig', None),
            config_drive=config_drive,
            availability_zone=api_node.get('OS-EXT-AZ:availability_zone'),
            volumes_attached=volumes_attached,
            task_state=api_node.get("OS-EXT-STS:task_state", None),
            vm_state=api_node.get("OS-EXT-STS:vm_state", None),
            power_state=api_node.get("OS-EXT-STS:power_state", None),
            progress=api_node.get("progress", None),
            fault=api_node.get('fault')
        ),
    )

def patch_libcloud():
    OpenStack_1_1_NodeDriver._to_node = _to_node
    OpenStackComputeConnection.service_name = None
    OpenStackServiceCatalog._parse_service_catalog_auth_v3 = _parse_service_catalog_auth_v3

