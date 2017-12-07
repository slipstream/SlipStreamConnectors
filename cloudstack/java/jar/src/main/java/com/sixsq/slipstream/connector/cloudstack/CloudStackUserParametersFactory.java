package com.sixsq.slipstream.connector.cloudstack;

import com.sixsq.slipstream.connector.UserParametersFactoryBase;
import com.sixsq.slipstream.exceptions.ValidationException;
import com.sixsq.slipstream.persistence.ParameterType;

public class CloudStackUserParametersFactory extends UserParametersFactoryBase {

	public static final String ZONE_PARAMETER_NAME = "zone";

	public CloudStackUserParametersFactory(String connectorInstanceName)
			throws ValidationException {
		super(connectorInstanceName);
	}

	@Override
	protected void initReferenceParameters() throws ValidationException {
		initReferenceParameters(CloudStackConnector.CLOUD_SERVICE_NAME);
	}

}
