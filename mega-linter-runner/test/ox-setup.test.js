const assert = require("assert");
const fs = require("fs-extra");
const { OxSecuritySetup } = require("../lib/ox-setup");
const { OX_REPO_LOCAL_CONFIG_FILE } = require("../lib/config");

describe("Ox setup", function () {
    it("(Ox setup) register", async () => {
        const oxSetup = new OxSecuritySetup();
        const dummyOxToken = Math.random();
        await oxSetup.run();
        await oxSetup.handleResponse({ clientToken: oxSetup.clientToken, oxToken: dummyOxToken });
        assert(fs.existsSync(OX_REPO_LOCAL_CONFIG_FILE), `Local config file does not exists`);
        assert(fs.readJSONSync(OX_REPO_LOCAL_CONFIG_FILE).oxToken === dummyOxToken, "Ox token is not good or missing");
        await fs.remove(OX_REPO_LOCAL_CONFIG_FILE);
    })
})
