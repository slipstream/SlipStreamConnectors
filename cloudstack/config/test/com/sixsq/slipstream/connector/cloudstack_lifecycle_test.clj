(ns com.sixsq.slipstream.connector.cloudstack-lifecycle-test
  (:require
    [clojure.test :refer :all]

    [com.sixsq.slipstream.connector.lifecycle-test-utils :as ltu]
    [com.sixsq.slipstream.connector.cloudstack-template :as cit]
    [com.sixsq.slipstream.connector.test-utils :as tu]

    [com.sixsq.slipstream.ssclj.resources.common.dynamic-load :as dyn]))

(use-fixtures :each ltu/with-test-client-fixture)

;; initialize must to called to pull in ConnectorTemplate test examples
(dyn/initialize)

(deftest lifecycle
  (tu/connector-lifecycle cit/cloud-service-type))

