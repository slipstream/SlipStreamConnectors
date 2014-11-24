package com.sixsq.slipstream.connector.occi;

import com.sixsq.slipstream.connector.AbstractDiscoverableConnectorService;
import com.sixsq.slipstream.connector.Connector;
import slipstream.credcache.JavaWrapper;

public class OcciDiscoverableConnectorService extends AbstractDiscoverableConnectorService {
    public OcciDiscoverableConnectorService() {
        super(OcciConnector.CLOUD_SERVICE_NAME);
    }

    public Connector getInstance(String instanceName) {
        return new OcciConnector(instanceName);
    }

    @Override
    public void initialize() {
        JavaWrapper.start();
    }

    @Override
    public void shutdown() {
        JavaWrapper.stop();
    }
}
