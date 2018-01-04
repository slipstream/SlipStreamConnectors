package com.sixsq.slipstream.connector.stratuslab;

import com.sixsq.slipstream.credentials.CloudCredential;
import com.sixsq.slipstream.persistence.UserParameter;

import java.util.Map;

public class StratusLabIterCloudCredDef extends CloudCredential<StratusLabIterCloudCredDef> {

    public StratusLabIterCloudCredDef(String instanceName, String key, String secret) {
        super(instanceName, key, secret, StratusLabIterConnector.CLOUD_SERVICE_NAME);
    }
    public StratusLabIterCloudCredDef(String instanceName, String key, String secret, Integer quota) {
        super(instanceName, key, secret, StratusLabIterConnector.CLOUD_SERVICE_NAME);
        this.quota = quota;
    }

    StratusLabIterCloudCredDef(String instanceName, Map<String, UserParameter> params) {
        super(instanceName, StratusLabIterConnector.CLOUD_SERVICE_NAME);
        setParams(params);
    }

    @Override
    public StratusLabIterCloudCredDef fromJson(String json) {
        return (StratusLabIterCloudCredDef) fromJson(json, StratusLabIterCloudCredDef.class);
    }
}
