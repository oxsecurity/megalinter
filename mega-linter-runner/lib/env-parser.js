const ENV_KEY_VALUE_RE = /^[A-Za-z_][A-Za-z0-9_]*=/;

// Expand a list of -e values, splitting the legacy comma-separated KEY=VAL,KEY=VAL form
// into multiple entries while preserving values that simply contain a comma
// (e.g. ENABLE_LINTERS=YAML_PRETTIER,YAML_YAMLLINT).
//
// Heuristic: split on `,` only when every comma-separated part looks like KEY=...
// Otherwise the comma belongs to the value of a single env var.
export function expandEnvEntries(envList) {
  if (!Array.isArray(envList)) {
    return envList;
  }
  const result = [];
  for (const entry of envList) {
    if (typeof entry !== "string" || !entry.includes(",")) {
      result.push(entry);
      continue;
    }
    const parts = entry.split(",");
    const allLookLikeKv = parts.every((p) => ENV_KEY_VALUE_RE.test(p));
    if (allLookLikeKv && parts.length > 1) {
      result.push(...parts);
    } else {
      result.push(entry);
    }
  }
  return result;
}
