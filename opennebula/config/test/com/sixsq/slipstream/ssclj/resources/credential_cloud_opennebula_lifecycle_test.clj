(ns com.sixsq.slipstream.ssclj.resources.credential-cloud-opennebula-lifecycle-test
  (:require
    [clojure.test :refer [are deftest is use-fixtures]]
    [com.sixsq.slipstream.connector.opennebula-template :as cont]
    [com.sixsq.slipstream.ssclj.resources.credential-cloud-lifecycle-test-utils :as cclt]
    [com.sixsq.slipstream.ssclj.resources.credential-template :as ct]
    [com.sixsq.slipstream.ssclj.resources.credential-template-cloud-opennebula :as cloud-opennebula]
    [com.sixsq.slipstream.ssclj.resources.lifecycle-test-utils :as ltu]))

(use-fixtures :each ltu/with-test-server-fixture)

(deftest lifecycle
  (cclt/cloud-cred-lifecycle {:href      (str ct/resource-url "/" cloud-opennebula/method)
                              :key       "key"
                              :secret    "secret"
                              :quota     7
                              :connector {:href "connector/foo-bar-baz"}}
                             cont/cloud-service-type))
