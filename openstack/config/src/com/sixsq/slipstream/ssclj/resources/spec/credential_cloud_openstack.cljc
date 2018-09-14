(ns com.sixsq.slipstream.ssclj.resources.spec.credential-cloud-openstack
  (:require
    [clojure.spec.alpha :as s]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-cloud :as cloud-cred]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template :as ct]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template-cloud :as ctc]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template-cloud-openstack :as openstack-tpl]
    [com.sixsq.slipstream.ssclj.util.spec :as us]))

(s/def ::tenant-name string?)
(s/def ::domain-name string?)

(def credential-keys-spec
  (-> ctc/credential-template-cloud-keys-spec
      (update-in [:opt-un] concat [::tenant-name
                                   ::domain-name])))

(s/def ::credential
  (us/only-keys-maps cloud-cred/credential-keys-spec
                     credential-keys-spec))

(s/def ::credential-create
  (us/only-keys-maps ct/create-keys-spec
                     {:req-un [::openstack-tpl/credentialTemplate]}))
