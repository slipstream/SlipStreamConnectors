(ns com.sixsq.slipstream.ssclj.resources.credential-cloud-opennebula
  (:require
    [com.sixsq.slipstream.auth.acl :as acl]
    [com.sixsq.slipstream.ssclj.resources.common.utils :as u]
    [com.sixsq.slipstream.ssclj.resources.credential :as p]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-cloud-opennebula]
    [com.sixsq.slipstream.ssclj.resources.credential-template-cloud-opennebula :as tpl]))

;;
;; convert template to credential
;;
(defmethod p/tpl->credential tpl/credential-type
  [{:keys [type method connector key secret quota acl]} request]
  (let [resource (cond-> {:resourceURI p/resource-uri
                          :type        type
                          :method      method
                          :connector   connector
                          :quota       (or quota (:quota tpl/resource))
                          :key         key
                          :secret      secret}
                         acl (assoc :acl acl))]
    [nil resource]))

;;
;; multimethods for validation
;;

(def validate-fn (u/create-spec-validation-fn :cimi/credential.cloud-opennebula))
(defmethod p/validate-subtype tpl/credential-type
  [resource]
  (validate-fn resource))

(def create-validate-fn (u/create-spec-validation-fn :cimi/credential.cloud-opennebula.create))
(defmethod p/create-validate-subtype tpl/credential-type
  [resource]
  (create-validate-fn resource))


