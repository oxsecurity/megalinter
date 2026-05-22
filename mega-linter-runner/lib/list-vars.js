import { default as fs } from "fs-extra";
import * as path from "path";
import { dirname } from "path";
import { fileURLToPath } from "url";

const VARS_FILE = path.join(
  dirname(fileURLToPath(import.meta.url)),
  "megalinter-vars.json",
);

function loadVars() {
  if (!fs.existsSync(VARS_FILE)) {
    throw new Error(
      `Bundled variables file not found at ${VARS_FILE}. Re-run \`make megalinter-build\` to regenerate it.`,
    );
  }
  return fs.readJsonSync(VARS_FILE);
}

function matches(variable, pattern) {
  if (!pattern) return true;
  const p = pattern.toLowerCase();
  return (
    variable.name.toLowerCase().includes(p) ||
    (variable.category || "").toLowerCase().includes(p) ||
    (variable.section || "").toLowerCase().includes(p) ||
    (variable.title || "").toLowerCase().includes(p)
  );
}

function formatType(variable) {
  const t = variable.type;
  if (Array.isArray(t)) return t.join(" | ");
  return t || "string";
}

function renderHuman(variables, pattern, meta) {
  const lines = [];
  if (pattern) {
    lines.push(
      `MegaLinter variables matching "${pattern}" (${variables.length}/${meta.variable_count}):`,
    );
  } else {
    lines.push(`MegaLinter variables (${variables.length} total):`);
  }
  lines.push("");
  for (const v of variables) {
    lines.push(`  ${v.name}  [${formatType(v)}]  (${v.category || "GENERAL"})`);
    if (v.title) {
      lines.push(`    ${v.title}`);
    }
    if (v.description && v.description !== v.title) {
      lines.push(`    ${v.description}`);
    }
    if (v.default !== undefined) {
      lines.push(`    default: ${JSON.stringify(v.default)}`);
    }
    if (Array.isArray(v.enum) && v.enum.length > 0) {
      lines.push(`    allowed: ${v.enum.join(", ")}`);
    }
    if (Array.isArray(v.items_enum) && v.items_enum.length > 0) {
      const preview = v.items_enum.slice(0, 6).join(", ");
      const suffix =
        v.items_enum.length > 6
          ? `, … (${v.items_enum.length} values)`
          : "";
      lines.push(`    item values: ${preview}${suffix}`);
    }
    if (Array.isArray(v.examples) && v.examples.length > 0) {
      lines.push(`    examples: ${v.examples.map((e) => JSON.stringify(e)).join(", ")}`);
    }
    lines.push("");
  }
  lines.push(`Reference: ${meta.doc_url}`);
  lines.push(
    pattern
      ? "Pass variables with: mega-linter-runner -e KEY=VALUE"
      : "Filter results: mega-linter-runner --list-vars <pattern>",
  );
  return lines.join("\n");
}

export function listVars({ pattern, asJson } = {}) {
  const data = loadVars();
  const all = Object.values(data.variables);
  const filtered = all.filter((v) => matches(v, pattern));
  if (asJson) {
    return {
      stdout: JSON.stringify(
        {
          _meta: { ...data._meta, pattern: pattern || null, returned: filtered.length },
          variables: filtered,
        },
        null,
        2,
      ),
    };
  }
  return { stdout: renderHuman(filtered, pattern, data._meta) };
}
