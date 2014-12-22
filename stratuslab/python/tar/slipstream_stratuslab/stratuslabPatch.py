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
