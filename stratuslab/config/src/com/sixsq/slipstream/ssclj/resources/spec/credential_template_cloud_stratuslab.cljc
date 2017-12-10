(ns com.sixsq.slipstream.ssclj.resources.spec.credential-template-cloud-stratuslab
  (:require
    [clojure.spec.alpha :as s]
    [com.sixsq.slipstream.ssclj.util.spec :as us]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template :as ct]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template-cloud :as ctc]))

(def credential-template-keys-spec {})

(def credential-template-create-keys-spec credential-template-keys-spec)

;; Defines the contents of the cloud-stratuslab CredentialTemplate resource itself.
(s/def :cimi/credential-template.cloud-stratuslab
  (us/only-keys-maps ct/resource-keys-spec
                     ctc/credential-template-create-keys-spec
                     credential-template-keys-spec))

;; Defines the contents of the cloud-stratuslab template used in a create resource.
;; NOTE: The name must match the key defined by the resource, :credentialTemplate here.
(s/def :cimi.credential-template.cloud-stratuslab/credentialTemplate
  (us/only-keys-maps ct/template-keys-spec
                     ctc/credential-template-create-keys-spec
                     credential-template-create-keys-spec))

(s/def :cimi/credential-template.cloud-stratuslab-create
  (us/only-keys-maps ct/create-keys-spec
                     {:req-un [:cimi.credential-template.cloud-stratuslab/credentialTemplate]}))

