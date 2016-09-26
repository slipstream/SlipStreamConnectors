(ns com.sixsq.slipstream.connector.openstack-template-lifecycle-test
  (:require
    [clojure.test :refer :all]
    [peridot.core :refer :all]

    [com.sixsq.slipstream.connector.lifecycle-test-utils :as ltu]
    [com.sixsq.slipstream.connector.openstack-template :as ct-openstack]
    [com.sixsq.slipstream.connector.test-utils :as tu]

    [com.sixsq.slipstream.ssclj.app.params :as p]
    [com.sixsq.slipstream.ssclj.app.routes :as routes]
    [com.sixsq.slipstream.ssclj.middleware.authn-info-header :refer [authn-info-header]]
    [com.sixsq.slipstream.ssclj.resources.common.crud :as crud]
    [com.sixsq.slipstream.ssclj.resources.common.debug-utils :as du]
    [com.sixsq.slipstream.ssclj.resources.common.dynamic-load :as dyn]
    [com.sixsq.slipstream.ssclj.resources.common.schema :as c]
    [com.sixsq.slipstream.ssclj.resources.common.utils :as u]
    [com.sixsq.slipstream.ssclj.resources.connector-template :as ct]
    ))

(use-fixtures :each ltu/with-test-client-fixture)

(def base-uri (str p/service-context (u/de-camelcase ct/resource-name)))

(defn ring-app []
  (ltu/make-ring-app (ltu/concat-routes [(routes/get-main-routes)])))

;; initialize must to called to pull in ConnectorTemplate test examples
(dyn/initialize)

(deftest test-connector-template-is-registered
  (let [id  (str ct/resource-url "/" ct-openstack/cloud-service-type)
        doc (crud/retrieve-by-id id)]
    (is (= id (:id doc)))))

(deftest lifecycle

  ;; Get all regististered connector templates.
  ;; There should be only one connector of this type.
  (let [session (session (ring-app))
        entries (-> session
                    (content-type "application/json")
                    (header authn-info-header "root ADMIN")
                    (request base-uri)
                    (ltu/body->edn)
                    (ltu/is-status 200)
                    (ltu/is-resource-uri ct/collection-uri)
                    (ltu/is-count 1)
                    (ltu/is-operation-absent "add")
                    (ltu/is-operation-absent "delete")
                    (ltu/is-operation-absent "edit")
                    (ltu/is-operation-absent "describe")
                    (ltu/entries ct/resource-tag))
        ids     (set (map :id entries))
        types   (set (map :cloudServiceType entries))]
    (is (= #{(str ct/resource-url "/" ct-openstack/cloud-service-type)} ids))
    (is (= #{ct-openstack/cloud-service-type} types))

    ;; Get connector template and work with it.
    (let [entry        (first entries)
          ops          (ltu/operations->map entry)
          href         (get ops (c/action-uri :describe))
          entry-url    (str p/service-context (:id entry))
          describe-url (str p/service-context href)

          entry-resp   (-> session
                           (content-type "application/json")
                           (header authn-info-header "root ADMIN")
                           (request entry-url)
                           (ltu/is-status 200)
                           (ltu/body->edn))

          entry-body   (get-in entry-resp [:response :body])

          desc         (-> session
                           (content-type "application/json")
                           (header authn-info-header "root ADMIN")
                           (request describe-url)
                           (ltu/body->edn)
                           (ltu/is-status 200))
          desc-body    (get-in desc [:response :body])]
      (is (nil? (get ops (c/action-uri :add))))
      (is (nil? (get ops (c/action-uri :edit))))
      (is (nil? (get ops (c/action-uri :delete))))
      (is (:cloudServiceType desc-body))
      (is (:acl desc-body))

      (is (thrown-with-msg? clojure.lang.ExceptionInfo #".*resource does not satisfy defined schema.*" (crud/validate entry-body)))
      (is (crud/validate (assoc entry-body :instanceName (tu/new-instance-name))))
      )))


