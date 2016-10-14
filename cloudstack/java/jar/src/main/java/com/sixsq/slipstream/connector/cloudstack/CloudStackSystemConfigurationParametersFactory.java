package com.sixsq.slipstream.connector.cloudstack;

import com.sixsq.slipstream.connector.SystemConfigurationParametersFactoryBase;
import com.sixsq.slipstream.exceptions.ValidationException;

public class CloudStackSystemConfigurationParametersFactory extends SystemConfigurationParametersFactoryBase {
	
	public CloudStackSystemConfigurationParametersFactory(String connectorInstanceName) throws ValidationException {
		super(connectorInstanceName);
	}

	@Override
	protected void initReferenceParameters() throws ValidationException {
		initConnectorParameters(CloudStackConnector.CLOUD_SERVICE_NAME);
	}
	
}
