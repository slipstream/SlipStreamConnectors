(ns com.sixsq.slipstream.ssclj.resources.spec.credential-template-cloud-cloudstack
    (:require
    [clojure.spec.alpha :as s]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template :as ct]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template-cloud :as ctc]
    [com.sixsq.slipstream.ssclj.util.spec :as us]))

(def credential-template-keys-spec {})

(def credential-template-create-keys-spec credential-template-keys-spec)

;; Defines the contents of the cloud-cloudstack CredentialTemplate resource itself.
(s/def :cimi/credential-template.cloud-cloudstack
  (us/only-keys-maps ct/resource-keys-spec
                     ctc/credential-template-create-keys-spec
                     credential-template-keys-spec))

;; Defines the contents of the cloud-cloudstack template used in a create resource.
;; NOTE: The name must match the key defined by the resource, :credentialTemplate here.
(s/def :cimi.credential-template.cloud-cloudstack/credentialTemplate
  (us/only-keys-maps ct/template-keys-spec
                     ctc/credential-template-create-keys-spec
                     credential-template-create-keys-spec))

(s/def :cimi/credential-template.cloud-cloudstack-create
  (us/only-keys-maps ct/create-keys-spec
                     {:req-un [:cimi.credential-template.cloud-cloudstack/credentialTemplate]}))
