package com.sixsq.slipstream.connector.cloudstack;

import com.sixsq.slipstream.connector.SystemConfigurationParametersFactoryBase;
import com.sixsq.slipstream.exceptions.ValidationException;

public class CloudStackSystemConfigurationParametersFactory extends
		SystemConfigurationParametersFactoryBase {	
	
	public CloudStackSystemConfigurationParametersFactory(String connectorInstanceName)
			throws ValidationException {
		super(connectorInstanceName);
	}

	@Override
	protected void initReferenceParameters() throws ValidationException {

		super.initReferenceParameters();
		super.putMandatoryContextualizationType();
		super.putMandatoryOrchestratorUsernameAndPassword();

		putMandatoryEndpoint();

		putMandatoryParameter(constructKey(CloudStackUserParametersFactory.ORCHESTRATOR_INSTANCE_TYPE_PARAMETER_NAME),
				"Orchestrator instance type");
		
		putMandatoryParameter(constructKey(CloudStackUserParametersFactory.ZONE_PARAMETER_NAME), 
				"Zone");

		putMandatoryUpdateUrl();
	}
	
}
