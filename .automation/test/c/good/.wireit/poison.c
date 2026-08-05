// Deliberately failing fixture inside .wireit, a default excluded directory:
// the project lint mode success test passes only if excluded directories are
// forwarded to the linter (see MegaLinter issue #8645).
void poison(void) {
    int a[1];
    a[2] = 0;
}
