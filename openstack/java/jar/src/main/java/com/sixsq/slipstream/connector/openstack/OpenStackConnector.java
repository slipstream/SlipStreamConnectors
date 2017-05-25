package com.sixsq.slipstream.connector.openstack;

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


public class OpenStackConnector extends CliConnectorBase {

	public static final String CLOUD_SERVICE_NAME = "openstack";
	public static final String CLOUDCONNECTOR_PYTHON_MODULENAME = "slipstream_openstack.OpenStackClientCloud";

	public OpenStackConnector() {
		this(CLOUD_SERVICE_NAME);
	}

	public OpenStackConnector(String instanceName){
		super(instanceName != null ? instanceName : CLOUD_SERVICE_NAME);
	}

	public Connector copy(){
		return new OpenStackConnector(getConnectorInstanceName());
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
		userParams.put("project", getProject(user));
		userParams.put("endpoint", getEndpoint(user));
		userParams.put("region", getRegion());
		userParams.put("identity-version", getIdentityVersion());
        userParams.put("service-type", getServiceType());
		putUserParamDomain(userParams, user);
		putUserParamServiceName(userParams);
		return userParams;
	}

	@Override
	protected Map<String, String> getConnectorSpecificLaunchParams(Run run, User user)
			throws ConfigurationException, ValidationException {
		Map<String, String> launchParams = new HashMap<String, String>();
		launchParams.put("instance-type", getInstanceType(run));
        launchParams.put("network-public", getNetworkPublic());
        launchParams.put("network-private", getNetworkPrivate());
		putLaunchParamSecurityGroups(launchParams, run, user);
		putLaunchParamUseFloatingIp(launchParams);
		return launchParams;
	}

	protected void putUserParamDomain(Map<String, String> userParams, User user) throws ValidationException {
		String domain = getDomain(user);
		if (domain != null && !domain.isEmpty()) {
			userParams.put("domain", domain);
		}
	}

	protected void putUserParamServiceName(Map<String, String> userParams) throws ValidationException {
		String serviceName = getServiceName();
		if (serviceName != null && !serviceName.isEmpty()) {
			userParams.put("service-name", serviceName);
		}
	}

	protected void putLaunchParamUseFloatingIp(Map<String, String> launchParams) throws ValidationException {
		String useFloatingIp = getUseFloatingIp();
		if (useFloatingIp != null && !useFloatingIp.isEmpty() && Boolean.parseBoolean(useFloatingIp)) {
			launchParams.put("use-floating-ips", null);
		}
	}

	protected String getUseFloatingIp() throws ConfigurationException, ValidationException {
		return Configuration.getInstance().getRequiredProperty(constructKey(OpenStackUserParametersFactory.USE_FLOATING_IPS_NAME));
	}

	protected String getServiceType() throws ConfigurationException, ValidationException {
		return Configuration.getInstance().getRequiredProperty(constructKey(OpenStackUserParametersFactory.SERVICE_TYPE_PARAMETER_NAME));
	}

    protected String getServiceName() throws ConfigurationException, ValidationException {
        return Configuration.getInstance().getRequiredProperty(constructKey(OpenStackUserParametersFactory.SERVICE_NAME_PARAMETER_NAME));
    }

    protected String getNetworkPublic() throws ConfigurationException, ValidationException {
        return Configuration.getInstance().getRequiredProperty(constructKey(OpenStackUserParametersFactory.NETWORK_PUBLIC_NAME));
    }

    protected String getNetworkPrivate() throws ConfigurationException, ValidationException {
        return Configuration.getInstance().getRequiredProperty(constructKey(OpenStackUserParametersFactory.NETWORK_PRIVATE_NAME));
    }

    protected String getRegion() throws ConfigurationException, ValidationException {
		return Configuration.getInstance().getRequiredProperty(constructKey(OpenStackUserParametersFactory.SERVICE_REGION_PARAMETER_NAME));
	}

	protected String getProject(User user) throws ValidationException {
		return user.getParameter(constructKey(OpenStackUserParametersFactory.TENANT_NAME)).getValue(null);
	}

	protected String getDomain(User user) throws ValidationException {
		return user.getParameterValue(constructKey(OpenStackUserParametersFactory.DOMAIN_NAME), null);
	}

	protected String getInstanceType(Run run) throws ConfigurationException, ValidationException {
		return (isInOrchestrationContext(run)) ? Configuration.getInstance()
				.getRequiredProperty(constructKey(OpenStackUserParametersFactory.ORCHESTRATOR_INSTANCE_TYPE_PARAMETER_NAME))
				: getInstanceType(run);
	}

	protected String getIdentityVersion() throws ValidationException {
		return Configuration.getInstance().getRequiredProperty(constructKey(OpenStackUserParametersFactory.IDENTITY_VERSION_PARAMETER_NAME));
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
		return new OpenStackSystemConfigurationParametersFactory(getConnectorInstanceName()).getParameters();
	}

	@Override
	public Map<String, UserParameter> getUserParametersTemplate()
			throws ValidationException {
		return new OpenStackUserParametersFactory(getConnectorInstanceName()).getParameters();
	}

	@Override
	public Map<String, ModuleParameter> getImageParametersTemplate()
			throws ValidationException {
		return new OpenStackImageParametersFactory(getConnectorInstanceName()).getParameters();
	}

	@Override
	protected String constructKey(String key) throws ValidationException {
		return new OpenStackUserParametersFactory(getConnectorInstanceName()).constructKey(key);
	}

	@Override
	public Credentials getCredentials(User user) {
		return new OpenStackCredentials(user, getConnectorInstanceName());
	}

	protected java.util.Map<String,String> getConnectorSpecificEnvironment(Run run, User user)
			throws ConfigurationException, ValidationException {
		Configuration configuration = Configuration.getInstance();
        Map<String,String> environment = new HashMap<String,String>();

		environment.put("OPENSTACK_SERVICE_TYPE", configuration
				.getRequiredProperty(constructKey(OpenStackUserParametersFactory.SERVICE_TYPE_PARAMETER_NAME)));
		environment.put("OPENSTACK_SERVICE_NAME", configuration
				.getRequiredProperty(constructKey(OpenStackUserParametersFactory.SERVICE_NAME_PARAMETER_NAME)));
		environment.put("OPENSTACK_SERVICE_REGION", configuration
				.getRequiredProperty(constructKey(OpenStackUserParametersFactory.SERVICE_REGION_PARAMETER_NAME)));

        return environment;
	}

}
