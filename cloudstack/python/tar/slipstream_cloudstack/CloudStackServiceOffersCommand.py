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

from slipstream_cloudstack.CloudStackCommand import CloudStackCommand
from slipstream_cloudstack.CloudStackClientCloud import CloudStackClientCloud
from slipstream.command.CloudClientCommand import CloudClientCommand





import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from slipstream.command.CloudClientCommand import CloudClientCommand
from slipstream.NodeDecorator import KEY_RUN_CATEGORY
from slipstream.ConfigHolder import ConfigHolder
from slipstream.util import nostdouterr


import requests

class ServiceOffersInstancesCommand(CloudClientCommand):

    DEFAULT_TIMEOUT = 30
    prices = requests.get('https://portal.exoscale.ch/api/pricing/opencompute').json()
    rates = requests.get('https://portal.exoscale.ch/api/currency').json()

    def __init__(self):
        super(ServiceOffersInstancesCommand, self).__init__()

    def _get_default_timeout(self):
        return self.DEFAULT_TIMEOUT

    def _get_currency_exchange_rate(self, exchangeCode):
        for x in self.rates:
            if x['id'] == exchangeCode:
              return float(x['Rate'])
        return None

    def _get_price(self, instanceType):
        priceChf = float(self.prices['running_' + instanceType.lower().replace("-", "_")])
        priceEur = priceChf * self._get_currency_exchange_rate('CHFEUR')
        return priceEur 

    def do_work(self):
        ch = ConfigHolder(options={'verboseLevel': 0,
                                   'retry': False,
                                   KEY_RUN_CATEGORY: ''},
                                   context={'foo': 'bar'})
        cc = self.get_connector_class()(ch)
        cc._initialization(self.user_info, **self.get_initialization_extra_kwargs())

        for instanceType in cc.sizes:
            print "name:{} cpu:{:d} ram:{:d} disk:{:d}, price:{:f}".format(instanceType.name, instanceType.extra['cpu'], instanceType.ram, instanceType.disk, self._get_price(instanceType.name))

class CloudStackServiceOffers(ServiceOffersInstancesCommand, CloudStackCommand):

    def __init__(self):
        super(CloudStackServiceOffers, self).__init__()

