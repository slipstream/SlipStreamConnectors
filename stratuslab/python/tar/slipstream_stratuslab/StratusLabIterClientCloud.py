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

import base64
import os
import time

from stratuslab.vm_manager.Runner import Runner
from stratuslab.volume_manager.PersistentDisk import PersistentDisk

import slipstream.exceptions.Exceptions as Exceptions

from slipstream.util import override, importETree
from slipstream_stratuslab.StratusLabClientCloud import StratusLabClientCloud

import traceback
etree = importETree()


def getConnector(configHolder):
    return getConnectorClass()(configHolder)


def getConnectorClass():
    return StratusLabIterClientCloud


class StratusLabIterClientCloud(StratusLabClientCloud):
    """Implements extra disk functionality of SlipStream over the persistent disk
    of StratusLab.
    """

    cloudName = 'stratuslabiter'

    VOLATILE_DISK_PREFIX = 'volatile-'

    def __init__(self, slipstreamConfigHolder):
        super(StratusLabIterClientCloud, self).__init__(slipstreamConfigHolder)

        PersistentDisk._setPDiskUserCredentials = lambda x: x

    @staticmethod
    def _get_create_image_messaging_message(image_resource_uri):
        return base64.b64encode('{"uri":"%s", "imageid":""}' % image_resource_uri)

    def _start_image_for_deployment(self, node_instance, vm_name):
        self.slConfigHolder.set('pdiskEndpoint',
                                os.environ.get(['SLIPSTREAM_PDISK_ENDPOINT']))

        configHolder = self.slConfigHolder.deepcopy()

        image_id = node_instance.get_image_id()

        self._set_extra_context_data_on_config_holder(configHolder, node_instance)
        self._set_vm_name_on_config_holder(configHolder, vm_name)

        # Create an extra volatile disk as persistent one.
        # The size should be in GB.
        disk_uuid = ''
        disk_size = int(node_instance.get_volatile_extra_disk_size() or 0)
        if disk_size > 0:
            disk_uuid = self._volume_create(disk_size, '%s%s' % (self.VOLATILE_DISK_PREFIX, vm_name))
            node_instance.set_cloud_parameters({'extra_disk_persistent': disk_uuid})

        try:
            self._set_instance_params_on_config_holder(configHolder, node_instance)
            runner = self._run_instance(image_id, configHolder)
        except:
            if disk_uuid:
                self._volume_delete(disk_uuid)
            raise
        return runner

    def _volume_create(self, size, tag):
        pdisk = PersistentDisk(self.slConfigHolder)
        public = False
        return pdisk.createVolume(str(size), tag, public)

    def _volume_delete(self, uuid):
        pdisk = PersistentDisk(self.slConfigHolder)
        wait_time = 30
        time_stop = time.time() + wait_time
        while 0 != int(pdisk.getValue('count', uuid)):
            if time.time() <= time_stop:
                self._print_detail('Disk %s is still in use after waiting for %s sec.' %
                                   (uuid, wait_time))
            time.sleep(3)
        return pdisk.deleteVolume(uuid)

    def _volume_exists(self, uuid):
        pd = PersistentDisk(self.slConfigHolder)
        return pd.volumeExists(uuid)

    def _set_extra_disks_on_config_holder(self, configHolder, node_instance):
        configHolder.persistentDiskUUID = node_instance.get_cloud_parameter('extra_disk_persistent', '')
        configHolder.readonlyDiskId = node_instance.get_cloud_parameter('extra_disk_readonly', '')

    @override
    def _stop_deployment(self):
        errors = []
        for nodename, runner in self.get_vms().items():
            vm_id = runner.vmIds[0]
            try:
                vm_info = runner.cloud._vmInfo(vm_id)
                runner.killInstances()
                self._wait_vm_in_state(['Done', 'Failed'], runner, vm_id)
                time.sleep(2)
                self._delete_volatile_disks(vm_info)
            except Exception as ex:
                traceback.print_exc()
                try:
                    time.sleep(2)
                    runner.killInstances()
                    self._delete_volatile_disks(vm_info)
                except Exception as ex:
                    traceback.print_exc()
                    errors.append('Error killing node %s\n%s' % (nodename, str(ex)))
        if errors:
            raise Exceptions.CloudError('Failed stopping following instances. '
                                        'Details: %s' % '\n   -> '.join(errors))

    @staticmethod
    def _wait_vm_in_state(states, runner, vm_id, counts=3, sleep=2, throw=False):
        counter = 1
        while counter <= counts:
            state = runner.getVmState(vm_id)
            if state in states:
                return state
            time.sleep(sleep)
            counter += 1
        if throw:
            raise Exception('Timed out while waiting for states: %s' % states)

    def _delete_volatile_disks(self, vm_info):
        uuids = self._get_volatile_disk_ids_to_delete(vm_info)
        for uuid in uuids:
            self._print_detail('Deleting volatile disk: %s' % uuid)
            self._volume_delete(uuid)

    def _get_volatile_disk_ids_to_delete(self, vm_info):
        xml = etree.fromstring(vm_info)
        sources = [x.find('SOURCE').text for x in xml.findall('TEMPLATE/DISK')
                   if x.find('SOURCE') != None]
        pdisk = PersistentDisk(self.slConfigHolder)
        uuids = []
        for source in sources:
            if source.startswith('pdisk'):
                uuid = source.split(':')[-1]
                tag = pdisk.getValue('tag', uuid)
                if tag.startswith(self.VOLATILE_DISK_PREFIX):
                    uuids.append(uuid)
        return uuids

    @override
    def _stop_vms_by_ids(self, ids):
        """Stops VMs by IDs.
        ids: list of VM IDs to stop.
        """
        if not ids:
            return
        configHolder = self.slConfigHolder.copy()
        runner = Runner(None, configHolder)
        vm_infos = []
        for vm_id in ids:
            vm_info = runner.cloud._vmInfo(int(vm_id))
            vm_infos.append(vm_info)
        runner.killInstances(map(int, ids))
        for vm_id in ids:
            self._wait_vm_in_state(['Done', 'Failed'], runner, int(vm_id))
            time.sleep(2)
        for vm_info in vm_infos:
            self._delete_volatile_disks(vm_info)
