(ns com.sixsq.slipstream.connector.opennebula-template
  (:require
    [clojure.set :as set]
    [schema.core :as s]
    [com.sixsq.slipstream.ssclj.resources.common.schema :as sch]
    [com.sixsq.slipstream.ssclj.resources.common.utils :as u]
    [com.sixsq.slipstream.ssclj.resources.connector-template :as ctpl]
    [com.sixsq.slipstream.ssclj.util.config :as uc]
    ))

(def ^:const cloud-service-type "opennebula")

(def connector-kw->pname
  {:networkPublic       "network.public"
   :networkPrivate      "network.private"
   :orchestratorCpuSize "orchestrator.cpu.size"
   :orchestratorRamSize "orchestrator.ram.size"
   })

(def connector-pname->kw (set/map-invert connector-kw->pname))

(def ref-attrs [:endpoint
                :nativeContextualization
                :updateClientURL])

;;
;; schemas
;;

(def ConnectorAttrsSchema
  (merge (select-keys ctpl/ConnectorReferenceAttrs ref-attrs)
         {:networkPublic       sch/NonBlankString           ;; "1"
          :networkPrivate      sch/NonBlankString           ;; "2"
          :orchestratorCpuSize sch/NonBlankString           ;; "1"
          :orchestratorRamSize sch/NonBlankString           ;; "0.5"
          }))

(def ConnectorTemplateAttrs
  (merge ctpl/ConnectorTemplateAttrs
         ConnectorAttrsSchema))

(def ConnectorTemplateOpenNebula
  (merge ctpl/ConnectorTemplate
         ConnectorTemplateAttrs))

(def ConnectorTemplateOpenNebulaRef
  (s/constrained
    (merge ConnectorTemplateAttrs
           {(s/optional-key :href) sch/NonBlankString})
    seq 'not-empty?))

(def ConnectorTemplateOpenNebulaDescription
  (merge ctpl/ConnectorTemplateDescription
         (select-keys ctpl/connector-reference-attrs-description ref-attrs)
         (uc/read-config "com/sixsq/slipstream/connector/opennebula-desc.edn")))
;;
;; resource
;;
;; defautls for the template
(def ^:const resource
  (merge (select-keys ctpl/connector-reference-attrs-defaults ref-attrs)
         {:cloudServiceType        cloud-service-type

          :endpoint                "http://<HOSTNAME>:2633/RPC2"
          :nativeContextualization "linux-only"
          :updateClientURL         "https://<IP>/downloads/opennebulaclient.tgz"

          :networkPublic           "1"
          :networkPrivate          "2"
          :orchestratorCpuSize     "1"
          :orchestratorRamSize     "0.5"
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

(def validate-fn (u/create-validation-fn ConnectorTemplateOpenNebula))
(defmethod ctpl/validate-subtype cloud-service-type
  [resource]
  (validate-fn resource))
