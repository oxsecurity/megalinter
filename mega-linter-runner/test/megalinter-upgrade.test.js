import assert from 'assert';
import { MegaLinterUpgrader } from "../lib/upgrade.js";

describe("Upgrade config", function () {
  const upgrader = new MegaLinterUpgrader();
  let i = 0;
  for (const item of upgrader.replacements) {
    i++;
    it("(" + i + ") " + String(item.regex), () => {
      const replaceRes = item.test.replace(item.regex, item.replacement);
      assert(
        replaceRes === item.testRes,
        `${replaceRes} should be ${item.testRes}`
      );
    });
  }
});
