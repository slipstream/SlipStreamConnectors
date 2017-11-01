(ns com.sixsq.slipstream.ssclj.resources.credential-template-cloud-cloudstack
    "This CredentialTemplate allows creating a Cloud Credential instance to hold
    cloud credentials for CloudStack cloud."
    (:require
    [clojure.spec.alpha :as s]
    [com.sixsq.slipstream.ssclj.resources.common.utils :as u]
    [com.sixsq.slipstream.ssclj.resources.common.schema :as c]
    [com.sixsq.slipstream.ssclj.resources.credential-template :as p]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template-cloud-cloudstack]))

(def ^:const credential-type "cloud-cred-cloudstack")
(def ^:const method "store-cloud-cred-cloudstack")

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
   :name        "CloudStack cloud credentials store"
   :description "Stores user cloud credentials for CloudStack"
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
          :key         {:displayName "API key"
                        :category    credential-type
                        :description "On the default CloudStack web interface you can find this information on
                        'Accounts > [your account name] > View Users > [your user name] > API Key'"
                        :type        "string"
                        :mandatory   true
                        :readOnly    false
                        :order       20}
          :secret      {:displayName "API secret"
                        :category    credential-type
                        :description "On the default CloudStack web interface you can find this information on
                        'Accounts > [your account name] > View Users > [your user name] > Secret Key'"
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

(def validate-fn (u/create-spec-validation-fn :cimi/credential-template.cloud-cloudstack))
(defmethod p/validate-subtype method
  [resource]
  (validate-fn resource))
