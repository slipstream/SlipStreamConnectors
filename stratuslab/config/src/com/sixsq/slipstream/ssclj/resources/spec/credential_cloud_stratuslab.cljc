(ns com.sixsq.slipstream.ssclj.resources.spec.credential-cloud-stratuslab
    (:require
    [clojure.spec.alpha :as s]
    [com.sixsq.slipstream.ssclj.util.spec :as us]
    [com.sixsq.slipstream.ssclj.resources.spec.credential :as cred]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template :as ct]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template-cloud-stratuslab]))

(s/def :cimi.credential.cloud-stratuslab/connector :cimi.common/resource-link)
(s/def :cimi.credential.cloud-stratuslab/key :cimi.core/nonblank-string)
(s/def :cimi.credential.cloud-stratuslab/secret :cimi.core/nonblank-string)

(def credential-keys-spec
  {:req-un [:cimi.credential.cloud-stratuslab/connector
            :cimi.credential.cloud-stratuslab/key
            :cimi.credential.cloud-stratuslab/secret]})

(s/def :cimi/credential.cloud-stratuslab
  (us/only-keys-maps cred/credential-keys-spec
                     credential-keys-spec))

(s/def :cimi/credential.cloud-stratuslab.create
  (us/only-keys-maps ct/create-keys-spec
                     {:req-un [:cimi.credential-template.cloud-stratuslab/credentialTemplate]}))
