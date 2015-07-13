package com.sixsq.slipstream.connector.stratuslab;

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

import static org.hamcrest.Matchers.is;
import static org.junit.Assert.assertThat;

import java.util.Map;
import java.util.Properties;

import com.sixsq.slipstream.connector.ConnectorBase;
import org.junit.Test;

import com.sixsq.slipstream.connector.stratuslab.StratusLabConnector;
import com.sixsq.slipstream.exceptions.SlipStreamException;

public class StratusLabConnectorTest2 extends StratusLabConnector {

	@Test
	public void parseDescribeInstanceTest() throws SlipStreamException {
		String result = "id, state, ip, cpu, memory\n"
				+ "16, Running, 134.158.73.235, 1, 128\n"
				+ "17, Pending, 134.158.73.236, 1, 128\n";
		Map<String, Properties> res = StratusLabConnector.parseDescribeInstanceResult(result);
		Properties empty = new Properties();
		assertThat(res.getOrDefault("16", empty).getProperty(ConnectorBase.VM_STATE), is("Running"));
		assertThat(res.getOrDefault("17", empty).getProperty(ConnectorBase.VM_STATE), is("Pending"));
	}
}
