(ns com.sixsq.slipstream.ssclj.resources.credential-cloud-stratuslabiter-lifecycle-test
  (:require
    [clojure.test :refer [deftest is are use-fixtures]]
    [peridot.core :refer :all]
    [com.sixsq.slipstream.connector.stratuslabiter-template :as cont]
    [com.sixsq.slipstream.ssclj.resources.credential-template-cloud-stratuslabiter :as cloud-stratuslabiter]
    [com.sixsq.slipstream.ssclj.resources.credential-cloud-lifecycle-test-utils :as cclt]
    [com.sixsq.slipstream.ssclj.resources.credential-template :as ct]
    [com.sixsq.slipstream.ssclj.resources.lifecycle-test-utils :as ltu]
    [com.sixsq.slipstream.ssclj.resources.common.dynamic-load :as dyn]))

(use-fixtures :each ltu/with-test-es-client-fixture)

;; initialize must to called to pull in CredentialTemplate resources
(dyn/initialize)

(deftest lifecycle
  (cclt/cloud-cred-lifecycle {:href      (str ct/resource-url "/" cloud-stratuslabiter/method)
                              :key       "key"
                              :secret    "secret"
                              :quota     7
                              :connector {:href "connector/stratuslabiter-1"}}
                             cont/cloud-service-type))
