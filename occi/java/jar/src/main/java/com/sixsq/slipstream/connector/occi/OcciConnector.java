package com.sixsq.slipstream.connector.occi;

/*
 * +=================================================================+
 * SlipStream OCCI Connector (jar)
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

import java.io.File;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.sixsq.slipstream.configuration.Configuration;
import com.sixsq.slipstream.connector.CliConnectorBase;
import com.sixsq.slipstream.connector.Connector;
import com.sixsq.slipstream.credentials.Credentials;
import com.sixsq.slipstream.exceptions.AbortException;
import com.sixsq.slipstream.exceptions.ConfigurationException;
import com.sixsq.slipstream.exceptions.InvalidElementException;
import com.sixsq.slipstream.exceptions.NotFoundException;
import com.sixsq.slipstream.exceptions.ValidationException;
import com.sixsq.slipstream.persistence.DeploymentModule;
import com.sixsq.slipstream.persistence.ImageModule;
import com.sixsq.slipstream.persistence.ModuleCategory;
import com.sixsq.slipstream.persistence.ModuleParameter;
import com.sixsq.slipstream.persistence.Node;
import com.sixsq.slipstream.persistence.Run;
import com.sixsq.slipstream.persistence.RunType;
import com.sixsq.slipstream.persistence.ServiceConfigurationParameter;
import com.sixsq.slipstream.persistence.User;
import com.sixsq.slipstream.persistence.UserParameter;

public class OcciConnector extends CliConnectorBase {
	protected static final List<String> EXTRADISK_NAMES = Arrays
			.asList(new String[] { "volatile", "persistent"}); // "readonly"
	public static final String CLOUD_SERVICE_NAME = "occi";
	public static final String CLOUDCONNECTOR_PYTHON_MODULENAME = "slipstream_occi.OcciClientCloud";

	private File privateProxyFile = null;

	public OcciConnector() {
		this(CLOUD_SERVICE_NAME);
	}

	public OcciConnector(String instanceName) {
		super(instanceName != null ? instanceName : CLOUD_SERVICE_NAME);
	}

	public String getCloudServiceName() {
		return CLOUD_SERVICE_NAME;
	}

	@Override
    protected String getCloudConnectorPythonModule() {
	    return CLOUDCONNECTOR_PYTHON_MODULENAME;
    }

	public Map<String, ServiceConfigurationParameter> getServiceConfigurationParametersTemplate()
			throws ValidationException {
		return new OcciSystemConfigurationParametersFactory(getConnectorInstanceName()).getParameters();
	}

	private String getResourceTemplate(Run run) throws ConfigurationException, ValidationException {
		if (isInOrchestrationContext(run)) {
			return Configuration.getInstance().getRequiredProperty(constructKey("orchestrator.resource.type"));
		} else {
			ImageModule image = ImageModule.load(run.getModuleResourceUrl());
			return getInstanceType(image);
		}
    }

	private File getPrivateProxy(User user) throws InvalidElementException,
			ValidationException {
		return ((OcciCredentials) getCredentials(user)).getVomsProxyFile();
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
	}

	private void validateImageModule(ImageModule image, User user) throws ValidationException {
		validateInstanceType(image, user);
	}

	private void validateInstanceType(ImageModule image, User user)
			throws ValidationException {
		String instanceType = getInstanceType(image);

		if ((image.isBase().booleanValue()) && ("inherited".equals(instanceType))) {
			throw new ValidationException(
					"Base image cannot have inherited instance type. Please review the instance type under Parameters -> "
							+ getConnectorInstanceName());
		}

		if ((instanceType == null) && (getRam(image) == null) && (getCpu(image) == null)) {
			throw new ValidationException(
					"Missing instance type or ram/cpu information. Please review the instance type under Parameters -> "
							+ getConnectorInstanceName() + " Or it's parents.");
		}
	}

	protected boolean isParameterDefined(User user, String sshParameterName) {
		return (user.getParameters().containsKey(sshParameterName))
				&& (!"".equals(((UserParameter) user
						.getParameter(sshParameterName)).getValue()))
				&& (((UserParameter) user.getParameter(sshParameterName))
						.getValue() != null);
	}

	protected String getOrchestratorImageId() throws ConfigurationException,
			ValidationException {
		return Configuration.getInstance().getRequiredProperty(
				constructKey("cloud.connector.orchestrator.imageid"));
	}

	public Credentials getCredentials(User user) {
		return new OcciCredentials(user, getConnectorInstanceName());
	}

	public Map<String, ModuleParameter> getImageParametersTemplate()
			throws ValidationException {
		return new OcciImageParametersFactory(getConnectorInstanceName())
				.getParameters();
	}

	public Map<String, UserParameter> getUserParametersTemplate()
			throws ValidationException {
		return new OcciUserParametersFactory(getConnectorInstanceName())
				.getParameters();
	}

	public String constructKey(String key) throws ValidationException {
		return new OcciUserParametersFactory(getConnectorInstanceName())
				.constructKey(new String[] { key });
	}

	protected void validateCredentials(User user) throws ValidationException {
		String errorMessageLastPart = getErrorMessageLastPart(user);
		String secret = getSecret(user);
		if (secret == null) {
			throw (new ValidationException("MyProxy passphrase cannot be empty" + errorMessageLastPart));
		}
	}

	public Connector copy() {
		return new OcciConnector(getConnectorInstanceName());
	}

    public void setExtraUserParameters(User user) throws ValidationException {
    	UserParameter userParam = getVomsProxyParameter(user);
    	user.setParameter(userParam);
    }

    private UserParameter getVomsProxyParameter(User user) throws ValidationException {
    	String proxyMaterial = "";
        try {
	        proxyMaterial = getVomsProxyMaterial(user);
        } catch (InvalidElementException e) {
	        throw new ValidationException("Failed getting VOMS proxy material with: " + e.getMessage());
        }
        UserParameter vomsProxy = new UserParameter(constructKey("proxy"), proxyMaterial, "");
        vomsProxy.setCategory(getConnectorInstanceName());
    	return vomsProxy;
    }

    private String getVomsProxyMaterial(User user) throws InvalidElementException, ValidationException {
    	return ((OcciCredentials) getCredentials(user)).getVomsProxyMaterial();
    }

    protected void connectorCleanupAfterCliCall() {
		if (privateProxyFile != null) {
			privateProxyFile.delete();
		}
    }

	@Override
    protected Map<String, String> getConnectorSpecificUserParams(User user) throws ConfigurationException,
            ValidationException {
		Map<String, String> userParams = new HashMap<String, String>();
		userParams.put("proxy-file", getPrivateProxyFilePath(user));
		userParams.put("endpoint", getEndpoint(user));
		return userParams;
    }

	private String getPrivateProxyFilePath(User user) throws ConfigurationException, ValidationException {
		try {
	        privateProxyFile = getPrivateProxy(user);
        } catch (InvalidElementException e) {
        	e.printStackTrace();
	        throw (new ConfigurationException("Failed to get private proxy file path: "+ e.getMessage()));
        }
		return privateProxyFile.getPath();
	}

	@Override
    protected Map<String, String> getConnectorSpecificLaunchParams(Run run, User user) throws ConfigurationException,
            ValidationException {
		Map<String, String> launchParams = new HashMap<String, String>();
		launchParams.put("instance-type", getResourceTemplate(run));
		putExtraDiskParameters(launchParams, run);
		putNetworkIdParameter(launchParams, run);
		return launchParams;
    }

	private void putExtraDiskParameters(Map<String, String> launchParams, Run run) {
		Map<String, String> extraDisksCommand = getExtraDisksParameters(run);
		launchParams.putAll(extraDisksCommand);
	}

	private void putNetworkIdParameter(Map<String, String> launchParams, Run run) throws ValidationException {
		String networkId = getNetworkId(run);
		if (networkId != null && !networkId.isEmpty()) {
			launchParams.put("network-id", networkId);
		}
	}

	private Map<String, String> getExtraDisksParameters(Run run) {
		Map<String, String> extraDisks = new HashMap<String, String>();

		if (run.getType() == RunType.Machine) {
			return extraDisks;
		}

		for (String diskName : EXTRADISK_NAMES) {
			String extraDiskName = Run.MACHINE_NAME_PREFIX
					+ ImageModule.EXTRADISK_PARAM_PREFIX + diskName;

			String extraDiskValue = "";
			try {
				extraDiskValue = run.getRuntimeParameterValue(extraDiskName);
			} catch (NotFoundException e) {
				continue;
			} catch (AbortException e) {
				continue;
			}

			if (!extraDiskValue.isEmpty()) {
				extraDisks.put(diskName + "-disk", extraDiskValue);
			}
		}
		return extraDisks;
	}

	private String getNetworkId(Run run) throws ValidationException {
		String netIdParamName = OcciImageParametersFactory.NETWORK_ID_PARAMETER_NAME;
		if (isInOrchestrationContext(run)) {
			return Configuration.getInstance().getProperty(constructKey(netIdParamName));
		} else {
			return getParameterValue(netIdParamName, ImageModule.load(run.getModuleResourceUrl()));
		}
	}
}
