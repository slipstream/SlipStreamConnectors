(ns com.sixsq.slipstream.ssclj.resources.spec.credential-template-cloud-openstack-test
  (:require
    [clojure.test :refer [deftest is]]
    [com.sixsq.slipstream.ssclj.resources.credential :as p]
    [com.sixsq.slipstream.ssclj.resources.credential-template :as ct]
    [com.sixsq.slipstream.ssclj.resources.credential-template-cloud :as ctc]
    [com.sixsq.slipstream.ssclj.resources.credential-template-cloud :as ctc]
    [com.sixsq.slipstream.ssclj.resources.credential-template-cloud-openstack :as ctco]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template-cloud-openstack :as openstack-tpl]
    [com.sixsq.slipstream.ssclj.resources.spec.spec-test-utils :as stu]))


(def valid-acl ctc/resource-acl-default)


(deftest test-credential-template-cloud-openstack-create-schema-check
  (let [root {:resourceURI        p/resource-uri
              :credentialTemplate {:key                "foo"
                                   :secret             "bar"
                                   :connector          {:href "connector/xyz"}
                                   :quota              7
                                   :tenant-name        "tenant"
                                   :domain-name        "domain"
                                   :disabledMonitoring false}}]

    (stu/is-valid ::openstack-tpl/credential-template-create root)
    (doseq [k (keys (dissoc root :resourceURI))]
      (stu/is-invalid ::openstack-tpl/credential-template-create (dissoc root k)))))


(deftest test-credential-template-cloud-openstack-schema-check
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
              :quota              7
              :connector          {:href "connector/xyz"}
              :disabledMonitoring false}]

    (stu/is-valid ::openstack-tpl/credential-template root)
    (doseq [k (keys (dissoc root :disabledMonitoring))]
      (stu/is-invalid ::openstack-tpl/credential-template (dissoc root k)))
    (doseq [k [:disabledMonitoring]]
      (stu/is-valid ::openstack-tpl/credential-template (dissoc root k)))))
