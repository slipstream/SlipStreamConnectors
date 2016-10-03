(ns com.sixsq.slipstream.connector.cloudstack-advancedzone-template-lifecycle-test
  (:require
    [clojure.test :refer :all]
    [peridot.core :refer :all]

    [com.sixsq.slipstream.connector.cloudstack-advancedzone-template :as cit]
    [com.sixsq.slipstream.connector.lifecycle-test-utils :as ltu]
    [com.sixsq.slipstream.connector.test-utils :as tu]

    [com.sixsq.slipstream.ssclj.resources.common.dynamic-load :as dyn]))

(use-fixtures :each ltu/with-test-client-fixture)

;; initialize must to called to pull in ConnectorTemplate test examples
(dyn/initialize)


(deftest test-connector-template-is-registered
  (tu/connector-template-is-registered cit/cloud-service-type))

(deftest lifecycle
  (tu/template-lifecycle cit/cloud-service-type))

