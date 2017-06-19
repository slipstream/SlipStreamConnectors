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

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from slipstream.command.ServiceOffersCommand import ServiceOffersCommand
from slipstream_cloudstack.CloudStackCommand import CloudStackCommand


class CloudStackServiceOffersCommand(CloudStackCommand, ServiceOffersCommand):

    def __init__(self):
        super(CloudStackServiceOffersCommand, self).__init__()


    def _get_extra_attributes(self, vm_size):
        """
        Return the billing period
        :param vm_size: A vm_size object as returned by the method _get_vm_sizes() of the connector
        """
        instance_type = self.cc._size_get_instance_type(vm_size)
        zone = self.get_option(self.ZONE_KEY)
        return {
            "cloudstack:instanceType": instance_type,
            "cloudstack:zone": zone
        }

