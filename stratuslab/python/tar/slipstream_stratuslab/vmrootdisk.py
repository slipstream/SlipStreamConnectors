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

#
# Extraction / population of root disk size.
#

from stratuslab.volume_manager.volume_manager_factory import VolumeManagerFactory
from stratuslab.image.Image import Image

import slipstream.exceptions.Exceptions as Exceptions
import slipstream.util as util


class UnknownRootDiskSizeSourceError(Exceptions.ExecutionException):
    pass


def populate_vms_with_disk_sizes(vms, config_holder):
    sources_and_vms = {}
    for vm in vms:
        try:
            vm.template_disk_0_size
        except AttributeError:
            sources_and_vms.setdefault(vm.template_disk_source, []).append(vm)

    if sources_and_vms:
        _set_root_disk_sizes_on_vms(sources_and_vms, config_holder)

    return vms


def get_root_disk_size_from_disk_source(disk_source, config_holder):
    if disk_source.startswith('http'):
        return _vm_get_root_disk_size_from_marketplace(disk_source, config_holder)
    elif disk_source.startswith('pdisk'):
        return _vm_get_root_disk_size_from_pdisk(disk_source, config_holder)
    else:
        raise UnknownRootDiskSizeSourceError('Unknown source to get root disk size: %s' % disk_source)


def _set_root_disk_sizes_on_vms(sources_and_vms, config_holder):
    sources_and_sizes = {}
    for source in sources_and_vms.keys():
        try:
            sources_and_sizes[source] = get_root_disk_size_from_disk_source(source, config_holder)
        except Exception as ex:
            util.printDetail('WARNING: Failed to get root disk size for image %s. Reason: %s' %
                             (source, str(ex)))

    for source, size in sources_and_sizes.iteritems():
        for vm in sources_and_vms[source]:
            vm.template_disk_0_size = size


def _vm_get_root_disk_size_from_marketplace(disk_source, config_holder):
    image = Image(config_holder)
    image_id = _disk_source_get_image_id(disk_source)
    size_bytes = image._getImageElementValue('bytes', image_id)
    # NB! PDisk "rounds" the required volume size before creation by adding 1GB.
    return 1 + int(size_bytes) / 1024 ** 3


def _vm_get_root_disk_size_from_pdisk(disk_source, config_holder):
    pdisk_endpoint = ':'.join(disk_source.split(':')[1:3])
    config_holder.set('pdiskUsername', config_holder.username)
    config_holder.set('pdiskPassword', config_holder.password)
    config_holder.set('pdiskEndpoint', pdisk_endpoint)
    pdisk = VolumeManagerFactory.create(config_holder)
    image_uuid = _disk_source_get_image_id(disk_source)
    volume = pdisk.describeVolumes({'uuid': ['^%s$' % image_uuid]})
    if len(volume) == 0:
        raise Exceptions.ExecutionException('Failed to describe volume in %s with UUID %s' %
                                            (pdisk_endpoint, image_uuid))
    return int(volume[0]['size'])


def _disk_source_get_image_id(disk_source):
    if disk_source.startswith('http'):
        split_on = '/'
    elif disk_source.startswith('pdisk'):
        split_on = ':'
    else:
        raise UnknownRootDiskSizeSourceError('Unknown source to get image ID: %s' % disk_source)
    return disk_source.split(split_on)[-1]
