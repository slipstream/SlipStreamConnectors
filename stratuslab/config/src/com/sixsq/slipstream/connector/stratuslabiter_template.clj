(ns com.sixsq.slipstream.connector.stratuslabiter-template
  (:require
    [com.sixsq.slipstream.connector.stratuslab-template :as slt]
    [com.sixsq.slipstream.ssclj.resources.common.utils :as u]
    [com.sixsq.slipstream.ssclj.resources.connector-template :as ctpl]))

(def ^:const cloud-service-type "stratuslabiter")

;;
;; initialization: register this connector template
;;
(defn initialize
  []
  (ctpl/register (assoc slt/resource :cloudServiceType cloud-service-type)
                 slt/desc
                 slt/connector-pname->kw))

;;
;; multimethods for validation
;;

(def validate-fn (u/create-validation-fn slt/ConnectorTemplateStratusLab))
(defmethod ctpl/validate-subtype cloud-service-type
  [resource]
  (validate-fn resource))
