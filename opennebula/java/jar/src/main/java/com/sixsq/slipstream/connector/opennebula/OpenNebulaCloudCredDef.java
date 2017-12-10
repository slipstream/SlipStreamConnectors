package com.sixsq.slipstream.connector.opennebula;

import com.sixsq.slipstream.credentials.CloudCredential;
import com.sixsq.slipstream.persistence.UserParameter;

import java.util.Map;

public class OpenNebulaCloudCredDef extends CloudCredential<OpenNebulaCloudCredDef> {

    public String href = "credential-template/store-cloud-cred-opennebula";


    public OpenNebulaCloudCredDef(String instanceName, String key, String secret) {
        super(instanceName, key, secret);
    }
    public OpenNebulaCloudCredDef(String instanceName, String key, String secret, Integer quota) {
        super(instanceName, key, secret);
        this.quota = quota;
    }

    OpenNebulaCloudCredDef(String instanceName, Map<String, UserParameter> params) {
        super(instanceName);
        setParams(params);
    }

    @Override
    public OpenNebulaCloudCredDef fromJson(String json) {
        return (OpenNebulaCloudCredDef) fromJson(json, OpenNebulaCloudCredDef.class);
    }
}


