(ns com.sixsq.slipstream.connector.stratuslab
    (:require
    [com.sixsq.slipstream.connector.stratuslab-template :as tpl]
    [com.sixsq.slipstream.ssclj.resources.common.schema :as sch]
    [com.sixsq.slipstream.ssclj.resources.common.utils :as u]
    [com.sixsq.slipstream.ssclj.resources.connector :as cr]
    ))

;;
;; schemas
;;

(def ConnectorStratusLab tpl/ConnectorTemplateStratusLab)

(def ConnectorStratusLabCreate
  (merge sch/CreateAttrs
         {:connectorTemplate tpl/ConnectorTemplateStratusLabRef}))

;(def ConnectorStratusLabDescription tpl/ConnectorTemplateStratusLabDescription)
;
;;;
;;; description
;;;
;(def ^:const desc ConnectorStratusLabDescription)

;;
;; multimethods for validation
;;

(def validate-fn (u/create-validation-fn ConnectorStratusLab))
(defmethod cr/validate-subtype tpl/cloud-service-type
  [resource]
  (validate-fn resource))

(def create-validate-fn (u/create-validation-fn ConnectorStratusLabCreate))
(defmethod cr/create-validate-subtype tpl/cloud-service-type
  [resource]
  (create-validate-fn resource))
