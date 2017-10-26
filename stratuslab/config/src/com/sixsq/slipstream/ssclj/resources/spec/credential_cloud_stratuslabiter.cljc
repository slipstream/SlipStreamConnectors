(ns com.sixsq.slipstream.ssclj.resources.spec.credential-cloud-stratuslabiter
    (:require
    [clojure.spec.alpha :as s]
    [com.sixsq.slipstream.ssclj.util.spec :as us]
    [com.sixsq.slipstream.ssclj.resources.spec.credential :as cred]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template :as ct]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template-cloud-stratuslabiter]))

(s/def :cimi.credential.cloud-stratuslabiter/connector :cimi.common/resource-link)
(s/def :cimi.credential.cloud-stratuslabiter/key :cimi.core/nonblank-string)
(s/def :cimi.credential.cloud-stratuslabiter/secret :cimi.core/nonblank-string)

(def credential-keys-spec
  {:req-un [:cimi.credential.cloud-stratuslabiter/connector
            :cimi.credential.cloud-stratuslabiter/key
            :cimi.credential.cloud-stratuslabiter/secret]})

(s/def :cimi/credential.cloud-stratuslabiter
  (us/only-keys-maps cred/credential-keys-spec
                     credential-keys-spec))

(s/def :cimi/credential.cloud-stratuslabiter.create
  (us/only-keys-maps ct/create-keys-spec
                     {:req-un [:cimi.credential-template.cloud-stratuslabiter/credentialTemplate]}))
