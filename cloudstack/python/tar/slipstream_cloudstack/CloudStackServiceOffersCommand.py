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
from slipstream.util import override


class CloudStackServiceOffersCommand(CloudStackCommand, ServiceOffersCommand):

    prefix = 'cloudstack'

    def __init__(self):
        super(CloudStackServiceOffersCommand, self).__init__()

    @override
    def _get_prefix(self):
        return self.prefix

    @override
    def _get_extra_attributes(self, vm_size):
        """
        Return the billing period
        :param vm_size: A vm_size object as returned by the method _get_vm_sizes() of the connector
        """
        zone = self.get_option(self.ZONE_KEY)
        return {
            "zone": zone
        }

