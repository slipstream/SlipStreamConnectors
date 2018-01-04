package com.sixsq.slipstream.connector.stratuslab;

import com.sixsq.slipstream.credentials.CloudCredential;
import com.sixsq.slipstream.persistence.UserParameter;

import java.util.Map;

public class StratusLabCloudCredDef extends CloudCredential<StratusLabCloudCredDef> {

    public StratusLabCloudCredDef(String instanceName, String key, String secret) {
        super(instanceName, key, secret, StratusLabConnector.CLOUD_SERVICE_NAME);
    }
    public StratusLabCloudCredDef(String instanceName, String key, String secret, Integer quota) {
        super(instanceName, key, secret, StratusLabConnector.CLOUD_SERVICE_NAME);
        this.quota = quota;
    }

    StratusLabCloudCredDef(String instanceName, Map<String, UserParameter> params) {
        super(instanceName, StratusLabConnector.CLOUD_SERVICE_NAME);
        setParams(params);
    }

    @Override
    public StratusLabCloudCredDef fromJson(String json) {
        return (StratusLabCloudCredDef) fromJson(json, StratusLabCloudCredDef.class);
    }
}
