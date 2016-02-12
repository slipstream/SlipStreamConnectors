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

from libcloud.compute.drivers.cloudstack import CloudStackNodeDriver, CloudStackAddress, \
    CloudStackIPForwardingRule, CloudStackPortForwardingRule
from libcloud.compute.types import LibcloudError


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

        addresses = public_ips_map.get(vm['id'], {}).items()
        addresses = [CloudStackAddress(node, v, k) for k, v in addresses]
        node.extra['ip_addresses'] = addresses

        rules = []
        for addr in addresses:
            result = self._sync_request('listIpForwardingRules')
            for r in result.get('ipforwardingrule', []):
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
        public_ips = self.ex_list_public_ips()
        result = self._sync_request('listPortForwardingRules')
        for r in result.get('portforwardingrule', []):
            if str(r['virtualmachineid']) == node.id:
                addr = [a for a in public_ips if
                        a.address == r['ipaddress']]
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


def patch_libcloud():
    CloudStackNodeDriver.ex_authorize_security_group_ingress = ex_authorize_security_group_ingress
    CloudStackNodeDriver.list_nodes = list_nodes