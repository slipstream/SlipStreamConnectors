package com.sixsq.slipstream.connector.opennebula;

import com.sixsq.slipstream.exceptions.ValidationException;
import com.sixsq.slipstream.util.CloudCredDefTestBase;
import org.junit.Test;

import static org.junit.Assert.fail;

public class OpenNebulaCloudCredDefTest extends CloudCredDefTestBase {

    @Test
    public void cloudCredentialsDirectLifecycleTest() {
        OpenNebulaCloudCredDef credDef = new OpenNebulaCloudCredDef(
                getConnectorName(),
                "key",
                "secret");
        OpenNebulaSystemConfigurationParametersFactory sysConfParams = null;
        try {
            sysConfParams = new
                    OpenNebulaSystemConfigurationParametersFactory(getConnectorName());
        } catch (ValidationException e) {
            e.printStackTrace();
            fail("Failed to create connector " + CONNECTOR_NAME + " with: " +
                    e.getMessage());
        }
        runCloudCredentialsDirectLifecycle(
                credDef,
                OpenNebulaConnector.CLOUD_SERVICE_NAME,
                sysConfParams);
    }
}
