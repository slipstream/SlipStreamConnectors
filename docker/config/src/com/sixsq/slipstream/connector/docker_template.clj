(ns com.sixsq.slipstream.connector.docker-template
    (:require
    [clojure.set :as set]
    [clojure.spec.alpha :as s]
    [com.sixsq.slipstream.ssclj.resources.common.utils :as u]
    [com.sixsq.slipstream.ssclj.resources.connector-template :as ctpl]
    [com.sixsq.slipstream.ssclj.resources.spec.connector-template :as ps]
    [com.sixsq.slipstream.ssclj.util.config :as uc]
    [com.sixsq.slipstream.ssclj.util.spec :as su]))

(def ^:const cloud-service-type "docker")

(def connector-kw->pname
  {})

(def connector-pname->kw (set/map-invert connector-kw->pname))

(def ref-attrs [:endpoint
                :updateClientURL])

(def keys-spec {:req-un [::ps/endpoint
                         ::ps/updateClientURL]})

(def opt-keys-spec {:opt-un (concat (:req-un keys-spec) (:opt-un keys-spec))})

;; Defines the contents of the docker ConnectorTemplate resource itself.
(s/def :cimi/connector-template.docker
  (su/only-keys-maps ps/resource-keys-spec keys-spec))

;; Defines the contents of the docker template used in a create resource.
;; NOTE: The name must match the key defined by the resource, :connectorTemplate here.
(s/def :cimi.connector-template.docker/connectorTemplate
  (su/only-keys-maps ps/template-keys-spec opt-keys-spec))

(s/def :cimi/connector-template.docker-create
  (su/only-keys-maps ps/create-keys-spec
                     {:opt-un [:cimi.connector-template.docker/connectorTemplate]}))

(def ConnectorTemplateDockerDescription
  (merge ctpl/ConnectorTemplateDescription
         (select-keys ctpl/connector-reference-attrs-description ref-attrs)
         (uc/read-config "com/sixsq/slipstream/connector/docker-desc.edn")))
;;
;; resource
;;
;; defaults for the template
(def ^:const resource
  (merge (select-keys ctpl/connector-reference-attrs-defaults ref-attrs)
         {:cloudServiceType                  cloud-service-type
          :endpoint                          "https://<HOSTNAME>:2376"
          :updateClientURL                   "https://<IP>/downloads/dockerclient.tgz"
          }))

;;
;; description
;;
(def ^:const desc ConnectorTemplateDockerDescription)

;;
;; initialization: register this connector template
;;
(defn initialize
  []
  (ctpl/register resource desc connector-pname->kw))

;;
;; multimethods for validation
;;

(def validate-fn (u/create-spec-validation-fn :cimi/connector-template.docker))
(defmethod ctpl/validate-subtype cloud-service-type
  [resource]
  (validate-fn resource))
