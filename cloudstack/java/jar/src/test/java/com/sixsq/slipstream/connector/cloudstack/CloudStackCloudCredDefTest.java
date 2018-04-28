package com.sixsq.slipstream.connector.cloudstack;

import com.sixsq.slipstream.exceptions.ValidationException;
import com.sixsq.slipstream.util.CloudCredDefTestBase;
import org.junit.Test;

import static org.junit.Assert.fail;

public class CloudStackCloudCredDefTest extends CloudCredDefTestBase {

    @Test
    public void cloudCredentialsDirectLifecycleTest() {
        CloudStackCloudCredDef credDef = new CloudStackCloudCredDef(
                getConnectorName(),
                "key",
                "secret");
        CloudStackSystemConfigurationParametersFactory sysConfParams = null;
        try {
            sysConfParams = new
                    CloudStackSystemConfigurationParametersFactory(getConnectorName());
        } catch (ValidationException e) {
            e.printStackTrace();
            fail("Failed to create connector " + getConnectorName() + " with: " +
                    e.getMessage());
        }
        runCloudCredentialsDirectLifecycle(
                credDef,
                CloudStackConnector.CLOUD_SERVICE_NAME,
                sysConfParams);
    }
}
