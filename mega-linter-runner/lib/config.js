import * as path from "path";

const DEFAULT_RELEASE = 'v7';
const OX_PROTOCOL = process.env.OX_PROTOCOL || "https";
const OX_BASE_URL =
  process.env.OX_BASE_URL || `${OX_PROTOCOL}://app.ox.security`;
const OX_PORT = process.env.OX_PORT || 443;
const OX_LOGIN_URL = `${OX_BASE_URL}:${OX_PORT}/login`;
const OX_REPO_LOCAL_CONFIG_FILE =
  process.OX_REPO_AUTH_FILE || path.join(process.cwd(), ".ox/auth.json");
const ALLOWED_ORIGINS = {
  "https://app.ox.security:443": true,
};


export {
  DEFAULT_RELEASE,
  OX_BASE_URL,
  OX_PORT,
  OX_LOGIN_URL,
  ALLOWED_ORIGINS,
  OX_REPO_LOCAL_CONFIG_FILE,
};
