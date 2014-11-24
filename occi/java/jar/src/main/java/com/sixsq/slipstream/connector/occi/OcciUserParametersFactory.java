/*
 * Copyright (c) 2014.
 * SixSq Sarl (http://sixsq.com) and EGI.eu (http://egi.eu).
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.sixsq.slipstream.connector.occi;

import com.sixsq.slipstream.connector.UserParametersFactoryBase;
import com.sixsq.slipstream.exceptions.ValidationException;
import com.sixsq.slipstream.persistence.ParameterType;

public class OcciUserParametersFactory extends UserParametersFactoryBase {
	public static final String PROXY_PARAMETER_NAME = "proxy";

	public static final String MYPROXY_HOST_PARAMETER_NAME = "myproxy_host";
	public static final String MYPROXY_PORT_PARAMETER_NAME = "myproxy_port";
	public static final String MYPROXY_USERNAME_PARAMETER_NAME = "myproxy_username";
	public static final String MYPROXY_PASSWORD_PARAMETER_NAME = "myproxy_password";
	public static final String VO_NAME_PARAMETER_NAME = "vo_name";
	public static final String VO_ROLE_PARAMETER_NAME = "vo_role";
	public static final String VO_FQANS_PARAMETER_NAME = "vo_fqans";
	public static final String CREDCACHE_ID_PARAMETER_NAME = "credcache_id";
	public static final String CREDCACHE_ID_PARAMETER_DESCRIPTION = "ID of the credential in the credentials cache";
	public static final String PROXY_LIFETIME_PARAMTER_NAME = "proxy_lifetime";
	public static final String PROXY_LIFETIME_PARAMTER_DEFAULT = "12";
	public static final String PROXY_LIFETIME_PARAMTER_DESCRIPTION = "Proxy lifetime (<h>[:<min>]; e.g.: 6 (6h), 1:15 (1h 15min))";

	public OcciUserParametersFactory(String connectorInstanceName) throws ValidationException {
		super(connectorInstanceName);
	}

	protected void initReferenceParameters() throws ValidationException {

		putParameter(MYPROXY_HOST_PARAMETER_NAME, "MyProxy hostname", ParameterType.String, false);
		putParameter(MYPROXY_PORT_PARAMETER_NAME, "MyProxy port", ParameterType.String, false);
		putMandatoryParameter(MYPROXY_USERNAME_PARAMETER_NAME, "Username for short-lived proxy on MyProxy",
		        ParameterType.RestrictedString, 10);
		putMandatoryPasswordParameter(MYPROXY_PASSWORD_PARAMETER_NAME, "Password for short-lived proxy on MyProxy", 20);

		putMandatoryParameter(VO_NAME_PARAMETER_NAME, "VO name", ParameterType.String, 30);
		putParameter(VO_ROLE_PARAMETER_NAME, "VO role", ParameterType.String, false);
		putParameter(VO_FQANS_PARAMETER_NAME, "VO fqans", ParameterType.String, false);

		putParameter(PROXY_LIFETIME_PARAMTER_NAME, PROXY_LIFETIME_PARAMTER_DEFAULT, PROXY_LIFETIME_PARAMTER_DESCRIPTION,
				false);

		putParameter(CREDCACHE_ID_PARAMETER_NAME, "", CREDCACHE_ID_PARAMETER_DESCRIPTION, true, true);
	}
}
