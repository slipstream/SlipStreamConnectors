(ns slipstream.credcache.javawrapper
  (:require
    [clojure.walk :as walk]
    [slipstream.credcache.control :as ctl]
    [slipstream.credcache.credential :as cred]
    [slipstream.credcache.credential.myproxy-voms :as mpv]
    [slipstream.credcache.notify :as notify])
  (:import [java.util Map List Set])
  (:gen-class
    :name slipstream.credcache.JavaWrapper
    :methods [#^{:static true} [start [] void]
              #^{:static true} [stop [] void]
              #^{:static true} [create [java.util.Map] String]
              #^{:static true} [retrieve [String] java.io.File]]))

(defn java->clj
  "Transform java data structures into the equivalent clojure
   data structures.  Elements that are not a Map, List, or Set
   are left unchanged."
  [data]
  (cond
    (instance? Map data) (into {} (map (fn [[k v]] [k (java->clj v)]) data))
    (instance? List data) (into [] (map #(java->clj %) data))
    (instance? Set data) (into #{} (map #(java->clj %) data))
    :else data))

(defn -start
  []
  (ctl/start!))

(defn -stop
  []
  (ctl/stop!))

(defn -create
  [template]
  (try
    (-> (java->clj template)
        (walk/keywordize-keys)
        (cred/create))
    (catch Exception ex
      (notify/create-failure template)
      (throw ex))))

(defn -retrieve
  [id]
  (mpv/proxy->tfile (cred/retrieve id)))


