(ns com.sixsq.slipstream.connector.opennebula-template
  (:require
    [clojure.set :as set]
    [clojure.spec.alpha :as s]
    [com.sixsq.slipstream.ssclj.resources.common.utils :as u]
    [com.sixsq.slipstream.ssclj.resources.connector-template :as ctpl]
    [com.sixsq.slipstream.ssclj.resources.spec.connector-template :as ps]
    [com.sixsq.slipstream.ssclj.resources.spec.core :as cimi-core]
    [com.sixsq.slipstream.ssclj.util.config :as uc]
    [com.sixsq.slipstream.ssclj.util.spec :as su]))

(def ^:const cloud-service-type "opennebula")

(def connector-kw->pname
  {:networkPublic                     "network.public"
   :networkPrivate                    "network.private"
   :orchestratorCpuSize               "orchestrator.cpu.size"
   :orchestratorRamSize               "orchestrator.ram.size"
   :orchestratorContextualizationType "orchestrator.contextualization.type"
   :cpuRatio                          "cpu.ratio"
   })

(def connector-pname->kw (set/map-invert connector-kw->pname))

(def ref-attrs [:endpoint
                :nativeContextualization
                :updateClientURL
                :objectStoreEndpoint])

;;
;; schemas
;;

(s/def :cimi.connector-template.opennebula/networkPublic ::cimi-core/nonblank-string)
(s/def :cimi.connector-template.opennebula/networkPrivate ::cimi-core/nonblank-string)
(s/def :cimi.connector-template.opennebula/orchestratorCpuSize ::cimi-core/nonblank-string)
(s/def :cimi.connector-template.opennebula/orchestratorRamSize ::cimi-core/nonblank-string)
(s/def :cimi.connector-template.opennebula/orchestratorContextualizationType ::cimi-core/nonblank-string)
(s/def :cimi.connector-template.opennebula/cpuRatio ::cimi-core/nonblank-string)

(def keys-spec {:req-un [::ps/endpoint
                         ::ps/nativeContextualization
                         ::ps/updateClientURL

                         :cimi.connector-template.opennebula/networkPublic
                         :cimi.connector-template.opennebula/networkPrivate
                         :cimi.connector-template.opennebula/orchestratorCpuSize
                         :cimi.connector-template.opennebula/orchestratorRamSize
                         :cimi.connector-template.opennebula/cpuRatio
                         :cimi.connector-template.opennebula/orchestratorContextualizationType]
                :opt-un [::ps/objectStoreEndpoint]})

(def opt-keys-spec {:opt-un (concat (:req-un keys-spec) (:opt-un keys-spec))})

;; Defines the contents of the opennebula ConnectorTemplate resource itself.
(s/def :cimi/connector-template.opennebula
  (su/only-keys-maps ps/resource-keys-spec keys-spec))

;; Defines the contents of the opennebula template used in a create resource.
;; NOTE: The name must match the key defined by the resource, :connectorTemplate here.
(s/def :cimi.connector-template.opennebula/connectorTemplate
  (su/only-keys-maps ps/template-keys-spec opt-keys-spec))

(s/def :cimi/connector-template.opennebula-create
  (su/only-keys-maps ps/create-keys-spec
                     {:opt-un [:cimi.connector-template.opennebula/connectorTemplate]}))

(def ConnectorTemplateOpenNebulaDescription
  (merge ctpl/ConnectorTemplateDescription
         (select-keys ctpl/connector-reference-attrs-description ref-attrs)
         (uc/read-config "com/sixsq/slipstream/connector/opennebula-desc.edn")))
;;
;; resource
;;
;; defaults for the template
(def ^:const resource
  (merge (select-keys ctpl/connector-reference-attrs-defaults ref-attrs)
         {:cloudServiceType                  cloud-service-type

          :endpoint                          "http://<HOSTNAME>:2633/RPC2"
          :nativeContextualization           "linux-only"
          :updateClientURL                   "https://<IP>/downloads/opennebulaclient.tgz"

          :networkPublic                     "1"
          :networkPrivate                    "2"
          :orchestratorCpuSize               "1"
          :orchestratorRamSize               "0.5"
          :orchestratorContextualizationType "one-context"
          :cpuRatio                          "0.5"
          }))

;;
;; description
;;
(def ^:const desc ConnectorTemplateOpenNebulaDescription)

;;
;; initialization: register this connector template
;;
(defn initialize
  []
  (ctpl/register resource desc connector-pname->kw))

;;
;; multimethods for validation
;;

(def validate-fn (u/create-spec-validation-fn :cimi/connector-template.opennebula))
(defmethod ctpl/validate-subtype cloud-service-type
  [resource]
  (validate-fn resource))
