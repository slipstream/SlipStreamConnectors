(ns com.sixsq.slipstream.connector.cloudstack-template
  (:require
    [clojure.set :as set]
    [schema.core :as s]
    [com.sixsq.slipstream.ssclj.resources.common.schema :as sch]
    [com.sixsq.slipstream.ssclj.resources.common.utils :as u]
    [com.sixsq.slipstream.ssclj.resources.connector-template :as ctpl]
    [com.sixsq.slipstream.ssclj.util.config :as uc]
    ))

(def ^:const cloud-service-type "cloudstack")

(def connector-kw->pname
  {:orchestratorInstanceType "orchestrator.instance.type"
   :zone                     "zone"})

(def connector-pname->kw (set/map-invert connector-kw->pname))

;;
;; schemas
;;
(def ConnectorAttrsSchema
  (merge ctpl/ConnectorReferenceAttrs
         {:orchestratorInstanceType sch/NonBlankString      ;; "Basic"
          :zone                     sch/NonBlankString      ;; "Paris (ESX)"
          }))

(def ConnectorTemplateAttrs
  (merge ctpl/ConnectorTemplateAttrs
         ConnectorAttrsSchema))

(def ConnectorTemplateCloudstack
  (merge ctpl/ConnectorTemplate
         ConnectorTemplateAttrs))

(def ConnectorTemplateCloudstackRef
  (s/constrained
    (merge ConnectorTemplateAttrs
           {(s/optional-key :href) sch/NonBlankString})
    seq 'not-empty?))

(def ConnectorTemplateCloudstackDescription
  (merge ctpl/ConnectorTemplateDescription
         ctpl/connector-reference-attrs-description
         (uc/read-config "com/sixsq/slipstream/connector/cloudstack-desc.edn")))
;;
;; resource
;;
;; defautls for the template
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

(def validate-fn (u/create-validation-fn ConnectorTemplateCloudstack))
(defmethod ctpl/validate-subtype cloud-service-type
  [resource]
  (validate-fn resource))
