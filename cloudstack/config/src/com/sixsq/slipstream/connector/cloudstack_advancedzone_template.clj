(ns com.sixsq.slipstream.connector.cloudstack-advancedzone-template
  (:require
    [clojure.set :as set]
    [schema.core :as s]

    [com.sixsq.slipstream.connector.cloudstack-template :as cst]
    [com.sixsq.slipstream.ssclj.resources.common.schema :as sch]
    [com.sixsq.slipstream.ssclj.resources.common.utils :as u]
    [com.sixsq.slipstream.ssclj.resources.connector-template :as ctpl]
    [com.sixsq.slipstream.ssclj.util.config :as uc]
    ))

(def ^:const cloud-service-type "cloudstackadvancedzone")

(def connector-kw->pname
  (merge cst/connector-kw->pname
         {:orchestratorNetworks "orchestrator.networks"}))

(def connector-pname->kw (set/map-invert connector-kw->pname))

;;
;; schemas
;;
(def ConnectorAttrsSchema
  (merge cst/ConnectorAttrsSchema
         {:orchestratorNetworks s/Str                       ;; "n1,n2" or ""
          }))

(def ConnectorTemplateAttrs
  (merge ctpl/ConnectorTemplateAttrs
         ConnectorAttrsSchema))

(def ConnectorTemplateCloudstackAdvancedZone
  (merge ctpl/ConnectorTemplate
         ConnectorTemplateAttrs))

(def ConnectorTemplateCloudstackAdvancedZoneRef
  (s/constrained
    (merge ConnectorTemplateAttrs
           {(s/optional-key :href) sch/NonBlankString})
    seq 'not-empty?))

(def ConnectorTemplateCloudstackAdvancedZoneDescription
  (merge cst/ConnectorTemplateCloudstackDescription
         (uc/read-config "com/sixsq/slipstream/connector/cloudstack-advancedzone-desc.edn")))
;;
;; resource
;;
;; defautls for the template
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

(def validate-fn (u/create-validation-fn ConnectorTemplateCloudstackAdvancedZone))
(defmethod ctpl/validate-subtype cloud-service-type
  [resource]
  (validate-fn resource))
