(ns com.sixsq.slipstream.ssclj.resources.spec.credential-cloud-cloudstack
    (:require
    [clojure.spec.alpha :as s]
    [com.sixsq.slipstream.ssclj.util.spec :as us]
    [com.sixsq.slipstream.ssclj.resources.spec.credential :as cred]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template :as ct]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template-cloud-cloudstack]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template-cloud :as ctc]))

(s/def :cimi/credential.cloud-cloudstack
  (us/only-keys-maps cred/credential-keys-spec
                     ctc/credential-template-cloud-keys-spec))

(s/def :cimi/credential.cloud-cloudstack.create
  (us/only-keys-maps ct/create-keys-spec
                     {:req-un [:cimi.credential-template.cloud-cloudstack/credentialTemplate]}))
