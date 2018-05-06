(ns com.sixsq.slipstream.ssclj.resources.credential-template-cloud-cloudstack
  "This CredentialTemplate allows creating a Cloud Credential instance to hold
  cloud credentials for CloudStack cloud."
  (:require
    [com.sixsq.slipstream.connector.cloudstack-template :as ct]
    [com.sixsq.slipstream.ssclj.resources.common.utils :as u]
    [com.sixsq.slipstream.ssclj.resources.credential-template :as p]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template-cloud-cloudstack]
    [com.sixsq.slipstream.ssclj.util.userparamsdesc :refer [slurp-cloud-cred-desc]]))

(def ^:const credential-type (str "cloud-cred-" ct/cloud-service-type))
(def ^:const method (str "store-cloud-cred-" ct/cloud-service-type))

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
   :connector   {:href ""}
   :key         ""
   :secret      ""
   :quota       20
   :acl         resource-acl})

;;
;; description
;;
(def ^:const desc
  (merge p/CredentialTemplateDescription
         (slurp-cloud-cred-desc ct/cloud-service-type)))

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
