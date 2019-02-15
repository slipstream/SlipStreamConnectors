(ns com.sixsq.slipstream.ssclj.resources.credential-cloud-docker-lifecycle-test
    (:require
    [clojure.test :refer [are deftest is use-fixtures]]
    [com.sixsq.slipstream.connector.docker-template :as cont]
    [com.sixsq.slipstream.ssclj.resources.credential-cloud-lifecycle-test-utils :as cclt]
    [com.sixsq.slipstream.ssclj.resources.credential-template :as ct]
    [com.sixsq.slipstream.ssclj.resources.credential-template-cloud-docker :as cloud-docker]
    [com.sixsq.slipstream.ssclj.resources.lifecycle-test-utils :as ltu]))

(use-fixtures :each ltu/with-test-server-fixture)

(deftest lifecycle
  (cclt/cloud-cred-lifecycle {:href      (str ct/resource-url "/" cloud-docker/method)
                              :key       "key"
                              :secret    "secret"
                              :quota     7
                              :connector {:href "connector/foo-bar-baz"}}
                             cont/cloud-service-type))
