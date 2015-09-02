package com.sixsq.slipstream.connector.occi;

import com.sixsq.slipstream.connector.SystemConfigurationParametersFactoryBase;
import com.sixsq.slipstream.exceptions.ValidationException;

public class OcciSystemConfigurationParametersFactory extends
		SystemConfigurationParametersFactoryBase {
	public OcciSystemConfigurationParametersFactory(String connectorInstanceName)
			throws ValidationException {
		super(connectorInstanceName);
	}

	protected void initReferenceParameters() throws ValidationException {
		super.initReferenceParameters();

		putMandatoryEndpoint();

		putMandatoryParameter(constructKey("orchestrator.resource.type"),
				"Orchestrator resource type");
		putMandatoryUpdateUrl();
		putMandatoryParameter(
				constructKey(OcciImageParametersFactory.NETWORK_ID_PARAMETER_NAME),
				OcciImageParametersFactory.NETWORK_ID_DESCRIPTION_PARAMETER_NAME);
	}
}
