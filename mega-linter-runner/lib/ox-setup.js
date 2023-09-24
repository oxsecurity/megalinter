// const uuid = require("uuid");
import { OX_LOGIN_URL } from "./config.js";
import { default as open } from "open";

// Class to setup OX security on the repository
export class OXSecuritySetup {
  // Open OX registration page
  // Once SSO (managed internally by OX app) is performed, we'll receive an ox token in response
  async run() {
    //,this.clientToken = uuid.v4(); // generate a random key
    const registerUrl = OX_LOGIN_URL + "?ref=megalinter";
    // console.log(`Waiting for response from OX.security app...`);
    open(registerUrl);
  }

  /*
  
    // Handle response from ox server
    async handleResponse(body) {
      // Check if the response contains the sent clientToken
      if (body.clientToken !== this.clientToken) {
        throw new Error("Client token error");
      }
      if (body.oxToken) {
        await this.storeOXToken(body.oxToken);
      }
    }
  
    // Store ox token in local config file
    async storeOXToken(oxToken) {
      const oxAuthInfo = fs.existsSync(OX_REPO_LOCAL_CONFIG_FILE)
        ? fs.readJSONSync(OX_REPO_LOCAL_CONFIG_FILE)
        : {};
      oxAuthInfo.oxToken = oxToken;
      // Make sure ox directory is not existing
      fs.ensureDir(path.dirname(OX_REPO_LOCAL_CONFIG_FILE));
      await fs.writeJSON(OX_REPO_LOCAL_CONFIG_FILE, oxAuthInfo);
      console.log(`Written OX token in ${OX_REPO_LOCAL_CONFIG_FILE}`);
    }
    */
}

