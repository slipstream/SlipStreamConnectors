Installation
=======

To install the StratusLab connector, you first must add the StratusLab yum repository
to the yum configuration:

Create a file:
```
/etc/yum.repos.d/stratuslab.repo
```

With the following content:

```
[StratusLab-Releases]
name=StratusLab-Releases
baseurl=http://yum.stratuslab.eu/releases/${os-ver}
gpgcheck=0
```

Where ${os-ver} in our case is 'centos-6'.

Then install the SlipStream connector:
```
# yum install -y slipstream-connector-stratuslab
```

To create and configure a StratusLab connector instance, you can [drop a file in your configuration](http://ssdocs.sixsq.com/documentation/developer_guide/configuration_files.html).

Here is an example, which will configure the StratusLab connector to interact with the [official StratusLab demo infrastructure](http://www.stratuslab.eu/try/):

    $ cat stratuslab.conf
    cloud.connector.class = stratuslab:stratuslab
    stratuslab.max.iaas.workers = 20
    stratuslab.update.clienturl = http://<slipstream-ip>/downloads/stratuslabclient.tgz
    stratuslab.messaging.endpoint = https://pdisk.lal.stratuslab.eu/pdisk
    stratuslab.pdisk.endpoint = https://pdisk.lal.stratuslab.eu/pdisk
    stratuslab.orchestrator.imageid = N-Bu1h1jt3K8ODnCTw4JiyPaH5k
    stratuslab.quota.vm = 10
    stratuslab.endpoint = https://cloud.lal.stratuslab.eu/one-proxy/xmlrpc
    stratuslab.marketplace.endpoint = https://marketplace.stratuslab.eu/marketplace
    stratuslab.orchestrator.instance.type = m1.small


That's it. Re-start SlipStream so that it detects the new connector and load the new configuration.

More informations can be found on the [SlipStream documentation](http://ssdocs.sixsq.com/documentation/administrator_guide/cloud_connectors.html#stratuslab-connector)
