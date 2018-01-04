package com.sixsq.slipstream.connector.cloudstack;

import com.sixsq.slipstream.credentials.CloudCredential;
import com.sixsq.slipstream.persistence.UserParameter;

import java.util.Map;

public class CloudStackCloudCredDef extends CloudCredential<CloudStackCloudCredDef> {

    public CloudStackCloudCredDef(String instanceName, String key, String secret) {
        super(instanceName, key, secret, CloudStackConnector.CLOUD_SERVICE_NAME);
    }
    public CloudStackCloudCredDef(String instanceName, String key, String secret, Integer quota) {
        super(instanceName, key, secret, CloudStackConnector.CLOUD_SERVICE_NAME);
        this.quota = quota;
    }

    CloudStackCloudCredDef(String instanceName, Map<String, UserParameter> params) {
        super(instanceName, CloudStackConnector.CLOUD_SERVICE_NAME);
        setParams(params);
    }

    @Override
    public CloudStackCloudCredDef fromJson(String json) {
        return (CloudStackCloudCredDef) fromJson(json, CloudStackCloudCredDef.class);
    }
}


