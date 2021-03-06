(ns com.sixsq.slipstream.ssclj.resources.credential-cloud-openstack
  (:require
    [com.sixsq.slipstream.ssclj.resources.common.std-crud :as std-crud]
    [com.sixsq.slipstream.ssclj.resources.common.utils :as u]
    [com.sixsq.slipstream.ssclj.resources.credential :as p]
    [com.sixsq.slipstream.ssclj.resources.credential-template-cloud-openstack :as tpl]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-cloud-openstack :as openstack]))

;;
;; convert template to credential
;;
(defmethod p/tpl->credential tpl/credential-type
  [{:keys [type method connector key secret domain-name tenant-name quota acl]} request]
  (let [resource (cond-> {:resourceURI p/resource-uri
                          :type        type
                          :method      method
                          :connector   connector
                          :key         key
                          :secret      secret
                          :quota       (or quota (:quota tpl/resource))
                          :tenant-name tenant-name
                          :domain-name domain-name}
                         acl (assoc :acl acl))]
    [nil resource]))

;;
;; multimethods for validation
;;

(def validate-fn (u/create-spec-validation-fn ::openstack/credential))
(defmethod p/validate-subtype tpl/credential-type
  [resource]
  (validate-fn resource))

(def create-validate-fn (u/create-spec-validation-fn ::openstack/credential-create))
(defmethod p/create-validate-subtype tpl/credential-type
  [resource]
  (create-validate-fn resource))


;;
;; initialization
;;
(defn initialize
      []
      (std-crud/initialize p/resource-url ::openstack/credential))
