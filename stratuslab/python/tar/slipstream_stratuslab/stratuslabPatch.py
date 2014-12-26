
# FEXME: Patching an issue in SL 14.06.
# https://github.com/StratusLab/client/issues/156
# Remove when fixed in SL code-base.
# Issue: Constructor of BaseSystem unconditionally creates stratuslab_*.{log,err}
# files in temporary directory.
# When Creator imports some constants from stratuslab.system.ubuntu and
# stratuslab.system.ubuntu, python's module loader interprets constructors of
# Ubuntu and CentOS classes defined in the module.  But because they explicitely
# call their parent's constructor BaseSystem.__init__(), the log files in a
# temporary directory get created.
#
from stratuslab.system.BaseSystem import BaseSystem
def BaseSystem__init__(obj):
    obj.packages = {}
BaseSystem.__init__ = BaseSystem__init__


from stratuslab.Creator import Creator

# pylint: disable=protected-access


def createStep1(self):
    self._imageExists()
    self._retrieveManifest()
    self._Creator__setAttributesFromManifest()
    self._Creator__createRunner()
    self._startMachine()
    self._waitMachineNetworkUpOrAbort()


def createStep2(self):
    self._checkIfCanConnectToMachine()
    self.buildNodeIncrement()
    self._shutdownNode()
    self._printAction('Finished building image increment.')
    self._printAction('Please check %s for new image ID and instruction.' % \
                      self.authorEmail)
    self._localCleanUp()


def patch_stratuslab():
    Creator.createStep1 = createStep1
    Creator.createStep2 = createStep2
