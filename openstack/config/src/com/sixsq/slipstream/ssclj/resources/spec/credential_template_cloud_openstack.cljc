(ns com.sixsq.slipstream.ssclj.resources.spec.credential-template-cloud-openstack
    (:require
    [clojure.spec.alpha :as s]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template :as ct]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template-cloud :as ctc]
    [com.sixsq.slipstream.ssclj.util.spec :as us]))

(s/def ::tenant-name string?)
(s/def ::domain-name string?)

(def credential-template-keys-spec
  {:opt-un [::tenant-name
            ::domain-name]})

(def credential-template-create-keys-spec credential-template-keys-spec)

;; Defines the contents of the cloud-openstack CredentialTemplate resource itself.
(s/def ::credential-template
  (us/only-keys-maps ct/resource-keys-spec
                     ctc/credential-template-create-keys-spec
                     credential-template-keys-spec))

;; Defines the contents of the cloud-openstack template used in a create resource.
;; NOTE: The name must match the key defined by the resource, :credentialTemplate here.
(s/def ::credentialTemplate
  (us/only-keys-maps ct/template-keys-spec
                     ctc/credential-template-create-keys-spec
                     credential-template-create-keys-spec))

(s/def ::credential-template-create
  (us/only-keys-maps ct/create-keys-spec
                     {:req-un [::credentialTemplate]}))

