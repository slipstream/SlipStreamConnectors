(ns com.sixsq.slipstream.connector.test-utils
  (:require
    [com.sixsq.slipstream.connector.openstack-template :as ct-openstack]))

(defn new-instance-name
  []
  (str ct-openstack/cloud-service-type "-" (System/currentTimeMillis)))

