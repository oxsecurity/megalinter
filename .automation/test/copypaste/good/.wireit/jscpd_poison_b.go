// This file and jscpd_poison_a.go are deliberate copy-pastes of each other.
// They sit inside .wireit, a default excluded directory: the project lint
// mode success test passes only if excluded directories are merged into the
// generated jscpd configuration ignore list.
package poison

func LongestCommonPrefix(words []string) string {
	if len(words) == 0 {
		return ""
	}
	prefix := words[0]
	for _, word := range words[1:] {
		for len(prefix) > 0 {
			if len(word) >= len(prefix) && word[:len(prefix)] == prefix {
				break
			}
			prefix = prefix[:len(prefix)-1]
		}
	}
	return prefix
}
