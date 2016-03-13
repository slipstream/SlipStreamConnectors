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

	public static final String ORCHESTRATOR_CPU_SIZE_DEFAULT = "1";   //   1 vCPU
	public static final String ORCHESTRATOR_RAM_SIZE_DEFAULT = "0.5"; // 512 MB

	public OpenNebulaSystemConfigurationParametersFactory(String connectorInstanceName) throws ValidationException {
		super(connectorInstanceName);
	}

	@Override
	protected void initReferenceParameters() throws ValidationException {
		super.initReferenceParameters();
		super.putMandatoryEndpoint();

		putMandatoryParameter(constructKey(OpenNebulaUserParametersFactory.ORCHESTRATOR_CPU_PARAMETER_NAME),
				"Orchestrator CPU size",
				OpenNebulaSystemConfigurationParametersFactory.ORCHESTRATOR_CPU_SIZE_DEFAULT, "Number of vCPU", 16);

		putMandatoryParameter(constructKey(OpenNebulaUserParametersFactory.ORCHESTRATOR_RAM_PARAMETER_NAME),
				"Orchestrator RAM size",
				OpenNebulaSystemConfigurationParametersFactory.ORCHESTRATOR_RAM_SIZE_DEFAULT, "Ram size in GB", 17);

		putMandatoryParameter(constructKey(OpenNebulaUserParametersFactory.NETWORK_PUBLIC_NAME),
				"Mapping for Public network", "", "Numerical id", 30);

		putMandatoryParameter(constructKey(OpenNebulaUserParametersFactory.NETWORK_PRIVATE_NAME),
				"Mapping for Private network", "", "Numerical id", 31);

		putMandatoryUpdateUrl();

    }

}
