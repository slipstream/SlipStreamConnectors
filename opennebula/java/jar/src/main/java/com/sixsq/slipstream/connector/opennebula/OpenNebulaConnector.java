package com.sixsq.slipstream.connector.opennebula;

/*
 * +=================================================================+
 * SlipStream Server (WAR)
 * =====
 * Copyright (C) 2014 SixSq Sarl (sixsq.com)
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

import java.util.HashMap;
import java.util.Map;

import com.google.gson.JsonObject;
import com.sixsq.slipstream.configuration.Configuration;
import com.sixsq.slipstream.connector.CliConnectorBase;
import com.sixsq.slipstream.connector.Connector;
import com.sixsq.slipstream.credentials.Credentials;
import com.sixsq.slipstream.exceptions.ConfigurationException;
import com.sixsq.slipstream.exceptions.ValidationException;
import com.sixsq.slipstream.persistence.ImageModule;
import com.sixsq.slipstream.persistence.ModuleParameter;
import com.sixsq.slipstream.persistence.Run;
import com.sixsq.slipstream.persistence.ServiceConfigurationParameter;
import com.sixsq.slipstream.persistence.User;
import com.sixsq.slipstream.persistence.UserParameter;


public class OpenNebulaConnector extends CliConnectorBase {

	public static final String CLOUD_SERVICE_NAME = "opennebula";
	public static final String CLOUDCONNECTOR_PYTHON_MODULENAME = "slipstream_opennebula.OpenNebulaClientCloud";

	public OpenNebulaConnector() {
		this(CLOUD_SERVICE_NAME);
	}

	public OpenNebulaConnector(String instanceName){
		super(instanceName != null ? instanceName : CLOUD_SERVICE_NAME);
	}

	public Connector copy(){
		return new OpenNebulaConnector(getConnectorInstanceName());
	}

	public String getCloudServiceName() {
		return CLOUD_SERVICE_NAME;
	}

	@Override
	protected String getCloudConnectorPythonModule() {
		return CLOUDCONNECTOR_PYTHON_MODULENAME;
	}

	@Override
	protected Map<String, String> getConnectorSpecificUserParams(User user)
			throws ConfigurationException, ValidationException {
		Map<String, String> userParams = new HashMap<String, String>();
		userParams.put("endpoint", getEndpoint(user));
		return userParams;
	}

	@Override
	protected Map<String, String> getConnectorSpecificLaunchParams(Run run, User user)
			throws ConfigurationException, ValidationException {
		Map<String, String> launchParams = new HashMap<String, String>();
		launchParams.putAll(getInstanceSizeParams(run));
		launchParams.put("network-public", getNetworkPublic());
		launchParams.put("network-private", getNetworkPrivate());
		launchParams.put("custom-vm-template", getCustomVMTemplate(run));
		launchParams.put("network-specific-name", getNetworkSpecificName(run));
		launchParams.put("contextualization-type", getContextualizationType(run));
		launchParams.put("cpu-ratio", getCpuRatio(run));
		return launchParams;
	}

	private Map<String, String> getInstanceSizeParams(Run run) throws ValidationException {
		Map<String, String> instanceSize = new HashMap<String, String>();
		String cpu, ram;
		if (isInOrchestrationContext(run)) {
			cpu = getCpuSizeOrchestrator();
			ram = getRamSizeOrchestrator();
		} else {
			cpu = getCpu(run);
			ram = getRam(run);
		}
		instanceSize.put("cpu", cpu);
		instanceSize.put("ram", ram);
		return instanceSize;
	}

	private String getCustomVMTemplate(Run run) throws ValidationException {
		if (isInOrchestrationContext(run)) {
			return "";
		} else {
			String vm_additional_template = this.getParameterValue(
					OpenNebulaImageParametersFactory.CUSTOM_VM_TEMPLATE_NAME, run);
			if (vm_additional_template == null || vm_additional_template.isEmpty()) {
				return "";
			} else {
				return vm_additional_template;
			}
		}
	}

	private String getContextualizationType(Run run) throws ValidationException {
		String type;
		if (isInOrchestrationContext(run)) {
			type = Configuration
					.getInstance()
					.getRequiredProperty(
							constructKey(OpenNebulaUserParametersFactory.ORCHESTRATOR_CONTEXTUALIZATION_TYPE_NAME));
		} else {
			type = this.getParameterValue(OpenNebulaImageParametersFactory.CONTEXTUALIZATION_TYPE_NAME, run);
		}
		if (type == null || type.isEmpty()) {
			return OpenNebulaImageParametersFactory.ContextualizationType.ONECONTEXT.getValue();
		} else {
			return type;
		}
	}

	private String getNetworkSpecificName(Run run) throws ValidationException {
		if (isInOrchestrationContext(run)) {
			return "";
		} else {
			String network_specific_name = this.getParameterValue(
					OpenNebulaImageParametersFactory.NETWORK_SPECIFIC_NAME, run);
			if (network_specific_name == null || network_specific_name.isEmpty()) {
				return "";
			} else {
				return network_specific_name;
			}
		}
	}

	private String getCpuRatio(Run run) throws ValidationException {
		String cpu_ratio = Configuration
				.getInstance()
				.getRequiredProperty(
						constructKey(OpenNebulaUserParametersFactory.CPU_RATIO));
		if (cpu_ratio == null || cpu_ratio.isEmpty()) {
			return "0.5";
		} else {
			checkConvertsToFloat(cpu_ratio, "CPU Ratio");
			return cpu_ratio;
		}
	}

	protected String getCpuSizeOrchestrator() throws ValidationException {
		String cpu = Configuration
				.getInstance()
				.getRequiredProperty(
						constructKey(OpenNebulaUserParametersFactory.ORCHESTRATOR_CPU_PARAMETER_NAME));
		if (cpu == null || cpu.isEmpty()) {
			throw new ValidationException("Orchestrator CPU value should not be empty.");
		} else {
			checkConvertsToInt(cpu, "Orchestrator CPU");
			return cpu;
		}
	}

	protected String getRamSizeOrchestrator() throws ValidationException {
		String ram = Configuration
				.getInstance()
				.getRequiredProperty(
						constructKey(OpenNebulaUserParametersFactory.ORCHESTRATOR_RAM_PARAMETER_NAME));
		if (ram == null || ram.isEmpty()) {
			throw new ValidationException("Orchestrator RAM value should not be empty.");
		} else {
			checkConvertsToFloat(ram, "Orchestrator RAM");
			return ram;
		}
	}

	@Override
	protected String getCpu(Run run) throws ValidationException {
		String cpu = super.getCpu(run);
		if (cpu == null || cpu.isEmpty()) {
			return OpenNebulaImageParametersFactory.defaultCPU;
		} else {
			checkConvertsToInt(cpu, "CPU");
			return cpu;
		}
	}

	@Override
	protected String getRam(Run run) throws ValidationException {
		String ramGB = super.getRam(run);
		if (ramGB == null || ramGB.isEmpty()) {
			return OpenNebulaImageParametersFactory.defaultRAM;
		} else {
			checkConvertsToFloat(ramGB, "RAM");
			return ramGB;
		}
	}

	private void checkConvertsToInt(String value, String name) throws ValidationException {
		try {
			Integer.parseInt(value);
		} catch (NumberFormatException ex) {
			throw new ValidationException(name + " should be integer.");
		}

	}

	private void checkConvertsToFloat(String value, String name) throws ValidationException {
		try {
			Float.parseFloat(value);
		} catch (NumberFormatException ex) {
			throw new ValidationException(name + " should be float.");
		}

	}

	protected void validateCredentials(User user) throws ValidationException {
		super.validateCredentials(user);

		String endpoint = getEndpoint(user);
		if (endpoint == null || "".equals(endpoint)) {
			throw (new ValidationException("Cloud Endpoint cannot be empty. " +
					"Please contact your SlipStream administrator."));
		}
	}

	protected void validateLaunch(Run run, User user) throws ValidationException {

		String imageId = getImageId(run, user);
		if (imageId == null  || "".equals(imageId)){
			throw (new ValidationException("Image ID cannot be empty"));
		}

	}

	@Override
	public Map<String, ServiceConfigurationParameter> getServiceConfigurationParametersTemplate()
			throws ValidationException {
		return new OpenNebulaSystemConfigurationParametersFactory(getConnectorInstanceName())
				.getParameters();
	}

	@Override
	public Map<String, UserParameter> getUserParametersTemplate()
			throws ValidationException {
		return new OpenNebulaUserParametersFactory(getConnectorInstanceName()).getParameters();
	}

	@Override
	public Map<String, ModuleParameter> getImageParametersTemplate()
			throws ValidationException {
		return new OpenNebulaImageParametersFactory(getConnectorInstanceName()).getParameters();
	}

	@Override
	protected String constructKey(String key) throws ValidationException {
		return new OpenNebulaUserParametersFactory(getConnectorInstanceName()).constructKey(key);
	}

	@Override
	public Credentials getCredentials(User user) {
		return new OpenNebulaCredentials(user, getConnectorInstanceName());
	}

	protected String getNetworkPublic() throws ConfigurationException, ValidationException {
		return Configuration.getInstance().getRequiredProperty(
				constructKey(OpenNebulaUserParametersFactory.NETWORK_PUBLIC_NAME));
	}

	protected String getNetworkPrivate() throws ConfigurationException, ValidationException {
		return Configuration.getInstance().getRequiredProperty(
				constructKey(OpenNebulaUserParametersFactory.NETWORK_PRIVATE_NAME));
	}

	@Override
	public void applyServiceOffer(Run run, String nodeInstanceName, JsonObject serviceOffer)
			throws ValidationException
	{
		setRuntimeParameterValueFromServiceOffer(run, serviceOffer, nodeInstanceName,
				constructCloudParameterName(Run.CPU_PARAMETER_NAME),
				"resource:vcpu");

		String ram = getAttributeValueFromServiceOffer(serviceOffer,"resource:ram", nodeInstanceName);
		Float ramValue = Float.parseFloat(ram) / 1024;
		setRuntimeParameterValueWithCheck(run, constructCloudParameterName(Run.RAM_PARAMETER_NAME),
				nodeInstanceName, ramValue.toString());

		setRuntimeParameterValueFromServiceOffer(run, serviceOffer, nodeInstanceName,
				ImageModule.DISK_PARAM,
				"resource:disk");
	}

}
