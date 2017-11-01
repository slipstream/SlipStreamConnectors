(ns com.sixsq.slipstream.ssclj.resources.credential-template-cloud-stratuslabiter
    "This CredentialTemplate allows creating a Cloud Credential instance to hold
    cloud credentials for StratusLabIter cloud."
    (:require
    [clojure.spec.alpha :as s]
    [com.sixsq.slipstream.ssclj.resources.common.utils :as u]
    [com.sixsq.slipstream.ssclj.resources.common.schema :as c]
    [com.sixsq.slipstream.ssclj.resources.credential-template :as p]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template-cloud-stratuslabiter]))

(def ^:const credential-type "cloud-cred-stratuslabiter")
(def ^:const method "store-cloud-cred-stratuslabiter")

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
   :name        "StratusLab cloud credentials store"
   :description "Stores user cloud credentials for StratusLab"
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
                        :description "StratusLab account username"
                        :type        "string"
                        :mandatory   true
                        :readOnly    false
                        :order       20}
          :secret      {:displayName "Password"
                        :category    credential-type
                        :description "StratusLab account password"
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

(def validate-fn (u/create-spec-validation-fn :cimi/credential-template.cloud-stratuslabiter))
(defmethod p/validate-subtype method
  [resource]
  (validate-fn resource))
