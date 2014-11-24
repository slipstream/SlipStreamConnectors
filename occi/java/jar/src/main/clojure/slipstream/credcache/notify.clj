(ns slipstream.credcache.notify
  "Utilities for notifying users via email."
  (:require
    [clojure.tools.logging :as log]
    [postal.core :as postal]
    [schema.core :as s]
    [clj-time.core :as t]
    [clj-time.coerce :as tc]
    [clj-time.format :as tf])
  (:import
    [com.sixsq.slipstream.persistence
     ServiceConfiguration
     ServiceConfiguration$ParameterCategory
     ServiceConfiguration$RequiredParameters]))

(def email-parameters-category (str ServiceConfiguration$ParameterCategory/SlipStream_Support))

(def param-mapping
  {(.getName ServiceConfiguration$RequiredParameters/SLIPSTREAM_MAIL_HOST)     :host
   (.getName ServiceConfiguration$RequiredParameters/SLIPSTREAM_MAIL_PORT)     :port
   (.getName ServiceConfiguration$RequiredParameters/SLIPSTREAM_MAIL_USERNAME) :user
   (.getName ServiceConfiguration$RequiredParameters/SLIPSTREAM_MAIL_PASSWORD) :pass
   (.getName ServiceConfiguration$RequiredParameters/SLIPSTREAM_MAIL_SSL)      :ssl})

;;
;; smtp parameter schema
;;

(def SmtpParameters
  {:host                  s/Str
   (s/optional-key :port) s/Int
   (s/optional-key :from) s/Str
   :user                  s/Str
   :pass                  s/Str
   (s/optional-key :ssl)  s/Str})

(defn key-fn
  [key]
  (get param-mapping key))

(defn value-fn
  [value]
  (.getValue value))

(defn str->int
  "Converts the argument into an integer if possible.  If the conversion
   fails for any reason, the argument itself is returned."
  [s]
  (try
    (Integer/valueOf s)
    (catch Exception ex
      s)))

(defn convert-port
  "Converts value of :port key to an integer if possible."
  [{:keys [port] :as m}]
  (if port
    (assoc m :port (str->int port))
    m))

(defn get-smtp-parameters
  "Retrieves the SMTP parameters from the SlipStream service
   configuration."
  []
  (try
    (->> email-parameters-category
         (.getParameters (ServiceConfiguration/load))
         (filter (fn [[k _]] (key-fn k)))
         (map (fn [[k v]] [(key-fn k) (value-fn v)]))
         (into {})
         (convert-port)
         (s/validate SmtpParameters))
    (catch Exception e
      (log/warn "invalid SMTP parameters: " (str e)))))

(def fmt-renewal-failure-msg "
An attempt to renew your credential on the SlipStream server
has failed.  The renewal be tried again if there is sufficient
time left on the current credential (usually > 6 min).

The parameters for this credential are:

id     = %s
type   = %s
expiry = %s

Please be sure that appropriate credentials are available (for
example on the MyProxy server) for renewal.  If the credential
expires, then you will need to initialize a new credential in
your user account via the SlipStream server.
")

(def fmt-create-failure-msg "
The creation of your credential on the SlipStream server
has failed.  The type of credential to create was:

%s

Please be sure that appropriate credentials are available (for
example on the MyProxy server) and that you've given SlipStream
correct values for the parameters.
")

(defn get-sender
  [smtp]
  (if smtp
    (or (:from smtp)
        (str (:user smtp) "@" (:host smtp)))))

(defn get-body
  [{:keys [id subtypeURI expiry]}]
  (let [expiry-date (if expiry
                      (tf/unparse (tf/formatters :basic-date-time)
                                  (tc/from-long (* 1000 expiry)))
                      "unknown")]
    (format fmt-renewal-failure-msg id subtypeURI expiry-date)))

(defn get-create-body
  [{:keys [subtypeURI]}]
  (format fmt-create-failure-msg subtypeURI))

(defn renewal-failure
  [{:keys [id email] :as credential}]
  (if email
    (if-let [smtp (get-smtp-parameters)]
      (let [msg {:from    (get-sender smtp)
                 :to      [email]
                 :subject "SlipStream credential renewal failure"
                 :body    (get-body credential)}
            result (postal/send-message smtp msg)]
        (if-not (zero? (:code result))
          (log/error "error sending notification:" id (:error result) (:message result))
          (log/info "notification sent for renewal failure:" id))))))

(defn create-failure
  [{:keys [email] :as template}]
  (if email
    (if-let [smtp (get-smtp-parameters)]
      (let [msg {:from    (get-sender smtp)
                 :to      [email]
                 :subject "SlipStream credential creation failure"
                 :body    (get-create-body template)}
            result (postal/send-message smtp msg)]
        (if-not (zero? (:code result))
          (log/error "error sending notification:" (:error result) (:message result))
          (log/info "notification sent for creation failure to" email))))))
