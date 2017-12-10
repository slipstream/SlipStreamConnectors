(ns com.sixsq.slipstream.ssclj.resources.spec.credential-cloud-stratuslab-test
  (:require
    [clojure.test :refer :all]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-cloud-stratuslab]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template-cloud-stratuslab]
    [com.sixsq.slipstream.ssclj.resources.credential-template-cloud :as ctc]
    [com.sixsq.slipstream.ssclj.resources.credential-template :as ct]
    [com.sixsq.slipstream.ssclj.resources.credential-template-cloud-stratuslab :as ctcs]
    [com.sixsq.slipstream.ssclj.resources.credential-template :as ct]
    [clojure.spec.alpha :as s]
    [com.sixsq.slipstream.ssclj.resources.credential :as p]))

(def valid-acl ctc/resource-acl-default)

(deftest test-credential-cloud-stratuslab-create-schema-check
  (let [root {:resourceURI        p/resource-uri
              :credentialTemplate {:key       "foo"
                                   :secret    "bar"
                                   :quota     7
                                   :connector {:href "connector/xyz"}}}]
    (is (s/valid? :cimi/credential.cloud-stratuslab.create root))
    (is (s/valid? :cimi.credential-template.cloud-stratuslab/credentialTemplate (:credentialTemplate root)))
    (doseq [k (into #{} (keys (dissoc root :resourceURI)))]
      (is (not (s/valid? :cimi/credential.cloud-stratuslab.create (dissoc root k)))))))

(deftest test-credential-cloud-stratuslab-schema-check
  (let [timestamp "1972-10-08T10:00:00.0Z"
        root      {:id          (str ct/resource-url "/uuid")
                   :resourceURI p/resource-uri
                   :created     timestamp
                   :updated     timestamp
                   :acl         valid-acl
                   :type        ctcs/credential-type
                   :method      ctcs/method
                   :key         "foo"
                   :secret      "bar"
                   :quota       7
                   :connector   {:href "connector/xyz"}}]
    (is (s/valid? :cimi/credential.cloud-stratuslab root))
    (doseq [k (into #{} (keys root))]
      (is (not (s/valid? :cimi/credential.cloud-stratuslab (dissoc root k)))))))


