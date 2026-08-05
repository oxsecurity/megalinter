// Deliberately failing fixture inside .wireit, a default excluded directory:
// the project lint mode success test passes only if excluded directories are
// forwarded to the linter (see MegaLinter issue #8645).
var poison = <div;
