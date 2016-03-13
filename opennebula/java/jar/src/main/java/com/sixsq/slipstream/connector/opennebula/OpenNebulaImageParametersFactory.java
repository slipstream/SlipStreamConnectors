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

import com.sixsq.slipstream.exceptions.ValidationException;
import com.sixsq.slipstream.factory.ModuleParametersFactoryBase;
import com.sixsq.slipstream.persistence.ImageModule;
import com.sixsq.slipstream.persistence.Run;

public class OpenNebulaImageParametersFactory extends ModuleParametersFactoryBase {

	public static final String CUSTOM_VM_TEMPLATE_NAME = "custom.vm.template";
	public static final String CUSTOM_VM_TEMPLATE_DESCRIPTION = "Additional custom VM template";

	public OpenNebulaImageParametersFactory(String connectorInstanceName) throws ValidationException {
		super(connectorInstanceName);
	}

	@Override
	protected void initReferenceParameters() throws ValidationException {
		putMandatoryParameter(Run.CPU_PARAMETER_NAME, Run.CPU_PARAMETER_DESCRIPTION, 10);
		putMandatoryParameter(Run.RAM_PARAMETER_NAME, Run.RAM_PARAMETER_DESCRIPTION, 11);
		putMandatoryParameter(CUSTOM_VM_TEMPLATE_NAME, CUSTOM_VM_TEMPLATE_DESCRIPTION, 100);
	}
}
