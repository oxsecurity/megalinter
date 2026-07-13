;; --------------------------------------------------
;; Correctly formatted namespace
;; --------------------------------------------------


(ns clojure-good-2
  "Fraud API service component lifecycle management"
  (:gen-class)
  (:require
    [com.brunobonacci.mulog :as mulog]
    [integrant.core :as ig]
    ;; System dependencies
    [org.httpkit.server :as http-server]
    [practicalli.gameboard.environment :as environment]
    ;; Application dependencies
    [practicalli.gameboard.router :as router]))


;; --------------------------------------------------
;; Configure and start application components

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


(defn stop
  "Stop service using Integrant halt!"
  [system]
  (mulog/log ::http-server-sigterm :system system :local-time (java.time.LocalDateTime/now))
  ;; (println "Shutdown of Practicalli service via Integrant")
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
            {:app-name "Practicalli Service" :version  "0.1.0" :env profile})

        system (ig/init (environment/aero-prep profile))

        _ (mulog/log ::gameboard-system :system-config system)]

    ;; TODO: capture the reason for the shutdown - i.e. can we capture the sigterm
    (.addShutdownHook (Runtime/getRuntime) (Thread. ^Runnable #(stop system)))))
