(ns com.sixsq.slipstream.ssclj.resources.credential-template-cloud-docker
    "This CredentialTemplate allows creating a Cloud Credential instance to hold
    cloud credentials for Docker cloud."
    (:require
    [com.sixsq.slipstream.connector.docker-template :as ct]
    [com.sixsq.slipstream.ssclj.resources.common.utils :as u]
    [com.sixsq.slipstream.ssclj.resources.credential-template :as p]
    [com.sixsq.slipstream.ssclj.resources.credential-template-cloud :as ctc]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template-cloud-docker :as docker-tpl]))

(def ^:const credential-type (ctc/cred-type ct/cloud-service-type))
(def ^:const method (ctc/cred-method ct/cloud-service-type))

;;
;; resource
;;
(def ^:const resource (ctc/gen-resource {} ct/cloud-service-type))

;;
;; description
;;
(def ^:const desc (ctc/gen-description ct/cloud-service-type))

;;
;; initialization: register this Credential template
;;
(defn initialize
  []
  (p/register resource desc))

;;
;; multimethods for validation
;;

(def validate-fn (u/create-spec-validation-fn ::docker-tpl/credential-template))
(defmethod p/validate-subtype method
  [resource]
  (validate-fn resource))
