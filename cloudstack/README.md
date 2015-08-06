# CloudStack Connector Instance Configuration

To create and configure a CloudStack connector instance, you can [drop a file in your configuration]().

Here is an example, which will configure the CloudStack connector to interact with [Exoscale](http://exoscale.ch):

    $ cat exoscale-ch-gva.conf
    cloud.connector.class = exoscale-ch-gva:local
    exoscale-ch-gva.endpoint = https://api.exoscale.ch/compute
    exoscale-ch-gva.zone = CH-GV2
    exoscale-ch-gva.quota.vm = 20
    exoscale-ch-gva.orchestrator.imageid = 605d1ad4-b3b2-4b60-af99-843c7b8278f8
    exoscale-ch-gva.orchestrator.instance.type = Micro
    exoscale-ch-gva.orchestrator.ssh.password =
    exoscale-ch-gva.orchestrator.ssh.username =
    exoscale-ch-gva.native-contextualization = linux-only
    exoscale-ch-gva.max.iaas.workers = 20

