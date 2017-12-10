package com.sixsq.slipstream.connector.openstack;

import com.sixsq.slipstream.exceptions.ValidationException;
import com.sixsq.slipstream.util.CloudCredDefTestBase;
import org.junit.Test;

import static org.junit.Assert.fail;

public class OpenStackCloudCredDefTest extends CloudCredDefTestBase {

    @Test
    public void cloudCredentialsDirectLifecycleTest() {
        OpenStackCloudCredDef credDef = new OpenStackCloudCredDef(
                getConnectorName(),
                "key",
                "secret",
                "tn",
                "dn");
        OpenStackSystemConfigurationParametersFactory sysConfParams = null;
        try {
            sysConfParams = new
                    OpenStackSystemConfigurationParametersFactory(getConnectorName());
        } catch (ValidationException e) {
            e.printStackTrace();
            fail("Failed to create connector " + CONNECTOR_NAME + " with: " +
                    e.getMessage());
        }
        runCloudCredentialsDirectLifecycle(
                credDef,
                OpenStackConnector.CLOUD_SERVICE_NAME,
                sysConfParams);
    }
}
