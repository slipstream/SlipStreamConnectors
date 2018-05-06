(ns com.sixsq.slipstream.ssclj.resources.credential-cloud-openstack-lifecycle-test
  (:require
    [clojure.test :refer [are deftest is use-fixtures]]
    [com.sixsq.slipstream.connector.openstack-template :as cont]
    [com.sixsq.slipstream.ssclj.resources.credential-cloud-lifecycle-test-utils :as cclt]
    [com.sixsq.slipstream.ssclj.resources.credential-template :as ct]
    [com.sixsq.slipstream.ssclj.resources.credential-template-cloud-openstack :as cloud-openstack]
    [com.sixsq.slipstream.ssclj.resources.lifecycle-test-utils :as ltu]))

(use-fixtures :each ltu/with-test-server-fixture)

(deftest lifecycle
  (cclt/cloud-cred-lifecycle {:href        (str ct/resource-url "/" cloud-openstack/method)
                              :key         "key"
                              :secret      "secret"
                              :connector   {:href "connector/openstack-1"}
                              :quota       7
                              :tenant-name "tenant"
                              :domain-name "domain"}
                             cont/cloud-service-type))
