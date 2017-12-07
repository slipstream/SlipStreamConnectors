package com.sixsq.slipstream.connector.cloudstack;

import com.sixsq.slipstream.credentials.CloudCredential;
import com.sixsq.slipstream.persistence.UserParameter;

import java.util.Map;

public class CloudStackCloudCredDef extends CloudCredential<CloudStackCloudCredDef> {

    public String href = "credential-template/store-cloud-cred-cloudstack";


    public CloudStackCloudCredDef(String instanceName, String key, String secret) {
        super(instanceName, key, secret);
    }
    public CloudStackCloudCredDef(String instanceName, String key, String secret, Integer quota) {
        super(instanceName, key, secret);
        this.quota = quota;
    }

    CloudStackCloudCredDef(String instanceName, Map<String, UserParameter> params) {
        super(instanceName);
        setParams(params);
    }

    @Override
    public CloudStackCloudCredDef fromJson(String json) {
        return (CloudStackCloudCredDef) fromJson(json, CloudStackCloudCredDef.class);
    }
}


