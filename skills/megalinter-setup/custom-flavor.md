# Set up a MegaLinter custom flavor repository

Load this guide **only when the user explicitly asks to create or maintain a custom MegaLinter flavor**. This is not part of a normal MegaLinter installation.

A custom flavor is your own MegaLinter Docker image containing **only the linters you need**, published from a dedicated repository. It starts faster than the official flavors because it ships nothing else. It is a separate deliverable from installing MegaLinter on a project: a project consumes a flavor, a flavor repository produces one.

Full documentation (with screenshots): <https://megalinter.io/latest/custom-flavors/>

## 1. Reuse one of the user's own flavors before building another

The user may already have a custom flavor repository — maintaining two is wasted effort. Look for one **among the repositories they own or administer**, in their account and in their organizations:

```bash
gh search repos megalinter-custom-flavor --owner @me --json fullName,url
gh api user/orgs --jq '.[].login'                                    # then repeat with --owner <org>
```

**Only a repository the user owns or has admin rights on can be reused** — verify before proposing it:

```bash
gh api repos/<owner>/<repo> --jq '.permissions.admin'                # must be true
```

A third party's custom flavor is **not** a reuse candidate, even when its linter list matches: the user cannot rebuild, update or audit it, and depending on someone else's image makes their CI hostage to a repository they do not control. Build their own instead.

Inspect a candidate's linter list without cloning it:

```bash
gh api repos/<owner>/<repo>/contents/megalinter-custom-flavor.yml --jq '.content' | base64 -d
```

Then choose with the user:

- The `linters` list **already covers what they need** (extra linters only cost image size) → reuse it: skip to section 9 and point their project at the existing image.
- It is close but **missing a few linters** → extend that flavor rather than creating a second one: go to section 10 (add the keys, re-run the generator, release).
- No repository found, or the existing one serves a different purpose they want to keep separate → continue with section 2.

## 2. Prerequisites and repository

Needed before generating:

- **Node.js** installed.
- The **list of linter keys** to embed. If the user does not have one, take it from the `FLAVOR_SUGGESTIONS` line printed by any official flavor run on their project (`megalinter-check` surfaces it in `tips`), or ask them.
- A **dedicated repository whose name contains `megalinter-custom-flavor`** (e.g. `megalinter-custom-flavor-npm-groovy-lint`), cloned locally, with the user positioned in it. The generator reads the `origin` remote and **fails** if the name does not match — a hard requirement, not a convention. A custom flavor never lives in the project it lints: if the user is in a normal project repository, a new repository is required.

You can create that repository for them — ask first, and confirm the owner (personal account or organization) and the name:

```bash
gh repo create <owner>/megalinter-custom-flavor-<topic> --public --add-readme --clone
cd megalinter-custom-flavor-<topic>
```

Public is the documented setup and keeps the published image consumable by anyone; a private repository also works but its image inherits the repository's visibility, so every consumer then needs registry credentials. If the repository already exists, clone it (`gh repo clone <owner>/<repo>`) and work in it instead.

Work on `main` or a sub-branch, as the user prefers.

## 3. Generate the scaffolding

```bash
npx mega-linter-runner --custom-flavor-setup \
  --custom-flavor-linters "PYTHON_BANDIT,PYTHON_RUFF,REPOSITORY_TRIVY"
```

- Omit `--custom-flavor-linters` to pick the linters interactively (the generator prompts for the flavor label and a checkbox list of all linter keys).
- Invalid linter keys make the generator throw — take them from the [linters list](https://megalinter.io/latest/all_linters/) or from a `FLAVOR_SUGGESTIONS` output.
- If the runner rejects the option ("Invalid option" error), the resolved version is outdated: re-run with `npx mega-linter-runner@latest --custom-flavor-setup ...`.

## 4. What was generated

| File                                                     | Role                                                                                   |
|----------------------------------------------------------|----------------------------------------------------------------------------------------|
| `megalinter-custom-flavor.yml`                           | The flavor definition: label + list of linter keys. **This is the file to edit later** |
| `action.yml`                                             | GitHub Action wrapper, so others can use your flavor with `uses:`                      |
| `.github/workflows/megalinter-custom-flavor-builder.yml` | Builds and publishes the image                                                         |
| `.github/workflows/check-new-megalinter-version.yml`     | Daily check for new MegaLinter releases, creates matching releases in your repository  |
| `.github/zizmor.yml`                                     | Workflow-security policy (see below)                                                   |
| `README.md`                                              | Documentation of your flavor, including the mandatory License section                  |

Review them with the user, then commit and push.

## 5. Linting the flavor repository itself

The generated files pass MegaLinter out of the box, except for two checks that need a deliberate, documented exception:

- **zizmor** — the builder step intentionally tracks `oxsecurity/megalinter/flavors/custom-builder@main` instead of being hash-pinned, so your image is always built by the builder matching the MegaLinter release. The generated `.github/zizmor.yml` waives exactly that reference and keeps `hash-pin` as the blanket policy. Do not widen it.
- **checkov `CKV_GHA_7`** — it requires empty `workflow_dispatch` inputs, but the builder needs `megalinter-version` and `is-latest` inputs. Add to `.mega-linter.yml`:

  ```yaml
  REPOSITORY_CHECKOV_ARGUMENTS: "--skip-check CKV_GHA_7"
  ```

## 6. Optional: build for ARM

Check that every selected linter supports `linux/arm64` in the [linters list](https://megalinter.io/latest/all_linters/), then in `megalinter-custom-flavor-builder.yml` change `platform: "linux/amd64"` to `platform: "linux/amd64,linux/arm64"`.

## 7. Publishing

**Personal Access Token — optional, and worth declining.** It only enables the *automatic* daily release sync. Warn the user before setting one up: a leaked or compromised PAT grants broad write access, and open-source projects are actively targeted by supply-chain attacks. Without a PAT, they trigger builds manually (Actions tab → `check-new-megalinter-version`, a GitHub Release, or a push on a non-main branch), which is enough for most flavors.

If the user still wants automatic sync, create a **fine-grained** token (Settings → Personal access tokens → Fine-grained) and store it as the repository secret `PAT_TOKEN`:

- Repository access: **only this repository** — account-level or unscoped tokens do not work.
- Permissions: **Contents: Read and write** and **Actions: Read and write**.
- Set an expiration and plan to rotate it.

**Optional Docker Hub mirroring** (default is ghcr.io only): repository variable `DOCKERHUB_REPO`, secrets `DOCKERHUB_USERNAME` and `DOCKERHUB_PASSWORD`.

**Build triggers**: a GitHub Release builds that version; a push on any branch except `main` builds a `beta` tagged image; the builder workflow can also be run manually.

## 8. Licensing (mandatory)

A custom flavor is still MegaLinter, so it is covered by the **AGPL-3.0 license** — both the generated files and the published image, which is built from the official MegaLinter image.

- Add an `AGPL-3.0` `LICENSE` file at the repository root.
- Keep the link to <https://github.com/oxsecurity/megalinter> in the README so image users can find the source.

The generated README already contains the License section, so the `LICENSE` file is the only thing to add.

## 9. Use the published flavor in a project

In the consuming repository, replace the official MegaLinter reference:

```yaml
# GitHub Action: replace the official action with your flavor's action
- name: MegaLinter
  id: ml
  uses: <owner>/<flavor-repo>@main
  env:
    VALIDATE_ALL_CODEBASE: true
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

```yaml
# Docker image (GitLab CI, and anywhere an image is referenced)
image: ghcr.io/<owner>/<flavor-repo>/megalinter-custom-flavor:latest
```

## 10. Maintenance

**Change the linter list**: edit the `linters` entries of `megalinter-custom-flavor.yml`, re-run `npx mega-linter-runner --custom-flavor-setup` so the other generated files pick up the change, commit and push, then create a release (or push on a branch) to rebuild.

**Follow new MegaLinter versions**: the `check-new-megalinter-version` workflow does it daily and creates the matching release automatically, each release triggering a rebuild. To upgrade immediately, or if no `PAT_TOKEN` was configured, create a GitHub Release in the flavor repository with the same tag as the [upstream release](https://github.com/oxsecurity/megalinter/releases) (e.g. `v10.0.0`) — the builder then produces the flavor for that MegaLinter version. If automatic releases stop working, the `PAT_TOKEN` secret is the first thing to check (missing, expired, or wrongly scoped).
