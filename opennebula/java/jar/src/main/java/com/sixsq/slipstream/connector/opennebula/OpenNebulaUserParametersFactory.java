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

import com.sixsq.slipstream.connector.UserParametersFactoryBase;
import com.sixsq.slipstream.exceptions.ValidationException;

public class OpenNebulaUserParametersFactory extends UserParametersFactoryBase {

    public static final String NETWORK_PUBLIC_NAME = "network.public";
    public static final String NETWORK_PRIVATE_NAME = "network.private";
	public static final String ORCHESTRATOR_CPU_PARAMETER_NAME = "orchestrator.cpu.size";
	public static final String ORCHESTRATOR_RAM_PARAMETER_NAME = "orchestrator.ram.size";
	public static final String ORCHESTRATOR_CONTEXTUALIZATION_TYPE_NAME = "orchestrator.contextualization.type";

	public OpenNebulaUserParametersFactory(String connectorInstanceName)
			throws ValidationException {
		super(connectorInstanceName);
	}

	@Override
	protected void initReferenceParameters() throws ValidationException {
		putMandatoryParameter(KEY_PARAMETER_NAME, "Username", 10);
		putMandatoryPasswordParameter(SECRET_PARAMETER_NAME, "Password", 20);
	}

}
