SlipStream Occi connector 
===========================

The repository contains SlipStream connector for OCCI.

The connector uses rOCCI CLI ([1][rocci], [2][roccicode], [3][roccicli]).

The above dependency should be available on both SlipStream server and the 
Orchestrator VM for the SlipStream connector to work.

The following dependencies should be installed in advance.

```
# EPEL release
echo "Installing EPEL release..."
rpm -ivH "http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm"

# Install dependencies
echo "Installing dependencies..."
yum install -y yum-priorities libxslt libxml2 libyaml dos2unix

# Install EGI UMD release
# IGNORE: MyProxy and VOMS in UMD are too far out of date and do not work!!!
#echo "Installing EGI UMD 3 release (check for other updates) ..."
#rpm -ivH http://repository.egi.eu/sw/production/umd/3/sl6/x86_64/updates/umd-release-3.0.1-1.el6.noarch.rpm

# Install FedCloud CA Certificates
echo "Installing FedCloud CA Certificates release..."
yum install -y lcg-CA &>/dev/null

# Install CRL renewal
yum install -y fetch-crl
# run it immediately (it can take some time...)
/usr/sbin/fetch-crl
# enable the periodic fetch-crl cron job
/sbin/chkconfig fetch-crl-cron on
/sbin/service fetch-crl-cron start

# Provider of rOCCI client -- occi-cli RPM.
wget -O /etc/yum.repos.d/rocci.repo http://repository.egi.eu/community/software/rocci.cli/4.2.x/releases/repofiles/sl-6-x86_64.repo
yum install -y occi-cli
```

Example of VO configuration for VO fedcloud.egi.eu

```
mkdir -p /etc/grid-security/vomsdir/fedcloud.egi.eu
cd /etc/grid-security/vomsdir/fedcloud.egi.eu

cat > voms1.egee.cesnet.cz.lsc <<EOF
/DC=org/DC=terena/DC=tcs/OU=Domain Control Validated/CN=voms1.egee.cesnet.cz
/C=NL/O=TERENA/CN=TERENA eScience SSL CA
EOF

cat > voms2.grid.cesnet.cz <<EOF
/DC=org/DC=terena/DC=tcs/OU=Domain Control Validated/CN=voms2.grid.cesnet.cz
/C=NL/O=TERENA/CN=TERENA eScience SSL CA
EOF

cat >> /etc/vomses <<EOF 
"fedcloud.egi.eu" "voms1.egee.cesnet.cz" "15002" "/DC=org/DC=terena/DC=tcs/OU=Domain Control Validated/CN=voms1.egee.cesnet.cz" "fedcloud.egi.eu" "24"
"fedcloud.egi.eu" "voms2.grid.cesnet.cz" "15002" "/DC=org/DC=terena/DC=tcs/OU=Domain Control Validated/CN=voms2.grid.cesnet.cz" "fedcloud.egi.eu" "24"
EOF
```

Install the packages:
```
yum install -y voms-client myproxy
```
to have access to the VOMS and MyProxy command line clients.  These
should come from the EPEL repository and not UMD.


[rocci]: http://occi-wg.org/2012/04/02/rocci-a-ruby-occi-framework/
[roccicode]: https://github.com/ffeldhaus/rOCCI
[roccicli]: http://repository.egi.eu/community/software/rocci.cli/
[fedcloud]: http://www.egi.eu/infrastructure/cloud/

