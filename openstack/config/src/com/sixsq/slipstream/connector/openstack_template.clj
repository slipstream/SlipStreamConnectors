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
   :floatingIPs              "floating.ips"
   :networkPrivate           "network.private"
   :networkPublic            "network.public"
   })

(def connector-pname->kw (set/map-invert connector-kw->pname))

;;
;; schemas
;;

(def connector-madatory-attrs-schema
  {; mandatory parameters
   :endpoint                s/Str                           ;; ""
   :nativeContextualization sch/NonBlankString              ;; "linux-only"
   :orchestratorSSHUsername s/Str                           ;; ""
   :orchestratorSSHPassword s/Str                           ;; ""
   :securityGroups          s/Str                           ;; "slipstream_managed"
   :updateClientURL         s/Str                           ;; "https://nuv.la/downloads/openstackclient.tgz"
   })

(def connector-attrs-schema
  (merge connector-madatory-attrs-schema
         {:orchestratorInstanceType sch/NonBlankString      ;; "Basic"
          :identityVersion          sch/NonBlankString      ;; "v2"
          :serviceRegion            sch/NonBlankString      ;; "RegionOne"
          :serviceType              sch/NonBlankString      ;; "compute"
          :serviceName              s/Str                   ;; "nova"
          :floatingIPs              s/Bool                  ;; false
          :networkPrivate           s/Str                   ;; "private"
          :networkPublic            s/Str                   ;; "public"
          }))

(def ConnectorTemplateOpenstackAttrs
  (merge ctpl/ConnectorTemplateAttrs
         connector-attrs-schema))

(def ConnectorTemplateOpenstack
  (merge ctpl/ConnectorTemplate
         ConnectorTemplateOpenstackAttrs))

(def ConnectorTemplateOpenstackRef
  (s/constrained
    (merge ConnectorTemplateOpenstackAttrs
           {(s/optional-key :href) sch/NonBlankString})
    seq 'not-empty?))

(def ConnectorTemplateOpenstackDescription
  (merge ctpl/ConnectorTemplateDescription
         (uc/read-config "com/sixsq/slipstream/connector/openstack-desc.edn")))
;;
;; resource
;;
;; defautls for the template
(def ^:const resource
  {:cloudServiceType         cloud-service-type

   :orchestratorImageid      ""
   :quotaVm                  ""
   :maxIaasWorkers           20

   :endpoint                 ""
   :nativeContextualization  "linux-only"
   :orchestratorSSHUsername  ""
   :orchestratorSSHPassword  ""
   :securityGroups           "slipstream_managed"
   :updateClientURL          ""

   :orchestratorInstanceType "Basic"
   :identityVersion          "v2"
   :serviceRegion            "RegionOne"
   :serviceType              "compute"
   :serviceName              ""
   :floatingIPs              false
   :networkPrivate           ""
   :networkPublic            ""})

;;
;; description
;;
(def ^:const desc ConnectorTemplateOpenstackDescription)

;;
;; initialization: register this connector template
;;
(defn initialize
  []
  (ctpl/register resource desc))

;;
;; multimethods for validation
;;

(def validate-fn (u/create-validation-fn ConnectorTemplateOpenstack))
(defmethod ctpl/validate-subtype cloud-service-type
  [resource]
  (validate-fn resource))
