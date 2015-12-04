package com.sixsq.slipstream.connector.opennebula;

import com.sixsq.slipstream.connector.AbstractDiscoverableConnectorService;
import com.sixsq.slipstream.connector.Connector;

public class OpenNebulaDiscoverableConnectorService extends AbstractDiscoverableConnectorService {

    public OpenNebulaDiscoverableConnectorService() {
        super(OpenNebulaConnector.CLOUD_SERVICE_NAME);
    }

    public Connector getInstance(String instanceName) {
        return new OpenNebulaConnector(instanceName);
    }
}
