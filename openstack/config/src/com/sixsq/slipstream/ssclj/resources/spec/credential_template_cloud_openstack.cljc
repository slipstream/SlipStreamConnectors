(ns com.sixsq.slipstream.ssclj.resources.spec.credential-template-cloud-openstack
    (:require
    [clojure.spec.alpha :as s]
    [com.sixsq.slipstream.ssclj.util.spec :as us]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template :as ct]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template-cloud :as ctc]))

(s/def :cimi.credential-template.cloud-openstack/tenant-name :cimi.core/nonblank-string)
(s/def :cimi.credential-template.cloud-openstack/domain-name string?)

(def credential-template-keys-spec
  {:req-un [:cimi.credential-template.cloud-openstack/tenant-name]
   :opt-un [:cimi.credential-template.cloud-openstack/domain-name]})

(def credential-template-create-keys-spec credential-template-keys-spec)

;; Defines the contents of the cloud-openstack CredentialTemplate resource itself.
(s/def :cimi/credential-template.cloud-openstack
  (us/only-keys-maps ct/resource-keys-spec
                     ctc/credential-template-create-keys-spec
                     credential-template-keys-spec))

;; Defines the contents of the cloud-openstack template used in a create resource.
;; NOTE: The name must match the key defined by the resource, :credentialTemplate here.
(s/def :cimi.credential-template.cloud-openstack/credentialTemplate
  (us/only-keys-maps ct/template-keys-spec
                     ctc/credential-template-create-keys-spec
                     credential-template-create-keys-spec))

(s/def :cimi/credential-template.cloud-openstack-create
  (us/only-keys-maps ct/create-keys-spec
                     {:req-un [:cimi.credential-template.cloud-openstack/credentialTemplate]}))

