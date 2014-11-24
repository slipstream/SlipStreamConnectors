(ns slipstream.credcache.javawrapper-test
  (:require
    [expectations :refer :all]
    [slipstream.credcache.javawrapper :refer [java->clj]])
  (:import [java.util HashMap ArrayList HashSet]))

(def cm {"a" "1" "b" "2" "c" "3"})
(def m (HashMap. cm))

(def cs #{"a" "A" "b" "B"})
(def s (HashSet. cs))

(def cl ["one" "two" "three"])
(def l (ArrayList. cl))

(def nested-map (HashMap. {"map" m "set" s "list" l}))

(expect cm (java->clj m))

(expect cs (java->clj s))

(expect cl (java->clj l))

(expect map? (java->clj nested-map))
(expect cm (get (java->clj nested-map) "map"))
(expect cs (get (java->clj nested-map) "set"))
(expect cl (get (java->clj nested-map) "list"))






