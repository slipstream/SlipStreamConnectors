(ns com.sixsq.slipstream.ssclj.resources.spec.credential-cloud-cloudstack-test
  (:require
    [clojure.test :refer [deftest]]
    [com.sixsq.slipstream.ssclj.resources.credential :as p]
    [com.sixsq.slipstream.ssclj.resources.credential-template :as ct]
    [com.sixsq.slipstream.ssclj.resources.credential-template-cloud-cloudstack :refer [credential-type method resource-acl]]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-cloud-cloudstack :as cloudstack]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template-cloud-cloudstack :as cloudstack-tpl]
    [com.sixsq.slipstream.ssclj.resources.spec.spec-test-utils :as stu]))


(def valid-acl resource-acl)


(deftest test-credential-cloud-cloudstack-create-schema-check
  (let [root {:resourceURI        p/resource-uri
              :credentialTemplate {:key                "foo"
                                   :secret             "bar"
                                   :quota              20
                                   :connector          {:href "connector/xyz"}
                                   :disabledMonitoring false}}]

    (stu/is-valid ::cloudstack/credential-create root)
    (stu/is-valid ::cloudstack-tpl/credentialTemplate (:credentialTemplate root))
    (doseq [k (keys (dissoc root :resourceURI))]
      (stu/is-invalid ::cloudstack/credential-create (dissoc root k)))))


(deftest test-credential-cloud-cloudstack-schema-check
  (let [timestamp "1972-10-08T10:00:00.0Z"
        root {:id                 (str ct/resource-url "/uuid")
              :resourceURI        p/resource-uri
              :created            timestamp
              :updated            timestamp
              :acl                valid-acl
              :type               credential-type
              :method             method
              :key                "foo"
              :secret             "bar"
              :quota              20
              :connector          {:href "connector/xyz"}
              :disabledMonitoring false}]

    (stu/is-valid ::cloudstack/credential root)
    (doseq [k (keys (dissoc root :disabledMonitoring))]
      (stu/is-invalid ::cloudstack/credential (dissoc root k)))
    (doseq [k [:disabledMonitoring]]
      (stu/is-valid ::cloudstack/credential (dissoc root k)))))
