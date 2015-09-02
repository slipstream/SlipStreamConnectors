package com.sixsq.slipstream.connector.cloudstack;

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
import com.sixsq.slipstream.persistence.ModuleCategory;
import com.sixsq.slipstream.persistence.ModuleParameter;
import com.sixsq.slipstream.persistence.Run;
import com.sixsq.slipstream.persistence.ServiceConfigurationParameter;
import com.sixsq.slipstream.persistence.User;
import com.sixsq.slipstream.persistence.UserParameter;


public class CloudStackConnector extends CliConnectorBase {

	public static final String ZONE_TYPE = "Basic";
	public static final String CLOUD_SERVICE_NAME = "cloudstack";
	public static final String CLOUDCONNECTOR_PYTHON_MODULENAME = "slipstream_cloudstack.CloudStackClientCloud";

	public CloudStackConnector() {
		this(CLOUD_SERVICE_NAME);
	}

    public CloudStackConnector(String instanceName) {
		super(instanceName != null ? instanceName : CLOUD_SERVICE_NAME);
	}

    public Connector copy(){
    	return new CloudStackConnector(getConnectorInstanceName());
    }

    protected String getZoneType(){
		return ZONE_TYPE;
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
		userParams.put("zone", getZone(user));
		return userParams;
	}

	@Override
	protected Map<String, String> getConnectorSpecificLaunchParams(Run run, User user)
			throws ConfigurationException, ValidationException {
		Map<String, String> launchParams = new HashMap<String, String>();
		launchParams.put("instance-type", getInstanceType(run, user));
		String securityGroups = getSecurityGroups(run);
		if (securityGroups != null && !securityGroups.isEmpty()) {
			launchParams.put("security-groups", securityGroups);
		}
		launchParams.put("zone-type", getZoneType());
		launchParams.put("networks", getNetworks(run, user));
		return launchParams;
	}

	protected String getNetworks(Run run, User user) throws ValidationException{
		return "";
	}

	protected String getSecurityGroups(Run run) throws ValidationException{
		return (isInOrchestrationContext(run)) ? ""
				: getParameterValue(CloudStackImageParametersFactory.SECURITY_GROUPS,
						ImageModule.load(run.getModuleResourceUrl()));
	}

	protected String getInstanceType(Run run, User user) throws ValidationException {
		return (isInOrchestrationContext(run)) ? user.getParameter(
				constructKey(CloudStackUserParametersFactory.ORCHESTRATOR_INSTANCE_TYPE_PARAMETER_NAME)).getValue()
				: getInstanceType(ImageModule.load(run.getModuleResourceUrl()));
	}

	protected String getZone(User user) throws ValidationException {
		return user.getParameter(constructKey(
				CloudStackUserParametersFactory.ZONE_PARAMETER_NAME))
				.getValue();
	}

	protected void validateDescribe(User user) throws ValidationException {
		validateCredentials(user);
		validateBaseParameters(user);
	}

	protected void validateTerminate(Run run, User user) throws ValidationException {
		validateCredentials(user);
		validateBaseParameters(user);
	}

	protected void validateBaseParameters(User user) throws ValidationException {
		String errorMessageLastPart = ". Please contact your SlipStream administrator.";

		String endpoint = getEndpoint(user);
		if (endpoint == null || "".equals(endpoint)) {
			throw (new ValidationException("Cloud Endpoint cannot be empty. "+ errorMessageLastPart));
		}
		String zone = getZone(user);
		if (zone == null || "".equals(zone)) {
			throw (new ValidationException("Cloud Zone cannot be empty. "+ errorMessageLastPart));
		}
	}

	protected void validateCapabilities(Run run) throws ValidationException {
		if(isInOrchestrationContext(run) && run.getCategory() == ModuleCategory.Image) {
			throw new ValidationException("Image creation is not yet available for this connector");
		}
	}

	protected void validateLaunch(Run run, User user) throws ValidationException{
		validateCredentials(user);
		validateBaseParameters(user);
		validateCapabilities(run);

		String instanceType = getInstanceType(run, user);
		if (instanceType == null || "".equals(instanceType)){
			if (isInOrchestrationContext(run)){
				throw (new ValidationException("Orchestrator instance type cannot be empty. Please contact your SlipStream administrator"));
			}else{
				throw (new ValidationException("Instance type cannot be empty. Please update your image parameters"));
			}
		}

		String imageId = getImageId(run, user);
		if (imageId == null  || "".equals(imageId)){
			if (isInOrchestrationContext(run)){
				throw (new ValidationException("Orchestrator image id cannot be empty. Please contact your SlipStream administrator"));
			}else{
				throw (new ValidationException("Image id cannot be empty. Please update your image parameters"));
			}
		}
	}

	@Override
	public Credentials getCredentials(User user) {
		return new CloudStackCredentials(user, getConnectorInstanceName());
	}

	@Override
	public Map<String, ModuleParameter> getImageParametersTemplate()
			throws ValidationException {
		return new CloudStackImageParametersFactory(getConnectorInstanceName()).getParameters();
	}

	@Override
	public Map<String, UserParameter> getUserParametersTemplate()
			throws ValidationException {
		return new CloudStackUserParametersFactory(getConnectorInstanceName()).getParameters();
	}

	@Override
	public Map<String, ServiceConfigurationParameter> getServiceConfigurationParametersTemplate()
			throws ValidationException {
		return new CloudStackSystemConfigurationParametersFactory(getConnectorInstanceName()).getParameters();
	}

	@Override
	protected String constructKey(String key) throws ValidationException {
		return new CloudStackUserParametersFactory(getConnectorInstanceName()).constructKey(key);
	}

}
