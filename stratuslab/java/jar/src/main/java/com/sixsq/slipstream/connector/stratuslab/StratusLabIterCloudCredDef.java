package com.sixsq.slipstream.connector.stratuslab;

import com.sixsq.slipstream.credentials.CloudCredential;
import com.sixsq.slipstream.persistence.UserParameter;

import java.util.Map;

public class StratusLabIterCloudCredDef extends CloudCredential<StratusLabIterCloudCredDef> {

    public String href = "credential-template/store-cloud-cred-stratuslabiter";


    public StratusLabIterCloudCredDef(String instanceName, String key, String secret) {
        super(instanceName, key, secret);
    }
    public StratusLabIterCloudCredDef(String instanceName, String key, String secret, Integer quota) {
        super(instanceName, key, secret);
        this.quota = quota;
    }

    StratusLabIterCloudCredDef(String instanceName, Map<String, UserParameter> params) {
        super(instanceName);
        setParams(params);
    }

    @Override
    public StratusLabIterCloudCredDef fromJson(String json) {
        return (StratusLabIterCloudCredDef) fromJson(json, StratusLabIterCloudCredDef.class);
    }
}
