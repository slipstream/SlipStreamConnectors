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

import com.sixsq.slipstream.connector.SystemConfigurationParametersFactoryBase;
import com.sixsq.slipstream.exceptions.ValidationException;

import java.util.Arrays;

public class OpenStackSystemConfigurationParametersFactory extends SystemConfigurationParametersFactoryBase {

	public OpenStackSystemConfigurationParametersFactory(String connectorInstanceName) throws ValidationException {
		super(connectorInstanceName);
	}

	@Override
	protected void initReferenceParameters() throws ValidationException {
		super.initReferenceParameters();
		super.putMandatoryEndpoint();
		super.putMandatoryContextualizationType();
		super.putMandatoryOrchestratorUsernameAndPassword();

		putMandatoryParameter(constructKey(OpenStackUserParametersFactory.ORCHESTRATOR_INSTANCE_TYPE_PARAMETER_NAME),
				"OpenStack Flavor for the orchestrator. " +
				"The actual image should support the desired Flavor");

		putMandatoryParameter(constructKey(OpenStackUserParametersFactory.SERVICE_TYPE_PARAMETER_NAME),
				"Type-name of the service which provides the instances functionality",
				"compute");

		putMandatoryParameter(constructKey(OpenStackUserParametersFactory.SERVICE_NAME_PARAMETER_NAME),
				"Name of the service which provides the instances functionality",
				"nova");
				//"('nova' for OpenStack essex&folsom and 'Compute' for HP Cloud)"

        putMandatoryParameter(constructKey(OpenStackUserParametersFactory.SERVICE_REGION_PARAMETER_NAME),
                "Region used by this cloud connector", "RegionOne");

        putMandatoryParameter(constructKey(OpenStackUserParametersFactory.NETWORK_PUBLIC_NAME),
                "Mapping for Public network", "");

        putMandatoryParameter(constructKey(OpenStackUserParametersFactory.NETWORK_PRIVATE_NAME),
                "Mapping for Private network", "");


		putMandatoryEnumParameter(constructKey(OpenStackUserParametersFactory.IDENTITY_VERSION_PARAMETER_NAME),
				"Identity API version", Arrays.asList("v2", "v3"), "v2",
				"If the 'domain' feature is enable, you have to select 'v3'.", 10);

		putMandatoryOrchestratorSecurityGroups();

		putMandatoryUpdateUrl();

    }

}
