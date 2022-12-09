(ns clojure-good-1
  (:require
    [clojure.string :as string]))


(butlast [1 2 3])

(string/join "" "")


(defn calculation
  [x]
  (let [y (fn [] (inc x))]
    (y)))


(letfn
  [(f [g] (h g))
   (h [i] (f i))])


(defn incremetal
  []
  1)


(inc (incremetal))

(Thread/sleep 1000 1)


;; Here we switch to another namespace and require the previous:
#_{:clj-kondo/ignore [:namespace-name-mismatch]}


(ns bar
  (:require
    [clojure-good-1 :as good]))


(good/calculation 1)

{:a 1 :b 2}
#{1 2}
{:a 1 :b 2}

#_{:clj-kondo/ignore [:namespace-name-mismatch]}


(ns bar-test
  (:require
    [clojure.test :refer [deftest is testing]]))


(deftest oddity-test
  (testing "Is something odd?"
    (is (odd? (inc 1)))))
