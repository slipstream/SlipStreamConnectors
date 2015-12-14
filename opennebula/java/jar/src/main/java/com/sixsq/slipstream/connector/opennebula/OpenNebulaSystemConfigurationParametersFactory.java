package com.sixsq.slipstream.connector.opennebula;

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

public class OpenNebulaSystemConfigurationParametersFactory extends SystemConfigurationParametersFactoryBase {

	public OpenNebulaSystemConfigurationParametersFactory(String connectorInstanceName) throws ValidationException {
		super(connectorInstanceName);
	}

	@Override
	protected void initReferenceParameters() throws ValidationException {
		super.initReferenceParameters();
		super.putMandatoryEndpoint();

		putMandatoryParameter(constructKey(OpenNebulaUserParametersFactory.ORCHESTRATOR_INSTANCE_TYPE_PARAMETER_NAME),
				"OpenNebula instance type for the orchestrator.");


		putMandatoryParameter(constructKey(OpenNebulaUserParametersFactory.NETWORK_PUBLIC_NAME),
				"Mapping for Public network. Network ID:", "");

		putMandatoryParameter(constructKey(OpenNebulaUserParametersFactory.NETWORK_PRIVATE_NAME),
				"Mapping for Private network. Network ID", "");

		putMandatoryUpdateUrl();

    }

}
