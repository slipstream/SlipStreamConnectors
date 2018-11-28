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
import com.sixsq.slipstream.persistence.Run;
import com.sixsq.slipstream.persistence.ParameterType;

import java.util.ArrayList;
import java.util.List;

public class OpenNebulaImageParametersFactory extends ModuleParametersFactoryBase {

	public static final String CUSTOM_VM_TEMPLATE_NAME = "custom.vm.template";
	public static final String CUSTOM_VM_TEMPLATE_DESCRIPTION = "Additional custom textual VM template";
	public static final String CUSTOM_VM_TEMPLATE_EXAMPLE = "Example: " +
			"GRAPHICS = [ TYPE = VNC, LISTEN = 0.0.0.0, PORT = 5900 ]";
	public static final String CONTEXTUALIZATION_TYPE_NAME = "contextualization.type";
	public static final String CONTEXTUALIZATION_TYPE_DESCRIPTION = "Contextualization type";
	public static final String NETWORK_SPECIFIC_NAME = "network.specific.name";
	public static final String NETWORK_SPECIFIC_DESCRIPTION = "Network name";
	public static final String NETWORK_SPECIFIC_EXAMPLE = "Override network in Cloud configuration section! " +
			"Connect VM network interface on specified virtual network name. " +
			"Format: NETWORK_NAME or NETWORK_NAME;NETWORK_UNAME";

	public static String defaultCPU = "1";
	public static String defaultRAM = "0.5";

	public enum ContextualizationType {
		ONECONTEXT("one-context"),
		CLOUDINIT("cloud-init");

		private final String value;

		ContextualizationType(String value) {
			this.value = value;
		}

		public String getValue() {
			return value;
		}

		public static List<String> getValues() {
			List<String> types = new ArrayList<String>();

			for (ContextualizationType type : ContextualizationType.values()) {
				types.add(type.getValue());
			}
			return types;
		}

	}

	public OpenNebulaImageParametersFactory(String connectorInstanceName) throws ValidationException {
		super(connectorInstanceName);
	}

	@Override
	protected void initReferenceParameters() throws ValidationException {
		putMandatoryParameter(Run.CPU_PARAMETER_NAME, Run.CPU_PARAMETER_DESCRIPTION, defaultCPU, 10);
		putMandatoryParameter(Run.RAM_PARAMETER_NAME, Run.RAM_PARAMETER_DESCRIPTION, defaultRAM, 11);
		putMandatoryParameter(NETWORK_SPECIFIC_NAME, NETWORK_SPECIFIC_DESCRIPTION, "",
				NETWORK_SPECIFIC_EXAMPLE, 12);
		putEnumParameter(CONTEXTUALIZATION_TYPE_NAME, CONTEXTUALIZATION_TYPE_DESCRIPTION,
				ContextualizationType.getValues(), ContextualizationType.ONECONTEXT.getValue(), true, 100);
		putMandatoryParameter(CUSTOM_VM_TEMPLATE_NAME, CUSTOM_VM_TEMPLATE_DESCRIPTION, ParameterType.RestrictedText,
				CUSTOM_VM_TEMPLATE_EXAMPLE, 101);
	}
}
