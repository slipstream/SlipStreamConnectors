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

from libcloud.compute.drivers.openstack import OpenStackComputeConnection
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

def patch_libcloud():
    OpenStackComputeConnection.service_name = None
    OpenStackServiceCatalog._parse_service_catalog_auth_v3 = _parse_service_catalog_auth_v3

