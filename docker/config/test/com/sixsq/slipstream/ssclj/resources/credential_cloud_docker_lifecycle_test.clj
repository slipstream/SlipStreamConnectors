(ns com.sixsq.slipstream.ssclj.resources.credential-cloud-docker-lifecycle-test
  (:require
    [clojure.data.json :as json]
    [clojure.string :as str]
    [clojure.test :refer [are deftest is use-fixtures]]
    [com.sixsq.slipstream.connector.docker-template :as dt]
    [com.sixsq.slipstream.ssclj.app.params :as p]
    [com.sixsq.slipstream.ssclj.middleware.authn-info-header :refer [authn-info-header]]
    [com.sixsq.slipstream.ssclj.resources.common.utils :as u]
    [com.sixsq.slipstream.ssclj.resources.connector :as con]
    [com.sixsq.slipstream.ssclj.resources.connector-template :as cont]
    [com.sixsq.slipstream.ssclj.resources.credential-cloud-lifecycle-test-utils :as cclt]
    [com.sixsq.slipstream.ssclj.resources.credential-template :as ct]
    [com.sixsq.slipstream.ssclj.resources.credential-template-cloud-docker :as cloud-docker]
    [com.sixsq.slipstream.ssclj.resources.lifecycle-test-utils :as ltu]
    [peridot.core :refer :all]))

(use-fixtures :each ltu/with-test-server-fixture)

(defn create-connector-instance
  [cloud-service-type instanceName]
  (let [connector-create-uri (str p/service-context con/resource-url)
        href (str cont/resource-url "/" cloud-service-type)
        href-create (cclt/get-connector-template cloud-service-type instanceName)]
    (-> (session (ltu/ring-app))
        (content-type "application/json")
        (header authn-info-header "internal ADMIN")
        (request connector-create-uri
                 :request-method :post
                 :body (json/write-str href-create))
        (ltu/body->edn)
        (ltu/is-status 201)
        (ltu/location))))


(defn cloud-cred-lifecycle
  [{cloud-method-href :href :as credential-template-data} cloud-service-type]

  (let [conn-id (create-connector-instance cloud-service-type "foo-bar-baz")
        session (-> (ltu/ring-app)
                    session
                    (content-type "application/json"))
        session-admin (header session authn-info-header "root ADMIN USER ANON")
        session-user (header session authn-info-header "jane USER ANON")
        session-anon (header session authn-info-header "unknown ANON")
        name-attr "name"
        description-attr "description"
        properties-attr {:a "one", :b "two"}
        template-url (str p/service-context cloud-method-href)
        template (-> session-admin
                     (request template-url)
                     (ltu/body->edn)
                     (ltu/is-status 200)
                     (get-in [:response :body]))
        create-import-no-href {:credentialTemplate (ltu/strip-unwanted-attrs template)}
        create-import-href {:name               name-attr
                            :description        description-attr
                            :properties         properties-attr
                            :credentialTemplate (assoc credential-template-data :connector {:href conn-id})}]

    ;; admin/user query should succeed but be empty (no credentials created yet)
    (doseq [session [session-admin session-user]]
      (-> session
          (request cclt/base-uri)
          (ltu/body->edn)
          (ltu/is-status 200)
          (ltu/is-count zero?)
          (ltu/is-operation-present "add")
          (ltu/is-operation-absent "delete")
          (ltu/is-operation-absent "edit")))

    ;; anonymous credential collection query should not succeed
    (-> session-anon
        (request cclt/base-uri)
        (ltu/body->edn)
        (ltu/is-status 403))

    ;; creating a new credential without reference will fail for all types of users
    (doseq [session [session-admin session-user session-anon]]
      (-> session
          (request cclt/base-uri
                   :request-method :post
                   :body (json/write-str create-import-no-href))
          (ltu/body->edn)
          (ltu/is-status 400)))

    ;; creating a new credential as anon will fail
    (-> session-anon
        (request cclt/base-uri
                 :request-method :post
                 :body (json/write-str create-import-href))
        (ltu/body->edn)
        (ltu/is-status 400))

    ;; create a credential as a normal user
    (let [resp (-> session-user
                   (request cclt/base-uri
                            :request-method :post
                            :body (json/write-str create-import-href))
                   (ltu/body->edn)
                   (ltu/is-status 201))
          _ (ltu/refresh-es-indices)
          id (get-in resp [:response :body :resource-id])
          uri (-> resp
                  (ltu/location))
          abs-uri (str p/service-context (u/de-camelcase uri))]

      ;; resource id and the uri (location) should be the same
      (is (= id uri))

      ;; admin/user should be able to see and delete credential
      (doseq [session [session-admin session-user]]
        (-> session
            (request abs-uri)
            (ltu/body->edn)
            (ltu/is-status 200)
            (ltu/is-operation-present "delete")
            (ltu/is-operation-present "edit")))

      ;; ensure credential contains correct information
      (let [{:keys [name description
                    properties key secret]} (-> session-user
                                                (request abs-uri)
                                                (ltu/body->edn)
                                                (ltu/is-status 200)
                                                :response
                                                :body)]
        (is (= name name-attr))
        (is (= description description-attr))
        (is (= properties properties-attr))
        (is (= (get-in create-import-href [:credentialTemplate :key]) key))
        (is (= (get-in create-import-href [:credentialTemplate :secret]) secret))

        ;; delete the credential
        (-> session-user
            (request abs-uri
                     :request-method :delete)
            (ltu/body->edn)
            (ltu/is-status 200))))

    ;; Check that manual update cycle (search / merge / create new / delete old) works.
    (let [secret {:secret (str "new" (:secret credential-template-data))}

          ;; CREATION
          ;; create initial cred
          id (-> (cclt/cred-create session-user create-import-href)
                 (ltu/location))

          conn-id (-> session-user
                      (request (str p/service-context id))
                      (ltu/body->edn)
                      (get-in [:response :body :connector :href])
                      (str/split #"/")
                      (second))

          ;; another one as different user
          id-admin (-> (cclt/cred-create session-admin create-import-href)
                       (ltu/location))

          _ (ltu/refresh-es-indices)

          ;; UPDATE OPERATION
          ;; search and get - only one is expected
          old-doc (-> (cclt/cred-find session-user conn-id)
                      (ltu/is-count 1)
                      cclt/cred-take-first)
          id-old (:id old-doc)
          ;; merge
          new-doc (-> (ltu/strip-unwanted-attrs old-doc)
                      (merge secret)
                      (assoc :href cloud-method-href))]

      ;; create new
      (-> (cclt/cred-create session-user {:credentialTemplate new-doc})
          (ltu/location))

      (ltu/refresh-es-indices)

      ;; VERIFY: check that both the old and new credentials are visible
      (-> (cclt/cred-find session-user conn-id)
          (ltu/is-count 2))

      ;; DELETE: remove the old, original credential
      (-> session-user
          (request (str p/service-context id-old)
                   :request-method :delete)
          (ltu/body->edn)
          (ltu/is-status 200))

      (ltu/refresh-es-indices)

      ;; VALIDATION
      (let [new-doc (-> (cclt/cred-find session-user conn-id)
                        (ltu/is-count 1)
                        cclt/cred-take-first)
            id-new (:id new-doc)]

        (is (= (:secret secret) (:secret new-doc)))

        ;; CLEAN UP: remove the generated credentials
        (-> session-user
            (request (str p/service-context id-new)
                     :request-method :delete)
            (ltu/body->edn)
            (ltu/is-status 200))

        (-> session-admin
            (request (str p/service-context id-admin)
                     :request-method :delete)
            (ltu/body->edn)
            (ltu/is-status 200))))

    ;; Check that direct editing works as expected.
    (let [new-secret (str "new-" (:secret credential-template-data))

          ;; CREATION: create initial credential and get identifier
          id (-> (cclt/cred-create session-user create-import-href)
                 (ltu/location))

          conn-id (-> session-user
                      (request (str p/service-context id))
                      (ltu/body->edn)
                      (get-in [:response :body :connector :href])
                      (str/split #"/")
                      (second))]

      (ltu/refresh-es-indices)

      ;; VERIFY CREATION: ensure that document is visible and has the correct ID
      (let [old-doc (-> (cclt/cred-find session-user conn-id)
                        (ltu/is-count 1)
                        cclt/cred-take-first)
            check-id (:id old-doc)]

        (is (= check-id id))

        ;; EDIT: change the secret in the credential
        (cclt/cred-edit session-user (assoc old-doc :secret new-secret)))

      (ltu/refresh-es-indices)

      ;; VERIFY EDIT: one credential should be visible and secret should have been changed
      (let [new-doc (-> (cclt/cred-find session-user conn-id)
                        (ltu/is-count 1)
                        cclt/cred-take-first)
            id-new (:id new-doc)]

        (is (= id id-new))
        (is (= new-secret (:secret new-doc))))

      ;; DELETE: remove the created credential
      (-> session-user
          (request (str p/service-context id)
                   :request-method :delete)
          (ltu/body->edn)
          (ltu/is-status 200))

      (ltu/refresh-es-indices))))


(deftest lifecycle
  (cloud-cred-lifecycle {:href   (str ct/resource-url "/" cloud-docker/method)
                         :key    "key"
                         :secret "secret"
                         :quota  7
                         ;;no docker connector provided yet
                         }
                        dt/cloud-service-type))




