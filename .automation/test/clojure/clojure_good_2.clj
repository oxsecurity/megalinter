;; --------------------------------------------------
;; Correctly formatted namespace
;; --------------------------------------------------


(ns practicalli.gameboard.service
  "Fraud API service component lifecycle management"
  (:gen-class)
  (:require
   ;; Application dependencies
   [practicalli.gameboard.router :as router]
   [practicalli.gameboard.environment :as environment]

   ;; System dependencies
   [org.httpkit.server :as http-server]
   [integrant.core :as ig]
   [com.brunobonacci.mulog :as mulog]))


;; --------------------------------------------------
;; Configure and start application components

;; Start mulog publisher for the given publisher type, i.e. console, cloud-watch
#_{:clj-kondo/ignore [:unused-binding]}
(defmethod ig/init-key ::log-publish
  [_ {:keys [mulog] :as config}]
  (mulog/log ::log-publish-component :publisher-config mulog :local-time (java.time.LocalDateTime/now))
  (let [publisher (mulog/start-publisher! mulog)]
    publisher))

;; Connection values for Relational Database
;; return hash-map of connection values: endpoint, access-key, secret-key
(defmethod ig/init-key ::relational-store
  [_ {:keys [connection] :as config}]
  (mulog/log ::persistence-component :connection connection :local-time (java.time.LocalDateTime/now))
  config)

;; Configure environment for router application, e.g. database connection details, etc.
(defmethod ig/init-key ::router
  [_ config]
  (mulog/log ::app-routing-component :app-config config)
  (router/app config))


;; HTTP server start - returns function to stop the server
(defmethod ig/init-key ::http-server
  [_ {:keys [handler port join?]}]
  (mulog/log ::http-server-component :handler handler :port port :local-time (java.time.LocalDateTime/now))
  (http-server/run-server handler {:port port :join? join?}))


;; Shutdown HTTP service
(defmethod ig/halt-key! ::http-server
  [_ http-server-instance]
  (mulog/log ::http-server-component-shutdown  :http-server-object http-server-instance :local-time (java.time.LocalDateTime/now))
  ;; Calling http instance shuts down that instance
  (http-server-instance))


;; Shutdown Log publishing
(defmethod ig/halt-key! ::log-publish
  [_ publisher]
  (mulog/log ::log-publish-component-shutdown :publisher-object publisher :local-time (java.time.LocalDateTime/now))
  ;; Pause so final messages have chance to be published
  (Thread/sleep 250)
  ;; Call publisher again to stop publishing
  (publisher))


(defn stop
  "Stop service using Integrant halt!"
  [system]
  (mulog/log ::http-server-sigterm :system system :local-time (java.time.LocalDateTime/now))
  ;; (println "Shutdown of Practicalli Gameboard service via Integrant")
  (ig/halt! system))


;; --------------------------------------------------
;; Application entry point

(defn -main
  "Practicalli service is started with `ig/init` and the Integrant configuration,
  with the return value bound to the namespace level `system` name.
  Aero is used to configure Integrant configuration based on profile (dev, test, prod),
  allowing environment specific configuration, e.g. mulog publisher
  The shutdown hook calling a zero arity function, gracefully stopping the service
  on receipt of a SIGTERM from the infrastructure, giving the application 30 seconds before forced termination."
  []

  (let [profile (or (keyword (System/getenv "SERVICE_PROFILE"))
                    :dev)

        ;; Add keys to every event / publish profile use to start the service
        _ (mulog/set-global-context!
           {:app-name "Practicalli Gameboard Service" :version  "0.1.0" :env profile})

        system (ig/init (environment/aero-prep profile))

        _ (mulog/log ::gameboard-system :system-config system)]

    ;; TODO: capture the reason for the shutdown - i.e. can we capture the sigterm
    (.addShutdownHook (Runtime/getRuntime) (Thread. ^Runnable #(stop system)))))
