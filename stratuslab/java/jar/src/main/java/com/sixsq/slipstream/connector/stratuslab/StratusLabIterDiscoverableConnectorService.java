package com.sixsq.slipstream.connector.stratuslab;

import com.sixsq.slipstream.connector.AbstractDiscoverableConnectorService;
import com.sixsq.slipstream.connector.Connector;

public class StratusLabIterDiscoverableConnectorService extends AbstractDiscoverableConnectorService {

    public StratusLabIterDiscoverableConnectorService() {
        super(StratusLabIterConnector.CLOUD_SERVICE_NAME);
    }

    public Connector getInstance(String instanceName) {
        return new StratusLabIterConnector(instanceName);
    }
}
