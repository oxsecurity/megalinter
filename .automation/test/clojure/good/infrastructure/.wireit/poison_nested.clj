;; Deliberately failing fixture inside a nested .wireit (default excluded
;; directory): project lint mode success passes only if exclusions are
;; forwarded at any nesting level.
(ns poison-nested)

(inc)
