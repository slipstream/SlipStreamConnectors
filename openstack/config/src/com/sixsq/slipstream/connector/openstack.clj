(ns com.sixsq.slipstream.connector.openstack
  (:require
    [com.sixsq.slipstream.connector.openstack-template :as tpl]
    [com.sixsq.slipstream.ssclj.resources.common.schema :as sch]
    [com.sixsq.slipstream.ssclj.resources.common.utils :as u]
    [com.sixsq.slipstream.ssclj.resources.connector :as cr]
    ))

;;
;; schemas
;;

(def ConnectorOpenstack tpl/ConnectorTemplateOpenstack)

(def ConnectorOpenstackCreate
  (merge sch/CreateAttrs
         {:connectorTemplate tpl/ConnectorTemplateOpenstackRef}))

(def ConnectorOpenstackDescription tpl/ConnectorTemplateOpenstackDescription)

;;
;; description
;;
(def ^:const desc ConnectorOpenstackDescription)

;;
;; multimethods for validation
;;

(def validate-fn (u/create-validation-fn ConnectorOpenstack))
(defmethod cr/validate-subtype tpl/cloud-service-type
  [resource]
  (validate-fn resource))

(def create-validate-fn (u/create-validation-fn ConnectorOpenstackCreate))
(defmethod cr/create-validate-subtype tpl/cloud-service-type
  [resource]
  (create-validate-fn resource))
