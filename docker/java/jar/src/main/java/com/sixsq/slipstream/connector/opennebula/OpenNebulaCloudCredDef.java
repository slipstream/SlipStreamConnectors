package com.sixsq.slipstream.connector.opennebula;

import com.sixsq.slipstream.credentials.CloudCredential;
import com.sixsq.slipstream.persistence.UserParameter;

import java.util.Map;

public class OpenNebulaCloudCredDef extends CloudCredential<OpenNebulaCloudCredDef> {

    public OpenNebulaCloudCredDef(String instanceName, String key, String secret) {
        super(instanceName, key, secret, OpenNebulaConnector.CLOUD_SERVICE_NAME);
    }
    public OpenNebulaCloudCredDef(String instanceName, String key, String secret, Integer quota) {
        super(instanceName, key, secret, OpenNebulaConnector.CLOUD_SERVICE_NAME);
        this.quota = quota;
    }

    OpenNebulaCloudCredDef(String instanceName, Map<String, UserParameter> params) {
        super(instanceName, OpenNebulaConnector.CLOUD_SERVICE_NAME);
        setParams(params);
    }

    @Override
    public OpenNebulaCloudCredDef fromJson(String json) {
        return (OpenNebulaCloudCredDef) fromJson(json, OpenNebulaCloudCredDef.class);
    }
}


