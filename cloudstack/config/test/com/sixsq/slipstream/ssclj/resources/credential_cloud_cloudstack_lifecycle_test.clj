(ns com.sixsq.slipstream.ssclj.resources.credential-cloud-cloudstack-lifecycle-test
  (:require
    [clojure.test :refer [deftest is are use-fixtures]]
    [peridot.core :refer :all]
    [clojure.data.json :as json]
    [com.sixsq.slipstream.ssclj.resources.common.dynamic-load :as dyn]
    [com.sixsq.slipstream.ssclj.resources.lifecycle-test-utils :as ltu]
    [com.sixsq.slipstream.ssclj.resources.credential-template :as ct]
    [com.sixsq.slipstream.ssclj.resources.credential-cloud-lifecycle-test-utils :as cclt]
    [com.sixsq.slipstream.ssclj.resources.credential-template-cloud-cloudstack :as cloud-cloudstack]))

(use-fixtures :each ltu/with-test-es-client-fixture)

;; initialize must to called to pull in CredentialTemplate resources
(dyn/initialize)

(deftest lifecycle
  (cclt/cloud-cred-lifecycle {:href        (str ct/resource-url "/" cloud-cloudstack/method)
                              :key         "key"
                              :secret      "secret"
                              :connector   "connector/cloudstack-xyz"}))
