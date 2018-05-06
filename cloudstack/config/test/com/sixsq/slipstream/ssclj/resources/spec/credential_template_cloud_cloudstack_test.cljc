(ns com.sixsq.slipstream.ssclj.resources.spec.credential-template-cloud-cloudstack-test
  (:require
    [clojure.spec.alpha :as s]
    [clojure.test :refer :all]
    [com.sixsq.slipstream.ssclj.resources.credential :as p]
    [com.sixsq.slipstream.ssclj.resources.credential-template :as ct]
    [com.sixsq.slipstream.ssclj.resources.credential-template-cloud-cloudstack
     :refer [credential-type method resource-acl]]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template-cloud-cloudstack]))

(def valid-acl resource-acl)

(deftest test-credential-template-cloud-cloudstack-create-schema-check
  (let [root {:resourceURI        p/resource-uri
              :credentialTemplate {:key       "foo"
                                   :secret    "bar"
                                   :quota     20
                                   :connector {:href "connector/xyz"}}}]
    (is (s/valid? :cimi/credential-template.cloud-cloudstack-create root))
    (doseq [k (into #{} (keys (dissoc root :resourceURI)))]
      (is (not (s/valid? :cimi/credential-template.cloud-cloudstack-create (dissoc root k)))))))

(deftest test-credential-template-cloud-cloudstack-schema-check
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
                   :quota       20
                   :connector   {:href "connector/xyz"}}]
    (is (s/valid? :cimi/credential-template.cloud-cloudstack root))
    (doseq [k (into #{} (keys root))]
      (is (not (s/valid? :cimi/credential-template.cloud-cloudstack (dissoc root k)))))))