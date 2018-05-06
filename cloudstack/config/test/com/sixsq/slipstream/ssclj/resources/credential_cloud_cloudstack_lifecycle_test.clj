(ns com.sixsq.slipstream.ssclj.resources.credential-cloud-cloudstack-lifecycle-test
  (:require
    [clojure.test :refer [are deftest is use-fixtures]]
    [com.sixsq.slipstream.connector.cloudstack-template :as cont]
    [com.sixsq.slipstream.ssclj.resources.credential-cloud-lifecycle-test-utils :as cclt]
    [com.sixsq.slipstream.ssclj.resources.credential-template :as ct]
    [com.sixsq.slipstream.ssclj.resources.credential-template-cloud-cloudstack :as cloud-cloudstack]
    [com.sixsq.slipstream.ssclj.resources.lifecycle-test-utils :as ltu]))

(use-fixtures :each ltu/with-test-server-fixture)

(deftest lifecycle
  (cclt/cloud-cred-lifecycle {:href      (str ct/resource-url "/" cloud-cloudstack/method)
                              :key       "key"
                              :secret    "secret"
                              :quota     7
                              :connector {:href "connector/cloudstack-xyz"}}
                             cont/cloud-service-type))
