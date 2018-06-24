(ns com.sixsq.slipstream.connector.openstack-template
  (:require
    [clojure.set :as set]
    [clojure.spec.alpha :as s]
    [com.sixsq.slipstream.ssclj.resources.common.utils :as u]
    [com.sixsq.slipstream.ssclj.resources.connector-template :as ctpl]
    [com.sixsq.slipstream.ssclj.resources.spec.connector-template :as ps]
    [com.sixsq.slipstream.ssclj.resources.spec.core :as cimi-core]
    [com.sixsq.slipstream.ssclj.util.config :as uc]
    [com.sixsq.slipstream.ssclj.util.spec :as su]))

(def ^:const cloud-service-type "openstack")

(def connector-kw->pname
  {:orchestratorInstanceType "orchestrator.instance.type"
   :identityVersion          "identity.version"
   :serviceRegion            "service.region"
   :serviceType              "service.type"
   :serviceName              "service.name"
   :floatingIps              "floating.ips"
   :reuseFloatingIps         "reuse.floating.ips"
   :networkPrivate           "network.private"
   :networkPublic            "network.public"})

(def connector-pname->kw (set/map-invert connector-kw->pname))

;;
;; schemas
;;

(s/def :cimi.connector-template.openstack/orchestratorInstanceType ::cimi-core/nonblank-string)
(s/def :cimi.connector-template.openstack/identityVersion ::cimi-core/nonblank-string)
(s/def :cimi.connector-template.openstack/serviceRegion ::cimi-core/nonblank-string)
(s/def :cimi.connector-template.openstack/serviceType ::cimi-core/nonblank-string)
(s/def :cimi.connector-template.openstack/serviceName string?)
(s/def :cimi.connector-template.openstack/floatingIps boolean?)
(s/def :cimi.connector-template.openstack/reuseFloatingIps boolean?)
(s/def :cimi.connector-template.openstack/networkPrivate string?)
(s/def :cimi.connector-template.openstack/networkPublic string?)

(def keys-spec {:req-un [::ps/endpoint
                         ::ps/objectStoreEndpoint
                         ::ps/nativeContextualization
                         ::ps/orchestratorSSHUsername
                         ::ps/orchestratorSSHPassword
                         ::ps/securityGroups
                         ::ps/updateClientURL

                         :cimi.connector-template.openstack/orchestratorInstanceType
                         :cimi.connector-template.openstack/identityVersion
                         :cimi.connector-template.openstack/serviceRegion
                         :cimi.connector-template.openstack/serviceType
                         :cimi.connector-template.openstack/serviceName
                         :cimi.connector-template.openstack/floatingIps
                         :cimi.connector-template.openstack/reuseFloatingIps
                         :cimi.connector-template.openstack/networkPrivate
                         :cimi.connector-template.openstack/networkPublic]})

(def opt-keys-spec {:opt-un (:req-un keys-spec)})

;; Defines the contents of the openstack ConnectorTemplate resource itself.
(s/def :cimi/connector-template.openstack
  (su/only-keys-maps ps/resource-keys-spec keys-spec))

;; Defines the contents of the openstack template used in a create resource.
;; NOTE: The name must match the key defined by the resource, :connectorTemplate here.
(s/def :cimi.connector-template.openstack/connectorTemplate
  (su/only-keys-maps ps/template-keys-spec opt-keys-spec))

(s/def :cimi/connector-template.openstack-create
  (su/only-keys-maps ps/create-keys-spec
                     {:opt-un [:cimi.connector-template.openstack/connectorTemplate]}))

(def ConnectorTemplateOpenstackDescription
  (merge ctpl/ConnectorTemplateDescription
         ctpl/connector-reference-attrs-description
         (uc/read-config "com/sixsq/slipstream/connector/openstack-desc.edn")))
;;
;; resource
;;
;; defaults for the template
(def ^:const resource
  (merge ctpl/connector-reference-attrs-defaults
         {:cloudServiceType         cloud-service-type

          :orchestratorInstanceType "Basic"
          :identityVersion          "v2"
          :serviceRegion            "RegionOne"
          :serviceType              "compute"
          :serviceName              ""
          :floatingIps              false
          :reuseFloatingIps         false
          :networkPrivate           ""
          :networkPublic            ""}))

;;
;; description
;;
(def ^:const desc ConnectorTemplateOpenstackDescription)

;;
;; initialization: register this connector template
;;
(defn initialize
  []
  (ctpl/register resource desc connector-pname->kw))

;;
;; multimethods for validation
;;

(def validate-fn (u/create-spec-validation-fn :cimi/connector-template.openstack))
(defmethod ctpl/validate-subtype cloud-service-type
  [resource]
  (validate-fn resource))
