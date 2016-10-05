(ns com.sixsq.slipstream.connector.stratuslab-template
  (:require
    [clojure.set :as set]
    [schema.core :as s]
    [com.sixsq.slipstream.ssclj.resources.common.schema :as sch]
    [com.sixsq.slipstream.ssclj.resources.common.utils :as u]
    [com.sixsq.slipstream.ssclj.resources.connector-template :as ctpl]
    [com.sixsq.slipstream.ssclj.util.config :as uc]
    ))

(def ^:const cloud-service-type "stratuslab")

(def connector-kw->pname
  {:orchestratorInstanceType "orchestrator.instance.type"
   :marketplaceEndpoint      "marketplace.endpoint"
   :pdiskEndpoint            "pdisk.endpoint"
   })

(def connector-pname->kw (set/map-invert connector-kw->pname))

(def ref-attrs [:endpoint
                :updateClientURL])

;;
;; schemas
;;

(def ConnectorAttrsSchema
  (merge (select-keys ctpl/ConnectorReferenceAttrs ref-attrs)
         {:orchestratorInstanceType sch/NonBlankString      ;; "m1.small"
          :marketplaceEndpoint      sch/NonBlankString      ;; "http://192.168.41.1:8080/marketplace/"
          :pdiskEndpoint            sch/NonBlankString      ;; "154.48.152.10:8445"
          }))

(def ConnectorTemplateAttrs
  (merge ctpl/ConnectorTemplateAttrs
         ConnectorAttrsSchema))

(def ConnectorTemplateStratusLab
  (merge ctpl/ConnectorTemplate
         ConnectorTemplateAttrs))

(def ConnectorTemplateStratusLabRef
  (s/constrained
    (merge ConnectorTemplateAttrs
           {(s/optional-key :href) sch/NonBlankString})
    seq 'not-empty?))

(def ConnectorTemplateStratusLabDescription
  (merge ctpl/ConnectorTemplateDescription
         (select-keys ctpl/connector-reference-attrs-description ref-attrs)
         (uc/read-config "com/sixsq/slipstream/connector/stratuslab-desc.edn")))
;;
;; resource
;;
;; defautls for the template
(def ^:const resource
  (merge (select-keys ctpl/connector-reference-attrs-defaults ref-attrs)
         {:cloudServiceType         cloud-service-type

          :endpoint                 "<HOSTNAME>"
          :updateClientURL          "https://<IP>/downloads/stratuslabclient.tgz"

          :orchestratorInstanceType "m1.small"
          :marketplaceEndpoint      "https://marketplace.stratuslab.eu/marketplace/"
          :pdiskEndpoint            "<HOSTNAME>:8445"
          }))

;;
;; description
;;
(def ^:const desc ConnectorTemplateStratusLabDescription)

;;
;; initialization: register this connector template
;;
(defn initialize
  []
  (ctpl/register resource desc connector-pname->kw))

;;
;; multimethods for validation
;;

(def validate-fn (u/create-validation-fn ConnectorTemplateStratusLab))
(defmethod ctpl/validate-subtype cloud-service-type
  [resource]
  (validate-fn resource))
