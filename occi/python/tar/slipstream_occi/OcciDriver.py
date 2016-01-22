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

import os
import time

from slipstream import util
from slipstream.exceptions import Exceptions

# TODO: Set to True when OCCI endpoints start supporting this.
VOLATILE_DISK_DEF_BY_ATTRIBUTE = False
VOLATILE_DISK_NAME_PREFIX = 'volatile-'


class OcciDriver(object):

    COMPUTE_RESOURCE = 'compute'
    STORAGE_RESOURCE = 'storage'
    NETWORK_RESOURCE = 'network'
    SUPPORTED_RESOURCES = [COMPUTE_RESOURCE, STORAGE_RESOURCE, NETWORK_RESOURCE]

    occi_exe = os.path.join(os.sep, 'opt', 'occi-cli', 'bin', 'occi')

    def __init__(self, endpoint, proxy_file, occi_exe=None):
        self.endpoint = endpoint
        self.proxy_file = proxy_file
        if occi_exe:
            self.occi_exe = occi_exe
        if not os.path.exists(self.occi_exe):
            raise Exceptions.ExecutionException("OCCI CLI doesn't exist: %s" %
                                                self.occi_exe)

    def create_compute(self, context_file, ostpl, restpl, vmname,
                             extra_disk_ids):
        '''Return URL of the created compute instance. E.g.:
        https://cloud.cesga.es:3202/compute/33865
        '''
        attributes = {'occi.core.title': vmname}
        attributes_cmd = self._get_cmd_attributes(attributes)
        storage_links_cmd = self._get_cmd_storage_links(extra_disk_ids)
        return self._call_occi(['--action', 'create',
                                '--resource', 'compute',
                                '--context', 'user_data=file://%s' % context_file,
                                '--mixin=%s' % ostpl,
                                '--mixin=%s' % restpl]
                                + attributes_cmd
                                + storage_links_cmd)

    def create_volatile_storage(self, size):
        '''Return URL of the created disk. E.g.:
        https://carach5.ics.muni.cz:11443/storage/140
        '''
        # TODO: Use org.opennebula.storage.persistent="no"
        #       when supported by OCCI sites.
        attributes = VOLATILE_DISK_DEF_BY_ATTRIBUTE and \
            {'org.opennebula.storage.persistent': 'no'} or {}
        name = VOLATILE_DISK_NAME_PREFIX + str(int(time.time()))
        return self._create_storage(name, size, attributes)

    def _create_storage(self, name, size, extra_attrs={}):
        '''Return URL of the created disk. E.g.:
        https://carach5.ics.muni.cz:11443/storage/140
        '''
        attributes = {'occi.core.title': name,
                      'occi.storage.size': 'num(%s)' % size}
        attributes.update(zip(extra_attrs.keys(), extra_attrs.values()))
        attributes_cmd = self._get_cmd_attributes(attributes)
        return self._call_occi(['--action', 'create',
                                '--resource', 'storage']
                                + attributes_cmd)

    def attach_network(self, node_id, network_id):
        '''Attach network to compute resource by network ID.
        '''
        self._link(self.COMPUTE_RESOURCE, node_id, self.NETWORK_RESOURCE,
                   network_id)

    def describe_compute(self, vm_id=''):
        '''Return JSON rendering of nodes.
        '''
        return self._describe(self.COMPUTE_RESOURCE, vm_id)

    def describe_storage(self, volume_id=''):
        '''Return JSON rendering of volumes.
        '''
        return self._describe(self.STORAGE_RESOURCE, volume_id)

    def _describe(self, resource_name, _id=''):
        '''Return JSON rendering of either all the elements in the requested
        named resource or just one referenced by _id.
        '''
        if resource_name not in self.SUPPORTED_RESOURCES:
            raise Exceptions.ExecutionException('Wrong resource name for '
                                                'describing resource.')
        resource = self._build_resource_name(resource_name, _id)
        return self._call_occi(['--action', 'describe',
                                '--resource', resource])

    def unlink_disk_from_vm(self, vm_id, disk_id):
        '''Remove extra disk from VM.
        '''
        return self._unlink(self.COMPUTE_RESOURCE, vm_id,
                            self.STORAGE_RESOURCE, disk_id)

    def _link(self, resource_name, _id, link_resource_name, link_id):
        '''Link two resources.
        '''
        self._check_resource_name_valid(resource_name)
        self._check_resource_name_valid(link_resource_name)
        resource = self._build_resource_name(resource_name, _id)
        link = self._build_resource_name(link_resource_name, link_id)
        return self._call_occi(['--action', 'link',
                                '--resource', resource,
                                '--link', link])

    def _unlink(self, resource_name, _id, link_resource_name, link_id):
        '''Unlink two resources.
        '''
        self._check_resource_name_valid(resource_name)
        self._check_resource_name_valid(link_resource_name)
        resource = self._build_resource_name(resource_name, _id)
        link = self._build_resource_name(link_resource_name, link_id)
        return self._call_occi(['--action', 'unlink',
                                '--resource', resource,
                                '--link', link])

    def delete_storage(self, volume_id):
        return self._delete(self.STORAGE_RESOURCE, volume_id)

    def delete_compute(self, vm_id):
        return self._delete(self.COMPUTE_RESOURCE, vm_id)

    def _delete(self, resource_name, _id):
        self._check_resource_name_valid(resource_name)
        resource = self._build_resource_name(resource_name, _id)
        return self._call_occi(['--action', 'delete',
                                '--resource', resource])

    def _call_occi(self, options=[]):
        '''Return JSON rendering of nodes by calling
        occi -e <endpoint> -n x509 -X -x <proxy file> [options]
        '''
        cmd_base = [self.occi_exe,
                   '--endpoint', self.endpoint,
                   '--auth', 'x509',
                   '--voms',
                   '--skip-ca-check',
                   '--user-cred', self.proxy_file,
                   '--output-format', 'json_extended']

        cmd = cmd_base + self._update_resource_to_full_url(options, self.endpoint)

        rc, output = util.execute(cmd, withOutput=True)
        if rc != 0:
            raise Exceptions.ExecutionException('Failed running: %s\n%s' %
                                                (' '.join(cmd), output))
        return output

    @staticmethod
    def _update_resource_to_full_url(options, endpoint):
        if '--resource' in options:
            i = options.index('--resource')
            options[i + 1] = '/'.join([endpoint.rstrip('/'), options[i + 1].lstrip('/')])
        return options

    def _check_resource_name_valid(self, resource_name):
        if resource_name not in self.SUPPORTED_RESOURCES:
            raise Exceptions.ExecutionException('Wrong resource name '
                '%s. Supported %s' % (resource_name, self.SUPPORTED_RESOURCES))

    def _get_cmd_storage_links(self, extra_disk_ids):
        storage_links = []
        for disk_id in extra_disk_ids:
            storage_links.extend(['--link', '/storage/' + str(disk_id)])
        return storage_links

    def _get_cmd_attributes(self, attrs):
        return ['--attribute', self._serialise_attrs(attrs)]

    def _serialise_attrs(self, attrs):
        '''Return rOCCI CLI attributes serialised into string from the given
        dictionary.
        '''
        return ','.join(["%s=%s" % (k, v) for k, v in attrs.items()])

    def _build_resource_name(self, resource_name, _id=''):
        return (_id == '') and resource_name or '/%s/%s' % (resource_name, _id)
