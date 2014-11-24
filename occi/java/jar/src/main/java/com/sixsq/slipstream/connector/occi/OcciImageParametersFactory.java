package com.sixsq.slipstream.connector.occi;

import com.sixsq.slipstream.exceptions.ValidationException;
import com.sixsq.slipstream.factory.ModuleParametersFactoryBase;
import com.sixsq.slipstream.persistence.ImageModule;

public class OcciImageParametersFactory extends ModuleParametersFactoryBase {

	public static final String NETWORK_ID_PARAMETER_NAME = "network.id";
	public static final String NETWORK_ID_DESCRIPTION_PARAMETER_NAME = "Network ID";
	public static final String INSTANCE_TYPE_PARAMETER_NAME = ImageModule.INSTANCE_TYPE_KEY;
	public static final String INSTANCE_TYPE_DESCRIPTION_PARAMETER_NAME = "Instance type";

	public OcciImageParametersFactory(String connectorInstanceName)
			throws ValidationException {
		super(connectorInstanceName);
	}

	protected void initReferenceParameters() throws ValidationException {
		putMandatoryParameter(INSTANCE_TYPE_PARAMETER_NAME, INSTANCE_TYPE_DESCRIPTION_PARAMETER_NAME);
		putMandatoryParameter(NETWORK_ID_PARAMETER_NAME, NETWORK_ID_DESCRIPTION_PARAMETER_NAME);
	}
}
