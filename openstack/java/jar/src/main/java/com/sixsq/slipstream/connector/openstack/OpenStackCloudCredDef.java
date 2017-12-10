package com.sixsq.slipstream.connector.openstack;

/*
 * +=================================================================+
 * SlipStream Server (WAR)
 * =====
 * Copyright (C) 2013 SixSq Sarl (sixsq.com)
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

import com.google.gson.annotations.SerializedName;
import com.sixsq.slipstream.credentials.CloudCredential;
import com.sixsq.slipstream.credentials.ICloudCredential;
import com.sixsq.slipstream.exceptions.ValidationException;
import com.sixsq.slipstream.persistence.UserParameter;

import java.util.Map;

public class OpenStackCloudCredDef extends CloudCredential<OpenStackCloudCredDef> {

    public String href = "credential-template/store-cloud-cred-openstack";

    @SerializedName("tenant-name")
    public String tenantName;

    @SerializedName("domain-name")
    public String domainName;

    public OpenStackCloudCredDef(String instanceName, String key, String secret,
                                 String tenantName, String domainName) {
        super(instanceName, key, secret);
        this.tenantName = tenantName;
        this.domainName = domainName;
    }

    public OpenStackCloudCredDef(String instanceName, String key, String secret,
                                 Integer quota, String tenantName, String domainName) {
        this(instanceName, key, secret, tenantName, domainName);
        this.quota = quota;
    }

    OpenStackCloudCredDef(String instanceName, Map<String, UserParameter> params) {
        super(instanceName);
        setParams(params);
    }

    public void setParams(Map<String, UserParameter> params) {
        super.setParams(params);

        String instanceName = getConnectorInstanceName();
        String k;

        k = UserParameter.constructKey(instanceName, "domain", "name");
        if (params.containsKey(k)) {
            domainName = params.get(k).getValue();
        }
        k = UserParameter.constructKey(instanceName, "tenant", "name");
        if (params.containsKey(k)) {
            tenantName = params.get(k).getValue();
        }
    }

    public Map<String, UserParameter> getParams() throws ValidationException {
        Map<String, UserParameter> params = super.getParams();

        String instanceName = getConnectorInstanceName();
        String k;

        if (null != this.domainName) {
            k = UserParameter.constructKey(instanceName, "domain", "name");
            params.put(k, new UserParameter(k, this.domainName, ""));
        }
        if (null != this.tenantName) {
            k = UserParameter.constructKey(instanceName, "tenant", "name");
            params.put(k, new UserParameter(k, this.tenantName, ""));
        }
        return params;
    }

    @Override
    public OpenStackCloudCredDef fromJson(String json) {
        return (OpenStackCloudCredDef) fromJson(json, OpenStackCloudCredDef.class);
    }

    public boolean credEquals(ICloudCredential<OpenStackCloudCredDef> other) {
        OpenStackCloudCredDef o = (OpenStackCloudCredDef) other;
        return super.credEquals(o) && this.tenantName.equals(o.tenantName) && this
                .domainName.equals(o.domainName);
    }
}
