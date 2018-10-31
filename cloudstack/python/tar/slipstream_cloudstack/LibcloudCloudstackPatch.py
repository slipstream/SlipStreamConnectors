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

import datetime

from libcloud.compute.drivers.cloudstack import (CloudStackNodeDriver,
                                                 CloudStackAddress,
                                                 CloudStackIPForwardingRule,
                                                 CloudStackPortForwardingRule,
                                                 CloudStackNode,
                                                 RESOURCE_EXTRA_ATTRIBUTES_MAP)
from libcloud.utils.networking import is_private_subnet
from libcloud.compute.types import LibcloudError
from libcloud.compute.base import NodeImage



def ex_authorize_security_group_ingress(self, securitygroupname, protocol,
                                        cidrlist, startport=None, endport=None,
                                        icmptype=None, icmpcode=None, **kwargs):
    """
    Creates a new Security Group Ingress rule

    :param   securitygroupname: The name of the security group.
                                Mutually exclusive with securitygroupid.
    :type    securitygroupname: ``str``

    :param   protocol: Can be TCP, UDP or ICMP.
                       Sometime other protocols can be used like AH, ESP, GRE.
    :type    protocol: ``str``

    :param   cidrlist: Source address CIDR for which this rule applies.
    :type    cidrlist: ``str``

    :param   startport: Start port of the range for this ingress rule.
                        Applies to protocols TCP and UDP.
    :type    startport: ``int``

    :param   endport: End port of the range for this ingress rule.
                      It can be None to set only one port.
                      Applies to protocols TCP and UDP.
    :type    endport: ``int``

    :param   icmptype: Type of the ICMP packet (eg: 8 for Echo Request).
                       -1 or None means "all types".
                       Applies to protocol ICMP.
    :type    icmptype: ``int``

    :param   icmpcode: Code of the ICMP packet for the specified type.
                       If the specified type doesn't require a code set this
                       value to 0.
                       -1 or None means "all codes".
                       Applies to protocol ICMP.
    :type    icmpcode: ``int``

    :keyword   account: An optional account for the security group.
                        Must be used with domainId.
    :type      account: ``str``

    :keyword domainid: An optional domainId for the security group.
                       If the account parameter is used, domainId must also
                       be used.

    :keyword projectid: An optional project of the security group
    :type    projectid: ``str``

    :param securitygroupid: The ID of the security group.
                            Mutually exclusive with securitygroupname
    :type  securitygroupid: ``str``

    :param usersecuritygrouplist: User to security group mapping
    :type  usersecuritygrouplist: ``dict``

    :rtype: ``dict``
    """

    args = kwargs.copy()
    protocol = protocol.upper()

    args.update({
        'securitygroupname': securitygroupname,
        'protocol': protocol,
        'cidrlist': cidrlist
    })

    if protocol not in ('TCP', 'UDP') and \
            (startport is not None or endport is not None):
        raise LibcloudError('"startport" and "endport" are only valid with '
                            'protocol TCP or UDP.')

    if protocol != 'ICMP' and (icmptype is not None or icmpcode is not None):
        raise LibcloudError('"icmptype" and "icmpcode" are only valid with '
                            'protocol ICMP.')

    if protocol in ('TCP', 'UDP'):
        if startport is None:
            raise LibcloudError('Protocols TCP and UDP require at least '
                                '"startport" to be set.')
        if startport is not None and endport is None:
            endport = startport

        args.update({
            'startport': startport,
            'endport': endport
        })

    if protocol == 'ICMP':
        if icmptype is None:
            icmptype = -1
        if icmpcode is None:
            icmpcode = -1

        args.update({
            'icmptype': icmptype,
            'icmpcode': icmpcode
        })

    return self._async_request(command='authorizeSecurityGroupIngress',
                               params=args,
                               method='GET')['securitygroup']


def list_nodes(self, project=None, location=None):
    """
    @inherits: :class:`NodeDriver.list_nodes`
    :keyword    project: Limit nodes returned to those configured under
                         the defined project.
    :type       project: :class:`.CloudStackProject`
    :keyword    location: Limit nodes returned to those in the defined
                          location.
    :type       location: :class:`.NodeLocation`
    :rtype: ``list`` of :class:`CloudStackNode`
    """

    args = {}

    if project:
        args['projectid'] = project.id

    if location is not None:
        args['zoneid'] = location.id

    vms = self._sync_request('listVirtualMachines', params=args)
    addrs = self._sync_request('listPublicIpAddresses', params=args)
    port_forwarding_rules = self._sync_request('listPortForwardingRules')
    ip_forwarding_rules = self._sync_request('listIpForwardingRules')

    public_ips_map = {}
    for addr in addrs.get('publicipaddress', []):
        if 'virtualmachineid' not in addr:
            continue
        vm_id = str(addr['virtualmachineid'])
        if vm_id not in public_ips_map:
            public_ips_map[vm_id] = {}
        public_ips_map[vm_id][addr['ipaddress']] = addr['id']

    nodes = []

    for vm in vms.get('virtualmachine', []):
        public_ips = public_ips_map.get(str(vm['id']), {}).keys()
        public_ips = list(public_ips)
        node = self._to_node(data=vm, public_ips=public_ips)

        addresses = public_ips_map.get(str(vm['id']), {}).items()
        addresses = [CloudStackAddress(id=address_id, address=address,
                                       driver=node.driver) for
                     address, address_id in addresses]
        node.extra['ip_addresses'] = addresses

        rules = []
        for addr in addresses:
            for r in ip_forwarding_rules.get('ipforwardingrule', []):
                if str(r['virtualmachineid']) == node.id:
                    rule = CloudStackIPForwardingRule(node, r['id'],
                                                      addr,
                                                      r['protocol']
                                                      .upper(),
                                                      r['startport'],
                                                      r['endport'])
                    rules.append(rule)
        node.extra['ip_forwarding_rules'] = rules

        rules = []
        for r in port_forwarding_rules.get('portforwardingrule', []):
            if str(r['virtualmachineid']) == node.id:
                addr = [CloudStackAddress(id=a['id'],
                                          address=a['ipaddress'],
                                          driver=node.driver)
                        for a in addrs.get('publicipaddress', [])
                        if a['ipaddress'] == r['ipaddress']]
                rule = CloudStackPortForwardingRule(node, r['id'],
                                                    addr[0],
                                                    r['protocol'].upper(),
                                                    r['publicport'],
                                                    r['privateport'],
                                                    r['publicendport'],
                                                    r['privateendport'])
                if not addr[0].address in node.public_ips:
                    node.public_ips.append(addr[0].address)
                rules.append(rule)
        node.extra['port_forwarding_rules'] = rules

        nodes.append(node)

    return nodes


def list_images(self, location=None):
    args = {
        'templatefilter': 'executable'
    }
    if location is not None:
        args['zoneid'] = location.id

    imgs = self._sync_request(command='listTemplates',
                              params=args,
                              method='GET')
    images = []
    for img in imgs.get('template', []):

        extra = {'hypervisor': img['hypervisor'],
                 'format': img['format'],
                 'os': img['ostypename'],
                 'displaytext': img['displaytext'],
                 'location': img.get('zonename'),
                 'ready': img.get('isready', True),
                 'featured': img.get('isfeatured', False)}

        size = img.get('size', None)
        if size is not None:
            extra.update({'size': img['size']})

        if 'created' in img:
            try:
                created = datetime.datetime.strptime(img['created'][:19], '%Y-%m-%dT%H:%M:%S')
                extra.update({'created': created})
            except:
                pass

        images.append(NodeImage(
            id=img['id'],
            name=img['name'],
            driver=self.connection.driver,
            extra=extra))
    return images


def _to_node(self, data, public_ips=None):
    """
    :param data: Node data object.
    :type data: ``dict``

    :param public_ips: A list of additional IP addresses belonging to
                       this node. (optional)
    :type public_ips: ``list`` or ``None``
    """
    id = data['id']

    if 'name' in data:
        name = data['name']
    elif 'displayname' in data:
        name = data['displayname']
    else:
        name = None

    state = self.NODE_STATE_MAP[data['state']]

    public_ips = public_ips if public_ips else []
    private_ips = []

    for nic in data['nic']:
        if 'ipaddress' in nic:
            if is_private_subnet(nic['ipaddress']):
                private_ips.append(nic['ipaddress'])
            else:
                public_ips.append(nic['ipaddress'])

    security_groups = data.get('securitygroup', [])

    if security_groups:
        security_groups = [sg['name'] for sg in security_groups]

    affinity_groups = data.get('affinitygroup', [])

    if affinity_groups:
        affinity_groups = [ag['id'] for ag in affinity_groups]

    created = data.get('created', False)

    extra = self._get_extra_dict(data,
                                 RESOURCE_EXTRA_ATTRIBUTES_MAP['node'])

    # Add additional parameters to extra
    extra['security_group'] = security_groups
    extra['affinity_group'] = affinity_groups
    extra['ip_addresses'] = []
    extra['ip_forwarding_rules'] = []
    extra['port_forwarding_rules'] = []
    extra['created'] = created

    if 'tags' in data:
        extra['tags'] = self._get_resource_tags(data['tags'])

    node = CloudStackNode(id=id, name=name, state=state,
                          public_ips=public_ips, private_ips=private_ips,
                          driver=self, extra=extra)
    return node


def patch_libcloud():
    CloudStackNodeDriver.ex_authorize_security_group_ingress = ex_authorize_security_group_ingress
    CloudStackNodeDriver.list_nodes = list_nodes
    CloudStackNodeDriver.list_images = list_images
    CloudStackNodeDriver._to_node = _to_node

