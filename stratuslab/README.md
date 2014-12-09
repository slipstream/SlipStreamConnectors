Installation
=======

To install the StratusLab connector, you first must add the StratusLab yum repository
to the yum configuration:

Create a file:
'''
/etc/yum.repos.d/stratuslab.repo
'''

With the following content:

'''
[StratusLab-Releases]
name=StratusLab-Releases
baseurl=http://yum.stratuslab.eu/releases/${os-ver}
gpgcheck=0
'''

Where ${os-ver} in our case is 'centos-6'.

Then install the SlipStream connector:
'''
$ yum install -y slipstream-connector-stratuslab
'''

That's it. Re-start SlipStream so that it detects the new connector.
