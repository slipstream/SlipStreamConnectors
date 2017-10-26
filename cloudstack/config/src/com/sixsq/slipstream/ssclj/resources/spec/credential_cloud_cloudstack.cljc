(ns com.sixsq.slipstream.ssclj.resources.spec.credential-cloud-cloudstack
    (:require
    [clojure.spec.alpha :as s]
    [com.sixsq.slipstream.ssclj.util.spec :as us]
    [com.sixsq.slipstream.ssclj.resources.spec.credential :as cred]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template :as ct]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template-cloud-cloudstack]))

(s/def :cimi.credential.cloud-cloudstack/connector :cimi.common/resource-link)
(s/def :cimi.credential.cloud-cloudstack/key :cimi.core/nonblank-string)
(s/def :cimi.credential.cloud-cloudstack/secret :cimi.core/nonblank-string)

(def credential-keys-spec
  {:req-un [:cimi.credential.cloud-cloudstack/connector
            :cimi.credential.cloud-cloudstack/key
            :cimi.credential.cloud-cloudstack/secret]})

(s/def :cimi/credential.cloud-cloudstack
  (us/only-keys-maps cred/credential-keys-spec
                     credential-keys-spec))

(s/def :cimi/credential.cloud-cloudstack.create
  (us/only-keys-maps ct/create-keys-spec
                     {:req-un [:cimi.credential-template.cloud-cloudstack/credentialTemplate]}))
