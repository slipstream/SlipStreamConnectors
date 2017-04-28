(ns com.sixsq.slipstream.connector.stratuslab-template
  (:require
    [clojure.set :as set]
    [clojure.spec.alpha :as s]
    [com.sixsq.slipstream.ssclj.resources.common.schema :as sch]
    [com.sixsq.slipstream.ssclj.resources.common.utils :as u]
    [com.sixsq.slipstream.ssclj.resources.connector-template :as ctpl]
    [com.sixsq.slipstream.ssclj.util.config :as uc]
    [com.sixsq.slipstream.ssclj.resources.spec.connector-template :as ps]
    [com.sixsq.slipstream.ssclj.util.spec :as su]))

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

(s/def :cimi.connector-template.stratuslab/orchestratorInstanceType :cimi.core/nonblank-string)
(s/def :cimi.connector-template.stratuslab/marketplaceEndpoint :cimi.core/nonblank-string)
(s/def :cimi.connector-template.stratuslab/pdiskEndpoint :cimi.core/nonblank-string)

(def keys-spec {:req-un [:cimi.connector-template/endpoint
                         :cimi.connector-template/updateClientURL
                         :cimi.connector-template.stratuslab/orchestratorInstanceType
                         :cimi.connector-template.stratuslab/marketplaceEndpoint
                         :cimi.connector-template.stratuslab/pdiskEndpoint]})

(def opt-keys-spec {:opt-un (:req-un keys-spec)})

;; Defines the contents of the stratuslab ConnectorTemplate resource itself.
(s/def :cimi/connector-template.stratuslab
  (su/only-keys-maps ps/resource-keys-spec keys-spec))

;; Defines the contents of the stratuslab template used in a create resource.
;; NOTE: The name must match the key defined by the resource, :connectorTemplate here.
(s/def :cimi.connector-template.stratuslab/connectorTemplate
  (su/only-keys-maps ps/template-keys-spec opt-keys-spec))

(s/def :cimi/connector-template.stratuslab-create
  (su/only-keys-maps ps/create-keys-spec
                     {:opt-un [:cimi.connector-template.stratuslab/connectorTemplate]}))

(def ConnectorTemplateStratusLabDescription
  (merge ctpl/ConnectorTemplateDescription
         (select-keys ctpl/connector-reference-attrs-description ref-attrs)
         (uc/read-config "com/sixsq/slipstream/connector/stratuslab-desc.edn")))
;;
;; resource
;;
;; defaults for the template
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

(def validate-fn (u/create-spec-validation-fn :cimi/connector-template.stratuslab))
(defmethod ctpl/validate-subtype cloud-service-type
  [resource]
  (validate-fn resource))
