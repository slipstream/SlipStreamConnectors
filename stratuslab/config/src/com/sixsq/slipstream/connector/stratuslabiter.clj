(ns com.sixsq.slipstream.connector.stratuslabiter
    (:require
    [com.sixsq.slipstream.connector.stratuslabiter-template :as t]
    [com.sixsq.slipstream.connector.stratuslab-template :as slt]
    [com.sixsq.slipstream.ssclj.resources.common.schema :as sch]
    [com.sixsq.slipstream.ssclj.resources.common.utils :as u]
    [com.sixsq.slipstream.ssclj.resources.connector :as cr]
    ))

;;
;; schemas
;;

(def ConnectorStratusLab slt/ConnectorTemplateStratusLab)

(def ConnectorStratusLabCreate
  (merge sch/CreateAttrs
         {:connectorTemplate slt/ConnectorTemplateStratusLabRef}))

;(def ConnectorStratusLabDescription sltpl/ConnectorTemplateStratusLabDescription)
;
;;;
;;; description
;;;
;(def ^:const desc ConnectorStratusLabDescription)

;;
;; multimethods for validation
;;

(def validate-fn (u/create-validation-fn ConnectorStratusLab))
(defmethod cr/validate-subtype t/cloud-service-type
  [resource]
  (validate-fn resource))

(def create-validate-fn (u/create-validation-fn ConnectorStratusLabCreate))
(defmethod cr/create-validate-subtype t/cloud-service-type
  [resource]
  (create-validate-fn resource))
