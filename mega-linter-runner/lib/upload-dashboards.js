/**
 * @fileoverview Upload MegaLinter observability dashboards to Grafana,
 * Datadog, Elastic (Kibana) or New Relic.
 * Dashboard definitions are read from docs/dashboards of the MegaLinter
 * repository (fetched from GitHub raw, or from a local directory when
 * MEGALINTER_DASHBOARDS_DIR is defined).
 */

import fs from "fs-extra";
import path from "path";

const DASHBOARDS_BASE_URL =
  "https://raw.githubusercontent.com/oxsecurity/megalinter/main/docs/dashboards";

export const KNOWN_DASHBOARD_PROVIDERS = [
  "grafana",
  "datadog",
  "elastic",
  "newrelic",
];

export class DashboardUploader {
  constructor(provider, options = {}) {
    this.provider = provider;
    this.options = options;
    this.env = options.env || process.env;
  }

  async run() {
    if (!KNOWN_DASHBOARD_PROVIDERS.includes(this.provider)) {
      throw new Error(
        `Unknown dashboards provider: ${this.provider}. ` +
          `Allowed values: ${KNOWN_DASHBOARD_PROVIDERS.join(", ")}`
      );
    }
    const manifest = JSON.parse(await this.readDashboardFile("manifest.json"));
    const entries = manifest.dashboards.filter(
      (dashboard) => dashboard.provider === this.provider
    );
    const results = [];
    for (const entry of entries) {
      const content = await this.readDashboardFile(entry.file);
      const result = await this[this.provider](entry, content);
      console.log(
        `[MegaLinter dashboards] [${this.provider}] Uploaded ${entry.file}` +
          (result ? ` (${result})` : "")
      );
      results.push(result);
    }
    return results;
  }

  async readDashboardFile(relativePath) {
    const localDir = this.env.MEGALINTER_DASHBOARDS_DIR;
    if (localDir) {
      return await fs.readFile(path.join(localDir, relativePath), "utf8");
    }
    const response = await fetch(`${DASHBOARDS_BASE_URL}/${relativePath}`);
    if (!response.ok) {
      throw new Error(
        `Unable to fetch dashboard definition ${relativePath} (${response.status})`
      );
    }
    return await response.text();
  }

  requireEnv(names) {
    const missing = names.filter((name) => !this.env[name]);
    if (missing.length > 0) {
      throw new Error(
        `[MegaLinter dashboards] [${this.provider}] Missing environment variable(s): ${missing.join(", ")}`
      );
    }
  }

  async fetchJson(url, options, label) {
    const response = await fetch(url, options);
    const text = await response.text();
    if (!response.ok) {
      throw new Error(`${label} error (${response.status}): ${text.slice(0, 500)}`);
    }
    try {
      return JSON.parse(text);
    } catch {
      return {};
    }
  }

  // GRAFANA_URL + GRAFANA_TOKEN (service account token with dashboards:write)
  async grafana(entry, content) {
    this.requireEnv(["GRAFANA_URL", "GRAFANA_TOKEN"]);
    const host = this.env.GRAFANA_URL.replace(/\/$/, "");
    const headers = {
      Authorization: `Bearer ${this.env.GRAFANA_TOKEN}`,
      "Content-Type": "application/json",
    };
    const folderUid = "megalinter";
    // Create the folder if missing (409/412 = already exists)
    const folderResponse = await fetch(`${host}/api/folders`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        uid: folderUid,
        title: this.options.dashboardsFolder || "MegaLinter",
      }),
    });
    if (![200, 409, 412].includes(folderResponse.status)) {
      throw new Error(
        `Grafana folder error (${folderResponse.status}): ${await folderResponse.text()}`
      );
    }
    const dashboard = JSON.parse(content);
    dashboard.id = null;
    const result = await this.fetchJson(
      `${host}/api/dashboards/db`,
      {
        method: "POST",
        headers,
        body: JSON.stringify({ dashboard, folderUid, overwrite: true }),
      },
      "Grafana dashboard"
    );
    return result.url;
  }

  // DD_SITE (default datadoghq.com) + DD_API_KEY/DD_APP_KEY or DD_BEARER_TOKEN
  async datadog(entry, content) {
    const site = this.env.DD_SITE || "datadoghq.com";
    const headers = { "Content-Type": "application/json" };
    if (this.env.DD_API_KEY && this.env.DD_APP_KEY) {
      headers["DD-API-KEY"] = this.env.DD_API_KEY;
      headers["DD-APPLICATION-KEY"] = this.env.DD_APP_KEY;
    } else if (this.env.DD_BEARER_TOKEN) {
      headers["Authorization"] = `Bearer ${this.env.DD_BEARER_TOKEN}`;
    } else {
      this.requireEnv(["DD_BEARER_TOKEN (or DD_API_KEY + DD_APP_KEY)"]);
    }
    const dashboard = JSON.parse(content);
    const listing = await this.fetchJson(
      `https://api.${site}/api/v1/dashboard`,
      { headers },
      "Datadog dashboards list"
    );
    const existing = (listing.dashboards || []).filter(
      (item) => item.title === dashboard.title
    );
    let dashboardId = existing.length ? existing[0].id : null;
    if (dashboardId === null) {
      // First creation: obtain the dashboard id, then update it below so that
      // the __SELF_URL__ drill-down links point to the created dashboard
      const created = await this.fetchJson(
        `https://api.${site}/api/v1/dashboard`,
        { method: "POST", headers, body: JSON.stringify(dashboard) },
        "Datadog dashboard"
      );
      dashboardId = created.id;
    }
    const resolvedDashboard = JSON.parse(
      JSON.stringify(dashboard).replaceAll("__SELF_URL__", `/dashboard/${dashboardId}`)
    );
    const result = await this.fetchJson(
      `https://api.${site}/api/v1/dashboard/${dashboardId}`,
      { method: "PUT", headers, body: JSON.stringify(resolvedDashboard) },
      "Datadog dashboard"
    );
    return result.url;
  }

  // KIBANA_URL + ELASTIC_API_KEY
  async elastic(entry, content) {
    this.requireEnv(["KIBANA_URL", "ELASTIC_API_KEY"]);
    const host = this.env.KIBANA_URL.replace(/\/$/, "");
    const form = new FormData();
    form.append(
      "file",
      new Blob([content], { type: "application/ndjson" }),
      path.basename(entry.file)
    );
    const result = await this.fetchJson(
      `${host}/api/saved_objects/_import?overwrite=true`,
      {
        method: "POST",
        headers: {
          Authorization: `ApiKey ${this.env.ELASTIC_API_KEY}`,
          "kbn-xsrf": "true",
        },
        body: form,
      },
      "Kibana saved objects import"
    );
    return `${result.successCount} saved objects`;
  }

  // NEW_RELIC_API_KEY (user key) + NEW_RELIC_ACCOUNT_ID + optional NEW_RELIC_REGION (US/EU)
  async newrelic(entry, content) {
    this.requireEnv(["NEW_RELIC_API_KEY", "NEW_RELIC_ACCOUNT_ID"]);
    const region = (this.env.NEW_RELIC_REGION || "US").toUpperCase();
    const api =
      region === "EU"
        ? "https://api.eu.newrelic.com/graphql"
        : "https://api.newrelic.com/graphql";
    const accountId = parseInt(this.env.NEW_RELIC_ACCOUNT_ID, 10);
    const headers = {
      "API-Key": this.env.NEW_RELIC_API_KEY,
      "Content-Type": "application/json",
    };
    const resolvedContent = content.replaceAll(
      '"${NEW_RELIC_ACCOUNT_ID}"',
      String(accountId)
    );
    const PAGE_GUID_MARKERS = {
      __REPOSITORY_DETAIL_PAGE_GUID__: "Repository detail",
      __RATING_PAGE_GUID__: "Why this rating?",
    };
    // linkedEntityGuids markers live at widget top level (sibling of
    // rawConfiguration, as expected by the NerdGraph widget schema)
    const applyFacetLinks = (dashboardInput, guidsByMarker) => {
      for (const page of dashboardInput.pages || []) {
        for (const widget of page.widgets || []) {
          const guids = widget.linkedEntityGuids;
          if (!Array.isArray(guids)) {
            continue;
          }
          for (const marker of Object.keys(PAGE_GUID_MARKERS)) {
            if (guids.includes(marker)) {
              const pageGuid = guidsByMarker[marker];
              widget.linkedEntityGuids = pageGuid ? [pageGuid] : null;
            }
          }
        }
      }
      return dashboardInput;
    };
    // First pass without the facet-link markers (page guids are unknown yet)
    const dashboard = applyFacetLinks(JSON.parse(resolvedContent), {});
    const search = await this.fetchJson(
      api,
      {
        method: "POST",
        headers,
        body: JSON.stringify({
          query:
            `{ actor { entitySearch(query: "type = 'DASHBOARD' AND name = '${dashboard.name}'") ` +
            "{ results { entities { guid name } } } } }",
        }),
      },
      "New Relic entity search"
    );
    const entities =
      search.data?.actor?.entitySearch?.results?.entities || [];
    const runMutation = async (dashboardInput, existingGuid) => {
      const mutation = existingGuid
        ? "mutation($guid: EntityGuid!, $dashboard: DashboardInput!) { " +
          "dashboardUpdate(guid: $guid, dashboard: $dashboard) { " +
          "entityResult { guid name pages { guid name } } errors { description type } } }"
        : "mutation($accountId: Int!, $dashboard: DashboardInput!) { " +
          "dashboardCreate(accountId: $accountId, dashboard: $dashboard) { " +
          "entityResult { guid name pages { guid name } } errors { description type } } }";
      const variables = existingGuid
        ? { guid: existingGuid, dashboard: dashboardInput }
        : { accountId, dashboard: dashboardInput };
      const result = await this.fetchJson(
        api,
        {
          method: "POST",
          headers,
          body: JSON.stringify({ query: mutation, variables }),
        },
        "New Relic dashboard"
      );
      const mutationResult =
        result.data?.dashboardUpdate || result.data?.dashboardCreate || {};
      if (mutationResult.errors?.length) {
        throw new Error(
          `New Relic dashboard error: ${JSON.stringify(mutationResult.errors)}`
        );
      }
      return mutationResult.entityResult;
    };
    const firstPass = await runMutation(
      dashboard,
      entities.length ? entities[0].guid : null
    );
    // Second pass: replace each marker with the guid of its target page
    // ("Repository detail", "Why this rating?") now that guids are known
    const guidsByMarker = {};
    for (const [marker, pageName] of Object.entries(PAGE_GUID_MARKERS)) {
      const targetPage = (firstPass?.pages || []).find(
        (page) => page.name === pageName
      );
      guidsByMarker[marker] = targetPage ? targetPage.guid : null;
    }
    const hasMarkerToResolve = Object.entries(guidsByMarker).some(
      ([marker, pageGuid]) => pageGuid && resolvedContent.includes(marker)
    );
    if (hasMarkerToResolve) {
      const linkedDashboard = applyFacetLinks(
        JSON.parse(resolvedContent),
        guidsByMarker
      );
      // Carry the first-pass page guids into the update input so pages are
      // updated in place: without them dashboardUpdate recreates every page
      // with new guids, and the linkedEntityGuids just resolved would be stale
      for (const page of linkedDashboard.pages || []) {
        const firstPassPage = (firstPass?.pages || []).find(
          (candidate) => candidate.name === page.name
        );
        if (firstPassPage) {
          page.guid = firstPassPage.guid;
        }
      }
      await runMutation(linkedDashboard, firstPass.guid);
    }
    return firstPass?.guid;
  }
}
