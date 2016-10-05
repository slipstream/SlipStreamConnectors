(ns com.sixsq.slipstream.connector.opennebula
    (:require
    [com.sixsq.slipstream.connector.opennebula-template :as tpl]
    [com.sixsq.slipstream.ssclj.resources.common.schema :as sch]
    [com.sixsq.slipstream.ssclj.resources.common.utils :as u]
    [com.sixsq.slipstream.ssclj.resources.connector :as cr]
    ))

;;
;; schemas
;;

(def ConnectorOpenNebula tpl/ConnectorTemplateOpenNebula)

(def ConnectorOpenNebulaCreate
  (merge sch/CreateAttrs
         {:connectorTemplate tpl/ConnectorTemplateOpenNebulaRef}))

(def ConnectorOpenNebulaDescription tpl/ConnectorTemplateOpenNebulaDescription)

;;
;; description
;;
(def ^:const desc ConnectorOpenNebulaDescription)

;;
;; multimethods for validation
;;

(def validate-fn (u/create-validation-fn ConnectorOpenNebula))
(defmethod cr/validate-subtype tpl/cloud-service-type
  [resource]
  (validate-fn resource))

(def create-validate-fn (u/create-validation-fn ConnectorOpenNebulaCreate))
(defmethod cr/create-validate-subtype tpl/cloud-service-type
  [resource]
  (create-validate-fn resource))
