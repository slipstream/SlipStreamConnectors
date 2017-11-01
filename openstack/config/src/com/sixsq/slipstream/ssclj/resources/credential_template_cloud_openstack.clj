(ns com.sixsq.slipstream.ssclj.resources.credential-template-cloud-openstack
    "This CredentialTemplate allows creating a Cloud Credential instance to hold
    cloud credentials for OpenStack cloud."
    (:require
    [clojure.spec.alpha :as s]
    [com.sixsq.slipstream.ssclj.resources.common.utils :as u]
    [com.sixsq.slipstream.ssclj.resources.common.schema :as c]
    [com.sixsq.slipstream.ssclj.resources.credential-template :as p]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template-cloud-openstack]))

(def ^:const credential-type "cloud-cred-openstack")
(def ^:const method "store-cloud-cred-openstack")

(def resource-acl {:owner {:principal "ADMIN"
                           :type      "ROLE"}
                   :rules [{:principal "USER"
                            :type      "ROLE"
                            :right     "VIEW"}]})

;;
;; resource
;;
(def ^:const resource
  {:type        credential-type
   :method      method
   :name        "OpenStack cloud credentials store"
   :description "Stores user cloud credentials for OpenStack"
   :connector   ""
   :key         ""
   :secret      ""
   :tenant-name ""
   :domain-name ""
   :acl         resource-acl})

;;
;; description
;;
(def ^:const desc
  (merge p/CredentialTemplateDescription
         {:connector   {:displayName "Connector name"
                        :category    credential-type
                        :description "SlipStream connector instance name"
                        :type        "string"
                        :mandatory   true
                        :readOnly    false
                        :order       10}
          :key         {:displayName "User Name"
                        :category    credential-type
                        :description "Username"
                        :type        "string"
                        :mandatory   true
                        :readOnly    false
                        :order       20}
          :secret      {:displayName "Password"
                        :category    credential-type
                        :description "Password"
                        :type        "password"
                        :mandatory   true
                        :readOnly    false
                        :order       30}
          :tenant-name {:displayName "Project name"
                        :category    credential-type
                        :description "Project name"
                        :type        "string"
                        :mandatory   true
                        :readOnly    false
                        :order       100}
          :domain-name {:displayName "Domain name"
                        :category    credential-type
                        :description "Only useful if Identity API v3"
                        :type        "string"
                        :mandatory   true
                        :readOnly    false
                        :order       110}
          }))

;;
;; initialization: register this Credential template
;;
(defn initialize
  []
  (p/register resource desc))

;;
;; multimethods for validation
;;

(def validate-fn (u/create-spec-validation-fn :cimi/credential-template.cloud-openstack))
(defmethod p/validate-subtype method
  [resource]
  (validate-fn resource))
