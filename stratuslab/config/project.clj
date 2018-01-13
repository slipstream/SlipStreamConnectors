(def +version+ "3.43-SNAPSHOT")

;; FIXME: Provide HTTPS access to Nexus.
(require 'cemerick.pomegranate.aether)
(cemerick.pomegranate.aether/register-wagon-factory!
  "http" #(org.apache.maven.wagon.providers.http.HttpWagon.))

(defproject
  com.sixsq.slipstream/SlipStreamConnector-StratusLab-conf
  "3.43-SNAPSHOT"
  :license
  {"Apache 2.0" "http://www.apache.org/licenses/LICENSE-2.0.txt"}

  :plugins [[lein-parent "0.3.2"]]

  :parent-project {:coords  [com.sixsq.slipstream/parent "3.43-SNAPSHOT"]
                   :inherit [:min-lein-version :managed-dependencies :repositories :deploy-repositories]}

  :source-paths ["src"]

  :resource-paths ["resources"]

  :test-paths ["test"]

  :pom-location "target/"

  :dependencies
  [[org.clojure/clojure]]

  :profiles
  {:test
   {:dependencies [[com.sixsq.slipstream/SlipStreamCljResourcesTests-jar]
                   [com.sixsq.slipstream/SlipStreamDbTesting-jar]
                   [peridot]
                   [commons-logging]
                   [org.clojure/test.check]]}
   :provided
   {:dependencies [[superstring]
                   [com.sixsq.slipstream/SlipStreamCljResources-jar]]}})
