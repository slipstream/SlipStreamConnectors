(ns com.sixsq.slipstream.ssclj.resources.spec.credential-template-cloud-stratuslabiter-test
  (:require
    [clojure.test :refer :all]
    [clojure.spec.alpha :as s]
    [com.sixsq.slipstream.ssclj.resources.credential :as p]
    [com.sixsq.slipstream.ssclj.resources.credential-template-cloud :as ctc]
    [com.sixsq.slipstream.ssclj.resources.credential-template :as ct]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template-cloud-stratuslabiter]
    [com.sixsq.slipstream.ssclj.resources.credential-template-cloud-stratuslabiter :as ctcs]))

(def valid-acl ctc/resource-acl-default)

(deftest test-credential-template-cloud-stratuslabiter-create-schema-check
  (let [root {:resourceURI        p/resource-uri
              :credentialTemplate {:key       "foo"
                                   :secret    "bar"
                                   :quota     7
                                   :connector {:href "connector/xyz"}}}]
    (is (s/valid? :cimi/credential-template.cloud-stratuslabiter-create root))
    (doseq [k (into #{} (keys (dissoc root :resourceURI)))]
      (is (not (s/valid? :cimi/credential-template.cloud-stratuslabiter-create (dissoc root k)))))))

(deftest test-credential-template-cloud-stratuslabiter-schema-check
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
    (is (s/valid? :cimi/credential-template.cloud-stratuslabiter root))
    (doseq [k (into #{} (keys root))]
      (is (not (s/valid? :cimi/credential-template.cloud-stratuslabiter (dissoc root k)))))))
