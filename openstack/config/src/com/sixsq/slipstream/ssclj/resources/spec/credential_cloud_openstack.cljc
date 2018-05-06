(ns com.sixsq.slipstream.ssclj.resources.spec.credential-cloud-openstack
  (:require
    [clojure.spec.alpha :as s]
    [com.sixsq.slipstream.ssclj.resources.spec.credential :as cred]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template :as ct]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template-cloud :as ctc]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template-cloud-openstack]
    [com.sixsq.slipstream.ssclj.util.spec :as us]))

(s/def :cimi.credential.cloud-openstack/tenant-name string?)
(s/def :cimi.credential.cloud-openstack/domain-name string?)

(def credential-keys-spec
  (-> ctc/credential-template-cloud-keys-spec
      (update-in [:opt-un] concat [:cimi.credential.cloud-openstack/tenant-name
                                   :cimi.credential.cloud-openstack/domain-name])))

(s/def :cimi/credential.cloud-openstack
  (us/only-keys-maps cred/credential-keys-spec
                     credential-keys-spec))

(s/def :cimi/credential.cloud-openstack.create
  (us/only-keys-maps ct/create-keys-spec
                     {:req-un [:cimi.credential-template.cloud-openstack/credentialTemplate]}))
