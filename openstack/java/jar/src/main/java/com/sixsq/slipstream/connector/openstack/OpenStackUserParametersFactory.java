package com.sixsq.slipstream.connector.openstack;

/*
 * +=================================================================+
 * SlipStream Server (WAR)
 * =====
 * Copyright (C) 2013 SixSq Sarl (sixsq.com)
 * =====
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * -=================================================================-
 */

import com.sixsq.slipstream.connector.UserParametersFactoryBase;
import com.sixsq.slipstream.exceptions.ValidationException;
import com.sixsq.slipstream.persistence.ParameterType;

public class OpenStackUserParametersFactory extends UserParametersFactoryBase {

	public static final String TENANT_NAME = "tenant.name";
	public static final String DOMAIN_NAME = "domain.name";
	public static final String KEY_DOMAIN_NAME = DOMAIN_NAME;
	public static final String KEY_TENANT_NAME = TENANT_NAME;
	public static final String SERVICE_TYPE_PARAMETER_NAME = "service.type";
	public static final String SERVICE_NAME_PARAMETER_NAME = "service.name";
	public static final String SERVICE_REGION_PARAMETER_NAME = "service.region";
	public static final String IDENTITY_VERSION_PARAMETER_NAME = "identity.version";
	public static final String NETWORK_PUBLIC_NAME = "network.public";
	public static final String NETWORK_PRIVATE_NAME = "network.private";
	public static final String USE_FLOATING_IPS_NAME = "floating.ips";
	public static final String REUSE_FLOATING_IPS_NAME = "reuse.floating.ips";

	public OpenStackUserParametersFactory(String connectorInstanceName)
			throws ValidationException {
		super(connectorInstanceName);
	}

	@Override
	protected void initReferenceParameters() throws ValidationException {
		initReferenceParameters(OpenStackConnector.CLOUD_SERVICE_NAME);
	}

}
