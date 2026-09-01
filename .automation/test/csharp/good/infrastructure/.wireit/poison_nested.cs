// Deliberately failing fixture inside a NESTED .wireit, a default excluded
// directory: the project lint mode success test passes only if excluded
// directories are forwarded at any nesting level (see MegaLinter issue #8806).
class   PoisonNested{public   void M( ){  }}
