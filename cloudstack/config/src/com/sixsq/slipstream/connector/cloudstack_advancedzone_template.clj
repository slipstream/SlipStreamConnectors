(ns com.sixsq.slipstream.connector.cloudstack-advancedzone-template
  (:require
    [clojure.set :as set]
    [clojure.spec.alpha :as s]

    [com.sixsq.slipstream.connector.cloudstack-template :as cst]
    [com.sixsq.slipstream.ssclj.resources.common.schema :as sch]
    [com.sixsq.slipstream.ssclj.resources.common.utils :as u]
    [com.sixsq.slipstream.ssclj.resources.connector-template :as ctpl]
    [com.sixsq.slipstream.ssclj.util.config :as uc]
    [com.sixsq.slipstream.ssclj.resources.spec.connector-template :as ps]
    [com.sixsq.slipstream.ssclj.util.spec :as su]))

(def ^:const cloud-service-type "cloudstackadvancedzone")

(def connector-kw->pname
  (merge cst/connector-kw->pname
         {:orchestratorNetworks "orchestrator.networks"}))

(def connector-pname->kw (set/map-invert connector-kw->pname))

;;
;; schemas
;;

(s/def :cimi.connector-template.cloudstackadvancedzone/orchestratorNetworks string?)

(def keys-spec {:req-un [:cimi.connector-template/endpoint
                         :cimi.connector-template/nativeContextualization
                         :cimi.connector-template/orchestratorSSHUsername
                         :cimi.connector-template/orchestratorSSHPassword
                         :cimi.connector-template/securityGroups
                         :cimi.connector-template/updateClientURL

                         :cimi.connector-template.cloudstackadvancedzone/orchestratorNetworks]
                :opt-un [:cimi.connector-template/objectStoreEndpoint]})

(def opt-keys-spec {:opt-un (:req-un keys-spec)})

;; Defines the contents of the cloudstackadvancedzone ConnectorTemplate resource itself.
(s/def :cimi/connector-template.cloudstackadvancedzone
  (su/only-keys-maps ps/resource-keys-spec keys-spec))

;; Defines the contents of the cloudstackadvancedzone template used in a create resource.
;; NOTE: The name must match the key defined by the resource, :connectorTemplate here.
(s/def :cimi.connector-template.cloudstackadvancedzone/connectorTemplate
  (su/only-keys-maps ps/template-keys-spec opt-keys-spec))

(s/def :cimi/connector-template.cloudstackadvancedzone-create
  (su/only-keys-maps ps/create-keys-spec
                     {:opt-un [:cimi.connector-template.cloudstackadvancedzone/connectorTemplate]}))

(def ConnectorTemplateCloudstackAdvancedZoneDescription
  (merge cst/ConnectorTemplateCloudstackDescription
         (uc/read-config "com/sixsq/slipstream/connector/cloudstack-advancedzone-desc.edn")))
;;
;; resource
;;
;; defaults for the template
(def ^:const resource
  (merge cst/resource
         {:cloudServiceType     cloud-service-type
          :orchestratorNetworks ""}))

;;
;; description
;;
(def ^:const desc ConnectorTemplateCloudstackAdvancedZoneDescription)

;;
;; initialization: register this connector template
;;
(defn initialize
  []
  (ctpl/register resource desc connector-pname->kw))

;;
;; multimethods for validation
;;

(def validate-fn (u/create-spec-validation-fn :cimi/connector-template.cloudstackadvancedzone))
(defmethod ctpl/validate-subtype cloud-service-type
  [resource]
  (validate-fn resource))
