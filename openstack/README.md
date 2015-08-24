# OpenStack Connector Instance Configuration

Server-side client (`openstack-*` CLI) requires `apache-libcloud`.  It can be
installed with `pip`.  The version should be the same as defined in
`slipstream.sixsq.com:SlipStream:pom.xml` with `libcloud.version` property.

To create and configure a OpenStack connector instance, you can [drop a file in your configuration](http://ssdocs.sixsq.com/documentation/developer_guide/configuration_files.html).

Here is an example, which will configure the OpenStack connector to interact with [Ultimum Cloud](http://ulticloud.com):

    $ cat ultimum-cz1.conf
    cloud.connector.class = ultimum-cz1:openstack
    ultimum-cz1.quota.vm = 
    ultimum-cz1.max.iaas.workers = 20
    ultimum-cz1.service.name = nova
    ultimum-cz1.native-contextualization = linux-only
    ultimum-cz1.service.region = RegionOne
    ultimum-cz1.network.private = private
    ultimum-cz1.orchestrator.instance.type = Basic
    ultimum-cz1.service.type = compute
    ultimum-cz1.orchestrator.ssh.username =
    ultimum-cz1.orchestrator.imageid = 970da64c-c4be-4bb3-879b-75433751e71f
    ultimum-cz1.network.public = public
    ultimum-cz1.endpoint = https://console.ulticloud.com:5000/v2.0/tokens
    ultimum-cz1.orchestrator.ssh.password = 
