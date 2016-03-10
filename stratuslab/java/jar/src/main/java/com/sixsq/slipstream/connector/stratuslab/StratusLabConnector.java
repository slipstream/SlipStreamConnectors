package com.sixsq.slipstream.connector.stratuslab;

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

import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.sixsq.slipstream.configuration.Configuration;
import com.sixsq.slipstream.connector.CliConnectorBase;
import com.sixsq.slipstream.connector.Connector;
import com.sixsq.slipstream.credentials.Credentials;
import com.sixsq.slipstream.exceptions.ConfigurationException;
import com.sixsq.slipstream.exceptions.ValidationException;
import com.sixsq.slipstream.persistence.DeploymentModule;
import com.sixsq.slipstream.persistence.ImageModule;
import com.sixsq.slipstream.persistence.ModuleCategory;
import com.sixsq.slipstream.persistence.ModuleParameter;
import com.sixsq.slipstream.persistence.Node;
import com.sixsq.slipstream.persistence.Run;
import com.sixsq.slipstream.persistence.ServiceConfigurationParameter;
import com.sixsq.slipstream.persistence.User;
import com.sixsq.slipstream.persistence.UserParameter;

public class StratusLabConnector extends CliConnectorBase {

	protected static final List<String> EXTRADISK_NAMES = Arrays.asList(
			 "volatile", "persistent");
	public static final String CLOUD_SERVICE_NAME = "stratuslab";
	public static final String CLOUDCONNECTOR_PYTHON_MODULENAME = "slipstream_stratuslab.StratusLabClientCloud";

	public StratusLabConnector() {
		this(CLOUD_SERVICE_NAME);
	}

	public StratusLabConnector(String instanceName) {
		super(instanceName != null ? instanceName : CLOUD_SERVICE_NAME);
	}

	public Connector copy() {
		return new StratusLabConnector(getConnectorInstanceName());
	}

	@Override
	public String getCloudServiceName() {
		return CLOUD_SERVICE_NAME;
	}

	@Override
    protected String getCloudConnectorPythonModule() {
	    return CLOUDCONNECTOR_PYTHON_MODULENAME;
    }

	@Override
	protected Map<String, String> getConnectorSpecificUserParams(User user) throws ConfigurationException,
	        ValidationException {
		Map<String, String> userParams = new HashMap<String, String>();
		userParams.put("endpoint", getEndpoint(user));
		return userParams;
	}

	protected Map<String, String> getConnectorSpecificEnvironment(Run run, User user)
			throws ConfigurationException, ValidationException {
		HashMap<String, String> env = new HashMap<String, String>();
		env.put("SLIPSTREAM_PDISK_ENDPOINT", getPdiskEndpoint());
		return env;
	}

	@Override
	protected Map<String, String> getConnectorSpecificLaunchParams(Run run, User user) throws ConfigurationException,
	        ValidationException {
		Map<String, String> launchParams = new HashMap<String, String>();
		launchParams.putAll(getInstanceSizeParams(run));
		launchParams.put("markeptlace-endpoint", getMarketplaceEndpoint(user));
		launchParams.put("flavour", getCloudServiceName());
		return launchParams;
	}

	private Map<String, String> getInstanceSizeParams(Run run) throws ValidationException {
		Map<String, String> instanceSize = new HashMap<String, String>();
		if (isInOrchestrationContext(run)) {
			String instanceType = Configuration
					.getInstance()
					.getRequiredProperty(
							constructKey(StratusLabUserParametersFactory.ORCHESTRATOR_INSTANCE_TYPE_PARAMETER_NAME));
			instanceSize.put("instance-type", instanceType);
			return instanceSize;
		} else {
			ImageModule image = ImageModule.load(run.getModuleResourceUrl());
			String cpu = getCpu(image);
			String ram = getRam(image);
			if (cpu == null || cpu.isEmpty() || ram == null || ram.isEmpty()) {
				instanceSize.put("instance-type", getInstanceType(image));
				return instanceSize;
			} else {
				instanceSize.put("cpu", cpu);
				instanceSize.put("ram", ram);
				return instanceSize;
			}
		}
	}

	@Override
	protected String getCpu(ImageModule image) throws ValidationException {
		String cpu = super.getCpu(image);
		if (cpu == null || cpu.isEmpty()) {
			return "";
		} else {
			checkConvertsToInt(cpu, "CPU");
			return cpu;
		}
	}

	@Override
	protected String getRam(ImageModule image) throws ValidationException {
		String ramGb = super.getRam(image);
		if (ramGb == null || ramGb.isEmpty()) {
			return "";
		} else {
			checkConvertsToInt(ramGb, "RAM");
			return ramGb;
		}
	}

	private void checkConvertsToInt(String value, String name) throws ValidationException {
		try {
			Integer.parseInt(value);
		} catch (NumberFormatException ex) {
			throw new ValidationException(name + " should be integer.");
		}

	}

	private String getMarketplaceEndpoint(User user)
			throws ConfigurationException, ValidationException {
		return user
				.getParameter(
						constructKey(StratusLabUserParametersFactory.MARKETPLACE_ENDPOINT_PARAMETER_NAME))
				.getValue();
	}

	@Override
	protected void validateLaunch(Run run, User user) throws ValidationException {
		super.validateLaunch(run, user);

		if (run.getCategory() == ModuleCategory.Image) {
			ImageModule image = ImageModule.load(run.getModuleResourceUrl());
			validateImageModule(image, user);
		}
		if (run.getCategory() == ModuleCategory.Deployment) {
			for (Node node : DeploymentModule.load(run.getModuleResourceUrl()).getNodes().values()) {
				validateImageModule(node.getImage(), user);
			}
		}

		validateMarketplaceEndpoint(user);
		validatePDiskEndpoint();
	}

	private void validateMarketplaceEndpoint(User user) throws ValidationException {
		String endpoint = getMarketplaceEndpoint(user);
		if (endpoint == null || endpoint.isEmpty()) {
			throw (new ValidationException(
					"Marketplace endpoint should be set for "
							+ getConnectorInstanceName()));
		}
	}

	private void validatePDiskEndpoint() throws ValidationException {
	    String pdiskEndpoint =
	    		Configuration.getInstance().getRequiredProperty(
	    				constructKey(StratusLabUserParametersFactory.PDISK_ENDPOINT_PARAMETER_NAME));
	    if (pdiskEndpoint == null || pdiskEndpoint.isEmpty()){
	    	throw new ValidationException("Missing PDisk endpoint. Please contact your SlipStream administrator");
	    }
    }

	private void validateImageModule(ImageModule image, User user)
			throws ValidationException {
		validateParameters(image, user);
	}

	private void validateParameters(ImageModule image, User user)
			throws ValidationException {
		validateInstanceType(image, user);
	}

	private void validateInstanceType(ImageModule image, User user)
			throws ValidationException {

		String instanceType = getInstanceType(image);

		if (image.isBase() && ImageModule.INSTANCE_TYPE_INHERITED.equals(instanceType)) {
			throw (new ValidationException(
					"Base image cannot have inherited instance type. Please review the instance type under Parameters -> "
							+ getConnectorInstanceName()));
		}

		if (instanceType == null && (getRam(image) == null && getCpu(image) == null)) {
			throw new ValidationException(
					"Missing instance type or ram/cpu information. Please review the instance type under Parameters -> "
							+ getConnectorInstanceName() + " or it's parents.");
		}
	}

	private String getPdiskEndpoint() throws ConfigurationException, ValidationException {
		Configuration configuration = Configuration.getInstance();
		return configuration
				.getRequiredProperty(constructKey(
		        		StratusLabUserParametersFactory.PDISK_ENDPOINT_PARAMETER_NAME));
	}

	@Override
	public Credentials getCredentials(User user) {
		return new StratusLabCredentials(user, getConnectorInstanceName());
	}

	@Override
	public Map<String, ServiceConfigurationParameter> getServiceConfigurationParametersTemplate()
			throws ValidationException {
		return new StratusLabSystemConfigurationParametersFactory(
				getConnectorInstanceName()).getParameters();
	}

	@Override
	public Map<String, ModuleParameter> getImageParametersTemplate()
			throws ValidationException {
		return new StratusLabImageParametersFactory(getConnectorInstanceName())
				.getParameters();
	}

	@Override
	public Map<String, UserParameter> getUserParametersTemplate()
			throws ValidationException {
		return new StratusLabUserParametersFactory(getConnectorInstanceName())
				.getParameters();
	}

	@Override
	public String constructKey(String key) throws ValidationException {
		return new StratusLabUserParametersFactory(getConnectorInstanceName())
				.constructKey(key);
	}
}
