(ns com.sixsq.slipstream.ssclj.resources.credential-cloud-cloudstack
  (:require
    [com.sixsq.slipstream.ssclj.resources.common.utils :as u]
    [com.sixsq.slipstream.ssclj.resources.credential :as p]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-cloud-cloudstack]
    [com.sixsq.slipstream.ssclj.resources.credential-template-cloud-cloudstack :as tpl]
    [com.sixsq.slipstream.ssclj.resources.common.std-crud :as std-crud]))

;;
;; convert template to credential
;;
(defmethod p/tpl->credential tpl/credential-type
  [{:keys [type method connector key secret domain-name quota acl]} request]
  (let [resource (cond-> {:resourceURI p/resource-uri
                          :type        type
                          :method      method
                          :connector   connector
                          :key         key
                          :secret      secret
                          :quota       (or quota (:quota tpl/resource))}
                         acl (assoc :acl acl))]
    [nil resource]))

;;
;; multimethods for validation
;;

(def validate-fn (u/create-spec-validation-fn :cimi/credential.cloud-cloudstack))
(defmethod p/validate-subtype tpl/credential-type
  [resource]
  (validate-fn resource))

(def create-validate-fn (u/create-spec-validation-fn :cimi/credential.cloud-cloudstack.create))
(defmethod p/create-validate-subtype tpl/credential-type
  [resource]
  (create-validate-fn resource))


;;
;; initialization
;;
(defn initialize
      []
      (std-crud/initialize p/resource-url :cimi/credential.cloud-cloudstack))
