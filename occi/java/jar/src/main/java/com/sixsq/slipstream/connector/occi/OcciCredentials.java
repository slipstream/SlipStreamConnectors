package com.sixsq.slipstream.connector.occi;

import com.sixsq.slipstream.connector.CredentialsBase;
import com.sixsq.slipstream.credentials.Credentials;
import com.sixsq.slipstream.exceptions.InvalidElementException;
import com.sixsq.slipstream.exceptions.SlipStreamInternalException;
import com.sixsq.slipstream.exceptions.SlipStreamRuntimeException;
import com.sixsq.slipstream.exceptions.ValidationException;
import com.sixsq.slipstream.persistence.User;
import com.sixsq.slipstream.persistence.UserParameter;
import org.apache.commons.io.IOUtils;
import slipstream.credcache.JavaWrapper;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.*;
import java.util.logging.Logger;

class OcciCredentials extends CredentialsBase implements Credentials {

	private static Logger logger = Logger.getLogger(OcciCredentials.class.getName());

	public OcciCredentials(User user, String connectorInstanceName) {
		super(user);
		try {
			this.cloudParametersFactory = new OcciUserParametersFactory(
					connectorInstanceName);
		} catch (ValidationException e) {
			e.printStackTrace();
			throw new SlipStreamRuntimeException(e);
		}
	}

	public String getKey() throws InvalidElementException {
		return "dummy_username";
	}

	public String getSecret() throws InvalidElementException {
		return "dummy_password";
	}

	private String getMyproxyUsername() throws InvalidElementException {
		return getParameterValue(OcciUserParametersFactory.MYPROXY_USERNAME_PARAMETER_NAME);
	}

	private String getMyproxyPassword() throws InvalidElementException {
		return getParameterValue(OcciUserParametersFactory.MYPROXY_PASSWORD_PARAMETER_NAME);
	}

	public File getVomsProxyFile() throws InvalidElementException, ValidationException {
		File vomsProxyFile;
		String credcacheId = getCredcacheId();
		if (credcacheId.isEmpty()) {
		    credcacheId = createVomsProxyAndStoreCredcacheIdOnUser();
		}
		try {
			vomsProxyFile = JavaWrapper.retrieve(credcacheId);
		} catch (Exception e) {
			// Try to re-create the proxy using probably changed VOMS related User parameters.
			credcacheId = createVomsProxyAndStoreCredcacheIdOnUser();
			vomsProxyFile = JavaWrapper.retrieve(credcacheId);
		}
		if (vomsProxyFile == null) {
			throw new SlipStreamRuntimeException("Failed to get VOMS proxy.");
		}
		return vomsProxyFile;
	}

	public String getVomsProxyMaterial() throws InvalidElementException, ValidationException {
		File vomsProxyFile = getVomsProxyFile();
		try  {
		    FileInputStream inputStream = new FileInputStream(vomsProxyFile.getAbsolutePath());
    		try {
    	        return IOUtils.toString(inputStream);
    		} catch (IOException ex) {
    			throw new SlipStreamInternalException("Failed to get VOMS proxy material. Failed to read from file: "
    			        + vomsProxyFile.getAbsolutePath());
    		} finally {
    			try {
    				inputStream.close();
    			} catch (IOException ex) {
    				//
    			}
		    }
		} catch (FileNotFoundException ex) {
			throw new SlipStreamInternalException("Failed to get VOMS proxy material. File not found: "
			        + vomsProxyFile.getAbsolutePath());
		} finally {
			if (vomsProxyFile != null) {
				vomsProxyFile.delete();
			}
		}
	}

	private String createVomsProxyAndStoreCredcacheIdOnUser() throws InvalidElementException, ValidationException {
		Map<String, Object> template = getCredcacheTemplate();
		logger.fine("Create proxy from template: " + template);
	    String credcacheId = JavaWrapper.create(template);
	    storeCredcacheIdAsUserParameter(credcacheId);
	    return credcacheId;
    }

	private String getCredcacheId() throws InvalidElementException {
		String credcacheId = getParameterValue(OcciUserParametersFactory.CREDCACHE_ID_PARAMETER_NAME);
		return credcacheId == null ? "" : credcacheId;
	}

	private int getProxyLifetime() throws ValidationException, InvalidElementException {
		String lifetime = getParameterValue(OcciUserParametersFactory.PROXY_LIFETIME_PARAMTER_NAME);
		try {
			return parseProxyLifetimeParameter(lifetime);
		} catch (NumberFormatException ex) {
			throw new ValidationException("Failed to parse proxy lifetime parameter value '" + lifetime
			        + "'. Expected: " + OcciUserParametersFactory.PROXY_LIFETIME_PARAMTER_DESCRIPTION);
		}
	}

	private int parseProxyLifetimeParameter(String lifetime) throws NumberFormatException {
		if (lifetime == null || lifetime.isEmpty()) {
			return Integer.parseInt(OcciUserParametersFactory.PROXY_LIFETIME_PARAMTER_DEFAULT);
		}

		int hours = 0;
		String[] hoursMinutes = lifetime.split(":");
		String hoursStr = hoursMinutes[0];
		hours = Integer.parseInt(hoursStr) * 3660;
		if (hoursMinutes.length == 1) {
			return hours;
		} else {
			String minutes = hoursMinutes[1];
			return hours + Integer.parseInt(minutes) * 60;
		}
	}

	private Map<String, Object> getCredcacheTemplate() throws ValidationException, InvalidElementException {
		/**
		 * For the template schema validator see: slipstream/credcache/credential/myproxy_voms.clj
		 *
		 * Schema for the template
		 *
		 * "typeURI" -> required String: must be "http://schemas.dmtf.org/cimi/1/CredentialTemplate"
		 * "subtypeURI" -> required String: must be "http://sixsq.com/slipstream/credential/myproxy-voms"
		 *
		 * "myproxy-host" -> required String: host of the MyProxy server to use
		 * "myproxy-port" -> optional Integer: port of MyProxy server
		 * "username" -> required String: username of short-lived MyProxy credential
		 * "passphrase" -> required String: passphrase for short-lived MyProxy credential
		 * "email" -> optional String: email address of the user to notify of the failures in credentials renewal
   		 * "lifetime" -> optional Integer: proxy lifetime in seconds
		 * "voms" -> map of VOMS parameters
		 *           vo-name -> map with optional key "fqans" -> list of Strings
		 *                               optional key "targets" -> list of Strings
		 *
		 * "name" -> optional String: name of credential
		 * "description" -> optional String: description of credential
		 * "properties" -> optional String -> String map of properties
		 */
		Map<String, Object> template = new HashMap<String, Object>();

		template.put("typeURI", "http://schemas.dmtf.org/cimi/1/CredentialTemplate");
		template.put("subtypeURI", "http://sixsq.com/slipstream/credential/myproxy-voms");

		template.put("email", getUserEmail());
		template.put("lifetime", getProxyLifetime());

		// MyProxy
		template.put(
				"myproxy-host",
				getParameterValue(OcciUserParametersFactory.MYPROXY_HOST_PARAMETER_NAME));
		String port = getParameterValue(OcciUserParametersFactory.MYPROXY_PORT_PARAMETER_NAME);
		if (!port.isEmpty()) {
			template.put("myproxy-port", Integer.parseInt(port));
		}
		template.put("username", getMyproxyUsername());
		template.put("passphrase", getMyproxyPassword());

		// VOMS
		Map<String, HashMap<String, List<String>>> voms = new HashMap<String, HashMap<String, List<String>>>();
		String voName = getParameterValue(OcciUserParametersFactory.VO_NAME_PARAMETER_NAME);
		if (!voName.isEmpty()) {
			voms.put(voName, new HashMap<String, List<String>>());

			String fqans = getParameterValue(OcciUserParametersFactory.VO_FQANS_PARAMETER_NAME);
			if (!fqans.isEmpty()) {
				voms.get(voName).put("fqans", new ArrayList<String>(Arrays.asList(fqans.split(","))));
			}

			String targets = getParameterValue(OcciUserParametersFactory.VO_ROLE_PARAMETER_NAME);
			if (!targets.isEmpty()) {
				voms.get(voName).put("targets", new ArrayList<String>(Arrays.asList(targets.split(","))));
			}

			template.put("voms", voms);
		}

		return template;
	}

	private void storeCredcacheIdAsUserParameter(String credcacheId) throws ValidationException {
	    UserParameter credcacheUserParam = new UserParameter(
	            cloudParametersFactory.constructKey(OcciUserParametersFactory.CREDCACHE_ID_PARAMETER_NAME),
	            credcacheId, OcciUserParametersFactory.CREDCACHE_ID_PARAMETER_DESCRIPTION);
	    credcacheUserParam.setCategory(this.cloudParametersFactory.getCategory());
	    this.user.setParameter(credcacheUserParam);
	    this.user.store();
	}

	private String getUserEmail() {
		return this.user.getEmail();
	}
}
