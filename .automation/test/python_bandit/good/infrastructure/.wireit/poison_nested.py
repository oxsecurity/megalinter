# Deliberately failing fixture inside a NESTED .wireit, a default excluded
# directory: the project lint mode success test passes only if excluded
# directories are forwarded at any nesting level, not only when they exist at
# the workspace root (see MegaLinter issue #8806).
import pickle

pickle.loads(b"poison")
