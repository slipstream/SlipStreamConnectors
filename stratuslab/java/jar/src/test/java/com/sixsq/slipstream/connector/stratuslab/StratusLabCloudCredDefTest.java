package com.sixsq.slipstream.connector.stratuslab;

import com.sixsq.slipstream.exceptions.ValidationException;
import com.sixsq.slipstream.util.CloudCredDefTestBase;
import org.junit.Test;

import static org.junit.Assert.fail;

public class StratusLabCloudCredDefTest extends CloudCredDefTestBase {

    @Test
    public void cloudCredentialsDirectLifecycleTest() {
        StratusLabCloudCredDef credDef = new StratusLabCloudCredDef(
                getConnectorName(),
                "key",
                "secret");
        StratusLabSystemConfigurationParametersFactory sysConfParams = null;
        try {
            sysConfParams = new
                    StratusLabSystemConfigurationParametersFactory(getConnectorName());
        } catch (ValidationException e) {
            e.printStackTrace();
            fail("Failed to create connector " + CONNECTOR_NAME + " with: " +
                    e.getMessage());
        }
        runCloudCredentialsDirectLifecycle(
                credDef,
                StratusLabConnector.CLOUD_SERVICE_NAME,
                sysConfParams);
    }
}
