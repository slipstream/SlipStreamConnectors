(ns com.sixsq.slipstream.connector.cloudstack
  (:require
    [com.sixsq.slipstream.connector.cloudstack-template :as tpl]
    [com.sixsq.slipstream.ssclj.resources.common.schema :as sch]
    [com.sixsq.slipstream.ssclj.resources.common.utils :as u]
    [com.sixsq.slipstream.ssclj.resources.connector :as cr]
    ))

;;
;; schemas
;;

(def ConnectorCloudstack tpl/ConnectorTemplateCloudstack)

(def ConnectorCloudstackCreate
  (merge sch/CreateAttrs
         {:connectorTemplate tpl/ConnectorTemplateCloudstackRef}))

(def ConnectorCloudstackDescription tpl/ConnectorTemplateCloudstackDescription)

;;
;; description
;;
(def ^:const desc ConnectorCloudstackDescription)

;;
;; multimethods for validation
;;

(def validate-fn (u/create-validation-fn ConnectorCloudstack))
(defmethod cr/validate-subtype tpl/cloud-service-type
  [resource]
  (validate-fn resource))

(def create-validate-fn (u/create-validation-fn ConnectorCloudstackCreate))
(defmethod cr/create-validate-subtype tpl/cloud-service-type
  [resource]
  (create-validate-fn resource))
