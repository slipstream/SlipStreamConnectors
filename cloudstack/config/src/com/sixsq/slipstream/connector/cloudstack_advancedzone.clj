(ns com.sixsq.slipstream.connector.cloudstack-advancedzone
  (:require
    [com.sixsq.slipstream.connector.cloudstack-advancedzone-template :as tpl]
    [com.sixsq.slipstream.ssclj.resources.common.schema :as sch]
    [com.sixsq.slipstream.ssclj.resources.common.utils :as u]
    [com.sixsq.slipstream.ssclj.resources.connector :as cr]))

;;
;; schemas
;;

(def ConnectorCloudstackAdvancedZoneDescription tpl/ConnectorTemplateCloudstackAdvancedZoneDescription)

;;
;; description
;;
(def ^:const desc ConnectorCloudstackAdvancedZoneDescription)

;;
;; multimethods for validation
;;

(def validate-fn (u/create-spec-validation-fn :cimi/connector-template.cloudstackadvancedzone))
(defmethod cr/validate-subtype tpl/cloud-service-type
  [resource]
  (validate-fn resource))

(def create-validate-fn (u/create-spec-validation-fn :cimi/connector-template.cloudstackadvancedzone-create))
(defmethod cr/create-validate-subtype tpl/cloud-service-type
  [resource]
  (create-validate-fn resource))
