// Minimal replacement of the which dependency: resolve a command against PATH
import { constants as fsConstants } from "fs";
import { access } from "fs/promises";
import * as path from "path";

export async function which(command) {
  const isWindows = process.platform === "win32";
  const extensions = isWindows
    ? (process.env.PATHEXT || ".COM;.EXE;.BAT;.CMD").split(";")
    : [""];
  const directories = (process.env.PATH || "").split(path.delimiter).filter(Boolean);
  for (const directory of directories) {
    for (const extension of extensions) {
      const candidate = path.join(directory, command + extension);
      try {
        await access(candidate, isWindows ? fsConstants.F_OK : fsConstants.X_OK);
        return candidate;
      } catch {
        // Not found here: try next candidate
      }
    }
  }
  throw new Error(`Command not found in PATH: ${command}`);
}
