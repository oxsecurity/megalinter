#!/usr/bin/env node

/**
 * CRUD operations for Kibana Dashboards and Visualizations using the API.
 *
 * Usage:
 *   ./kibana-dashboards.js dashboard get <id>              - Get dashboard definition
 *   ./kibana-dashboards.js dashboard create <file|->       - Create dashboard
 *   ./kibana-dashboards.js dashboard update <id> <file|->  - Update dashboard
 *   ./kibana-dashboards.js dashboard upsert <id> <file|->  - Create or update dashboard
 *   ./kibana-dashboards.js dashboard delete <id>           - Delete dashboard
 *
 *   ./kibana-dashboards.js vis list [search]              - List Visualizations
 *   ./kibana-dashboards.js vis get <id>                   - Get Visualization
 *   ./kibana-dashboards.js vis create <file|->            - Create Visualization
 *   ./kibana-dashboards.js vis update <id> <file|->       - Update Visualization
 *   ./kibana-dashboards.js vis upsert <id> <file|->       - Create or update Visualization
 *   ./kibana-dashboards.js vis delete <id>                - Delete Visualization
 *
 *   ./kibana-dashboards.js test                            - Test Kibana connection
 */

// =============================================================================
// Stdin Reading
// =============================================================================

async function readStdin() {
  return new Promise((resolve, reject) => {
    let data = "";

    process.stdin.setEncoding("utf8");

    if (process.stdin.isTTY) {
      reject(new Error("No input provided via stdin. Use a file path or pipe JSON input."));
      return;
    }

    process.stdin.on("readable", () => {
      let chunk;
      while ((chunk = process.stdin.read()) !== null) {
        data += chunk;
      }
    });

    process.stdin.on("end", () => {
      resolve(data);
    });

    process.stdin.on("error", (err) => {
      reject(err);
    });
  });
}

// =============================================================================
// File System Helpers
// =============================================================================

import { readFileSync, existsSync } from "fs";

async function loadSpec(filePathOrStdin) {
  let content;

  if (filePathOrStdin === "-" || filePathOrStdin === "--stdin") {
    content = await readStdin();
  } else {
    if (!existsSync(filePathOrStdin)) {
      throw new Error(`File not found: ${filePathOrStdin}`);
    }
    content = readFileSync(filePathOrStdin, "utf-8");
  }

  return JSON.parse(content);
}

// =============================================================================
// Kibana Client Setup
// =============================================================================

function getKibanaConfig() {
  const cloudId = process.env.KIBANA_CLOUD_ID || process.env.ELASTICSEARCH_CLOUD_ID;
  let url = process.env.KIBANA_URL;

  if (!url && cloudId) {
    try {
      const parts = cloudId.split(":");
      if (parts.length === 2) {
        const decoded = Buffer.from(parts[1], "base64").toString("utf8");
        const decodedParts = decoded.split("$");
        if (decodedParts.length >= 3 && decodedParts[2]) {
          const domain = decodedParts[0];
          const kibanaUuid = decodedParts[2];

          let host = domain;
          let port = "";
          if (domain.includes(":")) {
            const splitDomain = domain.split(":");
            host = splitDomain[0];
            port = `:${splitDomain[1]}`;
          } else {
            port = ":443";
          }

          url = `https://${kibanaUuid}.${host}${port}`;
        }
      }
    } catch (e) {
      console.error("Error parsing Cloud ID:", e.message);
    }
  }

  const username = process.env.KIBANA_USERNAME || process.env.ELASTICSEARCH_USERNAME;
  const password = process.env.KIBANA_PASSWORD || process.env.ELASTICSEARCH_PASSWORD;
  const apiKey = process.env.KIBANA_API_KEY || process.env.ELASTICSEARCH_API_KEY;
  const spaceId = process.env.KIBANA_SPACE_ID;
  const insecure = process.env.KIBANA_INSECURE === "true";

  if (!url) {
    console.error("Error: No Kibana connection configured.");
    console.error("");
    console.error("Set one of these environment variable combinations:");
    console.error("  1. Elastic Cloud: KIBANA_CLOUD_ID + KIBANA_API_KEY");
    console.error("  2. URL + API Key: KIBANA_URL + KIBANA_API_KEY");
    console.error("  3. Basic Auth: KIBANA_URL + KIBANA_USERNAME + KIBANA_PASSWORD");
    console.error("");
    console.error("For local development, use start-local to run Elasticsearch and Kibana via Docker:");
    console.error("  https://github.com/elastic/start-local");
    console.error("");
    console.error("  curl -fsSL https://elastic.co/start-local | sh");
    console.error("");
    console.error("Then configure the environment:");
    console.error("  source elastic-start-local/.env");
    console.error('  export KIBANA_URL="$KB_LOCAL_URL"');
    console.error('  export KIBANA_USERNAME="elastic"');
    console.error('  export KIBANA_PASSWORD="$ES_LOCAL_PASSWORD"');
    process.exit(1);
  }

  return { url, username, password, apiKey, spaceId, insecure };
}

function getHeaders(config) {
  const headers = {
    "Content-Type": "application/json",
    "kbn-xsrf": "true",
    "User-Agent": "elastic-agentic",
  };

  if (config.apiKey) {
    headers["Authorization"] = `ApiKey ${config.apiKey}`;
  } else if (config.username && config.password) {
    const auth = Buffer.from(`${config.username}:${config.password}`).toString("base64");
    headers["Authorization"] = `Basic ${auth}`;
  }

  return headers;
}

function getBasePath(config) {
  let basePath = config.url.replace(/\/$/, "");
  if (config.spaceId && config.spaceId !== "default") {
    basePath += `/s/${config.spaceId}`;
  }
  return basePath;
}

async function kibanaFetch(path, options = {}) {
  const config = getKibanaConfig();
  const basePath = getBasePath(config);
  const url = `${basePath}${path}`;

  const fetchOptions = {
    ...options,
    headers: {
      ...getHeaders(config),
      ...options.headers,
    },
  };

  // Handle insecure TLS
  if (config.insecure && typeof process !== "undefined") {
    process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";
  }

  try {
    const response = await fetch(url, fetchOptions);
    const contentType = response.headers.get("content-type");

    let data;
    if (contentType && contentType.includes("application/json")) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    if (!response.ok) {
      return {
        success: false,
        status: response.status,
        error: data.message || data.error || `HTTP ${response.status}`,
        details: data,
      };
    }

    return { success: true, data };
  } catch (error) {
    return {
      success: false,
      error: error.message,
      details: error,
    };
  }
}

// =============================================================================
// Dashboards API
// =============================================================================

/**
 * Get a dashboard by ID
 * GET /api/dashboards/:id (with version header)
 */
async function getDashboard(id) {
  return kibanaFetch(`/api/dashboards/${encodeURIComponent(id)}`, {
    headers: { "Elastic-Api-Version": "2023-10-31" },
  });
}

/**
 * Create a dashboard
 * POST /api/dashboards (with version header)
 * Body: { title, panels, time_range?, ... }
 *
 * Accepts both formats:
 *   - Flat: { title, panels, ... }
 *   - Wrapped (legacy): { id?, data: { title, panels, ... }, spaces? }
 * The API expects the flat format; this function unwraps if needed.
 * POST does not accept an id parameter. Use PUT for upserts.
 */
async function createDashboard(definition) {
  const body = definition.data
    ? definition.data
    : (() => {
        const { id, spaces, ...rest } = definition;
        return rest;
      })();

  return kibanaFetch("/api/dashboards", {
    method: "POST",
    headers: { "Elastic-Api-Version": "2023-10-31" },
    body: JSON.stringify(body),
  });
}

/**
 * Update a dashboard
 * PUT /api/dashboards/:id (with version header)
 * Body: { title, panels, ... } - do NOT include id or spaces
 *
 * Accepts both formats:
 *   - Flat: { title, panels, ... }
 *   - Wrapped (legacy): { data: { title, panels, ... } }
 */
async function updateDashboard(id, definition) {
  const body = definition.data
    ? definition.data
    : (() => {
        const { id: _id, spaces, ...rest } = definition;
        return rest;
      })();

  return kibanaFetch(`/api/dashboards/${encodeURIComponent(id)}`, {
    method: "PUT",
    headers: { "Elastic-Api-Version": "2023-10-31" },
    body: JSON.stringify(body),
  });
}

/**
 * Delete a dashboard
 * DELETE /api/dashboards/:id (with version header)
 */
async function deleteDashboard(id) {
  return kibanaFetch(`/api/dashboards/${encodeURIComponent(id)}`, {
    method: "DELETE",
    headers: { "Elastic-Api-Version": "2023-10-31" },
  });
}

// =============================================================================
// Visualizations API
// =============================================================================

/**
 * List Visualizations
 * GET /api/visualizations?query=&page=&per_page=
 */
async function listVisualizations(query = "", page = 1, per_page = 100) {
  const params = new URLSearchParams({ page: String(page), per_page: String(per_page) });
  if (query) {
    params.set("query", query);
  }
  return kibanaFetch(`/api/visualizations?${params.toString()}`, {
    headers: { "Elastic-Api-Version": "2023-10-31" },
  });
}

/**
 * Get a Visualization by ID
 * GET /api/visualizations/:id
 */
async function getVisualization(id) {
  return kibanaFetch(`/api/visualizations/${id}`, {
    headers: { "Elastic-Api-Version": "2023-10-31" },
  });
}

/**
 * Create a Visualization
 * POST /api/visualizations
 * Body: visualization definition (without id)
 */
async function createVisualization(definition) {
  return kibanaFetch("/api/visualizations", {
    method: "POST",
    headers: { "Elastic-Api-Version": "2023-10-31" },
    body: JSON.stringify(definition),
  });
}

/**
 * Update a Visualization
 * PUT /api/visualizations/:id
 * Body: visualization definition
 */
async function updateVisualization(id, definition) {
  return kibanaFetch(`/api/visualizations/${id}`, {
    method: "PUT",
    headers: { "Elastic-Api-Version": "2023-10-31" },
    body: JSON.stringify(definition),
  });
}

/**
 * Delete a Visualization
 * DELETE /api/visualizations/:id
 */
async function deleteVisualization(id) {
  return kibanaFetch(`/api/visualizations/${id}`, {
    method: "DELETE",
    headers: { "Elastic-Api-Version": "2023-10-31" },
  });
}

// =============================================================================
// Test Connection
// =============================================================================

function parseVersion(versionString) {
  if (!versionString) return { major: 0, minor: 0, patch: 0, snapshot: false, raw: "unknown" };
  const clean = versionString.replace(/-SNAPSHOT.*$/, "");
  const [major, minor, patch] = clean.split(".").map(Number);
  return { major, minor, patch: patch || 0, snapshot: versionString.includes("-SNAPSHOT"), raw: versionString };
}

async function testConnection() {
  const result = await kibanaFetch("/api/status");

  if (result.success) {
    const status = result.data;
    const versionString = status.version?.number || "unknown";
    const buildFlavor = status.version?.build_flavor || "default";

    // Serverless Kibana can be identified by build_flavor or a non-semver version string
    const isSemver = /^\d+\.\d+\.\d+/.test(versionString);
    const isServerless = buildFlavor === "serverless" || (!isSemver && versionString !== "unknown");

    const parsed = isSemver ? parseVersion(versionString) : parseVersion("8.11.0");

    return {
      success: true,
      version: isServerless && !isSemver ? `${versionString} (Serverless)` : versionString,
      parsed,
      buildFlavor: isServerless ? "serverless" : buildFlavor,
      isServerless,
      status: status.status?.overall?.level || "unknown",
      name: status.name || "unknown",
    };
  }

  return result;
}

// =============================================================================
// Output Formatting
// =============================================================================

function formatDashboard(item) {
  const lines = [];
  lines.push("=== Dashboard ===");
  lines.push(`ID: ${item.id}`);

  if (item.spaces && item.spaces.length > 0) {
    lines.push(`Spaces: ${item.spaces.join(", ")}`);
  }

  if (item.meta) {
    lines.push(`Created: ${item.meta.created_at || "unknown"}`);
    lines.push(`Updated: ${item.meta.updated_at || "unknown"}`);
    lines.push(`Managed: ${item.meta.managed || false}`);
  }

  if (item.data) {
    lines.push(`Title: ${item.data.title || "Untitled"}`);
    lines.push(`Panels: ${item.data.panels?.length || 0}`);
    if (item.data.time_range) {
      lines.push(`Time Range: ${item.data.time_range.from} to ${item.data.time_range.to}`);
    }
  }

  lines.push("\n--- Definition (data) ---");
  lines.push(JSON.stringify(item.data, null, 2));

  return lines.join("\n");
}

function formatVisList(response) {
  const items = response.data || [];
  const meta = response.meta || {};

  if (!items || items.length === 0) {
    return "No Visualizations found.";
  }

  const lines = ["ID".padEnd(40) + " | " + "Type".padEnd(15) + " | " + "Title"];
  lines.push("-".repeat(40) + "-+-" + "-".repeat(15) + "-+-" + "-".repeat(40));

  for (const item of items) {
    const id = item.id || "unknown";
    const type = item.data?.type || "unknown";
    const title = item.data?.title || "Untitled";
    lines.push(`${id.substring(0, 40).padEnd(40)} | ${type.padEnd(15)} | ${title}`);
  }

  lines.push("");
  lines.push(
    `Page ${meta.page || 1} | Per Page: ${meta.per_page || items.length} | Total: ${meta.total || items.length}`,
  );

  return lines.join("\n");
}

function formatVisualization(item) {
  const lines = [];
  lines.push("=== Visualization ===");
  lines.push(`ID: ${item.id}`);

  if (item.meta) {
    lines.push(`Created: ${item.meta.created_at || "unknown"}`);
    lines.push(`Updated: ${item.meta.updated_at || "unknown"}`);
    lines.push(`Managed: ${item.meta.managed || false}`);
  }

  lines.push("\n--- Definition (data) ---");
  lines.push(JSON.stringify(item.data, null, 2));

  return lines.join("\n");
}

// =============================================================================
// Main CLI
// =============================================================================

async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args[0] === "help" || args[0] === "--help" || args[0] === "-h") {
    printUsage();
    process.exit(args.length === 0 ? 1 : 0);
  }

  const [resource, action, ...params] = args;

  try {
    switch (resource) {
      case "test":
        await handleTest();
        break;

      case "dashboard":
      case "dashboards":
      case "dash":
        await handleDashboard(action, params);
        break;

      case "vis":
        await handleVis(action, params);
        break;

      default:
        console.error(`Unknown resource: ${resource}`);
        printUsage();
        process.exit(1);
    }
  } catch (error) {
    console.error("Error:", error.message);
    process.exit(1);
  }
}

async function handleTest() {
  console.log("=== Testing Kibana Connection ===\n");

  const result = await testConnection();

  if (result.success) {
    const { parsed, isServerless, buildFlavor } = result;
    const { major, minor } = parsed;

    console.log("✓ Connected successfully!");
    console.log(`  Name:         ${result.name}`);
    console.log(`  Version:      ${result.version}`);
    console.log(`  Build flavor: ${buildFlavor}`);
    if (parsed.snapshot) console.log(`  Snapshot:     yes (treating as ${major}.${minor})`);
    if (isServerless) console.log("  NOTE: Serverless — features available regardless of reported version");
    console.log(`  Status:       ${result.status}`);

    // Check if Dashboards API is available
    console.log("\n=== Dashboards API Check ===");
    // Try to get a non-existent dashboard - 404 means API is available
    const dashResult = await getDashboard("__test_nonexistent__");
    if (dashResult.success || dashResult.status === 404) {
      console.log("✓ Dashboards API is available");
    } else if (dashResult.status === 400) {
      console.log("⚠ Dashboards API may not be available in this version");
    } else {
      console.log("✗ Dashboards API check failed:", dashResult.error);
    }

    // Check if Visualizations API is available
    console.log("\n=== Visualizations API Check ===");
    const visResult = await listVisualizations("", 1, 1);
    if (visResult.success) {
      console.log("✓ Visualizations API is available");
    } else {
      console.log("✗ Visualizations API check failed:", visResult.error);
    }
  } else {
    console.error("✗ Connection failed:", result.error);
    if (result.details) {
      console.error("Details:", JSON.stringify(result.details, null, 2));
    }
    process.exit(1);
  }
}

async function handleDashboard(action, params) {
  switch (action) {
    case "get": {
      const id = params[0];
      if (!id) {
        console.error("Error: Dashboard ID required");
        console.error("Usage: ./kibana-dashboards.js dashboard get <id>");
        process.exit(1);
      }

      const result = await getDashboard(id);

      if (result.success) {
        console.log(formatDashboard(result.data));
      } else {
        console.error("Error:", result.error);
        process.exit(1);
      }
      break;
    }

    case "create": {
      const file = params[0];

      if (!file) {
        console.error("Error: Definition file/stdin required");
        console.error("Usage: ./kibana-dashboards.js dashboard create <file.json>");
        console.error(
          '       echo \'{"title":"My Dashboard","panels":[]}\' | ./kibana-dashboards.js dashboard create -',
        );
        process.exit(1);
      }

      const definition = await loadSpec(file);
      const result = await createDashboard(definition);

      if (result.success) {
        console.log("✓ Dashboard created successfully!");
        console.log(`  ID: ${result.data.id}`);
        console.log(`  Title: ${result.data.data?.title || "Untitled"}`);
        console.log(`  Panels: ${result.data.data?.panels?.length || 0}`);
        if (result.data.spaces) {
          console.log(`  Spaces: ${result.data.spaces.join(", ")}`);
        }
      } else {
        console.error("Error:", result.error);
        if (result.details) {
          console.error("Details:", JSON.stringify(result.details, null, 2));
        }
        process.exit(1);
      }
      break;
    }

    case "update": {
      const id = params[0];
      const file = params[1];

      if (!id || !file) {
        console.error("Error: Dashboard ID and definition file/stdin required");
        console.error("Usage: ./kibana-dashboards.js dashboard update <id> <file.json>");
        console.error(
          '       echo \'{"title":"Updated","panels":[...]}\' | ./kibana-dashboards.js dashboard update <id> -',
        );
        process.exit(1);
      }

      const definition = await loadSpec(file);
      const result = await updateDashboard(id, definition);

      if (result.success) {
        console.log("✓ Dashboard updated successfully!");
        console.log(`  ID: ${result.data.id}`);
        console.log(`  Title: ${result.data.data?.title || "Untitled"}`);
      } else {
        console.error("Error:", result.error);
        if (result.details) {
          console.error("Details:", JSON.stringify(result.details, null, 2));
        }
        process.exit(1);
      }
      break;
    }

    case "upsert": {
      const id = params[0];
      const file = params[1];

      if (!id || !file) {
        console.error("Error: Dashboard ID and definition file/stdin required");
        console.error("Usage: ./kibana-dashboards.js dashboard upsert <id> <file.json>");
        process.exit(1);
      }

      const definition = await loadSpec(file);
      const result = await updateDashboard(id, definition);

      if (result.success) {
        console.log("✓ Dashboard upserted successfully!");
        console.log(`  ID: ${result.data.id}`);
        console.log(`  Title: ${result.data.data?.title || "Untitled"}`);
      } else {
        console.error("Error:", result.error);
        if (result.details) {
          console.error("Details:", JSON.stringify(result.details, null, 2));
        }
        process.exit(1);
      }
      break;
    }

    case "delete":
    case "rm": {
      const id = params[0];
      if (!id) {
        console.error("Error: Dashboard ID required");
        console.error("Usage: ./kibana-dashboards.js dashboard delete <id>");
        process.exit(1);
      }

      const result = await deleteDashboard(id);

      if (result.success) {
        console.log("✓ Dashboard deleted successfully!");
      } else {
        console.error("Error:", result.error);
        process.exit(1);
      }
      break;
    }

    default:
      console.error(`Unknown dashboard action: ${action}`);
      console.error("Available actions: get, create, update, upsert, delete");
      process.exit(1);
  }
}

async function handleVis(action, params) {
  switch (action) {
    case "list":
    case "ls": {
      const query = params[0] || "";
      const result = await listVisualizations(query);

      if (result.success) {
        console.log("=== Visualizations ===\n");
        console.log(formatVisList(result.data));
      } else {
        console.error("Error:", result.error);
        process.exit(1);
      }
      break;
    }

    case "get": {
      const id = params[0];
      if (!id) {
        console.error("Error: Visualization ID required");
        console.error("Usage: ./kibana-dashboards.js vis get <id>");
        process.exit(1);
      }

      const result = await getVisualization(id);

      if (result.success) {
        console.log(formatVisualization(result.data));
      } else {
        console.error("Error:", result.error);
        process.exit(1);
      }
      break;
    }

    case "create": {
      const file = params[0];

      if (!file) {
        console.error("Error: Definition file/stdin required");
        console.error("Usage: ./kibana-dashboards.js vis create <file.json>");
        console.error('       echo \'{"type":"metric",...}\' | ./kibana-dashboards.js vis create -');
        process.exit(1);
      }

      const definition = await loadSpec(file);
      const result = await createVisualization(definition);

      if (result.success) {
        console.log("✓ Visualization created successfully!");
        console.log(`  ID: ${result.data.id}`);
        console.log(`  Type: ${result.data.data?.type || "unknown"}`);
      } else {
        console.error("Error:", result.error);
        if (result.details) {
          console.error("Details:", JSON.stringify(result.details, null, 2));
        }
        process.exit(1);
      }
      break;
    }

    case "update": {
      const id = params[0];
      const file = params[1];

      if (!id || !file) {
        console.error("Error: Visualization ID and definition file/stdin required");
        console.error("Usage: ./kibana-dashboards.js vis update <id> <file.json>");
        console.error('       echo \'{"type":"metric",...}\' | ./kibana-dashboards.js vis update <id> -');
        process.exit(1);
      }

      const definition = await loadSpec(file);
      const result = await updateVisualization(id, definition);

      if (result.success) {
        console.log("✓ Visualization updated successfully!");
        console.log(`  ID: ${result.data.id}`);
      } else {
        console.error("Error:", result.error);
        if (result.details) {
          console.error("Details:", JSON.stringify(result.details, null, 2));
        }
        process.exit(1);
      }
      break;
    }

    case "upsert": {
      const id = params[0];
      const file = params[1];

      if (!id || !file) {
        console.error("Error: Visualization ID and definition file/stdin required");
        console.error("Usage: ./kibana-dashboards.js vis upsert <id> <file.json>");
        process.exit(1);
      }

      const definition = await loadSpec(file);
      const result = await updateVisualization(id, definition);

      if (result.success) {
        console.log("✓ Visualization upserted successfully!");
        console.log(`  ID: ${result.data.id}`);
      } else {
        console.error("Error:", result.error);
        if (result.details) {
          console.error("Details:", JSON.stringify(result.details, null, 2));
        }
        process.exit(1);
      }
      break;
    }

    case "delete":
    case "rm": {
      const id = params[0];
      if (!id) {
        console.error("Error: Visualization ID required");
        console.error("Usage: ./kibana-dashboards.js vis delete <id>");
        process.exit(1);
      }

      const result = await deleteVisualization(id);

      if (result.success) {
        console.log("✓ Visualization deleted successfully!");
      } else {
        console.error("Error:", result.error);
        process.exit(1);
      }
      break;
    }

    default:
      console.error(`Unknown vis action: ${action}`);
      console.error("Available actions: list, get, create, update, upsert, delete");
      process.exit(1);
  }
}

function printUsage() {
  console.log(`
Kibana as Code - Dashboards & Visualizations API

Usage:
  ./kibana-dashboards.js <resource> <action> [options]

Resources:
  dashboard  Manage dashboards via API
  vis        Manage visualizations via API
  test       Test Kibana connection and API availability

Dashboard Actions:
  get <id>                         Get dashboard definition
  create <file|->                  Create from JSON file (use - for stdin)
  update <id> <file|->             Update from JSON file (use - for stdin)
  upsert <id> <file|->             Create or update (use - for stdin)
  delete <id>                      Delete dashboard

Visualization Actions:
  list [search]                    List Visualizations (optional search)
  get <id>                         Get visualization definition
  create <file|->                  Create from JSON file (use - for stdin)
  update <id> <file|->             Update from JSON file (use - for stdin)
  upsert <id> <file|->             Create or update (use - for stdin)
  delete <id>                      Delete visualization

Environment Variables:
  KIBANA_CLOUD_ID            Elastic Cloud deployment ID (if KIBANA_URL is not set)
  KIBANA_URL                 Kibana URL (required if KIBANA_CLOUD_ID is not set)
  KIBANA_USERNAME            Username for basic auth
  KIBANA_PASSWORD            Password for basic auth
  KIBANA_API_KEY             API key for authentication
  KIBANA_SPACE_ID            Kibana space ID (optional)
  KIBANA_INSECURE            Set to "true" to skip TLS verification

Dashboard Panel Types:
  vis                      Visualization panel
  markdown       Markdown panel
  links                    Links panel
  map                      Maps panel
  discover_session         Saved search panel
  (and more embeddable types)

Chart Types:
  metric, xy, gauge, heatmap, tag_cloud,
  region_map, data_table, pie, treemap, mosaic, waffle

Examples:
  # Test connection and API availability
  ./kibana-dashboards.js test

  # Get a dashboard definition
  ./kibana-dashboards.js dashboard get my-dashboard-id

  # Create a dashboard from file
  ./kibana-dashboards.js dashboard create ./my-dashboard.json

  # Create a dashboard from stdin
  echo '{"title":"Test","panels":[]}' | \\
    ./kibana-dashboards.js dashboard create -

  # Update a dashboard (do not include id/spaces in body)
  echo '{"title":"Updated Title","panels":[]}' | \\
    ./kibana-dashboards.js dashboard update my-dashboard-id -

  # Delete a dashboard
  ./kibana-dashboards.js dashboard delete my-dashboard-id

  # List all Visualizations
  ./kibana-dashboards.js vis list

  # Create metric visualization from stdin
  echo '{"type":"metric","data_source":{"type":"esql","query":"FROM logs | STATS count=COUNT()"},"metrics":[{"type":"primary","column":"count"}]}' | \\
    ./kibana-dashboards.js vis create -

  # Copy dashboard: get from source, create on destination
  ./kibana-dashboards.js dashboard get source-id > dashboard.json
  # Edit dashboard.json as needed, then create
  ./kibana-dashboards.js dashboard create dashboard.json
`);
}

main().catch((error) => {
  console.error("Fatal error:", error.message);
  process.exit(1);
});
