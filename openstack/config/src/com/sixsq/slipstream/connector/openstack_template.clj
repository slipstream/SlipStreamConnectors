(ns com.sixsq.slipstream.connector.openstack-template
  (:require
    [clojure.set :as set]
    [schema.core :as s]
    [com.sixsq.slipstream.ssclj.resources.common.schema :as sch]
    [com.sixsq.slipstream.ssclj.resources.common.utils :as u]
    [com.sixsq.slipstream.ssclj.resources.connector-template :as ctpl]
    [com.sixsq.slipstream.ssclj.util.config :as uc]
    ))

(def ^:const cloud-service-type "openstack")

(def connector-kw->pname
  {:orchestratorInstanceType "orchestrator.instance.type"
   :identityVersion          "identity.version"
   :serviceRegion            "service.region"
   :serviceType              "service.type"
   :serviceName              "service.name"
   :floatingIps              "floating.ips"
   :networkPrivate           "network.private"
   :networkPublic            "network.public"})

(def connector-pname->kw (set/map-invert connector-kw->pname))

;;
;; schemas
;;

(def ConnectorAttrsSchema
  (merge ctpl/ConnectorReferenceAttrs
         {:orchestratorInstanceType sch/NonBlankString      ;; "Basic"
          :identityVersion          sch/NonBlankString      ;; "v2"
          :serviceRegion            sch/NonBlankString      ;; "RegionOne"
          :serviceType              sch/NonBlankString      ;; "compute"
          :serviceName              s/Str                   ;; "nova"
          :floatingIps              s/Bool                  ;; false
          :networkPrivate           s/Str                   ;; "private"
          :networkPublic            s/Str                   ;; "public"
          }))

(def ConnectorTemplateAttrs
  (merge ctpl/ConnectorTemplateAttrs
         ConnectorAttrsSchema))

(def ConnectorTemplateOpenstack
  (merge ctpl/ConnectorTemplate
         ConnectorTemplateAttrs))

(def ConnectorTemplateOpenstackRef
  (s/constrained
    (merge ConnectorTemplateAttrs
           {(s/optional-key :href) sch/NonBlankString})
    seq 'not-empty?))

(def ConnectorTemplateOpenstackDescription
  (merge ctpl/ConnectorTemplateDescription
         ctpl/connector-reference-attrs-description
         (uc/read-config "com/sixsq/slipstream/connector/openstack-desc.edn")))
;;
;; resource
;;
;; defautls for the template
(def ^:const resource
  (merge ctpl/connector-reference-attrs-defaults
         {:cloudServiceType         cloud-service-type

          :orchestratorInstanceType "Basic"
          :identityVersion          "v2"
          :serviceRegion            "RegionOne"
          :serviceType              "compute"
          :serviceName              ""
          :floatingIps              false
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

(def validate-fn (u/create-validation-fn ConnectorTemplateOpenstack))
(defmethod ctpl/validate-subtype cloud-service-type
  [resource]
  (validate-fn resource))
