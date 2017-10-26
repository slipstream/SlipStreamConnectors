(ns com.sixsq.slipstream.ssclj.resources.spec.credential-cloud-cloudstack-test
    (:require
    [clojure.test :refer :all]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-cloud-cloudstack]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template-cloud-cloudstack]
    [com.sixsq.slipstream.ssclj.resources.credential-template-cloud-cloudstack :refer [resource-acl credential-type method]]
    [com.sixsq.slipstream.ssclj.resources.credential-template :as ct]
    [clojure.spec.alpha :as s]
    [com.sixsq.slipstream.ssclj.resources.credential :as p]
    [com.sixsq.slipstream.ssclj.util.spec :as su]))

(def valid-acl resource-acl)

(deftest test-credential-cloud-cloudstack-create-schema-check
  (let [root {:resourceURI        p/resource-uri
              :credentialTemplate {:key         "foo"
                                   :secret      "bar"
                                   :connector   "connector/xyz"}}]
    (is (s/valid? :cimi/credential.cloud-cloudstack.create root))
    (is (s/valid? :cimi.credential-template.cloud-cloudstack/credentialTemplate (:credentialTemplate root)))
    (doseq [k (into #{} (keys (dissoc root :resourceURI)))]
      (is (not (s/valid? :cimi/credential.cloud-cloudstack.create (dissoc root k)))))))

(deftest test-credential-cloud-cloudstack-schema-check
  (let [timestamp "1972-10-08T10:00:00.0Z"
        root      {:id          (str ct/resource-url "/uuid")
                   :resourceURI p/resource-uri
                   :created     timestamp
                   :updated     timestamp
                   :acl         valid-acl
                   :type        credential-type
                   :method      method
                   :key         "foo"
                   :secret      "bar"
                   :connector   {:href "connector/xyz"}}]
    (is (s/valid? :cimi/credential.cloud-cloudstack root))
    (doseq [k (into #{} (keys root))]
      (is (not (s/valid? :cimi/credential.cloud-cloudstack (dissoc root k)))))))
