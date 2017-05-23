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

#TODO add depency to the package
from slipstream.api import Api

class ServiceOffersInstancesCommand(CloudClientCommand):

    DEFAULT_TIMEOUT = 600
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

    def _get_price(self, instanceType, os, diskSizeGiB):
        instanceName = 'running_' + instanceType.lower().replace("-", "_")
        if os == "windows":
          priceChf = float(self.prices.get(instanceName + '_win', -1))
        else:
          priceChf = float(self.prices.get(instanceName))
        if (priceChf >= 0):
            priceEur = (priceChf + diskSizeGiB * float(self.prices.get('volume'))) * self._get_currency_exchange_rate('CHFEUR')
            return priceEur
        else:
            return None

    def get_disk_sizes(self, instanceType):
        defaultDiskSizes = [10, 50, 100, 200, 400]
        diskSizes = {"Micro": [10, 50, 100, 200],
                     "Tiny": defaultDiskSizes,
                     "Small": defaultDiskSizes, 
                     "Medium": defaultDiskSizes,
                     "Large": defaultDiskSizes,
                     "Extra-large": defaultDiskSizes,
                     "Huge": defaultDiskSizes,
                     "Mega": [10, 50, 100, 200, 400, 800],
                     "Titan": [10, 50, 100, 200, 400, 800, 1600],
                     "GPU-small": [100, 200, 400, 800, 1600, 2000], 
                     "GPU-huge": [100, 200, 400, 800, 1600, 2000, 8000]}
        return diskSizes.get(instanceType, defaultDiskSizes)   
    
    def generateServiceOffer(self, connectorName, instanceTypeName, cpuSize, ramSizeMiB, diskSizeGiB, os, price):
        country = 'CH'
        resourceType = 'VM'
        resourceClass = 'standard'
        zone = self.get_option(self.ZONE_KEY)
        return {"name": "{:d}/{:d}/{:d} {} [{}] ({})".format(cpuSize,ramSizeMiB, diskSizeGiB, os, country, instanceTypeName),
                "description": "{} ({}) with {:d} vCPU, {:d} MiB RAM, {:d} GiB disk, {} [{}, {}] ({})"
                                   .format(resourceType, resourceClass, cpuSize, ramSizeMiB, diskSizeGiB, os, zone, country, instanceTypeName),
                "resource:vcpu": cpuSize,
                "resource:ram": ramSizeMiB,
                "resource:disk": diskSizeGiB,
                "resource:diskType": "SSD",
                "resource:type": resourceType,
                "resource:class": resourceClass,
                "resource:country": country,
                "resource:platform": "cloudstack",
                "resource:operatingSystem": os,
                "price:unitCost": price,
                "price:unitCode": "C62",
                "price:freeUnits": 0,
                "price:currency": "EUR",
                "price:billingUnitCode": "HUR",
                "price:billingPeriodCode": "MIN",
                "schema-org:name": instanceTypeName,
                "exoscale:instanceType": instanceTypeName,
                "exoscale:zone": zone,
                "connector": {"href": connectorName},
		"acl" : {
			"owner" : {
				"type" : "ROLE",
				"principal" : "ADMIN"
			},
			"rules" : [ {
				"principal" : "USER",
				"right" : "VIEW",
				"type" : "ROLE"
			}, {
				"principal" : "ADMIN",
				"right" : "ALL",
				"type" : "ROLE"
			} ]
		},
	}

    def do_work(self):
        ch = ConfigHolder(options={'verboseLevel': 0,
                                   'retry': False,
                                   KEY_RUN_CATEGORY: ''},
                                   context={'foo': 'bar'})
        cc = self.get_connector_class()(ch)
        cc._initialization(self.user_info, **self.get_initialization_extra_kwargs())
        
        dryrun = self.get_option(self.DRY_RUN_KEY)
        ss_endpoint = self.get_option(self.SS_ENDPOINT_KEY)
        connectorName = self.get_option(self.CONNECTOR_NAME_KEY)
        ssapi = Api(endpoint=ss_endpoint, cookie_file=None, insecure=True)
        if (not dryrun):
            ssapi.login(self.get_option(self.SS_USERNAME_KEY), self.get_option(self.SS_PASSWORD_KEY))

        for instanceType in cc.sizes:
            instanceTypeName = instanceType.name
            for diskSizeGiB in self.get_disk_sizes(instanceTypeName):
                for os in ["linux", "windows"]:
                    price = self._get_price(instanceType.name, os, diskSizeGiB)
                    if (price is None or (os == "windows" and diskSizeGiB < 50)):
                        continue
                    cpuSize = int(instanceType.extra['cpu'])
                    ramSizeMiB = int(instanceType.ram)
                    serviceOffer = self.generateServiceOffer(connectorName, instanceTypeName, cpuSize, ramSizeMiB, diskSizeGiB, os, price)
                    
                    cimiFilter = 'connector/href="{}" and description="{}"'.format(connectorName, serviceOffer['description'])
                    searchResult = ssapi.cimi_search('serviceOffers', filter=cimiFilter)
                    resultCount = len(searchResult.resources_list)
                    
                    if resultCount == 0:
                        print('\nAddinging following service offer {} to {}...\n{}'.format(serviceOffer['name'], ss_endpoint, serviceOffer))
                        if (not dryrun):
                            ssapi.cimi_add('serviceOffers', serviceOffer)
                    elif resultCount == 1:
                        print('\nUpdating following service offer {} to {}...\n{}'.format(serviceOffer['name'], ss_endpoint, serviceOffer))
                        if (not dryrun):
                            ssapi.cimi_edit(searchResult.resources_list[0].id, serviceOffer)
                    else:
                        print('\n!!! Warning duplicates find of following service offer on {} !!!/n{}'.format(ss_endpoint, serviceOffer['name']))
        print('\n\nCongratulation, executon completed.')
 
class CloudStackServiceOffers(ServiceOffersInstancesCommand, CloudStackCommand):

    CONNECTOR_NAME_KEY = 'connector-name'
    SS_ENDPOINT_KEY = 'ss-url'
    SS_USERNAME_KEY = 'ss-user'
    SS_PASSWORD_KEY = 'ss-pass'
    DRY_RUN_KEY = 'dry-run'

    def __init__(self):
        super(CloudStackServiceOffers, self).__init__()

    def set_cloud_specific_options(self, parser):
        CloudStackCommand.set_cloud_specific_options(self, parser)

        self.parser.add_option('--' + self.CONNECTOR_NAME_KEY, dest=self.CONNECTOR_NAME_KEY,
                               help='Connector name to be used as a connector href for service offers',
                               default=None, metavar='CONNECTOR_NAME')

        self.parser.add_option('--' + self.SS_ENDPOINT_KEY, dest=self.SS_ENDPOINT_KEY,
                               help='SlipStream endpoint used where the service offers are pushed to. (default: https://nuv.la)',
                               default='https://nuv.la', metavar='URL')

        self.parser.add_option('--' + self.SS_USERNAME_KEY, dest=self.SS_USERNAME_KEY,
                               help='Username to be used on SlipStream Endpoint',
                               default=None, metavar='USERNAME')

        self.parser.add_option('--' + self.SS_PASSWORD_KEY, dest=self.SS_PASSWORD_KEY,
                               help='Password to be used on SlipStream Endpoint',
                               default=None, metavar='PASSWORD')

        self.parser.add_option('--' + self.DRY_RUN_KEY, dest=self.DRY_RUN_KEY,
                               help='Just print service offers to stdout and exit',
                               action='store_true')

    def get_cloud_specific_mandatory_options(self):
        return CloudStackCommand.get_cloud_specific_mandatory_options(self) + \
               [self.CONNECTOR_NAME_KEY]
