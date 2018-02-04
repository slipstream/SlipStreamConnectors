(def +version+ "3.46-SNAPSHOT")

(defproject com.sixsq.slipstream/SlipStreamConnector-OpenNebula-conf "3.46-SNAPSHOT"

  :description "OpenNebula connector configuration"

  :url "https://github.com/slipstream/SlipStreamConnectors"
  
  :license {:name "Apache 2.0"
            :url "http://www.apache.org/licenses/LICENSE-2.0.txt"
            :distribution :repo}

  :plugins [[lein-parent "0.3.2"]]

  :parent-project {:coords  [com.sixsq.slipstream/parent "3.46-SNAPSHOT"]
                   :inherit [:min-lein-version
                             :managed-dependencies
                             :repositories
                             :deploy-repositories]}

  :source-paths ["src"]

  :resource-paths ["resources"]

  :test-paths ["test"]

  :pom-location "target/"

  :dependencies
  [[org.clojure/clojure]]

  :profiles
  {:test
   {:dependencies   [[com.sixsq.slipstream/SlipStreamCljResourcesTests-jar]
                     [com.sixsq.slipstream/SlipStreamDbTesting-jar]
                     [peridot]
                     [commons-logging]
                     [org.clojure/test.check]]
    :resource-paths ["test-resources"]}
   :provided
   {:dependencies [[com.sixsq.slipstream/SlipStreamCljResources-jar]]}})
