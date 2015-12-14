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
		launchParams.put("instance-type", getInstanceType(run));
		launchParams.put("network-public", getNetworkPublic());
		launchParams.put("network-private", getNetworkPrivate());
		return launchParams;
	}

	protected String getInstanceType(Run run)
			throws ConfigurationException, ValidationException {
		return (isInOrchestrationContext(run)) ? Configuration.getInstance()
				.getRequiredProperty(constructKey(OpenNebulaUserParametersFactory.ORCHESTRATOR_INSTANCE_TYPE_PARAMETER_NAME))
				: getInstanceType(ImageModule.load(run.getModuleResourceUrl()));
	}

	protected void validateCredentials(User user) throws ValidationException {
		super.validateCredentials(user);

		String endpoint = getEndpoint(user);
		if (endpoint == null || "".equals(endpoint)) {
			throw (new ValidationException("Cloud Endpoint cannot be empty. Please contact your SlipStream administrator."));
		}
	}

	protected void validateLaunch(Run run, User user) throws ValidationException {

		String instanceSize = getInstanceType(run);
		if (instanceSize == null || instanceSize.isEmpty() || "".equals(instanceSize) ){
			throw (new ValidationException("Instance type cannot be empty."));
		}

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
		return Configuration.getInstance().getRequiredProperty(constructKey(OpenNebulaUserParametersFactory.NETWORK_PUBLIC_NAME));
	}

	protected String getNetworkPrivate() throws ConfigurationException, ValidationException {
		return Configuration.getInstance().getRequiredProperty(constructKey(OpenNebulaUserParametersFactory.NETWORK_PRIVATE_NAME));
	}

}
