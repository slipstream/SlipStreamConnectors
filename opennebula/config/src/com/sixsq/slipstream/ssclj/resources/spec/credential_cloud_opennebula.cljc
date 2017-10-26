(ns com.sixsq.slipstream.ssclj.resources.spec.credential-cloud-opennebula
    (:require
    [clojure.spec.alpha :as s]
    [com.sixsq.slipstream.ssclj.util.spec :as us]
    [com.sixsq.slipstream.ssclj.resources.spec.credential :as cred]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template :as ct]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template-cloud-opennebula]))

(s/def :cimi.credential.cloud-opennebula/connector :cimi.common/resource-link)
(s/def :cimi.credential.cloud-opennebula/key :cimi.core/nonblank-string)
(s/def :cimi.credential.cloud-opennebula/secret :cimi.core/nonblank-string)

(def credential-keys-spec
  {:req-un [:cimi.credential.cloud-opennebula/connector
            :cimi.credential.cloud-opennebula/key
            :cimi.credential.cloud-opennebula/secret]})

(s/def :cimi/credential.cloud-opennebula
  (us/only-keys-maps cred/credential-keys-spec
                     credential-keys-spec))

(s/def :cimi/credential.cloud-opennebula.create
  (us/only-keys-maps ct/create-keys-spec
                     {:req-un [:cimi.credential-template.cloud-opennebula/credentialTemplate]}))
