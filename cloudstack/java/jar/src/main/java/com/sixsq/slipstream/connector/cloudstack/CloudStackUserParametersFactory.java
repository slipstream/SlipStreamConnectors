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
		putMandatoryParameter(KEY_PARAMETER_NAME, "API Key", ParameterType.RestrictedString,
				"On the default CloudStack web interface you can find this information on <code>Accounts > [your account name] > View Users > [your user name] > API Key</code>", 10);
		putMandatoryPasswordParameter(SECRET_PARAMETER_NAME, "Secret Key",
				"On the default CloudStack web interface you can find this information on <code>Accounts > [your account name] > View Users > [your user name] > Secret Key</code>", 20);
	}

}
