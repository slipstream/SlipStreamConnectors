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
from libcloud.compute.types import NodeState, LibcloudError
from libcloud.utils.networking import is_public_subnet
from libcloud.common.openstack import OpenStackDriverMixin, \
                                      OpenStackBaseConnection
from libcloud.compute.drivers.openstack import OpenStackComputeConnection, \
                                               OpenStack_1_1_NodeDriver, \
                                               OpenStack_1_1_FloatingIpAddress
from libcloud.common.openstack_identity import OpenStackServiceCatalog,\
                                               OpenStackServiceCatalogEntry, \
                                               OpenStackServiceCatalogEntryEndpoint, \
                                               OpenStackIdentityConnection, \
                                               OpenStackIdentity_3_0_Connection, \
                                               OpenStackIdentityEndpointType, \
                                               OpenStackIdentityTokenScope, \
                                               get_class_for_auth_version


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

# -------------------------------------------------------------------------------- #


def OpenStackDriverMixin__init__(self, *args, **kwargs):
    self._ex_force_base_url = kwargs.get('ex_force_base_url', None)
    self._ex_force_auth_url = kwargs.get('ex_force_auth_url', None)
    self._ex_force_auth_version = kwargs.get('ex_force_auth_version', None)
    self._ex_force_auth_token = kwargs.get('ex_force_auth_token', None)
    self._ex_token_scope = kwargs.get('ex_token_scope', None)
    self._ex_domain_name = kwargs.get('ex_domain_name', None)
    self._ex_tenant_name = kwargs.get('ex_tenant_name', None)
    self._ex_force_service_type = kwargs.get('ex_force_service_type', None)
    self._ex_force_service_name = kwargs.get('ex_force_service_name', None)
    self._ex_force_service_region = kwargs.get('ex_force_service_region',
                                               None)


def openstack_connection_kwargs(self):
    """

    :rtype: ``dict``
    """
    rv = {}
    if self._ex_force_base_url:
        rv['ex_force_base_url'] = self._ex_force_base_url
    if self._ex_force_auth_token:
        rv['ex_force_auth_token'] = self._ex_force_auth_token
    if self._ex_force_auth_url:
        rv['ex_force_auth_url'] = self._ex_force_auth_url
    if self._ex_force_auth_version:
        rv['ex_force_auth_version'] = self._ex_force_auth_version
    if self._ex_token_scope:
        rv['ex_token_scope'] = self._ex_token_scope
    if self._ex_domain_name:
        rv['ex_domain_name'] = self._ex_domain_name
    if self._ex_tenant_name:
        rv['ex_tenant_name'] = self._ex_tenant_name
    if self._ex_force_service_type:
        rv['ex_force_service_type'] = self._ex_force_service_type
    if self._ex_force_service_name:
        rv['ex_force_service_name'] = self._ex_force_service_name
    if self._ex_force_service_region:
        rv['ex_force_service_region'] = self._ex_force_service_region
    return rv

"""
    :param token_scope: Whether to scope a token to a "project", a
                        "domain" or "unscoped".
    :type token_scope: ``str``

:param ex_domain_name: When authenticating, provide this domain
name to the identity service.  A scoped token will be returned.
Some cloud providers require the domain name to be provided at
authentication time.  Others will use a default domain if none
is provided.
:type ex_domain_name: ``str``
"""

AUTH_API_VERSION = '1.1'


def OpenStackBaseConnection__init__(self, user_id, key, secure=True,
                                    host=None, port=None, timeout=None,
                                    ex_force_base_url=None,
                                    ex_force_auth_url=None,
                                    ex_force_auth_version=None,
                                    ex_force_auth_token=None,
                                    ex_token_scope=None,
                                    ex_domain_name=None,
                                    ex_tenant_name=None,
                                    ex_force_service_type=None,
                                    ex_force_service_name=None,
                                    ex_force_service_region=None,
                                    retry_delay=None, backoff=None):
    super(OpenStackBaseConnection, self).__init__(
        user_id, key, secure=secure, timeout=timeout,
        retry_delay=retry_delay, backoff=backoff)

    if ex_force_auth_version:
        self._auth_version = ex_force_auth_version

    self._ex_force_base_url = ex_force_base_url
    self._ex_force_auth_url = ex_force_auth_url
    self._ex_force_auth_token = ex_force_auth_token
    self._ex_token_scope = ex_token_scope
    self._ex_domain_name = ex_domain_name
    self._ex_tenant_name = ex_tenant_name
    self._ex_force_service_type = ex_force_service_type
    self._ex_force_service_name = ex_force_service_name
    self._ex_force_service_region = ex_force_service_region
    self._osa = None

    if ex_force_auth_token and not ex_force_base_url:
        raise LibcloudError(
            'Must also provide ex_force_base_url when specifying '
            'ex_force_auth_token.')

    if ex_force_auth_token:
        self.auth_token = ex_force_auth_token

    if not self._auth_version:
        self._auth_version = AUTH_API_VERSION

    auth_url = self._get_auth_url()

    if not auth_url:
        raise LibcloudError('OpenStack instance must ' +
                            'have auth_url set')


def get_auth_class(self):
    """
    Retrieve identity / authentication class instance.

    :rtype: :class:`OpenStackIdentityConnection`
    """
    if not self._osa:
        auth_url = self._get_auth_url()

        cls = get_class_for_auth_version(auth_version=self._auth_version)
        self._osa = cls(auth_url=auth_url,
                        user_id=self.user_id,
                        key=self.key,
                        domain_name=self._ex_domain_name,
                        tenant_name=self._ex_tenant_name,
                        token_scope=self._ex_token_scope,
                        timeout=self.timeout,
                        parent_conn=self)

    return self._osa


def OpenStackIdentityConnection__init__(self, auth_url, user_id, key, tenant_name=None,
                                        domain_name=None, token_scope=None,
                                        timeout=None, parent_conn=None):
    super(OpenStackIdentityConnection, self).__init__(user_id=user_id,
                                                      key=key,
                                                      url=auth_url,
                                                      timeout=timeout)

    self.parent_conn = parent_conn

    # enable tests to use the same mock connection classes.
    if parent_conn:
        self.conn_classes = parent_conn.conn_classes
        self.driver = parent_conn.driver
    else:
        self.driver = None

    self.auth_url = auth_url
    self.tenant_name = tenant_name
    self.domain_name = domain_name if domain_name is not None else 'Default'
    self.token_scope = token_scope if token_scope is not None else \
        OpenStackIdentityTokenScope.PROJECT
    self.timeout = timeout

    self.urls = {}
    self.auth_token = None
    self.auth_token_expires = None
    self.auth_user_info = None


def OpenStackIdentity_3_0_Connection__init__(self, auth_url, user_id, key, tenant_name=None,
                                             domain_name=None, token_scope=None,
                                             timeout=None, parent_conn=None):
    """
    :param tenant_name: Name of the project this user belongs to. Note:
                        When token_scope is set to project, this argument
                        control to which project to scope the token to.
    :type tenant_name: ``str``

    :param domain_name: Domain the user belongs to. Note: Then token_scope
                        is set to token, this argument controls to which
                        domain to scope the token to.
    :type domain_name: ``str``

    :param token_scope: Whether to scope a token to a "project", a
                        "domain" or "unscoped"
    :type token_scope: ``str``
    """
    super(OpenStackIdentity_3_0_Connection,
          self).__init__(auth_url=auth_url,
                         user_id=user_id,
                         key=key,
                         tenant_name=tenant_name,
                         domain_name=domain_name,
                         token_scope=token_scope,
                         timeout=timeout,
                         parent_conn=parent_conn)

    if self.token_scope not in self.VALID_TOKEN_SCOPES:
        raise ValueError('Invalid value for "token_scope" argument: %s' %
                         (self.token_scope))

    if (self.token_scope == OpenStackIdentityTokenScope.PROJECT and
            (not self.tenant_name or not self.domain_name)):
        raise ValueError('Must provide tenant_name and domain_name '
                         'argument')
    elif (self.token_scope == OpenStackIdentityTokenScope.DOMAIN and
              not self.domain_name):
        raise ValueError('Must provide domain_name argument')

    self.auth_user_roles = None


def ex_create_floating_ip(self, ip_pool=None):
    """
    Create new floating IP. The ip_pool attribute is optional only if your
    infrastructure has only one IP pool available.

    :param      ip_pool: name of the floating IP pool
    :type       ip_pool: ``str``

    :rtype: :class:`OpenStack_1_1_FloatingIpAddress`
    """
    data = {'pool': ip_pool} if ip_pool is not None else {}
    resp = self.connection.request('/os-floating-ips',
                                   method='POST',
                                   data=data)

    data = resp.object['floating_ip']
    id = data['id']
    ip_pool_ = data.get('pool')
    ip_address = data['ip']
    return OpenStack_1_1_FloatingIpAddress(id=id,
                                           ip_address=ip_address,
                                           pool=ip_pool_,
                                           node_id=None,
                                           driver=self)


def patch_libcloud():
    OpenStack_1_1_NodeDriver._to_node = _to_node
    OpenStack_1_1_NodeDriver.ex_create_floating_ip = ex_create_floating_ip

    OpenStackComputeConnection.service_name = None
    OpenStackComputeConnection.service_name = None

    OpenStackServiceCatalog._parse_service_catalog_auth_v3 = _parse_service_catalog_auth_v3

    OpenStackDriverMixin.__init__ = OpenStackDriverMixin__init__
    OpenStackDriverMixin.openstack_connection_kwargs = openstack_connection_kwargs

    OpenStackBaseConnection._ex_domain_name = None
    OpenStackBaseConnection.__init__ = OpenStackBaseConnection__init__
    OpenStackBaseConnection.get_auth_class = get_auth_class

    OpenStackIdentityConnection.__init__ = OpenStackIdentityConnection__init__
    OpenStackIdentity_3_0_Connection.__init__ = OpenStackIdentity_3_0_Connection__init__


