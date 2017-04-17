(ns com.sixsq.slipstream.connector.cloudstack-template
  (:require
    [clojure.set :as set]
    [clojure.spec :as s]
    [com.sixsq.slipstream.ssclj.resources.spec.common]
    [com.sixsq.slipstream.ssclj.resources.common.schema :as sch]
    [com.sixsq.slipstream.ssclj.resources.common.utils :as u]
    [com.sixsq.slipstream.ssclj.resources.connector-template :as ctpl]
    [com.sixsq.slipstream.ssclj.util.config :as uc]
    [com.sixsq.slipstream.ssclj.resources.spec.connector-template :as ps]
    [com.sixsq.slipstream.ssclj.util.spec :as su]))

(def ^:const cloud-service-type "cloudstack")

(def connector-kw->pname
  {:orchestratorInstanceType "orchestrator.instance.type"
   :zone                     "zone"})

(def connector-pname->kw (set/map-invert connector-kw->pname))

;;
;; schemas
;;

(s/def :cimi.connector-template.cloudstack/orchestratorInstanceType :cimi.core/nonblank-string)
(s/def :cimi.connector-template.cloudstack/zone :cimi.core/nonblank-string)

(def keys-spec {:req-un [:cimi.connector-template/endpoint
                         :cimi.connector-template/nativeContextualization
                         :cimi.connector-template/orchestratorSSHUsername
                         :cimi.connector-template/orchestratorSSHPassword
                         :cimi.connector-template/securityGroups
                         :cimi.connector-template/updateClientURL

                         :cimi.connector-template.cloudstack/orchestratorInstanceType
                         :cimi.connector-template.cloudstack/zone]})

(def opt-keys-spec {:opt-un (:req-un keys-spec)})

;; Defines the contents of the cloudstack ConnectorTemplate resource itself.
(s/def :cimi/connector-template.cloudstack
  (su/only-keys-maps ps/resource-keys-spec keys-spec))

;; Defines the contents of the cloudstack template used in a create resource.
;; NOTE: The name must match the key defined by the resource, :connectorTemplate here.
(s/def :cimi.connector-template.cloudstack/connectorTemplate
  (su/only-keys-maps ps/template-keys-spec opt-keys-spec))

(s/def :cimi/connector-template.cloudstack-create
  (su/only-keys-maps ps/create-keys-spec
                     {:opt-un [:cimi.connector-template.cloudstack/connectorTemplate]}))

(def ConnectorTemplateCloudstackDescription
  (merge ctpl/ConnectorTemplateDescription
         ctpl/connector-reference-attrs-description
         (uc/read-config "com/sixsq/slipstream/connector/cloudstack-desc.edn")))
;;
;; resource
;;
;; defaults for the template
(def ^:const resource
  (merge ctpl/connector-reference-attrs-defaults
         {:cloudServiceType         cloud-service-type

          :orchestratorInstanceType "512-1"
          :zone                     "Paris (ESX)"}))

;;
;; description
;;
(def ^:const desc ConnectorTemplateCloudstackDescription)

;;
;; initialization: register this connector template
;;
(defn initialize
  []
  (ctpl/register resource desc connector-pname->kw))

;;
;; multimethods for validation
;;

(def validate-fn (u/create-spec-validation-fn :cimi/connector-template.cloudstack))
(defmethod ctpl/validate-subtype cloud-service-type
  [resource]
  (validate-fn resource))
