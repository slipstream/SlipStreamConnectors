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

from libcloud.compute.drivers.cloudstack import CloudStackNodeDriver
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

def patch_libcloud():
    CloudStackNodeDriver.ex_authorize_security_group_ingress = ex_authorize_security_group_ingress