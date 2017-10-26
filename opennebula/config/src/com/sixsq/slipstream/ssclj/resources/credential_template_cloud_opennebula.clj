(ns com.sixsq.slipstream.ssclj.resources.credential-template-cloud-opennebula
    "This CredentialTemplate allows creating a Cloud Credential instance to hold
    cloud credentials for Exoscale cloud."
    (:require
    [clojure.spec.alpha :as s]
    [com.sixsq.slipstream.ssclj.resources.common.utils :as u]
    [com.sixsq.slipstream.ssclj.resources.common.schema :as c]
    [com.sixsq.slipstream.ssclj.resources.credential-template :as p]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template-cloud-opennebula]))

(def ^:const credential-type "cloud-cred-opennebula")
(def ^:const method "store-cloud-cred-opennebula")

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
   :name        "OpenNebula cloud credentials store"
   :description "Stores user cloud credentials for OpenNebula"
   :connector   ""
   :key         ""
   :secret      ""
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

(def validate-fn (u/create-spec-validation-fn :cimi/credential-template.cloud-opennebula))
(defmethod p/validate-subtype method
  [resource]
  (validate-fn resource))
