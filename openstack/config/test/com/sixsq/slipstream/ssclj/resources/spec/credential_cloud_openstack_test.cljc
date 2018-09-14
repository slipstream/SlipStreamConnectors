(ns com.sixsq.slipstream.ssclj.resources.spec.credential-cloud-openstack-test
  (:require
    [clojure.test :refer [deftest is]]
    [com.sixsq.slipstream.ssclj.resources.credential :as p]
    [com.sixsq.slipstream.ssclj.resources.credential-template :as ct]
    [com.sixsq.slipstream.ssclj.resources.credential-template-cloud :as ctc]
    [com.sixsq.slipstream.ssclj.resources.credential-template-cloud-openstack :as ctco]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-cloud-openstack :as openstack]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template-cloud-openstack :as openstack-tpl]
    [com.sixsq.slipstream.ssclj.resources.spec.spec-test-utils :as stu]))


(def valid-acl ctc/resource-acl-default)


(deftest test-credential-cloud-openstack-create-schema-check
  (let [root {:resourceURI        p/resource-uri
              :credentialTemplate {:key                "foo"
                                   :secret             "bar"
                                   :connector          {:href "connector/xyz"}
                                   :quota              7
                                   :tenant-name        "tenant"
                                   :domain-name        "domain"
                                   :disabledMonitoring false}}]

    (stu/is-valid ::openstack/credential-create root)
    (stu/is-valid ::openstack-tpl/credentialTemplate (:credentialTemplate root))
    (doseq [k (keys (dissoc root :resourceURI))]
      (stu/is-invalid ::openstack/credential-create (dissoc root k)))))


(deftest test-credential-cloud-openstack-schema-check
  (let [timestamp "1972-10-08T10:00:00.0Z"
        root {:id                 (str ct/resource-url "/uuid")
              :resourceURI        p/resource-uri
              :created            timestamp
              :updated            timestamp
              :acl                valid-acl
              :type               ctco/credential-type
              :method             ctco/method
              :key                "foo"
              :secret             "bar"
              :connector          {:href "connector/xyz"}
              :quota              8
              :disabledMonitoring false}]

    (stu/is-valid ::openstack/credential root)
    (doseq [k (keys (dissoc root :disabledMonitoring))]
      (stu/is-invalid ::openstack/credential (dissoc root k)))
    (doseq [k [:disabledMonitoring]]
      (stu/is-valid ::openstack/credential (dissoc root k)))))


