(ns com.sixsq.slipstream.connector.docker
    (:require
    [com.sixsq.slipstream.connector.docker-template :as tpl]
    [com.sixsq.slipstream.ssclj.resources.common.schema :as sch]
    [com.sixsq.slipstream.ssclj.resources.common.utils :as u]
    [com.sixsq.slipstream.ssclj.resources.connector :as cr]))

;;
;; schemas
;;

(def ConnectorDockerDescription tpl/ConnectorTemplateDockerDescription)

;;
;; description
;;
(def ^:const desc ConnectorDockerDescription)

;;
;; multimethods for validation
;;

(def validate-fn (u/create-spec-validation-fn :cimi/connector-template.docker))
(defmethod cr/validate-subtype tpl/cloud-service-type
  [resource]
  (validate-fn resource))

(def create-validate-fn (u/create-spec-validation-fn :cimi/connector-template.docker-create))
(defmethod cr/create-validate-subtype tpl/cloud-service-type
  [resource]
  (create-validate-fn resource))


(defmethod cr/new-identifier-subtype tpl/cloud-service-type
  [resource resource-name]
  (if-let [name (:instanceName resource)]
    (assoc resource :id (str (u/de-camelcase resource-name) "/" (u/random-uuid)))))