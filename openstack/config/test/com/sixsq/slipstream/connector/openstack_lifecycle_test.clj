(ns com.sixsq.slipstream.connector.openstack-lifecycle-test
  (:require
    [clojure.test :refer :all]
    [clojure.data.json :as json]
    [peridot.core :refer :all]

    [com.sixsq.slipstream.connector.lifecycle-test-utils :as ltu]
    [com.sixsq.slipstream.connector.openstack-template :as ct-openstack]
    [com.sixsq.slipstream.connector.test-utils :as tu]

    [com.sixsq.slipstream.ssclj.app.params :as p]
    [com.sixsq.slipstream.ssclj.app.routes :as routes]
    [com.sixsq.slipstream.ssclj.middleware.authn-info-header :refer [authn-info-header]]
    [com.sixsq.slipstream.ssclj.resources.common.debug-utils :as du]
    [com.sixsq.slipstream.ssclj.resources.common.dynamic-load :as dyn]
    [com.sixsq.slipstream.ssclj.resources.common.utils :as u]
    [com.sixsq.slipstream.ssclj.resources.connector :refer :all]
    [com.sixsq.slipstream.ssclj.resources.connector-template :as ct]))

(use-fixtures :each ltu/with-test-client-fixture)

(def base-uri (str p/service-context (u/de-camelcase resource-name)))

(defn ring-app []
  (ltu/make-ring-app (ltu/concat-routes [(routes/get-main-routes)])))

;; initialize must to called to pull in ConnectorTemplate test examples
(dyn/initialize)

(defn strip-unwanted-attrs [m]
  (let [unwanted #{:id :resourceURI :acl :operations
                   :created :updated :name :description}]
    (into {} (remove #(unwanted (first %)) m))))

(deftest lifecycle

  (let [href           (str ct/resource-url "/" ct-openstack/cloud-service-type)
        template-url   (str p/service-context ct/resource-url "/" ct-openstack/cloud-service-type)
        resp           (-> (session (ring-app))
                           (content-type "application/json")
                           (header authn-info-header "root ADMIN")
                           (request template-url)
                           (ltu/body->edn)
                           (ltu/is-status 200))
        template       (get-in resp [:response :body])
        valid-create   {:connectorTemplate (-> template
                                               strip-unwanted-attrs
                                               (assoc :endpoint "http://example.com")
                                               (assoc :instanceName (tu/new-instance-name)))}
        href-create    {:connectorTemplate {:href         href
                                            :endpoint     "http://google.com"
                                            :instanceName (tu/new-instance-name)}}
        invalid-create (assoc-in valid-create [:connectorTemplate :invalid] "BAD")]

    ;; admin create with invalid template fails
    (-> (session (ring-app))
        (content-type "application/json")
        (header authn-info-header "root ADMIN")
        (request base-uri
                 :request-method :post
                 :body (json/write-str invalid-create))
        (ltu/body->edn)
        (ltu/is-status 400))

    ;; full connector lifecycle as administrator should work
    (let [uri     (-> (session (ring-app))
                      (content-type "application/json")
                      (header authn-info-header "root ADMIN")
                      (request base-uri
                               :request-method :post
                               :body (json/write-str valid-create))
                      (ltu/body->edn)
                      (ltu/is-status 201)
                      (ltu/location))
          abs-uri (str p/service-context (u/de-camelcase uri))]


      ;; create again with the same connector instance name should fail with 409
      (-> (session (ring-app))
          (content-type "application/json")
          (header authn-info-header "root ADMIN")
          (request base-uri
                   :request-method :post
                   :body (json/write-str (assoc valid-create :instanceName uri)))
          (ltu/body->edn)
          (ltu/is-status 400))

      ;; admin get succeeds
      (-> (session (ring-app))
          (header authn-info-header "root ADMIN")
          (request abs-uri)
          (ltu/body->edn)
          (ltu/is-status 200))

      ;; anonymous query fails
      (-> (session (ring-app))
          (request base-uri)
          (ltu/body->edn)
          (ltu/is-status 403))

      ;; admin query succeeds
      (let [entries (-> (session (ring-app))
                        (content-type "application/json")
                        (header authn-info-header "root ADMIN")
                        (request base-uri)
                        (ltu/body->edn)
                        (ltu/is-status 200)
                        (ltu/is-resource-uri collection-uri)
                        (ltu/is-count #(= 1 %))
                        (ltu/entries resource-tag))]
        (is ((set (map :id entries)) uri))

        ;; verify that all entries are accessible
        (let [pair-fn (juxt :id #(str p/service-context (:id %)))
              pairs   (map pair-fn entries)]
          (doseq [[id entry-uri] pairs]
            (-> (session (ring-app))
                (header authn-info-header "root ADMIN")
                (request entry-uri)
                (ltu/body->edn)
                (ltu/is-status 200)
                (ltu/is-id id)))))

      ;; admin delete succeeds
      (-> (session (ring-app))
          (header authn-info-header "root ADMIN")
          (request abs-uri
                   :request-method :delete)
          (ltu/body->edn)
          (ltu/is-status 200))

      ;; ensure entry is really gone
      (-> (session (ring-app))
          (header authn-info-header "root ADMIN")
          (request abs-uri)
          (ltu/body->edn)
          (ltu/is-status 404)))

    ;; abbreviated lifecycle using href to template instead of copy
    (let [uri     (-> (session (ring-app))
                      (content-type "application/json")
                      (header authn-info-header "root ADMIN")
                      (request base-uri
                               :request-method :post
                               :body (json/write-str href-create))
                      (ltu/body->edn)
                      (ltu/is-status 201)
                      (ltu/location))
          abs-uri (str p/service-context (u/de-camelcase uri))]

      ;; admin delete succeeds
      (-> (session (ring-app))
          (header authn-info-header "root ADMIN")
          (request abs-uri
                   :request-method :delete)
          (ltu/body->edn)
          (ltu/is-status 200))

      ;; ensure entry is really gone
      (-> (session (ring-app))
          (header authn-info-header "root ADMIN")
          (request abs-uri)
          (ltu/body->edn)
          (ltu/is-status 404)))))

