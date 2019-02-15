(ns com.sixsq.slipstream.ssclj.resources.spec.credential-cloud-docker
    (:require
    [clojure.spec.alpha :as s]
    [com.sixsq.slipstream.ssclj.resources.spec.credential :as cred]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template :as ct]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template-cloud :as ctc]
    [com.sixsq.slipstream.ssclj.resources.spec.credential-template-cloud-docker :as docker-tpl]
    [com.sixsq.slipstream.ssclj.util.spec :as us]))

(def credential-keys-spec ctc/credential-template-cloud-keys-spec)

(s/def ::credential
  (us/only-keys-maps cred/credential-keys-spec
                     credential-keys-spec))

(s/def ::credential-create
  (us/only-keys-maps ct/create-keys-spec
                     {:req-un [::docker-tpl/credentialTemplate]}))
