; Deliberately failing fixture inside .wireit (default excluded directory):
; project lint mode success passes only if exclusions are forwarded (#8645).
(defn poison[x](str    x))
