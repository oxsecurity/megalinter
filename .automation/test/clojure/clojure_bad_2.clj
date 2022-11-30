(  ns
 foo.bar.baz  "some doc"
    (:require (foo.bar [abc :as abc]
        def))
    (:use foo.bar.qux)
    (:import foo.bar.qux.Foo
      ;; Need this for the thing
      foo.bar.qux.Bar)
    )

(defn hello "says hi" (
      [] (hello "world")
  ) ([name]
  ( println "Hello," name  )
  ))


(comment
( let [x 3
    y 4]
  (+ (* x x
  )(* y y)
  ))

)