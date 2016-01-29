
from mock import Mock
import os
import unittest

from slipstream.UserInfo import UserInfo
from slipstream.exceptions import Exceptions
from slipstream.ConfigHolder import ConfigHolder
from slipstream_occi.OcciClientCloud import OcciClientCloud, NoPublicIpFound

JSON_NODES = \
'''[{"kind":"http://schemas.ogf.org/occi/infrastructure#compute","mixins":["http://opennebula.org/occi/infrastructure#compute","http://schemas.openstack.org/compute/instance#user_data"],"actions":["http://schemas.ogf.org/occi/infrastructure/compute/action#stop","http://schemas.ogf.org/occi/infrastructure/compute/action#restart","http://schemas.ogf.org/occi/infrastructure/compute/action#suspend"],"attributes":{"occi":{"core":{"id":"31139","title":"test-slipstream1"},"compute":{"cores":1,"memory":0.9765625,"speed":1.0,"state":"active"}},"org":{"opennebula":{"compute":{"id":"31139","cpu":1.0,"root":"hda1"}},"openstack":{"compute":{"user_data":"IyEvYmluL2Jhc2gKCmNkIC9yb290Lwpta2RpciAuc3NoCmVjaG8gJ3NzaC1yc2EgQUFBQUIzTnphQzF5YzJFQUFBQUJJd0FBQVFFQTFWdStRQ0VHVGNEWlRiNFFlTEhRN0FsYUVYVEp6MFpVWUx3SU1aU1lFMFpWcE53alRQZ000OTBMcklndzVRMlNvL0RNckdMalMxQ1RzS2phV3gvcHdReWxLcE9OQlhqeUpjMmZSUXFHakEvNlFiQkxpRG54N1FnbThtTnpSUFVnTkJLRmN4YVZDMEVZU3BkaHNlTkhaZS9Id0FEbW1DZFNnVGd5VU1xaGlCbmV5ZHFRRkRDa1E0dlBmdW5VSzB0YXg3TEpITUNRWkV2RGdWblZHQ3pzYzU1UWtaRnVMYlNkTE5mZXRWZWN3akNtaUQ5OUlTUG9WbEJnSks2S3IzNk1wTWgwcithYURRZFkxdnUwamVLamtSRC9iL0t1UnpGOVM2dnh0bEdObEduWkdjNnJ0SGtiTFRaZzNDWlY3SjJsZFFWazlrd09CbVNRblVJZ0xDeDB6UT09IHJvb3RAdzQzYXNkJyA+IC5zc2gvYXV0aG9yaXplZF9rZXlzCmNobW9kIG9nLXJ3eCAtUiAuc3NoCnVzZXJhZGQgLWcgd2hlZWwgc3BpbnRvCm1rZGlyIC1wIC9ob21lL3NwaW50by8uc3NoCmVjaG8gJ3NzaC1yc2EgQUFBQUIzTnphQzF5YzJFQUFBQUJJd0FBQVFFQTFWdStRQ0VHVGNEWlRiNFFlTEhRN0FsYUVYVEp6MFpVWUx3SU1aU1lFMFpWcE53alRQZ000OTBMcklndzVRMlNvL0RNckdMalMxQ1RzS2phV3gvcHdReWxLcE9OQlhqeUpjMmZSUXFHakEvNlFiQkxpRG54N1FnbThtTnpSUFVnTkJLRmN4YVZDMEVZU3BkaHNlTkhaZS9Id0FEbW1DZFNnVGd5VU1xaGlCbmV5ZHFRRkRDa1E0dlBmdW5VSzB0YXg3TEpITUNRWkV2RGdWblZHQ3pzYzU1UWtaRnVMYlNkTE5mZXRWZWN3akNtaUQ5OUlTUG9WbEJnSks2S3IzNk1wTWgwcithYURRZFkxdnUwamVLamtSRC9iL0t1UnpGOVM2dnh0bEdObEduWkdjNnJ0SGtiTFRaZzNDWlY3SjJsZFFWazlrd09CbVNRblVJZ0xDeDB6UT09IHJvb3RAdzQzYXNkJyA+IC5zc2gvYXV0aG9yaXplZF9rZXlzCmNob3duIHNwaW50bzp3aGVlbCAtUiAvaG9tZS9zcGludG8KY2htb2Qgb2ctcnd4IC1SIC9ob21lL3NwaW50by8uc3NoCg=="}}}},"id":"31139","links":[{"kind":"http://schemas.ogf.org/occi/infrastructure#storagelink","mixins":["http://opennebula.org/occi/infrastructure#storagelink"],"attributes":{"occi":{"core":{"id":"compute_31139_disk_0","title":"Fedcloud SL6-CESGA","target":"/storage/190","source":"/compute/31139"},"storagelink":{"deviceid":"/dev/vda","state":"active"}},"org":{"opennebula":{"storagelink":{"driver":"qcow2"}}}},"id":"compute_31139_disk_0","rel":"http://schemas.ogf.org/occi/infrastructure#storage","source":"/compute/31139","target":"/storage/190"},

 {"attributes": {"occi": {"core": {"id": "compute_31139_nic_1",
                                     "source": "/compute/31139",
                                     "target": "/network/10",
                                     "title": "red-EGI-193.144.35"},
                           "networkinterface": {"address": "192.168.0.7",
                                                 "interface": "eth0",
                                                 "mac": "02:00:c1:90:23:56",
                                                 "state": "active"}},
                 "org": {"opennebula": {"networkinterface": {"bridge": "virbrPUBLIC",
                                                                "model": "virtio"}}}},
 "id": "compute_31139_nic_1",
 "kind": "http://schemas.ogf.org/occi/infrastructure#networkinterface",
 "mixins": ["http://schemas.ogf.org/occi/infrastructure/networkinterface#ipnetworkinterface",
             "http://opennebula.org/occi/infrastructure#networkinterface"],
 "rel": "http://schemas.ogf.org/occi/infrastructure#network",
 "source": "/compute/31139",
 "target": "/network/10"},

 {"attributes": {"occi": {"core": {"id": "compute_31139_nic_0",
                                     "source": "/compute/31139",
                                     "target": "/network/10",
                                     "title": "red-EGI-193.144.35"},
                           "networkinterface": {"address": "193.144.35.84",
                                                 "interface": "eth0",
                                                 "mac": "02:00:c1:90:23:54",
                                                 "state": "active"}},
                 "org": {"opennebula": {"networkinterface": {"bridge": "virbrPUBLIC",
                                                                "model": "virtio"}}}},
 "id": "compute_31139_nic_0",
 "kind": "http://schemas.ogf.org/occi/infrastructure#networkinterface",
 "mixins": ["http://schemas.ogf.org/occi/infrastructure/networkinterface#ipnetworkinterface",
             "http://opennebula.org/occi/infrastructure#networkinterface"],
 "rel": "http://schemas.ogf.org/occi/infrastructure#network",
 "source": "/compute/31139",
 "target": "/network/10"}
]}]
'''


class TestOcciClientCloud(unittest.TestCase):

    def setUp(self):
        os.environ['SLIPSTREAM_CONNECTOR_INSTANCE'] = 'occi-test'

    def test_OcciClientCloudInit(self):
        assert OcciClientCloud(ConfigHolder(config={'foo': 'bar'},
                                            context={'foo': 'bar'}))

    def test_node_get_id_ip(self):
        cc = OcciClientCloud(ConfigHolder(config={'foo': 'bar'},
                                          context={'foo': 'bar'}))
        cc.driver = Mock()
        cc.driver.describe_compute = Mock(return_value=JSON_NODES)
        nodes = cc.list_instances()

        assert isinstance(nodes, list)
        assert '31139' == cc._vm_get_id(nodes[0])
        assert '193.144.35.84' == cc._vm_get_ip(nodes[0])
        assert 'active' == cc._vm_get_state(nodes[0])

    def test_node_get_public_ip_only(self):
        cc = OcciClientCloud(ConfigHolder(config={'foo': 'bar'},
                                          context={'foo': 'bar'}))
        cc.driver = Mock()
        cc.driver.describe_compute = Mock(return_value=JSON_NODES)
        nodes = cc.list_instances()

        assert isinstance(nodes, list)
        assert '193.144.35.84' == cc._vm_get_ip(nodes[0], public_ip_only=True)

        cc._is_public_ip = Mock(return_value=False)
        self.assertRaises(NoPublicIpFound, cc._vm_get_ip, nodes[0],
                          public_ip_only=True)

    def test_get_proxy_file(self):
        user_info = UserInfo('occi')
        cc = OcciClientCloud(ConfigHolder(config={'foo': 'bar'},
                                          context={'foo': 'bar'}))

        self.assertRaises(Exceptions.ExecutionException, cc._get_proxy_file, *(user_info,))

        user_info['occi.proxy'] = 'material'
        fn = cc._get_proxy_file(user_info)
        try:
            assert os.path.exists(fn)
            with open(fn) as fh:
                assert fh.read().startswith('material')
        finally:
            try: os.unlink(fn)
            except: pass

        user_info['occi.proxy_file'] = '/path/to/proxy'
        assert '/path/to/proxy' == cc._get_proxy_file(user_info)

