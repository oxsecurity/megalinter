# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] (beta, main branch content)

Note: Can be used with `oxsecurity/megalinter@beta` in your GitHub Action mega-linter.yml file, or with `oxsecurity/megalinter:beta` docker image

- Breaking changes

- Core

- New linters

- Disabled linters

- Re-enabled linters

- Deprecated linters

- Removed linters

- Media

- Linters enhancements

- Fixes

- Reporters

- Flavors

- Doc

- mega-linter-runner

- Agent Skills

- Dev

- CI

- Linter versions upgrades (N)
<!-- linter-versions-end -->

## [v10.1.0] - 2026-09-05

- Core
  - MegaLinter now prints a **crash traceback** when it is killed by a fatal signal (`SIGSEGV`, `SIGBUS`…), instead of exiting silently with no clue about what happened (#8779)
  - The **LLM Advisor** supports a new provider, **OrcaRouter**, an OpenAI-compatible AI gateway: set **`LLM_PROVIDER: orcarouter`** and **`ORCAROUTER_API_KEY`** in your environment to get fix suggestions routed through [OrcaRouter](https://www.orcarouter.ai) (see the [OrcaRouter provider page](https://megalinter.io/latest/llm-provider/llm_provider_orcarouter/)) (#8826)

- New linters
  - **[biome](https://biomejs.dev)**, one fast toolchain linting, formatting and sorting imports of JavaScript, TypeScript, JSX, TSX, JSON, CSS and GraphQL files, available as **JAVASCRIPT_BIOME**, **TYPESCRIPT_BIOME**, **JSX_BIOME**, **TSX_BIOME**, **JSON_BIOME**, **CSS_BIOME** and **GRAPHQL_BIOME** (#8706)
    - Activated only when a **biome.json** or **biome.jsonc** configuration file is found in the repository
    - Supports **APPLY_FIXES** (safe fixes with `--write`) and native **SARIF** output
    - `EXCLUDED_DIRECTORIES` are forwarded in project lint mode through a generated configuration extending the workspace one
  - **[ApexGuru](https://developer.salesforce.com/docs/platform/salesforce-code-analyzer/guide/engine-apexguru.html)**, the AI-driven engine of **Salesforce Code Analyzer**, available as **SALESFORCE_CODE_ANALYZER_APEXGURU** (#8820)
    - Detects **SOQL inefficiencies**, critical anti-patterns and scalability hotspots in your `.cls` and `.trigger` files, with line-level highlights, severity ratings and suggested fixes
    - The analysis runs **in a connected Salesforce org**, not locally: store the [auth url](https://developer.salesforce.com/docs/platform/salesforce-cli-reference/guide/cli_reference_org_display.html) of the target org in a CI secret named **`SFDX_AUTH_URL`**, and MegaLinter logs in to that org before the scan
    - The scan is sent to that org **explicitly**, so a `.sfdx/sfdx-config.json` left at the root of the repository, usually naming a long gone scratch org, can not hijack it
    - **Inactive by default**: it activates only when `SFDX_AUTH_URL` is defined, so nothing changes for existing Salesforce projects
    - Requires **ApexGuru to be enabled** on the org: it needs Scale Center, and is available for Unlimited Edition production orgs, full copy sandboxes, Signature orgs and Scale Test customers
    - A run where the engine **could not analyze anything** is reported as an **error** rather than a silent success, together with the reason and how to fix it
    - Supports native **SARIF** output, like the other Code Analyzer engines
  - **[tofu fmt](https://opentofu.org/docs/cli/commands/fmt/)**, the built-in formatter of **OpenTofu** (the MPL-2.0 licensed fork of Terraform), available as **TERRAFORM_TOFU_FMT** ([#8729](https://github.com/oxsecurity/megalinter/issues/8729))
    - Analyzes **`.tofu`** files only, the OpenTofu specific extension, so it never doubles up with **TERRAFORM_TERRAFORM_FMT** which keeps `.tf`
    - To format your `.tf` files with OpenTofu instead, set `TERRAFORM_TOFU_FMT_FILE_EXTENSIONS: [".tofu", ".tf", ".tfvars"]` and `DISABLE_LINTERS: [TERRAFORM_TERRAFORM_FMT]`
    - Supports **APPLY_FIXES** to rewrite files in the canonical OpenTofu style
  - **[tofu validate](https://opentofu.org/docs/cli/commands/validate/)**, the built-in validator of **OpenTofu**, available as **TERRAFORM_TOFU_VALIDATE** ([#8793](https://github.com/oxsecurity/megalinter/issues/8793))
    - Reports what formatters and rule-based linters can not see: unsupported or missing arguments, wrong attribute types, references to undeclared variables, locals or outputs, and broken module input contracts
    - Analyzes **`.tofu`** files only, like **TERRAFORM_TOFU_FMT**, leaving `.tf` free for a future `terraform validate` linter. To validate `.tf` files, set `TERRAFORM_TOFU_VALIDATE_FILE_EXTENSIONS: [".tofu", ".tf"]`
    - Validates one whole module per directory, so every `.tf` and `.tofu` file of a selected directory is parsed and can produce diagnostics
    - Every directory is initialized with `tofu init -backend=false` beforehand, so no state is read, no state lock is taken and no cloud credentials are needed
    - Set **TERRAFORM_TOFU_VALIDATE_INIT_ARGUMENTS** to change those initialization arguments, for example adding `-lockfile=readonly` to have an out-of-sync `.terraform.lock.hcl` reported as an error instead of being updated

- Disabled linters
  - **COFFEE_COFFEELINT** is disabled: CoffeeScript tooling is discontinued, and coffeelint can not receive `EXCLUDED_DIRECTORIES` in project lint mode (it has no exclusion option and reads `.coffeelintignore` only from its working directory). The linter will be removed in a future version (#8720)
  - **GRAPHQL_GRAPHQL_SCHEMA_LINTER** is disabled: [graphql-schema-linter](https://github.com/cjoudrey/graphql-schema-linter) is unmaintained, with no release or commit since May 2022, and its peer dependency range pins **graphql** to `^15 || ^16`, which held the whole GraphQL install back from **graphql v17**. Use **[GRAPHQL_BIOME](https://megalinter.io/latest/descriptors/graphql_biome/)** to lint your GraphQL files. The linter will be removed in a future version (#8894)

- Re-enabled linters
  - **[spectral](https://megalinter.io/latest/descriptors/api_spectral/)** is back as **API_SPECTRAL**, together with the **API** descriptor, to lint your **OpenAPI**, **AsyncAPI** and **Arazzo** specifications ([#8717](https://github.com/oxsecurity/megalinter/issues/8717))
    - It was removed in v10.0.0 because it crashed at startup on every run: the cause has been found and fixed
    - Nothing to change in your configuration: `API_SPECTRAL` works again in `ENABLE_LINTERS` / `DISABLE_LINTERS`, and the default ruleset file is still `.spectral.yaml`

- Linters enhancements
  - **TERRAFORM_TFLINT** now documents the tflint native **`GITHUB_TOKEN_github_com`** variable to authenticate plugin downloads on github.com, which is the recommended way to fix `tflint --init` failures when your `GITHUB_TOKEN` targets a GitHub Enterprise instance ([#8795](https://github.com/oxsecurity/megalinter/issues/8795))
    - Set your github.com token in `GITHUB_TOKEN_github_com`, then list it in `TERRAFORM_TFLINT_UNSECURED_ENV_VARIABLES`: tflint gives it priority over `GITHUB_TOKEN`, which other linters and reporters keep using
    - **`PAT_GITHUB_COM` is deprecated**: it still works and now logs a warning, and will be removed in a future major release
  - **CLOJURE_CLJSTYLE** now forwards `EXCLUDED_DIRECTORIES` through its native repeatable `--ignore` argument, instead of a temporary `.cljstyle` written in your repository. Exclusions are now also applied when your repository already has a `.cljstyle` config, whose own ignore patterns are preserved (#8720)
  - **SQL_SQLFLUFF** does not receive `EXCLUDED_DIRECTORIES` in `project` lint mode anymore: sqlfluff reads path exclusions only from a `.sqlfluffignore`, `.sqlfluff` or `pyproject.toml` located inside the analyzed sources, where MegaLinter used to write a temporary file. List the directories to skip in your own `.sqlfluffignore`, or keep the default `list_of_files` lint mode where MegaLinter filters the files itself (#8720)
  - **SARIF output** is now available for 13 more linters: **zizmor**, **bicep_linter**, **cppcheck**, **clj-kondo**, **roslynator**, **htmlhint**, **protolint**, **sqlfluff**, **swiftlint**, **osv-scanner**, **trufflehog**, **jscpd** and **lintr**. Enable it the same way as any other SARIF-capable linter, with `SARIF_REPORTER: true` (optionally scoped with `SARIF_REPORTER_LINTERS`) (#8715)
    - The 4 **Salesforce Code Analyzer** engines (`SALESFORCE_CODE_ANALYZER_APEX`, `_AURA`, `_LWC`, `_FLOW`) also gained SARIF output: their report switches from CSV to SARIF automatically when SARIF reporting is requested
    - `csharp_roslynator` is bumped from 0.12.0 to **0.13.0**, the first release including its SARIF output support
    - `clj-kondo`'s upstream SARIF output currently nests the `region` property one level too deep, which may affect line/column display in strict SARIF consumers (clj-kondo/clj-kondo#2345)
  - **Prettier** linters (**JSON_PRETTIER**, **YAML_PRETTIER**, **JAVASCRIPT_PRETTIER**, **TYPESCRIPT_PRETTIER**) now tell you how to install a **Prettier plugin** when one declared in your `.prettierrc` fails to load with `Cannot find package ... imported from noop.js` ([#6980](https://github.com/oxsecurity/megalinter/issues/6980))
    - Prettier v3 resolves plugins with a native ESM `import()` from the workspace and ignores `NODE_PATH`, so plugins installed with the default `cwd: root` land in `/node-deps` where Prettier never looks for them
    - The guidance surfaced in the log is to install them through `<LINTER_KEY>_PRE_COMMANDS` with **`cwd: workspace`**, which keeps plain package names in `.prettierrc` so the very same config still works when you run Prettier locally without MegaLinter

- Fixes
  - MegaLinter does not crash anymore with **`This module only works with the 'fork' start method`** right after `Processing linters on [N] parallel cores`, which made every v10.0.0 run fail unless `PARALLEL: false` was set ([#8808](https://github.com/oxsecurity/megalinter/issues/8808))
    - The **`PARALLEL: false`** workaround is not needed anymore, on the main image as well as on custom flavors
    - Messages logged by linters **running in parallel** are back in the console and in `megalinter.log`, including the extra output of `LOG_LEVEL: DEBUG`
  - **PAT_GITHUB_COM** is now hidden from the linters commands, like every other credential variable ([#8795](https://github.com/oxsecurity/megalinter/issues/8795))
    - The GitHub Personal Access Token used by **TERRAFORM_TFLINT** was sent in cleartext to every linter, as it matched no pattern of `SECURED_ENV_VARIABLES_DEFAULT`
    - The default list now hides **any variable named `PAT`, `PAT_*` or `*_PAT`** (`PAT_GITHUB_COM`, `AZURE_PAT`...), and `tflint --init` still receives the real token
    - Add such a variable to `<LINTER_KEY>_UNSECURED_ENV_VARIABLES` if one of your linters really needs to read it
  - Fixed random **`Segmentation fault`** crashes of MegaLinter itself, which stopped the whole run with no error message ([#8733](https://github.com/oxsecurity/megalinter/issues/8733)). MegaLinter threads now get a full-size stack instead of the 128 KiB default of the Alpine images
  - Fixed leaked **`git` processes** when **APPLY_FIXES** is active: one was left behind by every fixer linter, which could exhaust the available file descriptors on long runs (#8779)
  - Fixed **random crashes of project-mode linters** (`REPOSITORY_TRIVY`, `REPOSITORY_GRYPE`, `REPOSITORY_SYFT`…) caused by MegaLinter writing temporary ignore files inside the analyzed sources: a file appearing then disappearing while another linter walked the repository aborted its scan (`walk dir error: ... no such file or directory`). **MegaLinter now writes only in REPORT_OUTPUT_FOLDER**, never in your sources (#8720)
  - **EXCLUDED_DIRECTORIES** and **ADDITIONAL_EXCLUDED_DIRECTORIES** are now forwarded to `project` lint mode linters even when the directory is **nested**, not only when it sits at the root of your repository ([#8806](https://github.com/oxsecurity/megalinter/issues/8806))
    - A directory like `infrastructure/cdk.out` was previously scanned anyway, for example by **REPOSITORY_BETTERLEAKS**, which reported findings in generated files
    - Excluded entries are now looked up the same way MegaLinter filters files: by **directory name, at any nesting level**
    - Nothing changes when the excluded directory does not exist in your repository: it is still not sent to the linters
    - This also covers **PYTHON_BANDIT**, **YAML_V8R**, **CSHARP_DOTNET_FORMAT**, **VBDOTNET_DOTNET_FORMAT** and **REPOSITORY_LS_LINT**, whose exclusions are anchored on the repository root: they now receive the **path of each nested directory** found
    - A **`^`-anchored FILTER_REGEX_EXCLUDE** keeps excluding root-level directories only: `^docs/` does not silence findings in `packages/a/docs` anymore
    - Looking up the excluded directories **never descends** into an excluded directory, and costs **no extra repository scan**: it reuses the one MegaLinter already does to list your files, and falls back to a single scan when only changed files are analyzed
  - **REPOSITORY_TRUFFLEHOG** does not silently skip findings anymore in a directory whose name merely **ends with** an excluded one: with `dist` excluded, secrets in `my-dist/` were not reported (#8811)
  - **REPORT_OUTPUT_FOLDER** is now always excluded from what linters analyze, even when you override `EXCLUDED_DIRECTORIES`, and even when the folder does not exist yet when a linter starts (#8720)
  - The **API reporter** variables (`API_REPORTER`, `API_REPORTER_URL`…) are not flagged as **deprecated** anymore in the configuration JSON schema: they were collateral damage of the removal of the `API` descriptor in v10.0.0, and IDEs displayed them as obsolete (#8718)
  - **REPOSITORY_BETTERLEAKS** does not crash the whole MegaLinter run anymore when `REPOSITORY_BETTERLEAKS_PR_COMMITS_SCAN: true` is used on **Azure Pipelines** with the default shallow checkout ([#8732](https://github.com/oxsecurity/megalinter/issues/8732))
    - The target branch commit is now searched across several reference spellings, so a branch available only locally is found too
    - When the Pull Request commit range can not be determined — on any platform — betterleaks now logs a **warning explaining how to fix your checkout** and scans the whole repository, instead of aborting the run
    - The **Pull Request scan setup documentation** lost when gitleaks was replaced by betterleaks is restored on the [betterleaks page](https://megalinter.io/latest/descriptors/repository_betterleaks/): checkout depth for each platform, Azure Pipelines variables to forward to the container, and how to compute the SHAs yourself ([#8731](https://github.com/oxsecurity/megalinter/issues/8731))
  - The **REPOSITORY_BETTERLEAKS Pull Request scan variables** (`REPOSITORY_BETTERLEAKS_PR_COMMITS_SCAN`, `REPOSITORY_BETTERLEAKS_PR_SOURCE_SHA`, `REPOSITORY_BETTERLEAKS_PR_TARGET_SHA`) are now declared in the configuration JSON schema, so your IDE stops flagging them as unknown keys in `.mega-linter.yml` (#8805)
  - **Bitbucket Pipelines** is now recognized as a Pull Request context: `PULL_REQUEST` optimizations that were silently skipped there are applied again (#8780)
    - **REPOSITORY_CHECKOV** and **REPOSITORY_BETTERLEAKS** only analyze the Pull Request changes when asked to
    - Set `BITBUCKET_PR_ID` in your pipeline (Bitbucket provides it on Pull Request builds) to benefit from it
  - A run where all linters pass does not **exit with an error** anymore when MegaLinter can not list the files updated by the linters ([#8649](https://github.com/oxsecurity/megalinter/issues/8649))
    - Happens on a **read-only workspace** whose repository uses **git-lfs**: the required LFS filter has nowhere to write its temporary files, so the `git diff` used to detect updated files exits 128
    - MegaLinter now logs a **warning** naming the workspace and the failed command, reports no updated source file, and completes the run. The `UPDATED_SOURCES_REPORTER: false` workaround is not needed anymore
  - **REPOSITORY_CHECKOV** does not fail anymore with `argument -f/--file: expected at least one argument` in a Pull Request where **no file has been updated** ([#8802](https://github.com/oxsecurity/megalinter/issues/8802))
    - With `VALIDATE_ALL_CODEBASE: false`, checkov is now **skipped** when the Pull Request contains no updated file, instead of scanning the whole project or building an invalid command
    - Any linter using the **`list_of_files` lint mode** with no file to analyze is skipped the same way, instead of being called with an empty list of files

- Reporters
  - Linters reporting in **SARIF** format no longer show **No output available** in Pull Request comments and summaries: the details section now names the SARIF report to open and links the **MegaLinter artifacts** ([#8730](https://github.com/oxsecurity/megalinter/issues/8730))
    - Applies to the **GitHub**, **GitLab**, **Azure** and **Bitbucket** comment reporters and to the markdown summary
    - The link points where the reporter already links its detailed reports, so it follows `REPORTERS_ACTION_RUN_URL` when you set it

- Doc
  - **Comments are back** at the bottom of every documentation page, powered by [Giscus](https://giscus.app/) and backed by [MegaLinter GitHub Discussions](https://github.com/oxsecurity/megalinter/discussions): ask a question or share a tip right from the page it applies to. The previous utteranc.es widget had silently stopped rendering
  - [megalinter.io](https://megalinter.io/) gets a **dark mode**: use the toggle in the header, or let it follow your system preference (#8848)
  - Refreshed **look and feel**, aligned with the [OX Security](https://www.ox.security/?ref=megalinter) brand: navy, indigo and lime replace the previous purple palette, and the **Satoshi** typeface is now actually loaded (it was silently falling back to the default font) (#8848)
  - New **Docker pulls per month** graph, showing the growth of MegaLinter adoption since October 2020, displayed in the README and on the [Flavors statistics](https://megalinter.io/latest/flavors-stats/) page (#8698)
  - Refreshed the **MegaLinter references in linters documentation** (`linter_megalinter_ref_url`): verified all existing links, updated moved pages (ktlint, robocop, csharpier, zizmor, ruff, proselint), and opened 47 suggestion PRs on linters repositories that did not mention MegaLinter yet (#8701, #8777)
  - New **Security linting with ESLint** section in the JAVASCRIPT_ES and TYPESCRIPT_ES documentation: states that no security plugin is bundled, shows the `PRE_COMMANDS` recipe and the `createRequire` reference needed under flat config, and lists commonly used plugins. Closes the gap left by the "Security Issues (with security plugins)" line, which previously named no plugin and had no working example (#8712)

- mega-linter-runner
  - **Node.js 22 or higher** is now required (was 20) (#8710)
  - **8 npm dependencies removed** (`chalk`, `fs-extra`, `which`, `uuid`, `find-package-json`, `simple-git`, `mem-fs`, `assert`), replaced by Node.js built-in modules: faster `npx mega-linter-runner` startup and a smaller supply-chain attack surface (#8710)
  - Fixed `mega-linter-runner --version` displaying `error` instead of the version when the `npm_package_version` environment variable is not set (#8710)

- Agent Skills
  - The MegaLinter **agent plugin** now ships its three sub-agents to **GitHub Copilot** clients (VS Code, Copilot CLI, the Copilot app) (#8821)
    - Agent Plugins 1.0 standardizes skills but not sub-agents, so Copilot loads them from `com.github.copilot/agents`: the plugin now carries them there, generated from the Claude Code definitions so the two can not drift
    - **megalinter-setup** installs them correctly outside the plugin too: on Copilot the file name must end with **`.agent.md`** in `.github/agents/`, and the `model: haiku` override must be dropped
    - The skills stop guessing how they were installed from the skill naming, which only some platforms namespace: the install mode is now read from the filesystem, and you are asked when it stays ambiguous
    - The `licence` frontmatter key of the four skills is corrected to **`license`**, the spelling agents actually read
  - **megalinter-check** now handles the commit MegaLinter pushes itself when the repository uses `APPLY_FIXES_MODE: commit` (#8713)
    - CI providers ignore pushes made with the CI token, so the branch used to stay stuck on the **stale checks** of the run that produced the fixes
    - The commit is amended with a **🤖** prefix and re-pushed with `--force-with-lease`, which re-triggers the checks (you are asked first on the default branch)
    - Nothing is amended when another commit landed after the auto-fix one, when it was already amended, or when you have local commits left to push — a normal push already re-triggers the checks in those cases
  - **megalinter-setup** can now set up a [custom flavor](https://megalinter.io/latest/custom-flavors/) repository on request, from creating the repository to publishing and maintaining the image (#8713)
    - It first looks for a custom flavor **you already own or administer**, to reuse or extend it instead of maintaining a second one
  - **megalinter-setup** in upgrade mode now also updates the **installed skills and sub-agents** (`npx skills update`), so the guidance you run matches the MegaLinter version you just upgraded to (#8713)
  - The MegaLinter skills are now installable as an **agent plugin**, so one command brings the four skills and the three sub-agents at once, and keeps them updated (#8791)
    - **Claude Code**: `/plugin marketplace add oxsecurity/megalinter` then `/plugin install megalinter@megalinter`
    - **Cursor**, **GitHub Copilot**, **Codex**, **Gemini CLI** and **Antigravity** each have their own install command, listed on the [Coding Agents (Plugins)](https://megalinter.io/latest/agent-plugins/) page
    - The sub-agents ship with the plugin on **Claude Code** and **Cursor**; elsewhere the skills install alone and run inline
    - `npx skills add oxsecurity/megalinter/skills` keeps working for every other coding agent

- Dev
  - **REPOSITORY_TRUFFLEHOG tests no longer depend on a third-party endpoint.** The good and bad fixtures differed only by a basic-auth credential that trufflehog validated over the network, so the whole test suite went red whenever the runner could not reach that site (#8848)
    - The fixtures now differ by what is **detected**, the good ones carrying no secret material at all, and the tests drop `--only-verified`, which stays the production default
    - The `.wireit` poison fixture gains a private key, so the excluded-directories forwarding guard actually fires instead of being vacuous
  - The documentation site is now built with **[Zensical](https://zensical.org/)**, the successor of Material for MkDocs, replacing `mkdocs`, `mkdocs-material` and `mkdocs-glightbox` (#8848)
    - `mkdocs.yml` stays the configuration file, so `.automation/build.py` nav generation is unchanged; `hatch run docs:serve` and `hatch run docs:build` now call `zensical`
    - Versioned deploys still use **mike**, from the Zensical-compatible fork `squidfunk/mike` pinned to a commit SHA and watched by a new Renovate custom manager
    - The `Check MkDocs generation` workflow becomes `Check documentation generation` (`test-docs.yml`) and also runs on `docs/**` changes
    - Three long-dead pieces of documentation configuration were found and removed or fixed on the way: the `disqus` template block (Material has no such block, so comments never rendered), the `Satoshi, sans-serif` theme font (one quoted family name that matched nothing), and the `h1[content~=Home]` CSS rule (`h1` has no `content` attribute)
  - **Parallel linters logging does not depend on the multiprocessing start method anymore**: `init_worker()` installs a `QueueHandler` on the worker root logger, built from the queue and the level passed by `process_linters_parallel()`, instead of relying on the handlers a `fork`ed worker inherits ([#8808](https://github.com/oxsecurity/megalinter/issues/8808))
    - Python 3.14 changed the default start method on Linux from `fork` to `forkserver`: workers then started with no handler and the default `WARNING` level, so their records were lost or written directly to their own stdout, bypassing the queue listener and the log file
    - The `AssertionError` crash itself came from `multiprocessing_logging.install_mp_handler()`, which asserts the `fork` start method; the dependency was already dropped in this version
    - New `parallel_logging_test.py` runs a worker with every start method available on the platform and checks that its records reach the main process handlers
  - **`replacement_env_vars`** is now declared in the MegaLinter configuration JSON schema (`command_info` definition, with its `var_src` / `var_dest` items) and documented in the [Pre-commands](https://megalinter.io/latest/config-precommands/) page: it was implemented but validated by nothing, as `additionalProperties` is unset (#8812)
    - `pre_post_factory.build_command_env()` extracts the child environment build from `run_command()`, and resolves `var_src` from the raw configuration instead of the already secured environment, so a secured source variable is not copied as `HIDDEN_BY_MEGALINTER`
  - **Crash diagnostics**: `megalinter.run.enable_crash_diagnostics()` enables `faulthandler` and raises the thread stack size to 8 MiB (the glibc default) before any thread is started, and worker processes enable `faulthandler` too. musl gives threads a 128 KiB stack and CPython below 3.14.7 miscomputed its stack guard there ([cpython#148260](https://github.com/python/cpython/issues/148260)), so C-level recursion in a thread - such as pickling the linter object graph in the `multiprocessing.Pool` handler threads, which reaches the whole `Megalinter` instance through `Linter.master` - crashed the process with `SIGSEGV` instead of raising `RecursionError` (#8779)
    - Verified on `python:3.14.6-alpine`: pickling a deeply nested object in a thread exits with signal 11, and either raising the thread stack size or moving to `python:3.14.7-alpine` turns it into a plain `RecursionError`
    - `faulthandler` can not report a stack overflow itself (the handler has no stack left to run on), which is why the crash in [#8733](https://github.com/oxsecurity/megalinter/issues/8733) left no output at all; it does report every other fatal signal
  - The Docker images assert a **Python 3.14.7 floor** at build time, the first release carrying the CPython musl thread stack fixes. The `python:3.14-alpine3.24` tag stays floating because `renovate.json5` scopes the `dockerfile` manager away from the main `Dockerfile`, whose `FROM` lines are generated from descriptors (#8779)
  - Retired the `cli_lint_mode_project_exclude_workspace_file_name` descriptor property and the `write_workspace_generated_file()` helper, and removed the property from the descriptor JSON schema so a future descriptor can not silently reintroduce a write inside the analyzed sources. Exclusion forwarding now offers three mechanisms only: native CLI flag, generated ignore file in the report folder, generated config via `manage_excluded_directories_config()` (#8720)
  - **Deprecation flags of removed linters are now reversible** in the configuration JSON schema: `build.py` clears the `deprecated` flag and the `(deprecated)` title prefix of variables whose linter or descriptor is back, instead of only ever adding them (#8718)
  - New **`megalinter/ci_providers/`** package, mirroring the `api_providers` pattern: `CiProvider` base class plus `CiProviderAzurePipelines`, `CiProviderGithubActions` and `CiProviderGitlab`, exposing `get_pr_commit_shas()` and a platform specific `get_pr_commit_shas_hint()` (#8780)
    - `ci_providers.get_pr_ci_provider()` returns the provider matching the current Pull Request context, falling back to the neutral base provider so callers never handle a missing provider
    - The Azure Pipelines and GitHub Pull Request SHA lookups moved out of `BetterleaksLinter`, which keeps only the orchestration, and are now covered by `ci_providers_test.py` outside Docker
  - **CI platform knowledge is concentrated in `megalinter/ci_providers/`** instead of being spread across `utils`, `utils_reporter`, `MegaLinter` and the reporters (#8780)
    - `reporters/jenkins_ci_vars.py` becomes `ci_providers/CiProviderJenkins.py`: it was never a reporter, it is called from `Megalinter.__init__`
    - New `CiProviderBitbucket`, and every provider implements `is_current()`, so `get_ci_provider()` resolves the platform running the build
    - `CiProvider` exposes `get_repo_name()`, `get_branch_name()`, `get_job_url()`, `log_section_start/end()`, `set_output()`, `publish_job_summary()` and `markdown_supports_html_details`
    - `utils.get_git_context_info()` and `utils_reporter.log_section_start/end()` delegate to the provider instead of their platform `if/elif` chains, and the GitHub run URL (built in 3 places), the Bitbucket step URL (2 places) and the Azure `BUILD_BUILDID`/`BUILD_BUILD_ID` fallback are deduplicated
    - `utils.is_ci()` and `utils.is_pr()` were missing Bitbucket Pipelines; new `utils.is_bitbucket_pr()`
    - The **comment reporters** (`GithubCommentReporter`, `GitlabCommentReporter`, `AzureCommentReporter`, `BitbucketCommentReporter`) and `GithubStatusReporter` now get their repository, Pull Request number, tokens, API urls and headers from their provider instead of reading platform variables themselves; they keep only the comment transport and rendering
    - Each reporter instantiates **its own platform provider directly** rather than calling `get_ci_provider()`: under Jenkins the running platform is Jenkins, which maps its variables onto the other platforms', so a factory lookup would disable the comment reporters there
    - `CiProviderAzurePipelines` owns the repository id resolution (`SYSTEM_PULLREQUEST_SOURCEREPOSITORYURI` parsing, API lookup, `BUILD_REPOSITORY_ID` fallback) and `build_git_api_url()`; `CiProviderGitlab` owns the merge request iid resolution and the python-gitlab auth options
    - GitHub keeps `get_auth_token()` (`GITHUB_TOKEN`) and `get_user_auth_token()` (`PAT`) **separate on purpose**: commit statuses need the `statuses:write` scope that the documented fine-grained PAT does not carry
  - **spectral is installed in its own `node_modules` tree** (`/node-deps-spectral`) instead of the shared `/node-deps` one, which is what made it crash: `@prantlf/jsonlint` pins `ajv` to exactly `8.17.1` and so owns the hoisted root copy, while `@stoplight/spectral-core` requires `ajv >= 8.18.0` and gets a nested one, so its hoisted `ajv-errors` bound to the other `ajv` instance and ajv generated invalid JavaScript (`SyntaxError: Unexpected token ':'` at `new Function`). Any npm linter sharing the tree with an exact-pinned transitive dependency can hit the same trap (#8718)
  - **6 Python dependencies removed** from the MegaLinter runtime, replaced by standard library equivalents: `commentjson`, `terminaltables` and `multiprocessing_logging` (unmaintained), plus `termcolor`, `regex` and the obsolete `importlib-metadata` backport (#8710)
  - **Shared linter definitions**: linter entries duplicated across several descriptors (eslint, prettier, v8r, dotnet-format, cpplint, cppcheck, clang-format) are now factorized in `megalinter/descriptors/shared/*.megalinter-linter.yml` files, referenced from descriptors with the new linter-level `extends` property (shallow merge, descriptor entry properties override the shared ones) (#8705)
  - **Docker pulls monthly chart**: the auto-update workflow now regenerates `docs/assets/images/docker-pulls-monthly.svg` (new pulls per month since October 2020, all images and registries), via the new `.automation/docker_pulls_chart.py` called by `build.py` after the pull counters update (#8698)
    - Historical monthly points are frozen in `.automation/generated/docker-pulls-monthly.json` (built once from the tracked stats plus a Web Archive reconstruction of the collection gaps); the script only appends newly completed months computed from `flavors-stats.json`
  - Docker pull counters now also track the **standalone `megalinter-only-*` images**: their download counts are stored in `flavors-stats.json` and included in the README badge total (#8698)
  - New descriptor `activation_rules` type **`variable_is_set`**, activating a linter as soon as a variable holds a value. The existing `variable` type can only compare a variable to a fixed `expected_value`, which can not express "a credential is present" - the condition **SALESFORCE_CODE_ANALYZER_APEXGURU** needs on `SFDX_AUTH_URL` (#8820)
    - Linter tests gated on such a variable **skip themselves** when it is missing, instead of failing: `LinterTestRoot.skip_if_required_variables_missing()` guards the per-lint-mode and SARIF tests, while the version and help tests keep running since they need no credential
  - The release build stages **newly generated documentation pages** too: `build.py` staged only already-tracked files (`git add -u`), so a page created for the first time was left out of the release commit and 404ed on megalinter.io — as `docs/licenses/rumdl.md` and `docs/licenses/zizmor.md` still do since v10.0.0

- CI
  - The generated linter guides in `skills/megalinter-fix/linters/` are excluded from the markdown linters: their error-format regexes end with a significant space that `markdownlint --fix` strips, which corrupted the documented regex and left the working tree dirty, failing the auto-fix commit step on every pull request (#8848)
  - **Supply-chain hardening of dependency updates**: Renovate (`minimumReleaseAge`) and Dependabot (`cooldown`) now wait until a release is at least **7 days old** before proposing an upgrade, so compromised releases can be caught by the community first. Security fixes are not delayed and still open immediately (#8710)
  - New **Check agent plugins manifests** workflow validating the agent plugin manifests on every change to them or to `skills/`: `.automation/validate_agent_plugins.py` checks the root `plugin.json` against the published Agent Plugins 1.0 schema and keeps the per-vendor manifests consistent with it, then `claude plugin validate ./ --strict` checks the Claude Code marketplace and plugin manifests (#8791)
  - The auto-update workflow patch-bumps the agent plugin version when it regenerates the skills: the plugin follows its own release train, since its fix guides change far more often than MegaLinter is released. `plugin.json` is the single source of truth, mirrored into the per-vendor manifests by `.automation/agent_plugin_manifests.py` (called by `build.py`) (#8791)
  - The test workflows forward the **`SFDX_AUTH_URL`** repository secret to the test container, so the **SALESFORCE_CODE_ANALYZER_APEXGURU** lint tests can reach a connected org. The secret is not exposed on pull requests from forked repositories, where those tests skip themselves (#8820)
  - The **Auto-Update Linters** workflow is fixed: `entrypoint.sh` still installed the MkDocs documentation stack, so `build.sh` aborted with `zensical: command not found` since the Zensical migration and no linter version update pull request could be created (#8901)

- Linter versions upgrades (44)
  - [ansible-lint](https://ansible-lint.readthedocs.io/) from 26.6.0 to **26.8.0**
  - [biome](https://biomejs.dev) from 2.5.7 to **2.5.11**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 1.54.0 to **1.55.1**
  - [checkov](https://www.checkov.io/) from 3.3.9 to **3.3.15**
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.97 to **0.1.98**
  - [code-analyzer-apex](https://developer.salesforce.com/docs/platform/salesforce-code-analyzer/guide/get-started.html) from 5.15.0 to **5.16.0**
  - [code-analyzer-aura](https://developer.salesforce.com/docs/platform/salesforce-code-analyzer/guide/get-started.html) from 5.15.0 to **5.16.0**
  - [code-analyzer-flow](https://developer.salesforce.com/docs/platform/salesforce-code-analyzer/guide/engine-flow.html) from 5.15.0 to **5.16.0**
  - [code-analyzer-lwc](https://developer.salesforce.com/docs/platform/salesforce-code-analyzer/guide/get-started.html) from 5.15.0 to **5.16.0**
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 10.0.1 to **10.1.1**
  - [djlint](https://djlint.com/) from 1.44.1 to **1.44.2**
  - [editorconfig-checker](https://editorconfig-checker.github.io/) from 3.10.0 to **3.11.1**
  - [eslint](https://eslint.org) from 10.8.0 to **10.9.1**
  - [golangci-lint](https://golangci-lint.run/) from 2.12.2 to **2.13.2**
  - [grype](https://github.com/anchore/grype) from 0.116.1 to **0.118.0**
  - [jscpd](https://github.com/kucherenko/jscpd/tree/master/apps/jscpd) from 5.0.14 to **5.0.16**
  - [kingfisher](https://github.com/mongodb/kingfisher) from 1.112.0 to **2.0.0**
  - [npm-package-json-lint](https://npmpackagejsonlint.org/) from 10.4.1 to **11.0.0**
  - [php-cs-fixer](https://cs.symfony.com/) from 3.95.18 to **3.95.23**
  - [phpstan](https://phpstan.org/) from 2.2.8 to **2.2.9**
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.6.4 to **7.6.5**
  - [powershell_formatter](https://github.com/PowerShell/PSScriptAnalyzer) from 7.6.4 to **7.6.5**
  - [protolint](https://github.com/yoheimuta/protolint) from 0.56.4 to **0.57.0**
  - [pylint](https://pylint.readthedocs.io) from 4.0.6 to **4.0.7**
  - [pyright](https://github.com/Microsoft/pyright) from 1.1.411 to **1.1.413**
  - [revive](https://revive.run/) from 1.15.0 to **1.16.0**
  - [robocop](https://github.com/MarketSquare/robotframework-robocop) from 8.6.0 to **9.0.0**
  - [roslynator](https://github.com/dotnet/Roslynator) from 0.12.0.0 to **0.13.0.0**
  - [rubocop](https://rubocop.org/) from 1.89.0 to **1.90.0**
  - [ruff](https://github.com/astral-sh/ruff) from 0.16.2 to **0.16.5**
  - [ruff-format](https://github.com/astral-sh/ruff) from 0.16.2 to **0.16.5**
  - [rumdl](https://github.com/rvben/rumdl) from 0.2.52 to **0.2.62**
  - [secretlint](https://github.com/secretlint/secretlint) from 13.0.4 to **13.0.5**
  - [semgrep](https://semgrep.dev/) from 1.172.0 to **1.175.0**
  - [snakemake](https://snakemake.github.io/) from 9.25.1 to **9.26.1**
  - [spectral](https://github.com/stoplightio/spectral) from 6.15.0 to **6.16.3**
  - [swiftlint](https://github.com/realm/SwiftLint) from 0.65.0 to **0.65.1**
  - [syft](https://github.com/anchore/syft) from 1.50.0 to **1.51.1**
  - [terraform-fmt](https://developer.hashicorp.com/terraform/cli/commands/fmt) from 1.15.8 to **1.16.0**
  - [terragrunt](https://docs.terragrunt.com/reference/cli/commands/hcl/fmt/) from 1.1.2 to **1.1.4**
  - [trivy](https://aquasecurity.github.io/trivy/) from 0.73.0 to **0.74.0**
  - [trivy-sbom](https://aquasecurity.github.io/trivy/) from 0.73.0 to **0.74.0**
  - [trufflehog](https://github.com/trufflesecurity/trufflehog) from 3.96.0 to **3.97.1**
  - [vale](https://vale.sh/) from 3.17.1 to **3.18.0**

## [v10.0.0] - 2026-08-08

- Breaking changes
  - **Removed 14 deprecated or long-disabled linters**, and the `API`, `MAKEFILE` and `PUPPET` descriptors, which had no other linter left. MegaLinter does not provide Makefile and Puppet linting anymore. See the new [Removed linters](https://megalinter.io/latest/removed-linters/) page for the full list and suggested replacements. (#8606)
  - **`REPOSITORY_GITLEAKS` has been removed**: migrate to [REPOSITORY_BETTERLEAKS](https://megalinter.io/latest/descriptors/repository_betterleaks/), which reads your existing `.gitleaks.toml` and `.gitleaksignore` files unchanged. (#8606)
  - **Existing `.mega-linter.yml` files keep working**: configuration variables of removed linters are simply ignored (a single notice lists any found in your configuration) and remain valid in the JSON schema. (#8606)
  - **API Reporter payload v2** replaces the v1 payload: metric series are renamed (`linter_run_*` becomes `megalinter_linter_run_*`, plus new run-level `megalinter_run_*` series), and the old `docs/grafana` dashboards are superseded. Re-provision the new dashboards with **`npx mega-linter-runner --upload-dashboards grafana`** — see the [migration notes](https://megalinter.io/latest/reporters/ApiReporter/#migration-from-payload-v1). Legacy `NOTIF_API_*` variables remain supported as aliases. (#8661)
  - **Linters now time out after 5 minutes by default** (`LINTER_TIMEOUT_SECONDS: 300`): a linter exceeding it is killed and reported as an error (exit code 124) instead of running (or hanging) unbounded. If some of your linters legitimately run longer, raise the limit globally with `LINTER_TIMEOUT_SECONDS`, per linter with `<LINTER_KEY>_TIMEOUT_SECONDS`, or restore the previous unbounded behavior with value `0`. (#8665)

- Core
  - **Coding agents integration**: MegaLinter can now be driven by Claude Code, Cursor CLI, GitHub Copilot CLI, Codex and many other coding agents — see the new [Coding Agents](https://megalinter.io/latest/coding-agents/) documentation page (#8614)
    - Install the [MegaLinter agent skills](https://megalinter.io/latest/install-agent-skills/) with **`npx skills add oxsecurity/megalinter`**
    - Then ask your agent to set up MegaLinter (`megalinter-setup`), watch CI or local runs (`megalinter-check`) or fix lint errors (`megalinter-fix`)
    - Before the first **local run**, the skills now make sure the user is aware that MegaLinter is Docker-based and needs a good computer configuration and internet connection (the image download can weigh several GB), and suggest watching CI results instead when that is a problem
    - Local runs launched by the skills now cap **`PARALLEL_PROCESS_NUMBER`** to 4 on local computers (CI runs keep one parallel linter process per CPU core), so linting does not saturate the machine
    - Local runs launched by the skills now always activate the **JSON reporter** (not generated by default) to read results reliably, and fall back to the report folder configuration then the console output instead of waiting for report files that a repository configuration may have disabled
  - **Excluded directories are now forwarded to project-mode linters**, massively speeding up local runs, fixes [#8645](https://github.com/oxsecurity/megalinter/issues/8645)
    - Linters that scan the whole workspace by themselves (`REPOSITORY_TRIVY`, `REPOSITORY_CHECKOV`, `REPOSITORY_GRYPE`, `REPOSITORY_TRUFFLEHOG`, `REPOSITORY_SEMGREP` and 50+ others) used to crawl everything, including build caches and `node_modules`: a seconds-long CI lint could take **hours on a local checkout**
    - MegaLinter now automatically passes the excluded directories (defaults, `EXCLUDED_DIRECTORIES`, `ADDITIONAL_EXCLUDED_DIRECTORIES`, and directories detected in `FILTER_REGEX_EXCLUDE`) to each of these linters, through its native exclusion flags or a generated ignore/config file
    - Every forwarded exclusion is logged in the linter's console section, and the ">300 gitignored files" performance warning now names the heaviest directories it found
    - Opt out globally with `FORWARD_EXCLUDED_DIRECTORIES: false`, or per linter with `<LINTER_KEY>_FORWARD_EXCLUDED_DIRECTORIES: false`
  - **Default excluded directories** now also include common build/cache folders: `.wireit`, `.turbo`, `.nx`, `.yarn/cache`, `.pnpm-store`, `.parcel-cache`, `.angular`, and the Salesforce CLI `.sf` / `.sfdx` state folders (#8646)
  - New **per-linter timeout**: a linter still running after **5 minutes** (`LINTER_TIMEOUT_SECONDS: 300` by default) is killed along with all its child processes and reported as an error (exit code 124) with an actionable message, while the other linters keep running. Raise the limit globally with `LINTER_TIMEOUT_SECONDS`, per linter with `<LINTER_KEY>_TIMEOUT_SECONDS`, or disable it with value `0` (#8665)
  - New **prerun analysis mode** (`mega-linter-runner --prerun`, or `MEGALINTER_PRERUN=true` environment variable): MegaLinter identifies active linters and collects files, then stops before running any linter and suggests configuration improvements, in the console and in `megalinter-reports/prerun-report.json` (#8653)
    - Suggested exclusions: top-level directories containing only gitignored files (safe: linting scope is unchanged, and project-mode linters stop scanning them), and well-known generated/vendored folder names (`site`, `dist`, `vendor`...) still containing lintable files (to confirm by the user)
    - A lighter matching flavor is also suggested when available
    - The `megalinter-check` agent skill uses it on the first local run to tune `.mega-linter.yml` with the user before the real lint
    - Fixed a performance issue where detecting `.gitignore`d files enumerated every individual file inside large ignored folders (`node_modules`, build output...) instead of stopping at the folder boundary, which could make the file collection step (including prerun) take several minutes on big repositories
  - **Much lighter Docker images**: the main image download shrinks by **9%**, flavors by **9% to 22%**, and standalone `megalinter-only-*` images are **35% to 65% smaller** (#8621)
    - If your `PRE_COMMANDS` compile native code: the compilation toolchain is no longer shipped in the images, install it back with `apk add --no-cache gcc make musl-dev`
    - Main and flavor images, compressed download size on ghcr.io, linux/amd64 (before = v9.6.0, so deltas also include the linters removed in this version):

      | Image                      |  Before |   After | Delta |
      |----------------------------|--------:|--------:|------:|
      | `megalinter` (main)        | 4.55 GB | 4.13 GB |   -9% |
      | `megalinter-c_cpp`         | 1.61 GB | 1.35 GB |  -16% |
      | `megalinter-ci_light`      |  724 MB |  657 MB |   -9% |
      | `megalinter-cupcake`       | 2.52 GB | 2.24 GB |  -11% |
      | `megalinter-documentation` | 1.47 GB | 1.21 GB |  -18% |
      | `megalinter-dotnet`        | 2.23 GB | 1.86 GB |  -17% |
      | `megalinter-dotnetweb`     | 2.25 GB | 1.88 GB |  -17% |
      | `megalinter-formatters`    |  936 MB |  849 MB |   -9% |
      | `megalinter-go`            | 1.55 GB | 1.35 GB |  -13% |
      | `megalinter-java`          | 1.59 GB | 1.32 GB |  -17% |
      | `megalinter-javascript`    | 1.49 GB | 1.23 GB |  -18% |
      | `megalinter-php`           | 1.51 GB | 1.26 GB |  -17% |
      | `megalinter-python`        | 1.61 GB | 1.26 GB |  -22% |
      | `megalinter-ruby`          | 1.49 GB | 1.22 GB |  -18% |
      | `megalinter-rust`          | 1.99 GB | 1.80 GB |  -10% |
      | `megalinter-salesforce`    | 2.09 GB | 1.87 GB |  -10% |
      | `megalinter-security`      | 1.30 GB | 1.17 GB |  -10% |
      | `megalinter-swift`         | 1.51 GB | 1.24 GB |  -18% |
      | `megalinter-terraform`     | 1.59 GB | 1.30 GB |  -18% |

    - Standalone single-linter images, uncompressed size on linux/amd64 (before = previous beta):

      | Image                                    |  Before |  After | Delta |
      |------------------------------------------|--------:|-------:|------:|
      | `megalinter-only-groovy_npm_groovy_lint` | 1.07 GB | 695 MB |  -35% |
      | `megalinter-only-r_lintr`                |  996 MB | 405 MB |  -59% |
      | `megalinter-only-spell_proselint`        |  813 MB | 284 MB |  -65% |
      | `megalinter-only-css_stylelint`          |  780 MB | 360 MB |  -54% |
      | `megalinter-only-spell_cspell`           |  755 MB | 357 MB |  -53% |
      | `megalinter-only-ruby_rubocop`           |  702 MB | 301 MB |  -57% |
      | `megalinter-only-perl_perlcritic`        |  696 MB | 293 MB |  -58% |
      | `megalinter-only-spell_vale`             |  683 MB | 286 MB |  -58% |
      | `megalinter-only-yaml_yamllint`          |  668 MB | 271 MB |  -59% |
      | `megalinter-only-bash_shellcheck`        |  660 MB | 263 MB |  -60% |
      | `megalinter-only-lua_luacheck`           |  652 MB | 252 MB |  -61% |
      | `megalinter-only-xml_xmllint`            |  645 MB | 246 MB |  -62% |

  - **Faster startup on every run** (~5 seconds saved) (#8624)
    - Linter versions now come from a manifest built into the Docker image, instead of calling every linter's `--version`
    - LLM Advisor libraries are only loaded when `LLM_ADVISOR_ENABLED` is true
    - Set the new `VERSION_GET_AT_RUNTIME: true` variable if your `PRE_COMMANDS` install different linter versions and you want the really installed versions reported
  - **Faster linting when fixes are applied** (`APPLY_FIXES`): the check-only linters of a language now run in parallel as soon as its fixer linters are done, instead of all linters of the language running one after another (#8624)
  - **Faster standalone images and file-list runs**: `megalinter-only-*` images only parse the descriptor of their single linter, and the repository-wide `.gitignore` enumeration is skipped when an explicit list of files is passed (e.g. `mega-linter-runner [files...]` on a large repository) (#8614)
  - **Runtime speed-ups combined**, measured on the MegaLinter repository itself and on real-world repositories upgraded to this version (average of the last successful CI runs before / first CI runs after the upgrade):

    | Measure                                                                                                                 | Before | After | Delta |
    |-------------------------------------------------------------------------------------------------------------------------|-------:|------:|------:|
    | MegaLinter repository: full run (all linters, fixes applied)                                                            |  4m26s | 3m18s |  -26% |
    | MegaLinter startup (`import megalinter`)                                                                                |    ~7s | ~0.9s |  -87% |
    | [sfdx-hardis](https://github.com/hardisgroupcom/sfdx-hardis) CI MegaLinter job (v9.6.0 → beta, javascript flavor)       |  6m02s | 3m17s |  -45% |
    | [vscode-sfdx-hardis](https://github.com/hardisgroupcom/vscode-sfdx-hardis) CI MegaLinter job (late-July → current beta) |  3m10s | 2m34s |  -19% |

  - **Better secrets masking in logs**, now powered by the [betterleaks](https://github.com/betterleaks/betterleaks) ruleset: redaction coverage nearly doubles (218 to 408 patterns), with no more network call at startup (#8606)
  - `FILTER_REGEX_INCLUDE` and `FILTER_REGEX_EXCLUDE` (global, per-descriptor and per-linter) can now be defined as **a list of regexes** combined with a logical OR, so filter regexes can be appended across `EXTENDS` configs via `CONFIG_PROPERTIES_TO_APPEND`; single-string values remain fully supported, fixes [#8361](https://github.com/oxsecurity/megalinter/issues/8361)
  - New **`ENABLE_DISABLE_LINTERS_PRIORITY`** variable to let `DISABLE_LINTERS` override `ENABLE_LINTERS` when a linter is in both lists (e.g. to trim an inherited `ENABLE_LINTERS` list via `EXTENDS`), fixes [#8296](https://github.com/oxsecurity/megalinter/issues/8296)
  - New **`MEGALINTER_FLAVOR`** and **`MEGALINTER_VERSION`** properties in `.mega-linter.yml`, to pin the flavor and version of the MegaLinter Docker image once in the repository and have them reused by mega-linter-runner and the agent skills (#8614)
  - Display a **distinct ☑️ status icon** (instead of ⚠️) for linters that found errors without blocking the run because the error count stayed under `<LINTER>_DISABLE_ERRORS_IF_LESS_THAN`, and show the configured maximum in the console and Pull Request summary tables (#8496)
  - A `<LINTER>_CLI_LINT_MODE` override targeting a lint mode the linter does not support is now **rejected with an explicit error** instead of failing at lint time, fixes [#7120](https://github.com/oxsecurity/megalinter/issues/7120)

- New linters
  - Add **[SALESFORCE_CODE_ANALYZER_FLOW](https://megalinter.io/latest/descriptors/salesforce_code_analyzer_flow/)**, the Salesforce Code Analyzer v5 Flow Scanner engine that audits Salesforce Flows for security issues (#8408)

- Removed linters
  - **API_SPECTRAL**: crashing with no upstream fix (#8606)
  - **JSON_ESLINT_PLUGIN_JSONC**: blocked by [eslint-plugin-jsonc#328](https://github.com/ota-meshi/eslint-plugin-jsonc/issues/328), use `JSON_PRETTIER` or `JSON_JSONLINT` instead (#8606)
  - **LUA_SELENE**: blocked by [selene#662](https://github.com/Kampfkarren/selene/issues/662), use `LUA_LUACHECK` instead (#8606)
  - **MAKEFILE_CHECKMAKE**: disabled for [security issues](https://github.com/checkmake/checkmake/issues/99) (#8606)
  - **MARKDOWN_REMARK_LINT**: blocked by [remark-lint#322](https://github.com/remarkjs/remark-lint/issues/322), use `MARKDOWN_MARKDOWNLINT` instead (#8606)
  - **PUPPET_PUPPET_LINT**: blocked by [puppet-lint#251](https://github.com/puppetlabs/puppet-lint/issues/251) (#8606)
  - **REPOSITORY_GITLEAKS**: superseded by [betterleaks](https://github.com/betterleaks/betterleaks), use `REPOSITORY_BETTERLEAKS` instead (#8606)
  - **REPOSITORY_KICS**: disabled after the [Checkmarx supply chain compromise](https://socket.dev/blog/checkmarx-supply-chain-compromise), use `REPOSITORY_CHECKOV` instead (#8606)
  - **SALESFORCE_LIGHTNING_FLOW_SCANNER**: upstream repository archived, use `SALESFORCE_CODE_ANALYZER_FLOW` instead (#8606)
  - **SALESFORCE_SFDX_SCANNER_APEX**, **SALESFORCE_SFDX_SCANNER_AURA**, **SALESFORCE_SFDX_SCANNER_LWC**: deprecated by Salesforce and incompatible with Node.js 22+, use the matching `SALESFORCE_CODE_ANALYZER_*` linters instead (#8606)
  - **SQL_TSQLLINT**: upstream unmaintained since 2024-09 and shipping unpatched .NET CVEs (#8606)
  - **TERRAFORM_TERRASCAN**: upstream repository archived by Tenable and shipping unpatched CVEs, use `REPOSITORY_CHECKOV` instead (#8606)

- Linters enhancements
  - **`REPOSITORY_CHECKOV` now skips its `secrets` framework** (`--skip-framework secrets`) when a dedicated secret scanner (betterleaks, kingfisher, secretlint or trufflehog) is active in the same run: the duplicated secrets scan added minutes to every run and could stall for hours on bind-mounted workspaces. Define `--framework` or `--skip-framework` in `REPOSITORY_CHECKOV_ARGUMENTS` (or in your checkov config file) to keep checkov's own secrets scan (#8665)

- Fixes
  - Stop **`FutureWarning: Possible nested set` warnings** appearing in the console at startup: a **secret-masking** regex used a POSIX character class (`[[:alnum:]]`) unsupported by Python. Such classes are now translated, which also makes the affected masking rule (Airtable personal access tokens) actually match (#8684)
  - Restore **multi-arch `megalinter-only-*` Docker images**: they were mistakenly published for a single architecture, linux/amd64 + linux/arm64 are back (#8247)
  - Fix linters relying on other linters' file lists (e.g. `SPELL_CSPELL`) **linting zero files** when run through their standalone `megalinter-only-*` Docker image (#8614)
  - Fix **`LINTER_RULES_PATH`** not being used to resolve config files for linters using `active_only_if_file_found` (e.g. `REPOSITORY_LS_LINT`, `SPELL_PROSELINT`, `SPELL_VALE`), fixes [#8416](https://github.com/oxsecurity/megalinter/issues/8416)
  - Honor `EXCLUDED_DIRECTORIES` and `ADDITIONAL_EXCLUDED_DIRECTORIES` in **changed-files mode** (`VALIDATE_ALL_CODEBASE: false`), the same way they are honored during full-codebase validation ([#8360](https://github.com/oxsecurity/megalinter/issues/8360))
  - Make **remote configuration loading** (`MEGALINTER_CONFIG` and `EXTENDS` files fetched over HTTP) resilient to transient network failures with a request timeout and retries (#8349)
  - Bound the **gitignored-files detection** (`git ls-files`) with a 120 seconds timeout: on workspaces with pathologically slow file access (e.g. bind-mounted from Windows into a WSL2-backed container engine) this internal git call could hang the whole run before any linter started; it now degrades to an actionable warning and the run continues (#8665)
  - Allow **`CSS_STYLELINT_COMMAND_REMOVE_ARGUMENTS`** to remove `--config-basedir`, and stop raising an error when an argument listed in `<LINTER>_COMMAND_REMOVE_ARGUMENTS` is not in the command line, fixes [#8552](https://github.com/oxsecurity/megalinter/issues/8552)
  - Treat **zero matching SARIF findings** as a valid result without logging the entire report, fixes [#8295](https://github.com/oxsecurity/megalinter/issues/8295)
  - Remove **invalid SARIF fixes** with empty `artifactChanges` arrays before report aggregation, fixes [#8474](https://github.com/oxsecurity/megalinter/issues/8474)
  - Fix **`SARIF_TO_HUMAN`** producing empty linter logs when the SARIF-to-text conversion crashed; raw SARIF is now shown as a fallback (#8294)
  - Keep **`REPOSITORY_CHECKOV`'s transient GitHub-configuration scan files** (`branch_protection_rules.json` and similar) out of the linted repository — they are now written inside the report folder, so they no longer appear in other linters' results (#8406)
  - Fix a **`REPOSITORY_SECRETLINT` crash** (ENOENT) when it scanned report files being written at the same time by other linters (#8624)
  - `COPYPASTE_JSCPD` now runs on **linux/amd64 only**: jscpd v5 provides no ARM64 binary compatible with MegaLinter images, so it always failed with `Unsupported platform linux/arm64` on ARM (#8610)

- Reporters
  - **Observability**: MegaLinter results can now feed [Grafana, Datadog, Elastic and New Relic](https://megalinter.io/latest/observability/), with **ready-to-use, linked dashboards** (fleet overview → repository detail → linter detail, with health score and errors evolution by repository, linter and language) — see the new [Observability](https://megalinter.io/latest/observability/) documentation section (#8661)
    - The **API Reporter payload v2** adds run-level KPIs (**quality gate** status, a 0-100 **repository health score**, blocking/non-blocking error counts, auto-fixed errors, run duration) and per-linter **top rules and top files** breakdowns (parsed from SARIF output, disable with `API_REPORTER_DETAILS: false`)
    - New **`API_REPORTER_PROVIDER`** variable: comma-separated list of target providers (`grafana` by default, `datadog`, `elastic`, `newrelic`) with per-provider auth variables (`API_REPORTER_DATADOG_*`, `API_REPORTER_ELASTIC_*`, `API_REPORTER_NEWRELIC_*`)
    - Dashboards are provisioned automatically with **`npx mega-linter-runner --upload-dashboards <provider>`** (idempotent create-or-update), also proposed during `--install` and `--upgrade`
  - New **`API_REPORTER_PAYLOAD_FORMAT`** variable (`auto`, `loki` or `default`) to force the payload format sent by the API Reporter, instead of only deducing it from the endpoint URL (#8661)
  - **Observability dashboards reviewed and improved** against each provider's official guidance — refresh yours with **`npx mega-linter-runner --upload-dashboards <provider>`** (#8667)
    - **Correct KPIs**: Grafana "latest run" stats no longer double-count when several branches or MegaLinter versions report in the window, and stale series (deleted branches, pre-upgrade versions) no longer linger; the **quality gate pass rate** is now a true pass rate over the selected period on Grafana, Datadog and New Relic; "errors auto-fixed" and "time saved" now show period totals consistently on all providers
    - **Working navigation**: Grafana drill-down links now keep the selected branch, and New Relic facet links to the **Repository detail** and **Why this rating?** pages now actually work (they were silently ignored)
    - **"Why this rating?"** explanations now render correctly on Datadog, Elastic and New Relic (they showed literal `\n` text), and Elastic and New Relic gain the missing **"Linters dragging the score down"** and **"Time saved by auto-fixes"** elements
    - **Readable with sparse CI data**: 1-week default windows on Datadog widgets, 1-day buckets on New Relic charts, run-marker annotations and sparklines on Grafana/Datadog tiles, sorted tables, and semantic colors everywhere (blocking=red, non-blocking=yellow, health A-E bands)
    - **New content**: A-E rating breakdown and quality-gate failure rate (New Relic), files analyzed and health score by MegaLinter version (Datadog), files analyzed and MegaLinter versions in use (Elastic), org-level filter variable (Grafana)
    - Fix the New Relic provider tagging every metric datapoint with `runId`, which burned metric cardinality for no query value
  - Refreshed **OX Security banner** displayed at the bottom of pull request comments and job summaries, using the current OX Security visual identity (#8692)

- Doc
  - **Home page**: mention Coding Agents compliance in the welcome phrase, display the supported coding agent icons next to the CI/CD integrations, and add a "Coding Agents compatible" badge (#8625)
  - **Home page banner** refreshed: highlights **v10**, compliance with **AI coding agents**, and up-to-date download (16 million+) and usage (6,000+ public repos) figures (#8692)
  - **Quick Start**: setting up MegaLinter with a coding agent (`npx skills add oxsecurity/megalinter` then _"setup megalinter"_) is now the first suggested option (#8625)
  - **Coding Agents page**: add Gemini CLI, Windsurf, Cline, Roo Code, Kilo Code, Amp, Goose, OpenHands and Qwen Code to the compatible coding agents (#8625)
  - **megalinter-setup skill**: after install or upgrade, suggest either running MegaLinter locally or creating a pull request and then watching its CI results with megalinter-check (#8625)
  - **megalinter-setup skill**: upgrade mode now systematically migrates CI Docker image references from **Docker Hub to ghcr.io** (images are only published on GitHub Container Registry since v9.5.0), with precise rules on what to rewrite and what to leave untouched (#8694)
  - **megalinter, megalinter-setup and megalinter-check skills**: local runs are flagged as **resource-consuming** and **running in CI is now the recommended option** — when both are possible, the skills ask the user to choose (CI first) instead of silently starting a local run (#8658)
  - **megalinter-check skill**: the first local run now starts with a `--prerun` analysis, so the user can validate the suggested `.mega-linter.yml` performance tuning before the real lint (#8653)
  - **megalinter-check skill and watcher/runner sub-agents**: the console tips MegaLinter prints (performance warnings, flavor suggestions, `[Activation]` notices, deprecations) are now extracted from the persisted log file and returned to the calling agent in a `tips` field, instead of being lost when reading only the JSON report (#8665)
  - **Custom Flavors**: new [Licensing](https://megalinter.io/latest/custom-flavors/#licensing) section — a custom flavor is still MegaLinter, so your flavor repository and the image it publishes are covered by **AGPL-3.0**. Add an `AGPL-3.0` `LICENSE` file to your flavor repository and keep the link to the MegaLinter source in its README, fixes [#8681](https://github.com/oxsecurity/megalinter/issues/8681)
  - Fix outdated links in `docs/descriptors/repository_kingfisher.md` (#8364)

- mega-linter-runner
  - New **`--upload-dashboards <provider>`** option: provision or refresh the MegaLinter observability dashboards in **Grafana**, **Datadog**, **Elastic (Kibana)** or **New Relic**, using the provider auth environment variables ([documentation](https://megalinter.io/latest/observability/)) (#8661)
    - Also proposed as a prompt during interactive `--install` and `--upgrade`, or with **`--setup-dashboards <provider>`** in non-interactive mode
  - **Non-interactive installation**: `--install` can now run without prompts (#8614)
    - Use `--no-prompt` with the new `--setup-*` options (`--setup-ci`, `--setup-copy-paste`, `--setup-spelling-mistakes`, `--setup-default-branch`, `--setup-validate-all-code-base`, `--setup-ox`) and the existing `--flavor`, `--release` and `--fix` flags
    - Pre-existing configuration/workflow files are backed up as `<file>.megalinter-setup.bak` before being overwritten, so customizations can be merged back
  - New **`--linter <LINTER_KEY>`** option to run a single linter using its standalone `megalinter-only-<linter_key>` Docker image, with an optional list of files to lint (#8614)
    - Reports are isolated in `megalinter-reports/<linter_key>`, so several standalone runs can execute in parallel
  - **Flavor and version resolution** now reads `MEGALINTER_FLAVOR` and `MEGALINTER_VERSION` from `.mega-linter.yml` when `--flavor`/`--release` are not passed on the command line, and the install generator writes both properties in the generated configuration (#8614)
  - **`--fix`** now respects an `APPLY_FIXES` value (other than `none`) defined in `.mega-linter.yml` instead of overriding it with `all` (#8614)
  - **`--upgrade`** also bumps a pinned `MEGALINTER_VERSION` property of `.mega-linter.yml` to the current major version (#8614)
  - **`--upgrade`** now migrates **v9 references to v10**: GitHub Action (`oxsecurity/megalinter@v9`, flavors) and Docker image (`ghcr.io/oxsecurity/megalinter:v9`, flavors) references are rewritten to `v10`, and `--install` defaults to `v10`
  - New **`--prerun`** option: analysis-only run that outputs configuration suggestions to improve performances (see the prerun mode in Core section). Combine with `--json` to print the prerun report on stdout (#8653)
  - New **`--timeout <seconds>`** option (`-t`): bound the whole run; on expiration the runner prints the container's last log lines, stops and removes the container (no orphan left behind, even on Windows where killing the CLI process does not stop the container), and exits with code 124 (#8665)
  - **Skip `docker pull`** when the requested version is a pinned release tag (`vX.Y.Z`, immutable) and the image is already available locally, removing a useless registry round-trip (#8614)
  - Print a hint before mounting the workspace when it contains **well-known heavy folders** (build caches, package stores), pointing at `SKIP_CLI_LINT_MODES=project` to keep local runs fast (#8646)
  - **`--custom-flavor-setup`**: the generated README now has a **License** section stating the flavor is covered by **AGPL-3.0**, with a link to the MegaLinter source repository (#8682)
  - **`--custom-flavor-setup` now generates a MegaLinter-clean repository**, so a new custom flavor repo starts green instead of failing its own first MegaLinter run, fixes [#8680](https://github.com/oxsecurity/megalinter/issues/8680)
    - The generated workflows and README now pass **actionlint**, **zizmor**, **editorconfig-checker** and **markdownlint**
    - Actions used by the generated workflows are **hash-pinned**, and a **`.github/zizmor.yml`** is generated to waive the one deliberate exception: the flavor builder tracks `@main` so your image is always built by the builder matching the MegaLinter release you target
    - Fixed the generated builder header comment, which advertised the image at `ghcr.io/<owner>/<repo>:<tag>` instead of `ghcr.io/<owner>/<repo>/megalinter-custom-flavor:<tag>`
    - Fixed the generated PAT setup instructions, which named the repository the template was originally written against
    - [Custom Flavors documentation](https://megalinter.io/latest/custom-flavors/) now covers linting your flavor repository, including the `REPOSITORY_CHECKOV_ARGUMENTS: "--skip-check CKV_GHA_7"` needed by the builder's `workflow_dispatch` inputs

- Dev
  - **ApiReporter refactoring**: provider delivery is now implemented by `ApiProvider` classes (`megalinter/api_providers/`: Grafana, Datadog, Elastic, New Relic), and dashboards are generated by `DashboardBuilder` classes (`.automation/dashboard_builders/`) from a shared metrics contract into `docs/dashboards/` — `build_dashboards.py --check` fails when dashboards and contract drift apart, and the internal `sync-dashboards` Claude skill maintains them (#8661)
  - Add **`megalinter/removed_linters.py`** as the single source of truth for every linter and descriptor removed since v6, used both at runtime and by the build system, and generate the [Removed linters](https://megalinter.io/latest/removed-linters/) documentation page from it (#8606)
  - Add **`supported_cli_lint_modes`** descriptor property to declare which CLI lint modes (`file`, `list_of_files`, `project`) each linter supports, and generate `success`/`failure` tests for every supported mode (#7150)
    - `ACTION_ZIZMOR`, `BASH_SHFMT` and `GO_REVIVE` now declare their real modes instead of falling back to the `file`-only default
  - **Project-mode excluded-directories forwarding internals**: (#8646)
    - New `cli_lint_mode_project_exclude_*` descriptor properties (native exclusion flag templates, ignore-file arguments, generated workspace ignore files) consumed by generic `Linter` base-class code: forwarding is pure descriptor data on 41 linters
    - 13 Python subclass workarounds for tools needing config-merge logic (trufflehog, betterleaks, jscpd, yamllint, rubocop, swiftlint, ls-lint, clj-kondo, eslint, gherkin-lint, luacheck, stylua, phpstan/php-cs-fixer/cljstyle)
    - Poison `.wireit/` test fixtures make the project-lint-mode success tests fail if forwarding regresses
  - New descriptor property **`install.apk_build`** for apk packages needed only while pip/gem packages compile native extensions: they join a virtual apk package removed from the final image layers (#8621)
    - Used by SPELL_PROSELINT (build-base, re2-dev, py3-pybind11-dev needed to build google-re2), which was keeping a full C++ toolchain in every flavor image
  - **Details of the Docker image slimming**: (#8621)
    - LLM Advisor provider SDKs move to an `llm` pip extra excluded from standalone `megalinter-only-*` images (~200 MB per standalone image)
    - The compilation toolchain (gcc, make, musl-dev, libffi-dev) and per-descriptor build toolchains (LUA luarocks, PERL cpm, R packages) are installed as apk virtual packages removed after the install steps (~110-150 MB per image)
    - GROOVY_NPM_GROOVY_LINT reuses the shared OpenJDK 21 instead of shipping its own OpenJDK 17 (~300 MB)
    - Python linter venvs share identical wheels through the uv cache in hardlink mode
    - Extended node_modules pruning, and standalone images drop the ~45 MB `__pycache__` layer
    - Removed a stray `cpplint` Python venv that was mistakenly declared in the CSS_STYLELINT descriptor
  - Keep the **Docker Pulls badge** in `docs/index.md` in sync by having `docker_stats.py` also update the hardcoded badge total in `.automation/build.py` (#8258)
  - Mark the repository's internal Claude Code skills (`.claude/skills/`) as **`internal`** so `npx skills add oxsecurity/megalinter` only offers the four MegaLinter agent skills from the `skills/` folder (#8627)
  - Vendor the **official Grafana, Elastic and Datadog agent skills** (Apache-2.0, with licenses and source attribution) into `.claude/skills/` (`grafana-dashboarding`, `grafana-promql`, `kibana-dashboards`, `datadog-dashboards`) to guide observability dashboard maintenance alongside the `sync-dashboards` skill — New Relic publishes no official agent skill (only an MCP server) (#8667)
  - Fix the **`/build` contribution skill** being accidentally gitignored by the `build/` packaging pattern, so it is now actually versioned (#8627)

- CI
  - **Speed up PR jobs** by handing the built Docker image over to consumer jobs through **ghcr.io** (`megalinter-dev` per-commit tags, pruned daily) instead of a workflow artifact + `docker load` (#8624)
    - For branches of the main repository only: forked PRs keep the artifact-based handoff, since their GITHUB_TOKEN cannot push packages
  - Build only the **per-linter Docker images impacted by the changed files** of a PR (descriptor edits, per-linter Dockerfiles, single-linter test fixtures); any change to shared code or unrecognized files keeps building the full matrix (#8624)
  - Remove **duplicate self-lint and mega-linter-runner test runs** on PR branches: the `push` trigger is now restricted to main-line branches, the `pull_request` trigger already covers PR commits (~15 duplicated job-minutes saved per PR commit) (#8624)
  - **Speed up the test suite** by skipping the `file` CLI lint mode tests for linters that also support `list_of_files`, since `list_of_files` exercises the same code path more cheaply (#8624)
  - **CI jobs before/after**, measured on the deploy-DEV workflow (average of 3 successful runs each, before = early July 2026, after = 2026-08-05):

    | CI job / step                               | Before |  After | Delta |
    |---------------------------------------------|-------:|-------:|------:|
    | Docker image handoff to a consumer job      |  4m51s |  2m39s |  -45% |
    | "Run against all code base" — whole job     | 11m16s |  7m16s |  -36% |
    | "Run against all code base" — lint step     |  5m08s |  3m18s |  -36% |
    | "Run Test Cases" (pytest suite) — whole job | 15m30s | 14m00s |  -10% |
    | "mega-linter-runner tests" — whole job      | 14m20s |  8m17s |  -42% |

    - The pytest suite gain is partly offset by the many new per-lint-mode and project-mode-exclusion tests added in this version
  - TAP reporter golden-file tests move from the 120+ generated per-linter test classes (where most of them skipped) to a dedicated `tap_reporter_test` class running on a curated sample of linters (bash, css, protobuf, cloudformation); stale Super-Linter-era expected files (some of them unreachable by the test suite) have been removed (#8624)
  - Make `test_api_output` resilient to remote server outages: probe several public echo endpoints, run the test with the ones that are up, retry with another server when a post fails, and skip the test when none of them is reachable, as a remote outage is not a MegaLinter issue (#8538)
  - Fix per-linter Docker images being published single-arch: the BETA and RELEASE linter workflows split each linter into independent per-platform jobs that all pushed the same tag, so the last push won and overwrote the other architecture. They now push each platform by digest and a dedicated merge job assembles a proper multi-arch manifest list per linter (#8247)

- Linter versions upgrades (50)
  - [ansible-lint](https://ansible-lint.readthedocs.io/) from 26.4.0 to **26.6.0**
  - [betterleaks](https://github.com/betterleaks/betterleaks) from 1.6.0 to **1.7.3**
  - [bicep_linter](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter) from 0.44.1 to **0.46.1**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 1.52.0 to **1.54.0**
  - [checkov](https://www.checkov.io/) from 3.3.2 to **3.3.9**
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.96 to **0.1.97**
  - [code-analyzer-apex](https://developer.salesforce.com/docs/platform/salesforce-code-analyzer/guide/get-started.html) from 5.13.0 to **5.15.0**
  - [code-analyzer-aura](https://developer.salesforce.com/docs/platform/salesforce-code-analyzer/guide/get-started.html) from 5.13.0 to **5.15.0**
  - [code-analyzer-flow](https://developer.salesforce.com/docs/platform/salesforce-code-analyzer/guide/engine-flow.html) from 5.14.0 to **5.15.0**
  - [code-analyzer-lwc](https://developer.salesforce.com/docs/platform/salesforce-code-analyzer/guide/get-started.html) from 5.13.0 to **5.15.0**
  - [codespell](https://github.com/codespell-project/codespell) from 2.4.2 to **2.4.3**
  - [djlint](https://djlint.com/) from 1.39.4 to **1.44.1**
  - [dotnet-format](https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-format) from 10.0.301 to **10.0.302**
  - [editorconfig-checker](https://editorconfig-checker.github.io/) from 3.7.0 to **3.10.0**
  - [eslint](https://eslint.org) from 10.5.0 to **10.8.0**
  - [golangci-lint](https://golangci-lint.run/) from 2.11.4 to **2.12.2**
  - [grype](https://github.com/anchore/grype) from 0.115.0 to **0.116.1**
  - [hadolint](https://github.com/hadolint/hadolint) from 2.14.0 to **2.15.1**
  - [jscpd](https://github.com/kucherenko/jscpd/tree/master/apps/jscpd) from 5.0.11 to **5.0.14**
  - [kingfisher](https://github.com/mongodb/kingfisher) from 1.104.0 to **1.112.0**
  - [markdownlint](https://github.com/DavidAnson/markdownlint) from 0.49.0 to **0.49.1**
  - [npm-groovy-lint](https://nvuillam.github.io/npm-groovy-lint/) from 17.0.5 to **18.0.0**
  - [php-cs-fixer](https://cs.symfony.com/) from 3.95.11 to **3.95.18**
  - [phpcs](https://github.com/PHPCSStandards/PHP_CodeSniffer) from 4.0.1 to **4.0.4**
  - [phpstan](https://phpstan.org/) from 2.2.2 to **2.2.8**
  - [pmd](https://pmd.github.io/) from 7.25.0 to **7.26.0**
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.6.3 to **7.6.4**
  - [powershell_formatter](https://github.com/PowerShell/PSScriptAnalyzer) from 7.6.3 to **7.6.4**
  - [prettier](https://prettier.io/) from 3.8.4 to **3.9.6**
  - [proselint](https://github.com/amperser/proselint) from 0.14.0 to **0.16.0**
  - [pyright](https://github.com/Microsoft/pyright) from 1.1.410 to **1.1.411**
  - [robocop](https://github.com/MarketSquare/robotframework-robocop) from 8.3.2 to **8.6.0**
  - [rstcheck](https://github.com/myint/rstcheck) from 6.2.5 to **6.3.0**
  - [rubocop](https://rubocop.org/) from 1.88.0 to **1.89.0**
  - [ruff](https://github.com/astral-sh/ruff) from 0.15.20 to **0.16.2**
  - [ruff-format](https://github.com/astral-sh/ruff) from 0.15.20 to **0.16.2**
  - [rumdl](https://github.com/rvben/rumdl) from 0.2.24 to **0.2.52**
  - [secretlint](https://github.com/secretlint/secretlint) from 11.7.1 to **13.0.4**
  - [semgrep](https://semgrep.dev/) from 1.168.0 to **1.172.0**
  - [snakemake](https://snakemake.github.io/) from 9.23.1 to **9.25.1**
  - [sqlfluff](https://www.sqlfluff.com/) from 4.2.2 to **4.3.0**
  - [stylelint](https://stylelint.io) from 17.13.0 to **17.14.1**
  - [syft](https://github.com/anchore/syft) from 1.46.0 to **1.50.0**
  - [terraform-fmt](https://developer.hashicorp.com/terraform/cli/commands/fmt) from 1.15.6 to **1.15.8**
  - [terragrunt](https://terragrunt.gruntwork.io) from 1.0.8 to **1.1.2**
  - [tflint](https://github.com/terraform-linters/tflint) from 0.63.1 to **0.64.0**
  - [trivy](https://aquasecurity.github.io/trivy/) from 0.71.2 to **0.73.0**
  - [trivy-sbom](https://aquasecurity.github.io/trivy/) from 0.71.2 to **0.73.0**
  - [trufflehog](https://github.com/trufflesecurity/trufflehog) from 3.95.6 to **3.96.0**
  - [vale](https://vale.sh/) from 3.15.1 to **3.17.1**

## [v9.6.0] - 2026-06-28

- Breaking changes
  - **Linters can no longer be run via a sibling Docker image at runtime.** The `cli_docker_image`, `cli_docker_image_version` and `cli_docker_args` descriptor properties (and the matching `<LINTER>_DOCKER_IMAGE_VERSION` variable) have been removed, and MegaLinter no longer mounts `/var/run/docker.sock` (in `mega-linter-runner`, the GitHub Action `action.yml` files, and the Docker daemon previously bundled in flavor images). This closes the host-privilege escalation surface that the mounted Docker socket exposed. The only linter that used this mechanism was `SWIFT_SWIFTLINT`, now installed natively (see below). (#8216)
  - **`SWIFT_SWIFTLINT` is now installed from the static `swiftlint-static` binary** instead of running the `ghcr.io/realm/swiftlint` container. It runs natively on the Alpine image with no Docker socket required. SourceKit-dependent rules are disabled in this build and reported to the console when encountered; pure-syntax style rules are unaffected. (#8216)
  - **`@eslint/eslintrc` shim removed** from JavaScript/TypeScript/JSX/TSX Docker images (was only needed for legacy `FlatCompat`); MegaLinter's bundled test fixtures use native flat config. (#7869)
  - **ESLint linters now force migration off `.eslintrc.*`**: `JAVASCRIPT_ES`, `TYPESCRIPT_ES`, `JSX_ESLINT`, `TSX_ESLINT` activate when they find any `eslint.config.*` _or_ any deprecated `.eslintrc.*` / `package.json#eslintConfig`. In the legacy case the linter does not call ESLint at all — it emits a single hard failure with a migration message so the build stays red until the config is migrated to flat config. See the [ESLint flat-config migration guide](https://eslint.org/docs/latest/use/configure/migration-guide). To opt out, set `DISABLE_LINTERS` or `DISABLE` to exclude the affected linter/descriptor. (#7869)
  - **`JSON_ESLINT_PLUGIN_JSONC` removed**: upstream bug [ota-meshi/eslint-plugin-jsonc#328](https://github.com/ota-meshi/eslint-plugin-jsonc/issues/328) blocks ESLint v10 compatibility and will not be fixed. Use `JSON_JSONLINT`, `JSON_PRETTIER`, or `JSON_V8R` for JSON validation instead. (#7869)

- Core
  - New linter descriptor property `common_linter_errors`: declare known non-lint failure patterns (config issue, remote service down, missing credentials…) and the guidance message shown to users, directly in YAML — no custom Python class needed. (#7907)
  - Skipped-linters summary now explains why a linter was skipped by an activation rule, including the variable to set to activate it (e.g. `MARKDOWN_RUMDL: MARKDOWN_DEFAULT_STYLE=markdownlint (set MARKDOWN_DEFAULT_STYLE=rumdl to activate)`), fixing [#8017](https://github.com/oxsecurity/megalinter/issues/8017).

- New linters
  - Add [betterleaks](https://github.com/betterleaks/betterleaks) linter for repository secrets scanning — successor to gitleaks with higher recall (98.6% vs 70.4%), lower false-positive rates, and 4–5× faster scanning via BPE-based detection and CEL filter expressions (#8186)

- Disabled linters
  - `SALESFORCE_SFDX_SCANNER_APEX`, `SALESFORCE_SFDX_SCANNER_AURA` and `SALESFORCE_SFDX_SCANNER_LWC` — disabled because sfdx-scanner 4.12.0 crashes on Node.js 22+ (`TypeError: Cannot read properties of undefined (reading 'prototype')`, caused by the removal of `SlowBuffer.prototype`), which is shipped with Alpine 3.24. These linters were already deprecated; use the `SALESFORCE_CODE_ANALYZER_APEX` / `SALESFORCE_CODE_ANALYZER_AURA` / `SALESFORCE_CODE_ANALYZER_LWC` variants instead (#8080).

- Deprecated linters
  - `REPOSITORY_GITLEAKS` — deprecated in favour of `REPOSITORY_BETTERLEAKS` (same author, fully compatible config, significantly better detection). Will be removed in the next major release. Disable it by adding `REPOSITORY_GITLEAKS` to `DISABLE_LINTERS` in your `.mega-linter.yml`. (#8186)

- Removed linters
  - `JSON_ESLINT_PLUGIN_JSONC` — permanently broken by upstream bug (see Breaking changes) (#7869)

- Linters enhancements
  - `REPOSITORY_CHECKOV`: in pull-request mode, scan only the files modified in the PR instead of the whole repository (#7119)

- Fixes
  - `REPOSITORY_BETTERLEAKS`: default scan now runs in filesystem (`dir`) mode instead of auto-switching to git-history (`git`) mode when a git repository is detected. betterleaks does not read the global git `safe.directory` config, so git mode failed with `fatal: detected dubious ownership in repository` in CI environments (e.g. GitHub Actions `/github/workspace`). Git-history mode is still used for the opt-in `REPOSITORY_BETTERLEAKS_PR_COMMITS_SCAN` feature. (#8186)
  - `REPOSITORY_BETTERLEAKS`: added `--verbose` so detected findings (file, line and rule) are reported instead of only the `leaks found: N` summary, matching gitleaks behavior. Secret values stay redacted via `--redact`. (#8186)
  - `REPOSITORY_OSV_SCANNER`: exit code 128 ("No package sources found") is now treated as a clean pass instead of a failure — osv-scanner returns this code when the repo contains no lockfiles/manifests/SBOMs, which is not a vulnerability finding (#7917).
  - Fix intermittent `ansible-lint` `load-failure[not-found]` error on `github_conf/branch_protection_rules.json` caused by a race condition with `checkov` running in parallel. Checkov's transient GitHub-conf directory is now written to a hidden path (`.megalinter_github_conf`) that project-mode linters skip, eliminating the conflict (#8092).
  - Complete the Alpine 3.24 upgrade across the whole image and fix how alpine version is detected. Docker images now build on the `python:3.14-alpine3.24` base image (#8080).
  - Avoid `DeprecationWarning` / future breakage on Python 3.14 by no longer passing `count` and `flags` as positional arguments to `re.sub` (#8211).
  - Exclude `REPORT_OUTPUT_FOLDER` from linting when configured as an absolute path inside the workspace (e.g. `/tmp/lint/megalinter-reports`), fixing #7845.
  - Fix command injection in Roslynator linter (`DOTNET_ROSLYNATOR`) where a crafted `.csproj` filename could break out of `dotnet restore` arguments and execute arbitrary shell commands. The command is now invoked via argv list instead of a shell string. Reported by Francesco Sabiu. (#7857)
  - Fix `IndexError` when building the single-linter Docker image for a linter whose activation depends on a file (e.g. `SPELL_VALE` requires `.vale.ini`): `python -m megalinter.run --linterversion` now bypasses activation filtering since the per-linter image is built for that linter unconditionally.
  - Fix `make bootstrap` appearing to hang because exported Make color variables re-evaluated `tput` during recursive `make` invocations. (#8090)
  - Allow MegaLinter containers to run in an opt-in non-root mode matching the host UID:GID on POSIX systems, avoiding root-owned generated files on the host (#1975).
  - Restore missing `examples` in the Dart descriptor that were dropped from the generated documentation (#7913).

- Reporters
  - Update Bitbucket pipeline generator template to trigger builds on pull requests from any branch, by @yermulnik in <https://github.com/oxsecurity/megalinter/pull/7421>

- Doc
  - Add pnpm installation and usage documentation for JavaScript and TypeScript linters (#8177)
  - Update Docker pull counters in README badges and `flavors-stats.json` with latest ghcr.io stats
  - Bump `peter-evans/create-pull-request` to v8 in the documented workflow examples (#8089)

- mega-linter-runner
  - Add `--user-map` / `--no-user-map` to control whether the MegaLinter container runs in non-root mode. On POSIX systems `--user-map` uses the current host UID:GID; on other hosts it falls back to `1000:1000`. (#8120)
  - Add `--no-prompt` flag to `mega-linter-runner --upgrade` for non-interactive upgrades (#8093)
  - Mark `mega-linter-runner/index.js` as executable in git (#8091)

- Dev
  - Add specialized Claude Code sub-agents (`pr-monitor`, `security-analyst`, `version-bumper`) and assign cost-effective models to mechanical tasks, to speed up and reduce the token cost of contributor workflows (#7906).
  - Add the `/fix-issue` Claude Code skill for end-to-end GitHub issue fixes (gather context, implement on a branch, open a PR, watch CI) (#7848).
  - Stop generating per-linter Dockerfiles for linters marked `disabled: true` in their descriptor. The matching images were already excluded from the build matrix (`linters_matrix.json`) and never published, so the on-disk `linters/<linter>/Dockerfile` was dead code. Deleted the 8 corresponding stale Dockerfile directories.
  - Make the build's config-schema write atomic with a retry (write to a temp file then `os.replace`), so a transient file lock from an editor's JSON language server or antivirus no longer crashes the build with `OSError: [Errno 22]` on Windows.
  - Move the `.devcontainer` setup from the Dockerfile to a JSON configuration file (#7865).
  - Update the Python version in the devcontainer image (#7853).

- CI
  - Build the real `{ linter, platform, runner }` job list directly in `get-linters-matrix` for the DEV and BETA linter workflows, instead of a linter×runner cross-product filtered at runtime by `job_enabled`. Removes the `Prepare` step and the no-op jobs while preserving selection logic (#8133, #8134).
  - Track image-runtime shell scripts (`setup-runtime-user`, `megalinter_exec`) in the image-build path filters by renaming them to `.sh`, so changes to them correctly trigger image rebuilds; generated images now use root-independent command wrappers instead of shell aliases (#8213).
  - Suppress the new `ref-version-mismatch` audit introduced by zizmor 1.25.0 for the project's pinned `uses:` action references. The SHA pins are correct (the supply-chain property); only the inline `# vX` comments lag behind exact subversions, and renovate maintains the hashes.
  - Simplify the workflow trigger condition to prevent duplicate runs for pushes from forks.
  - Fix the `deploy-dev` workflow (#8154).
  - Remove unused QEMU setup from workflows (#8132).
  - Prevent `FromAsCasing` build warning in generated Dockerfiles (#8094).
  - Fix the documentation release workflow (#7837).

- Linter versions upgrades (58)
  - [bash-exec](https://www.gnu.org/software/bash/) from 5.3.3 to **5.3.9**
  - [betterleaks](https://github.com/betterleaks/betterleaks) from 1.5.0 to **1.6.0**
  - [bicep_linter](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter) from 0.43.8 to **0.44.1**
  - [black](https://black.readthedocs.io/en/stable/) from 26.3.1 to **26.5.1**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 3.14 to **1.52.0**
  - [checkov](https://www.checkov.io/) from 3.2.529 to **3.3.2**
  - [clang-format](https://releases.llvm.org/21.1.0/tools/clang/docs/ClangFormat.html) from 21.1.2 to **22.1.3**
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.95 to **0.1.96**
  - [code-analyzer-apex](https://developer.salesforce.com/docs/platform/salesforce-code-analyzer/guide/get-started.html) from 5.12.0 to **5.13.0**
  - [code-analyzer-aura](https://developer.salesforce.com/docs/platform/salesforce-code-analyzer/guide/get-started.html) from 5.12.0 to **5.13.0**
  - [code-analyzer-lwc](https://developer.salesforce.com/docs/platform/salesforce-code-analyzer/guide/get-started.html) from 5.12.0 to **5.13.0**
  - [cppcheck](https://cppcheck.sourceforge.io/) from 2.18.3 to **2.21.0**
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 10.0.0 to **10.0.1**
  - [dartanalyzer](https://dart.dev/tools/dart-analyze) from 3.11.6 to **3.12.2**
  - [djlint](https://djlint.com/) from 1.36.4 to **1.39.4**
  - [dotnet-format](https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-format) from 10.0.108 to **10.0.301**
  - [editorconfig-checker](https://editorconfig-checker.github.io/) from 3.6.1 to **3.7.0**
  - [eslint](https://eslint.org) from 10.3.0 to **10.5.0**
  - [git_diff](https://git-scm.com) from 2.52.0 to **2.54.0**
  - [grype](https://github.com/anchore/grype) from 0.112.0 to **0.115.0**
  - [jscpd](https://github.com/kucherenko/jscpd/tree/master/apps/jscpd) from 4.1.1 to **5.0.11**
  - [kingfisher](https://github.com/mongodb/kingfisher) from 1.99.0 to **1.104.0**
  - [kubeconform](https://github.com/yannh/kubeconform) from 0.7.0 to **0.8.0**
  - [kubescape](https://github.com/kubescape/kubescape) from 4.0.8 to **4.0.9**
  - [markdownlint](https://github.com/DavidAnson/markdownlint) from 0.48.0 to **0.49.0**
  - [npm-package-json-lint](https://npmpackagejsonlint.org/) from 10.4.0 to **10.4.1**
  - [php-cs-fixer](https://cs.symfony.com/) from 3.95.2 to **3.95.11**
  - [phplint](https://github.com/overtrue/phplint) from 9.7.1 to **9.7.2**
  - [phpstan](https://phpstan.org/) from 2.1.54 to **2.2.2**
  - [pmd](https://pmd.github.io/) from 7.24.0 to **7.25.0**
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.6.1 to **7.6.3**
  - [powershell_formatter](https://github.com/PowerShell/PSScriptAnalyzer) from 7.6.1 to **7.6.3**
  - [prettier](https://prettier.io/) from 3.8.3 to **3.8.4**
  - [pylint](https://pylint.readthedocs.io) from 4.0.5 to **4.0.6**
  - [pyright](https://github.com/Microsoft/pyright) from 1.1.409 to **1.1.410**
  - [robocop](https://github.com/MarketSquare/robotframework-robocop) from 8.2.8 to **8.3.2**
  - [rubocop](https://rubocop.org/) from 1.86.2 to **1.88.0**
  - [ruff](https://github.com/astral-sh/ruff) from 0.15.13 to **0.15.20**
  - [ruff-format](https://github.com/astral-sh/ruff) from 0.15.13 to **0.15.20**
  - [rumdl](https://github.com/rvben/rumdl) from 0.1.93 to **0.2.24**
  - [scalafix](https://scalacenter.github.io/scalafix/) from 0.14.6 to **0.14.7**
  - [semgrep](https://semgrep.dev/) from 1.163.0 to **1.168.0**
  - [snakefmt](https://github.com/snakemake/snakefmt) from 1.1.0 to **2.0.3**
  - [snakemake](https://snakemake.github.io/) from 9.21.0 to **9.23.1**
  - [sqlfluff](https://www.sqlfluff.com/) from 4.2.1 to **4.2.2**
  - [stylelint](https://stylelint.io) from 17.11.0 to **17.13.0**
  - [stylua](https://github.com/JohnnyMorganz/StyLua) from 2.4.1 to **2.5.2**
  - [swiftlint](https://github.com/realm/SwiftLint) from 0.63.2 to **0.65.0**
  - [syft](https://github.com/anchore/syft) from 1.44.0 to **1.46.0**
  - [tekton-lint](https://github.com/IBM/tekton-lint) from 1.1.0 to **1.2.0**
  - [terraform-fmt](https://developer.hashicorp.com/terraform/cli/commands/fmt) from 1.15.2 to **1.15.6**
  - [terragrunt](https://terragrunt.gruntwork.io) from 1.0.4 to **1.0.8**
  - [tflint](https://github.com/terraform-linters/tflint) from 0.62.1 to **0.63.1**
  - [trivy](https://aquasecurity.github.io/trivy/) from 0.70.0 to **0.71.2**
  - [trivy-sbom](https://aquasecurity.github.io/trivy/) from 0.70.0 to **0.71.2**
  - [trufflehog](https://github.com/trufflesecurity/trufflehog) from 3.95.3 to **3.95.6**
  - [v8r](https://github.com/chris48s/v8r) from 6.0.0 to **6.1.0**
  - [vale](https://vale.sh/) from 3.14.2 to **3.15.1**

## [v9.5.0] - 2026-05-16

[**Take 2 mn to read MegaLinter v9.5.0 announcements**](https://github.com/oxsecurity/megalinter/issues/7835)

- Breaking changes
  - **Docker images published only to GitHub Container Registry (`ghcr.io`)** until OIDC-based publishing to Docker Hub is implemented. The Docker Hub registry (`docker.io/oxsecurity/megalinter`) is **frozen at v9.4.0**: pulls of `oxsecurity/megalinter:v9` (or `:beta`, or any flavor tag) will keep returning v9.4.0. To get v9.5.0 and later from CI tools other than GitHub Actions (GitLab CI, Azure Pipelines, Bitbucket, Jenkins, Drone, raw `docker run`, …), switch your image references:
    - `oxsecurity/megalinter:v9` → `ghcr.io/oxsecurity/megalinter:v9`
    - `oxsecurity/megalinter:beta` → `ghcr.io/oxsecurity/megalinter:beta`
    - `oxsecurity/megalinter-<flavor>:v9` → `ghcr.io/oxsecurity/megalinter-<flavor>:v9`

    GitHub Action users (`uses: oxsecurity/megalinter@v9`) and `mega-linter-runner` users are **not affected**, as both already pull from `ghcr.io`.
  - **ESLint-based linters upgraded to v10+**. Legacy `.eslintrc.*` configs are no longer supported: you must [migrate to flat-config](https://eslint.org/docs/latest/use/configure/migration-guide) (`eslint.config.js`) to keep using `JAVASCRIPT_ES`, `TYPESCRIPT_ES`, `JSX_ESLINT`, `TSX_ESLINT`, and `JSON_ESLINT_PLUGIN_JSONC`.
  - **Airbnb and Standard ESLint configs replaced** (they never shipped ESLint 9+ support):
    - `extends: ["airbnb"]` → `extends: ["airbnb-extended"]`
    - `extends: ["standard"]` → `extends: ["neostandard"]`

- Core
  - **User notifications system**: linters can surface structured "Notices" to end users in the PR comment / report footer (used for ESLint migration, deprecated options, etc.), replaces the ad-hoc migration warnings
  - Security: more [default hidden environment variables](https://megalinter.io/beta/config-variables-security/), so a compromised linter cannot leak your secrets
  - Upgrade .NET runtime to **10.0** (csharpier, dotnet-format, roslynator, devskim, tsqllint, vbdotnet-format)
  - Upgrade GO runtime to 1.26.3

- New linters
  - [osv-scanner](https://google.github.io/osv-scanner/): trivy-like vulnerability scanner by Google
  - [zizmor](https://docs.zizmor.sh/): GitHub Actions static analysis

- Disabled linters
  - KICS (until upstream security issue is fixed)
  - Spectral (crashing)

- Re-enabled linters
  - Trivy (v0.70.0): the [supply chain security incident](https://github.com/aquasecurity/trivy-action/security/advisories/GHSA-69fq-xp46-6x23) is resolved

- Deprecated linters

- Removed linters

- Media

- Linters enhancements
  - **ESLint**: legacy `.eslintrc.*` configs are now detected and a migration notice is emitted in the report so users know they need to switch to flat-config
  - **shellcheck**: honour the `BASH_SHELLCHECK_CONFIG_FILE` variable / `.shellcheckrc` config file
  - **raku** (Rakudo): now ships on ARM64 too
  - **scala**: linter installation is now deterministic (same binary across rebuilds)
  - **v8r** (JSON/YAML schema validation): output now shows only validation errors (no more "no schema found" or success noise)
  - **lychee**: removed the deprecated `exclude_mail` option (no longer supported by lychee upstream)
  - Faster image pulls: several linters (Lua/StyLua arm64, clj-kondo, kubescape, ls-lint, dotenv-linter) now use pre-built Alpine binaries instead of compiling from source

- Fixes
  - Console output: linters now show their log sections (not only on errors), the results table and reporter logs are printed after linters complete, and parallel-run logs are no longer interleaved
  - `YAML_V8R_CONFIG_FILE` / `JSON_V8R_CONFIG_FILE` are now correctly applied (the v8r `--catalogs` option is wired through)
  - **lychee**: fix the configured `headers` / Accept settings being ignored
  - **Custom flavor builder**: works correctly for repositories whose name contains uppercase characters
  - Docs: corrected the documented default value for the pre-commands `cwd` option

- Reporters
  - Comment reporters (GitHub, GitLab, Azure DevOps, Bitbucket) now work when running MegaLinter from **Jenkins CI**
  - **GitlabCommentReporter** activates as soon as `GITLAB_ACCESS_TOKEN_MEGALINTER` is set (no longer requires `CI_JOB_TOKEN`)
  - **BitbucketCommentReporter**: per-linter sections rendered as `###` headings (Bitbucket Cloud markdown was displaying the previous `<details>` HTML tags as literal text)
  - Display a default user notification on PR/console reports inviting users to read the [MegaLinter 9.5.0 release announcement](https://github.com/oxsecurity/megalinter/issues/7835). Can be disabled by setting `SECURITY_SUGGESTIONS: false`.

- Flavors
  - **Multi-arch images**: In custom flavors, linters can now build for `linux/arm64` in addition to `linux/amd64` whenever possible (Apple Silicon, AWS Graviton, Ampere…)

- Doc
  - Add documentation for the [megalinter-ado](https://github.com/DownAtTheBottomOfTheMoleHole/megalinter-ado) Azure DevOps extension and the [megalinter-mcp-server](https://github.com/DownAtTheBottomOfTheMoleHole/megalinter-mcp) MCP server
  - Explicitly discourage the use of Personal Access Tokens (PAT) in workflows for security reasons

- mega-linter-runner
  - New `--list-vars [pattern]` flag (with `--json`) lists every MegaLinter env variable that can be passed via `-e`, with type, default, allowed values and examples (handy for AI coding agents)
  - `-e ENABLE_LINTERS=YAML_PRETTIER,YAML_YAMLLINT` no longer silently drops values after the first comma ([#7500](https://github.com/oxsecurity/megalinter/issues/7500)). The `--env=KEY=VALUE` long form is also accepted.

- Dev
  - Add `CLAUDE.md` and a set of `/add-linter`, `/update-linter-version`, `/review-descriptor`, `/fix-linter-test`, `/add-reporter`, `/add-flavor`, `/build`, `/diagnose-config`, `/fix-security-issue` skills to help work on MegaLinter with coding agents (Claude Code, GitHub Copilot, Codex, gemini-cli…)
  - Migrate copilot-instructions into Claude Code Agents & Skills
  - New descriptor capabilities for custom linter integrations: `cli_lint_extra_args_after` per lint mode (`list_of_files` / `project` / `file`), a `{file}` template variable usable in command-line args, and a customizable files separator

- CI
  - Run ARM linter jobs only when the commit message contains "ARM" (avoids 200 jobs per PR)
  - Do not push a fix commit if only markdown or JSON files were updated
  - Run osv-scanner on MegaLinter's own sources
  - Optimize the linter-job matrix for dependabot and renovate PRs
  - Exclude test dependencies from dependabot
  - Faster Docker image builds: optimized Dockerfile layer order, buildx layer cache (`type=gha`, zstd-compressed) on all deploy workflows, DEV pipeline split into parallel jobs sharing the image via cache, and cargo-based tools (sarif-fmt, zizmor, shellcheck-sarif, stylua) built in parallel multi-stage builders so the Rust toolchain no longer ships in the final image (except for clippy)
  - Hardened MegaLinter's own GitHub Actions workflows against script injection via untrusted PR contexts (zizmor findings)

- Linter versions upgrades (62)
  - [actionlint](https://rhysd.github.io/actionlint/) from 1.7.11 to **1.7.12**
  - [ansible-lint](https://ansible-lint.readthedocs.io/) from 26.2.0 to **26.4.0**
  - [bicep_linter](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter) from 0.41.2 to **0.43.8**
  - [black](https://black.readthedocs.io/en/stable/) from 26.1.0 to **26.3.1**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 1.45.0 to **3.14**
  - [checkov](https://www.checkov.io/) from 3.2.506 to **3.2.529**
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.93 to **0.1.95**
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2026.01.19 to **2025.01.16**
  - [code-analyzer-apex](https://developer.salesforce.com/docs/platform/salesforce-code-analyzer/guide/get-started.html) from 5.10.0 to **5.12.0**
  - [code-analyzer-aura](https://developer.salesforce.com/docs/platform/salesforce-code-analyzer/guide/get-started.html) from 5.10.0 to **5.12.0**
  - [code-analyzer-lwc](https://developer.salesforce.com/docs/platform/salesforce-code-analyzer/guide/get-started.html) from 5.10.0 to **5.12.0**
  - [codespell](https://github.com/codespell-project/codespell) from 2.4.1 to **2.4.2**
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 9.7.0 to **10.0.0**
  - [dartanalyzer](https://dart.dev/tools/dart-analyze) from 3.11.1 to **3.11.6**
  - [dotnet-format](https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-format) from 9.0.114 to **10.0.108**
  - [eslint](https://eslint.org) from 9.39.4 to **10.3.0**
  - [gitleaks](https://github.com/gitleaks/gitleaks) from 8.30.0 to **8.30.1**
  - [golangci-lint](https://golangci-lint.run/) from 2.10.1 to **2.11.4**
  - [grype](https://github.com/anchore/grype) from 0.109.0 to **0.112.0**
  - [htmlhint](https://htmlhint.com/) from 1.9.1 to **1.9.2**
  - [isort](https://pycqa.github.io/isort/) from 8.0.0 to **8.0.1**
  - [jscpd](https://github.com/kucherenko/jscpd/tree/master/apps/jscpd) from 4.0.8 to **4.1.1**
  - [kics](https://www.kics.io) from 2.1.19 to **2.1.20**
  - [kingfisher](https://github.com/mongodb/kingfisher) from 1.84.0 to **1.99.0**
  - [kubescape](https://github.com/kubescape/kubescape) from 4.0.2 to **4.0.8**
  - [lychee](https://lychee.cli.rs) from 0.18.0 to **0.24.2**
  - [markdownlint](https://github.com/DavidAnson/markdownlint) from 0.47.0 to **0.48.0**
  - [npm-groovy-lint](https://nvuillam.github.io/npm-groovy-lint/) from 16.2.0 to **17.0.5**
  - [npm-package-json-lint](https://npmpackagejsonlint.org/) from 9.1.0 to **10.4.0**
  - [osv-scanner](https://google.github.io/osv-scanner/) from 2.3.5 to **2.3.8**
  - [php-cs-fixer](https://cs.symfony.com/) from 3.94.2 to **3.95.2**
  - [phpstan](https://phpstan.org/) from 2.1.40 to **2.1.54**
  - [pmd](https://pmd.github.io/) from 7.22.0 to **7.24.0**
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.5.4 to **7.6.1**
  - [powershell_formatter](https://github.com/PowerShell/PSScriptAnalyzer) from 7.5.4 to **7.6.1**
  - [prettier](https://prettier.io/) from 3.8.1 to **3.8.3**
  - [psalm](https://psalm.dev) from Psalm.6.15.1@ to **Psalm.6.16.1@**
  - [pyright](https://github.com/Microsoft/pyright) from 1.1.408 to **1.1.409**
  - [raku](https://raku.org/) from 2025.11 to **2026.03**
  - [revive](https://revive.run/) from 1.14.0 to **1.15.0**
  - [robocop](https://github.com/MarketSquare/robotframework-robocop) from 8.2.2 to **8.2.8**
  - [rubocop](https://rubocop.org/) from 1.85.0 to **1.86.2**
  - [ruff](https://github.com/astral-sh/ruff) from 0.15.4 to **0.15.13**
  - [ruff-format](https://github.com/astral-sh/ruff) from 0.15.4 to **0.15.13**
  - [rumdl](https://github.com/rvben/rumdl) from 0.1.32 to **0.1.93**
  - [secretlint](https://github.com/secretlint/secretlint) from 11.3.1 to **11.7.1**
  - [semgrep](https://semgrep.dev/) from 1.153.1 to **1.163.0**
  - [shfmt](https://github.com/mvdan/sh) from 3.12.0 to **3.13.1**
  - [snakefmt](https://github.com/snakemake/snakefmt) from 0.11.4 to **1.1.0**
  - [snakemake](https://snakemake.github.io/) from 9.16.3 to **9.21.0**
  - [sqlfluff](https://www.sqlfluff.com/) from 4.0.4 to **4.2.1**
  - [stylelint](https://stylelint.io) from 16.26.1 to **17.11.0**
  - [stylua](https://github.com/JohnnyMorganz/StyLua) from 2.0.0 to **2.4.1**
  - [syft](https://github.com/anchore/syft) from 1.42.1 to **1.44.0**
  - [terraform-fmt](https://developer.hashicorp.com/terraform/cli/commands/fmt) from 1.14.5 to **1.15.2**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.99.4 to **1.0.4**
  - [tflint](https://github.com/terraform-linters/tflint) from 0.61.0 to **0.62.1**
  - [trivy](https://aquasecurity.github.io/trivy/) from 0.69.1 to **0.70.0**
  - [trivy-sbom](https://aquasecurity.github.io/trivy/) from 0.69.1 to **0.70.0**
  - [trufflehog](https://github.com/trufflesecurity/trufflehog) from 3.93.6 to **3.95.3**
  - [vale](https://vale.sh/) from 3.13.1 to **3.14.2**
  - [zizmor](https://zizmor.sh/) from 1.23.1 to **1.25.0**

## [v9.4.0] - 2026-02-28

- Core
  - Improve files browsing performances (2 PRs)
  - Optimize parallel linter processing and improve grouping logic
  - Improve performance of listing .gitignored files by sending excluded directories to git ls-files
  - If there are more than 500 .gitignored files, advise to add more excluded directories using variable ADDITIONAL_EXCLUDED_DIRECTORIES, to improve performances
  - Reduce redundant config lookups, environment copies, and dict rebuilds across config, linter, and utils modules
  - Cache subprocess environment per linter run and excluded directories per request
  - Optimize parallel linter result update from O(n²) to O(n)
  - Add support in the build of Docker images for linux/arm64 in compatible linters

- New linters
  - Add [PYTHON_NBQA_MYPY](https://nbqa.readthedocs.io/) for type-checking Jupyter notebooks using nbqa + mypy

- Disabled linters
  - LUA_SELENE: <https://github.com/Kampfkarren/selene/issues/662>

- Linters enhancements
  - Use the official checkmake image by @bdovaz
  - Spectral: Add sarif support to spectral by @bdovaz
  - Spectral: Change cli_lint_mode to list_of_files to improve performances

- Fixes
  - Add support for SSH remote origins when building custom flavors (fixes: #6511)
  - Fix issue with plugins ignored when FLAVOR_SUGGESTIONS=false
  - Fix wrong tagging `apply_fixes=True` when linter has no fix options configured
  - Python mypy: Remove `.ipynb` from file extensions (mypy doesn't support notebooks directly) - fixes #6904
  - Fix operator precedence bug in pre_post_factory pre/post command logic
  - Fix file handle leak in GitleaksLinter
  - Fix variable name bug in utils.get_git_context_info
  - Minor fixes in logger, SqlFluffLinter, PowershellLinter, TrivyLinter

- Reporters
  - Add a link inviting to star MegaLinter
  - Display in the console reporter the working directory from which the commands are executed by @bdovaz
  - Update WebHook reporter so it can send more events for a better integration with UI
  - When truncating long comments in markdown reports, keep the end of the text instead of the beginning (which usually contains less useful information)
  - In case GitHub Api returns 500, do not make the whole MegaLinter fail, display a warning instead
  - Azure Reporter: Use Azure DevOps Services REST API instead of unmaintained python wrapper lib

- Flavors
  - Custom flavor builder
    - Add support for SSH remotes
    - Allow selection of platforms to build the custom flavor on (ex: linux/amd64, linux/arm64) and build compatible linters on these platforms
    - Build & release custom flavor builder image for linux/arm64

- Doc
  - JSON Schema: Add default values for file extensions and file names variables + improve descriptions
  - Update default secured env variables documentation
  - Fix banner img in json_prettier and yaml_prettier docs
  - Explain better how to run tests locally
  - Vale: Mention community style packages in linter description

- CI
  - Free more space on GitHub Actions runners to avoid build failures
  - Ignore .isorted files in secretlint to avoid scanning transient files created by other linters
  - Avoid duplicate jobs "Mirror docker image"
  - Allow to skip linters build using `skip linters` in latest commit text
  - Allow to disable build & push of standalone linters docker images using variable `BETA_LINTERS_ENABLED=false`
  - Improve performances of formatting markdown tables during build
  - Improve test classes performances and fix race conditions
  - Fix plugin test to work with forks and feature branches
  - Update .devcontainer image to trixie

- mega-linter-runner
  - If variables are defined in a local .env file, send their values to docker/podman run command (can be useful for secret variables)
  - Never send .env file to the docker run for security reasons, instead create an empty one if needed
  - Use npm trusted publishers (OIDC) to publish mega-linter-runner

- Linter versions upgrades (59)
  - [actionlint](https://rhysd.github.io/actionlint/) from 1.7.10 to **1.7.11**
  - [ansible-lint](https://ansible-lint.readthedocs.io/) from 25.12.2 to **26.2.0**
  - [bandit](https://bandit.readthedocs.io/en/latest/) from 1.9.2 to **1.9.4**
  - [bicep_linter](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter) from 0.39.26 to **0.41.2**
  - [black](https://black.readthedocs.io/en/stable/) from 25.12.0 to **26.1.0**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 1.43.1 to **1.45.0**
  - [checkov](https://www.checkov.io/) from 3.2.497 to **3.2.506**
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.92 to **0.1.93**
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2025.12.23 to **2026.01.19**
  - [code-analyzer-apex](https://developer.salesforce.com/docs/platform/salesforce-code-analyzer/guide/get-started.html) from 5.7.1 to **5.10.0**
  - [code-analyzer-aura](https://developer.salesforce.com/docs/platform/salesforce-code-analyzer/guide/get-started.html) from 5.7.1 to **5.10.0**
  - [code-analyzer-lwc](https://developer.salesforce.com/docs/platform/salesforce-code-analyzer/guide/get-started.html) from 5.7.1 to **5.10.0**
  - [csharpier](https://csharpier.com/) from 1.2.5 to **1.2.6**
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 9.4.0 to **9.7.0**
  - [dartanalyzer](https://dart.dev/tools/dart-analyze) from 3.10.7 to **3.11.1**
  - [devskim](https://github.com/microsoft/DevSkim) from 1.0.67 to **1.0.70**
  - [dotnet-format](https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-format) from 9.0.112 to **9.0.114**
  - [editorconfig-checker](https://editorconfig-checker.github.io/) from 3.6.0 to **3.6.1**
  - [golangci-lint](https://golangci-lint.run/) from 2.7.2 to **2.10.1**
  - [grype](https://github.com/anchore/grype) from 0.104.3 to **0.109.0**
  - [htmlhint](https://htmlhint.com/) from 1.8.0 to **1.9.1**
  - [isort](https://pycqa.github.io/isort/) from 7.0.0 to **8.0.0**
  - [jscpd](https://github.com/kucherenko/jscpd/tree/master/apps/jscpd) from 4.0.5 to **4.0.8**
  - [jsonlint](https://github.com/prantlf/jsonlint) from 16.0.0 to **17.0.1**
  - [kics](https://www.kics.io) from 2.1.18 to **2.1.19**
  - [kingfisher](https://github.com/mongodb/kingfisher) from 1.73.0 to **1.84.0**
  - [kubescape](https://github.com/kubescape/kubescape) from 3.0.47 to **4.0.2**
  - [npm-groovy-lint](https://nvuillam.github.io/npm-groovy-lint/) from 16.1.1 to **16.2.0**
  - [php-cs-fixer](https://cs.symfony.com/) from 3.92.4 to **3.94.2**
  - [phpstan](https://phpstan.org/) from 2.1.33 to **2.1.40**
  - [pmd](https://pmd.github.io/) from 7.20.0 to **7.22.0**
  - [prettier](https://prettier.io/) from 3.7.4 to **3.8.1**
  - [psalm](https://psalm.dev) from Psalm.6.14.3@ to **Psalm.6.15.1@**
  - [pylint](https://pylint.readthedocs.io) from 4.0.4 to **4.0.5**
  - [pyright](https://github.com/Microsoft/pyright) from 1.1.407 to **1.1.408**
  - [revive](https://revive.run/) from 1.13.0 to **1.14.0**
  - [robocop](https://github.com/MarketSquare/robotframework-robocop) from 7.2.0 to **8.2.2**
  - [rubocop](https://rubocop.org/) from 1.82.1 to **1.85.0**
  - [ruff-format](https://github.com/astral-sh/ruff) from 0.14.10 to **0.15.4**
  - [ruff](https://github.com/astral-sh/ruff) from 0.14.10 to **0.15.4**
  - [rumdl](https://github.com/rvben/rumdl) from 0.0.208 to **0.1.32**
  - [scalafix](https://scalacenter.github.io/scalafix/) from 0.14.5 to **0.14.6**
  - [secretlint](https://github.com/secretlint/secretlint) from 11.2.5 to **11.3.1**
  - [semgrep](https://semgrep.dev/) from 1.151.0 to **1.153.1**
  - [snakefmt](https://github.com/snakemake/snakefmt) from 0.11.2 to **0.11.4**
  - [snakemake](https://snakemake.github.io/) from 9.14.5 to **9.16.3**
  - [sqlfluff](https://www.sqlfluff.com/) from 3.5.0 to **4.0.4**
  - [swiftlint](https://github.com/realm/SwiftLint) from 0.63.0 to **0.63.2**
  - [syft](https://github.com/anchore/syft) from 1.39.0 to **1.42.1**
  - [terraform-fmt](https://developer.hashicorp.com/terraform/cli/commands/fmt) from 1.14.1 to **1.14.5**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.93.13 to **0.99.4**
  - [tflint](https://github.com/terraform-linters/tflint) from 0.60.0 to **0.61.0**
  - [trivy-sbom](https://aquasecurity.github.io/trivy/) from 0.68.2 to **0.69.1**
  - [trivy](https://aquasecurity.github.io/trivy/) from 0.68.2 to **0.69.1**
  - [trufflehog](https://github.com/trufflesecurity/trufflehog) from 3.92.4 to **3.93.6**
  - [v8r](https://github.com/chris48s/v8r) from 5.1.0 to **6.0.0**
  - [vale](https://vale.sh/) from 3.13.0 to **3.13.1**
  - [yamllint](https://yamllint.readthedocs.io/) from 1.37.1 to **1.38.0**

## [v9.3.0] - 2026-01-04

- Core
  - Add enum name support in MegaLinter config Json schema for better autocompletion in editors
  - Update base image to python:3.13-alpine3.23

- New linters
  - Add [codespell](https://github.com/codespell-project/codespell)
  - Add [kingfisher](https://github.com/mongodb/kingfisher) by @bdovaz
  - Add [rumdl](https://github.com/rvben/rumdl) by @bdovaz

- Linters enhancements
  - Change checkmake Docker image reference by @bdovaz

- Reporters
  - Handle multiple MegaLinter runs on the same repo using custom value sent in variable **MEGALINTER_MULTIRUN_KEY**
  - Allow to override url to CI build in Git based reporters using **REPORTERS_ACTION_RUN_URL** variable
  - Fix sections display in Gitlab console logs

- Doc
  - Classify all JSON schema config variables by category and section

- CI
  - Free disk space on GitHub actions runner when releasing a new flavor
  - Add missing Dockerfile patterns to Renovate Dockerfile manager
  - Remove gitpod custom image, workflow, and makefile targets

- Linter versions upgrades (54)
  - [actionlint](https://rhysd.github.io/actionlint/) from 1.7.9 to **1.7.10**
  - [ansible-lint](https://ansible-lint.readthedocs.io/) from 25.11.1 to **25.12.2**
  - [bash-exec](https://www.gnu.org/software/bash/) from 5.2.37 to **5.3.3**
  - [black](https://black.readthedocs.io/en/stable/) from 25.11.0 to **25.12.0**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 1.41.0 to **1.43.1**
  - [checkov](https://www.checkov.io/) from 3.2.495 to **3.2.497**
  - [clang-format](https://releases.llvm.org/21.1.0/tools/clang/docs/ClangFormat.html) from 20.1.8 to **21.1.2**
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.91 to **0.1.92**
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2025.10.23 to **2025.12.23**
  - [code-analyzer-apex](https://developer.salesforce.com/docs/platform/salesforce-code-analyzer/guide/get-started.html) from 5.6.1 to **5.7.1**
  - [code-analyzer-aura](https://developer.salesforce.com/docs/platform/salesforce-code-analyzer/guide/get-started.html) from 5.6.1 to **5.7.1**
  - [code-analyzer-lwc](https://developer.salesforce.com/docs/platform/salesforce-code-analyzer/guide/get-started.html) from 5.6.1 to **5.7.1**
  - [cppcheck](https://cppcheck.sourceforge.io/) from 2.14.2 to **2.18.3**
  - [csharpier](https://csharpier.com/) from 1.2.1 to **1.2.5**
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 9.3.2 to **9.4.0**
  - [dartanalyzer](https://dart.dev/tools/dart-analyze) from 3.8.3 to **3.10.7**
  - [dotnet-format](https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-format) from 9.0.111 to **9.0.112**
  - [git_diff](https://git-scm.com) from 2.49.1 to **2.52.0**
  - [golangci-lint](https://golangci-lint.run/) from 2.6.2 to **2.7.2**
  - [grype](https://github.com/anchore/grype) from 0.104.1 to **0.104.3**
  - [helm](https://helm.sh/docs/helm/helm_lint/) from 3.18.4 to **3.19.0**
  - [htmlhint](https://htmlhint.com/) from 1.7.1 to **1.8.0**
  - [kics](https://www.kics.io) from 2.1.16 to **2.1.18**
  - [kingfisher](https://github.com/mongodb/kingfisher) from 1.71.0 to **1.73.0**
  - [kubescape](https://github.com/kubescape/kubescape) from 3.0.45 to **3.0.47**
  - [markdown-table-formatter](https://www.npmjs.com/package/markdown-table-formatter) from 1.6.1 to **1.7.0**
  - [markdownlint](https://github.com/DavidAnson/markdownlint) from 0.45.0 to **0.47.0**
  - [mypy](https://mypy.readthedocs.io/en/stable/) from 1.18.2 to **1.19.1**
  - [npm-groovy-lint](https://nvuillam.github.io/npm-groovy-lint/) from 15.2.2 to **16.1.1**
  - [npm-package-json-lint](https://npmpackagejsonlint.org/) from 9.0.0 to **9.1.0**
  - [php-cs-fixer](https://cs.symfony.com/) from 3.90.0 to **3.92.4**
  - [phplint](https://github.com/overtrue/phplint) from 9.6.2 to **9.7.1**
  - [phpstan](https://phpstan.org/) from 2.1.32 to **2.1.33**
  - [pmd](https://pmd.github.io/) from 7.18.0 to **7.20.0**
  - [prettier](https://prettier.io/) from 3.6.2 to **3.7.4**
  - [psalm](https://psalm.dev) from Psalm.6.13.1@ to **Psalm.6.14.3@**
  - [pylint](https://pylint.readthedocs.io) from 4.0.3 to **4.0.4**
  - [robocop](https://github.com/MarketSquare/robotframework-robocop) from 6.11.0 to **7.2.0**
  - [roslynator](https://github.com/dotnet/Roslynator) from 0.11.0.0 to **0.12.0.0**
  - [rubocop](https://rubocop.org/) from 1.81.7 to **1.82.0**
  - [rubocop](https://rubocop.org/) from 1.82.0 to **1.82.1**
  - [ruff-format](https://github.com/astral-sh/ruff) from 0.14.6 to **0.14.10**
  - [ruff](https://github.com/astral-sh/ruff) from 0.14.6 to **0.14.10**
  - [rumdl](https://github.com/rvben/rumdl) from 0.0.199 to **0.0.208**
  - [scalafix](https://scalacenter.github.io/scalafix/) from 0.14.4 to **0.14.5**
  - [snakemake](https://snakemake.github.io/) from 9.13.7 to **9.14.5**
  - [stylelint](https://stylelint.io) from 16.26.0 to **16.26.1**
  - [swiftlint](https://github.com/realm/SwiftLint) from 0.62.2 to **0.63.0**
  - [syft](https://github.com/anchore/syft) from 1.38.0 to **1.39.0**
  - [terraform-fmt](https://developer.hashicorp.com/terraform/cli/commands/fmt) from 1.14.0 to **1.14.1**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.93.10 to **0.93.13**
  - [trivy-sbom](https://aquasecurity.github.io/trivy/) from 0.67.2 to **0.68.2**
  - [trivy](https://aquasecurity.github.io/trivy/) from 0.67.2 to **0.68.2**
  - [trufflehog](https://github.com/trufflesecurity/trufflehog) from 3.91.1 to **3.92.4**

## [v9.2.0] - 2025-11-29

- New linters
  - [Salesforce Code Analyzer](https://developer.salesforce.com/docs/platform/salesforce-code-analyzer/guide/code-analyzer.html), by @abdeslamads
    - [SALESFORCE_CODE_ANALYZER_APEX](https://megalinter.io/beta/descriptors/salesforce_code_analyzer_apex/)
    - [SALESFORCE_CODE_ANALYZER_AURA](https://megalinter.io/beta/descriptors/salesforce_code_analyzer_aura/)
    - [SALESFORCE_CODE_ANALYZER_LWC](https://megalinter.io/beta/descriptors/salesforce_code_analyzer_lwc/)

- Disabled linters
  - Reactivate [checkov](https://megalinter.io/beta/descriptors/repository_checkov/)

- Deprecated linters
  - Deprecate [terrascan](https://megalinter.io/latest/descriptors/terraform_terrascan/) as the project is discontinued. Will be completely removed in a future version.
  - `SALESFORCE_SFDX_SCANNER_*` linters have been deprecated and will be removed in a future version. (they are replaced by `SALESFORCE_CODE_ANALYZER_*` linters)

- Media
  - [Looking for the best CI/CD Pipeline Linting Tool? Try MegaLinter!](https://medium.com/@SeasonedDeveloper/looking-for-the-best-ci-cd-pipeline-linting-tool-try-megalinter-d89c9eba850d), by [Seasoned Developer](https://medium.com/@SeasonedDeveloper)
  - [(Brazilian) Qualidade e Segurança em Código com MegaLinter: automatizando análises em MAUI com GitHub Actions](https://www.youtube.com/watch?v=0JGusPYE4zc), by [Canal dotNET](https://www.youtube.com/@CanaldotNET)

- Linters enhancements
  - Install dotenv-linter deterministically, by @bdovaz in <https://github.com/oxsecurity/megalinter/pull/6385>

- Fixes
  - [#6544](https://github.com/oxsecurity/megalinter/issues/6544): Add GITHUB_TOKEN in docker build command for custom flavor
  - Hide warning when compiling a regex
  - Fix formatting in descriptor files to reduce changes in generated markdown, by @echoix in <https://github.com/oxsecurity/megalinter/pull/6449>

- Reporters
  - Add conversion from Jenkins variables to related Git based reporters variables

- Doc
  - Keep jsonschema html docs updated when using `build.py --doc`, by @echoix in <https://github.com/oxsecurity/megalinter/pull/6447>
  - Commit updated license info generated from build script by @echoix in <https://github.com/oxsecurity/megalinter/pull/6448>
  - Recreate docs/descriptors folder, delete old pages by @echoix in <https://github.com/oxsecurity/megalinter/pull/6451>

- Flavors
  - Add GITHUB_TOKEN in docker buildx build command for custom flavor, by @davidfevre-gouv-nc in <https://github.com/oxsecurity/megalinter/pull/6545>

- CI
  - Optimize performances of standalone linters releases
  - Renovate: Add langchain group for package updates, by @echoix in <https://github.com/oxsecurity/megalinter/pull/6400>
  - Refactor file handling in build.py to use pathlib for improved readability, by @echoix in <https://github.com/oxsecurity/megalinter/pull/6450>

- mega-linter-runner
  - Handle upgrade of stefanzweifel/git-auto-commit-action to v7

- Linter versions upgrades (53)
  - [actionlint](https://rhysd.github.io/actionlint/) from 1.7.7 to **1.7.9**
  - [ansible-lint](https://ansible-lint.readthedocs.io/) from 25.9.1 to **25.11.1**
  - [bandit](https://bandit.readthedocs.io/en/latest/) from 1.8.6 to **1.9.2**
  - [bicep_linter](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter) from 0.38.33 to **0.39.26**
  - [black](https://black.readthedocs.io/en/stable/) from 25.9.0 to **25.11.0**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 1.40.0 to **1.41.0**
  - [checkov](https://www.checkov.io/) from 3.2.413 to **3.2.495**
  - [checkstyle](https://checkstyle.org/) from 11.1.0 to **12.1.0**
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.90 to **0.1.91**
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2025.09.22 to **2025.10.23**
  - [csharpier](https://csharpier.com/) from 1.1.2 to **1.2.1**
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 9.2.1 to **9.3.2**
  - [dotenv-linter](https://dotenv-linter.github.io/) from 3.3.0 to **4.0.0**
  - [dotnet-format](https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-format) from 9.0.110 to **9.0.111**
  - [editorconfig-checker](https://editorconfig-checker.github.io/) from 3.4.0 to **3.6.0**
  - [git_diff](https://git-scm.com) from 2.47.0 to **2.49.1**
  - [gitleaks](https://github.com/gitleaks/gitleaks) from 8.28.0 to **8.30.0**
  - [golangci-lint](https://golangci-lint.run/) from 2.5.0 to **2.6.2**
  - [grype](https://github.com/anchore/grype) from 0.100.0 to **0.104.1**
  - [isort](https://pycqa.github.io/isort/) from 6.1.0 to **7.0.0**
  - [kics](https://www.kics.io) from 2.1.14 to **2.1.16**
  - [ktlint](https://ktlint.github.io) from 1.7.1 to **1.8.0**
  - [kubescape](https://github.com/kubescape/kubescape) from 3.0.41 to **3.0.45**
  - [php-cs-fixer](https://cs.symfony.com/) from 3.88.2 to **3.90.0**
  - [phpcs](https://github.com/PHPCSStandards/PHP_CodeSniffer) from 4.0.0 to **4.0.1**
  - [phpstan](https://phpstan.org/) from 2.1.30 to **2.1.32**
  - [pmd](https://pmd.github.io/) from 7.17.0 to **7.18.0**
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.5.3 to **7.5.4**
  - [pylint](https://pylint.readthedocs.io) from 3.3.9 to **4.0.3**
  - [pyright](https://github.com/Microsoft/pyright) from 1.1.406 to **1.1.407**
  - [raku](https://raku.org/) from 2024.12 to **2025.11**
  - [revive](https://revive.run/) from 1.12.0 to **1.13.0**
  - [robocop](https://github.com/MarketSquare/robotframework-robocop) from 6.7.2 to **6.11.0**
  - [roslynator](https://github.com/dotnet/Roslynator) from 0.10.2.0 to **0.11.0.0**
  - [rst-lint](https://github.com/twolfson/restructuredtext-lint) from 1.4.0 to **2.0.2**
  - [rubocop](https://rubocop.org/) from 1.81.1 to **1.81.7**
  - [ruff-format](https://github.com/astral-sh/ruff) from 0.13.3 to **0.14.6**
  - [ruff](https://github.com/astral-sh/ruff) from 0.13.3 to **0.14.6**
  - [scalafix](https://scalacenter.github.io/scalafix/) from 0.14.3 to **0.14.4**
  - [secretlint](https://github.com/secretlint/secretlint) from 11.2.4 to **11.2.5**
  - [snakemake](https://snakemake.github.io/) from 9.11.9 to **9.13.7**
  - [sqlfluff](https://www.sqlfluff.com/) from 3.4.2 to **3.5.0**
  - [stylelint](https://stylelint.io) from 16.24.0 to **16.26.0**
  - [swiftlint](https://github.com/realm/SwiftLint) from 0.61.0 to **0.62.2**
  - [syft](https://github.com/anchore/syft) from 1.33.0 to **1.38.0**
  - [terraform-fmt](https://developer.hashicorp.com/terraform/cli/commands/fmt) from 1.13.3 to **1.14.0**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.88.1 to **0.93.10**
  - [tflint](https://github.com/terraform-linters/tflint) from 0.59.1 to **0.60.0**
  - [trivy-sbom](https://aquasecurity.github.io/trivy/) from 0.67.0 to **0.67.2**
  - [trivy](https://aquasecurity.github.io/trivy/) from 0.67.0 to **0.67.2**
  - [trufflehog](https://github.com/trufflesecurity/trufflehog) from 3.90.11 to **3.91.1**
  - [vale](https://vale.sh/) from 3.12.0 to **3.13.0**
  - [xmllint](https://gitlab.gnome.org/GNOME/libxml2/-/wikis/home) from 21308 to **21309**

## [v9.1.0] - 2025-10-07

- New linters
  - Add [Robocop](https://github.com/MarketSquare/robotframework-robocop) linter, by @bdovaz in <https://github.com/oxsecurity/megalinter/pull/6232>

- Linters enhancements
  - Python Linting: Added more file type supports for various linters. Full description [here](https://github.com/oxsecurity/megalinter/pull/6214)

- Doc
  - Add OLLAMA_BASE_URL is MegaLinter config Json schema

- Flavors
  - Custom flavors: Add workflow to automate detection of new MegaLinter versions and generation of new Custom Flavor

- CI
  - Fix v9 release issue + mark hardcoded versions to upgrade at each new major release.

- Linter versions upgrades (22)
  - [ansible-lint](https://ansible-lint.readthedocs.io/) from 25.9.0 to **25.9.1**
  - [bicep_linter](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter) from 0.37.4 to **0.38.33**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 1.39.1 to **1.40.0**
  - [checkstyle](https://checkstyle.org/) from 11.0.1 to **11.1.0**
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2025.09.19 to **2025.09.22**
  - [golangci-lint](https://golangci-lint.run/) from 2.4.0 to **2.5.0**
  - [hadolint](https://github.com/hadolint/hadolint) from 2.13.1 to **2.14.0**
  - [isort](https://pycqa.github.io/isort/) from 6.0.1 to **6.1.0**
  - [kics](https://www.kics.io) from 2.1.13 to **2.1.14**
  - [npm-groovy-lint](https://nvuillam.github.io/npm-groovy-lint/) from 15.2.1 to **15.2.2**
  - [php-cs-fixer](https://cs.symfony.com/) from 3.87.2 to **3.88.2**
  - [phpstan](https://phpstan.org/) from 2.1.28 to **2.1.30**
  - [pylint](https://pylint.readthedocs.io) from 3.3.8 to **3.3.9**
  - [pyright](https://github.com/Microsoft/pyright) from 1.1.405 to **1.1.406**
  - [robocop](https://github.com/MarketSquare/robotframework-robocop) from 6.7.0 to **6.7.2**
  - [rubocop](https://rubocop.org/) from 1.80.2 to **1.81.1**
  - [ruff-format](https://github.com/astral-sh/ruff) from 0.13.1 to **0.13.3**
  - [ruff](https://github.com/astral-sh/ruff) from 0.13.1 to **0.13.3**
  - [snakemake](https://snakemake.github.io/) from 9.11.4 to **9.11.9**
  - [terraform-fmt](https://developer.hashicorp.com/terraform/cli/commands/fmt) from 1.13.2 to **1.13.3**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.87.2 to **0.88.1**
  - [trivy](https://aquasecurity.github.io/trivy/) from 0.66.0 to **0.67.0**

## [v9.0.1] - 2025-09-21

- Fix v9 release issue

## [v9.0.0] - 2025-09-20

- Core
  - Create your own **Megalinter Custom Flavors** to dramatically improve your performances
    - See [documentation](https://megalinter.io/beta/custom-flavors/) for usage
    - Use `npx mega-linter-runner@beta --custom-flavor-setup` to initialize repo
    - Suggest new flavors in reporters with a mega-linter-runner including the list of linters
  - New **LLM Advisor**: call external LLMs to get hints to solve linter errors, available in:
    - Console Reporter
    - Text Reporter
    - Git platforms PR/MR comments Reporter
  - Use ghcr.io docker images by default because of rate limits on docker.io
  - Use uv to create the venv folder for pip-installed linters
  - Add copilot instructions for GitHub Copilot
  - Update base image to python:3.13-alpine3.21 (also embeds go 1.24)

- Disabled linters
  - [puppet-lint](https://megalinter.io/beta/descriptors/puppet_puppet_lint/): Disabled Until fix is provided for <https://github.com/puppetlabs/puppet-lint/issues/251>
  - [checkov](https://megalinter.io/beta/descriptors/repository_checkov/): Disabled until fix is provided for <https://github.com/bridgecrewio/checkov/issues/7263>

- Removed linters
  - **markdown-link-check** has been removed because [**lychee**](https://megalinter.io/latest/descriptors/spell_lychee/) can be used instead, and has much better performances

- Linters enhancements
  - PHP-CS-Fixer is able to run on PHP 8.4 without error (change default configuration) by @llaville
  - [cspell](https://megalinter.io/latest/descriptors/spell_cspell/): Filter output lines that do not contain found issues
  - [hadolint](https://megalinter.io/latest/descriptors/docker_hadolint/): Extend DOCKERFILE_HADOLINT_FILE_NAMES_REGEX to include the `purpose.Dockerfile` convention eg service.Dockerfile.
  - [sqlfluff](https://megalinter.io/beta/descriptors/sql_sqlfluff/): Handle fixing of issues

- Fixes
  - When linter is docker based, force `--platform=linux/amd64` so it works when running locally on Mac
  - Added checking of `*.pyi` and `*.ipynb` files to the `ruff` and `ruff-format` linters

- Reporters
  - New default display for Pull Request comments, with expandable sections containing the first 1000 lines of the output log. Former display remains available by defining `REPORTERS_MARKDOWN_SUMMARY_TYPE=table`
  - Markdown summary reporter:
    - Write a file for Github integration if GITHUB_STEP_SUMMARY is set
    - Truncate less linter output lines
  - Text reporter: Change the output file names to put the linter name first, then the status
  - Enhance display of markdown summary

- Doc
  - Update documentation in all megalinter descriptor files to improve accuracy and consistency
  - Fix incorrect information in linters documentation and descriptors
  - Remove dead links
  - Add linter description (linter_text) in all linter descriptor, to generate a more exhaustive documentation.
  - Update contributing guide to explain how to manage python dependencies in the codebase

- Flavors
  - Do not suggest flavors that have more linters than the current one

- CI
  - Update default MegaLinter CI/CD workflows to disable LLM_ADVISOR in case of bot pull requests

- mega-linter-runner
  - Add all CI/CD providers in the --install command
  - Use ghcr.io docker images by default
  - New parameter **--container-engine** allowing to use **podman** as runner
  - `mega-linter-runner --upgrade`: Handle upgrade of github actions to their latest version
  - `mega-linter-runner --upgrade`: Upgrades MegaLinter actions and images to v9

- Linter versions upgrades (68)
  - [ansible-lint](https://ansible-lint.readthedocs.io/) from 25.5.0 to **25.9.0**
  - [bandit](https://bandit.readthedocs.io/en/latest/) from 1.8.3 to **1.8.6**
  - [bicep_linter](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter) from 0.36.1 to **0.37.4**
  - [black](https://black.readthedocs.io/en/stable/) from 25.1.0 to **25.9.0**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 1.36.0 to **1.39.1**
  - [checkstyle](https://checkstyle.org/) from 10.25.0 to **11.0.1**
  - [clang-format](https://releases.llvm.org/17.0.1/tools/clang/docs/ClangFormat.html) from 19.1.4 to **20.1.8**
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.87 to **0.1.90**
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2025.06.05 to **2025.09.19**
  - [csharpier](https://csharpier.com/) from 1.0.2 to **1.1.2**
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 9.1.1 to **9.2.1**
  - [dartanalyzer](https://dart.dev/tools/dart-analyze) from 3.8.1 to **3.8.3**
  - [devskim](https://github.com/microsoft/DevSkim) from 1.0.59 to **1.0.67**
  - [dotnet-format](https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-format) from 9.0.106 to **9.0.110**
  - [editorconfig-checker](https://editorconfig-checker.github.io/) from 3.3.0 to **3.4.0**
  - [flake8](https://flake8.pycqa.org) from 7.2.0 to **7.3.0**
  - [git_diff](https://git-scm.com) from 2.47.2 to **2.49.1**
  - [gitleaks](https://github.com/gitleaks/gitleaks) from 8.27.2 to **8.28.0**
  - [golangci-lint](https://golangci-lint.run/) from 2.1.6 to **2.4.0**
  - [grype](https://github.com/anchore/grype) from 0.94.0 to **0.100.0**
  - [hadolint](https://github.com/hadolint/hadolint) from 2.12.0 to **2.13.1**
  - [helm](https://helm.sh/docs/helm/helm_lint/) from 3.16.3 to **3.18.4**
  - [htmlhint](https://htmlhint.com/) from 1.5.1 to **1.7.1**
  - [kics](https://www.kics.io) from 2.1.10 to **2.1.13**
  - [ktlint](https://ktlint.github.io) from 1.6.0 to **1.7.1**
  - [kubescape](https://github.com/kubescape/kubescape) from 3.0.34 to **3.0.41**
  - [lightning-flow-scanner](https://github.com/Lightning-Flow-Scanner) from 3.23.0 to **3.29.0**
  - [mypy](https://mypy.readthedocs.io/en/stable/) from 1.16.0 to **1.18.2**
  - [npm-groovy-lint](https://nvuillam.github.io/npm-groovy-lint/) from 15.2.0 to **15.2.1**
  - [npm-package-json-lint](https://npmpackagejsonlint.org/) from 8.0.0 to **9.0.0**
  - [php-cs-fixer](https://cs.symfony.com/) from 3.75.0 to **3.87.2**
  - [phpcs](https://github.com/PHPCSStandards/PHP_CodeSniffer) from 3.13.1 to **4.0.0**
  - [phpstan](https://phpstan.org/) from 2.1.17 to **2.1.28**
  - [pmd](https://pmd.github.io/) from 7.14.0 to **7.17.0**
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.5.1 to **7.5.3**
  - [powershell_formatter](https://github.com/PowerShell/PSScriptAnalyzer) from 7.5.1 to **7.5.3**
  - [prettier](https://prettier.io/) from 3.5.3 to **3.6.2**
  - [protolint](https://github.com/yoheimuta/protolint) from 0.55.6 to **0.56.4**
  - [psalm](https://psalm.dev) from Psalm.6.12.0@ to **Psalm.6.13.1@**
  - [pylint](https://pylint.readthedocs.io) from 3.3.7 to **3.3.8**
  - [pyright](https://github.com/Microsoft/pyright) from 1.1.402 to **1.1.405**
  - [revive](https://revive.run/) from 1.10.0 to **1.12.0**
  - [roslynator](https://github.com/dotnet/Roslynator) from 0.10.1.0 to **0.10.2.0**
  - [rubocop](https://rubocop.org/) from 1.76.1 to **1.80.2**
  - [ruff-format](https://github.com/astral-sh/ruff) from 0.11.13 to **0.13.1**
  - [ruff](https://github.com/astral-sh/ruff) from 0.11.13 to **0.13.1**
  - [secretlint](https://github.com/secretlint/secretlint) from 10.1.0 to **11.2.4**
  - [selene](https://kampfkarren.github.io/selene/) from 0.28.0 to **0.29.0**
  - [shellcheck](https://github.com/koalaman/shellcheck) from 0.10.0 to **0.11.0**
  - [shfmt](https://github.com/mvdan/sh) from 3.11.0 to **3.12.0**
  - [snakefmt](https://github.com/snakemake/snakefmt) from 0.11.0 to **0.11.2**
  - [snakemake](https://snakemake.github.io/) from 9.5.1 to **9.11.4**
  - [sqlfluff](https://www.sqlfluff.com/) from 3.4.1 to **3.4.2**
  - [stylelint](https://stylelint.io) from 16.20.0 to **16.24.0**
  - [swiftlint](https://github.com/realm/SwiftLint) from 0.59.1 to **0.61.0**
  - [syft](https://github.com/anchore/syft) from 1.27.1 to **1.33.0**
  - [terraform-fmt](https://developer.hashicorp.com/terraform/cli/commands/fmt) from 1.12.2 to **1.13.2**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.81.6 to **0.87.2**
  - [tflint](https://github.com/terraform-linters/tflint) from 0.58.0 to **0.59.1**
  - [trivy-sbom](https://aquasecurity.github.io/trivy/) from 0.63.0 to **0.66.0**
  - [trivy](https://aquasecurity.github.io/trivy/) from 0.63.0 to **0.66.0**
  - [trufflehog](https://github.com/trufflesecurity/trufflehog) from 3.89.1 to **3.90.8**
  - [v8r](https://github.com/chris48s/v8r) from 5.0.0 to **5.1.0**
  - [vale](https://vale.sh/) from 3.11.2 to **3.12.0**
  - [xmllint](https://gitlab.gnome.org/GNOME/libxml2/-/wikis/home) from 21304 to **21308**

## [v8.8.0] - 2024-06-15

- Core
  - Retrieve SARIF errors and warnings correctly, by @bdovaz in <https://github.com/oxsecurity/megalinter/pull/4837>

- Linters enhancements
  - More config file name checks for ansible-lint activation, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/5590>

- Fixes
  - Fix crash when the markdown table summary is empty, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/5363>
  - Downgrade click to make rstcheck work again, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/5387>

- Doc
  - Display hash as plain text in markdown, by @johndutchover in <https://github.com/oxsecurity/megalinter/pull/5420>

- Flavors
  - Add Gherkin descriptor in java flavor, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/5592>

- CI
  - Fix rust setup & disable codecov-cli, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/5579>

- Linter versions upgrades (50)
  - [ansible-lint](https://ansible-lint.readthedocs.io/) from 25.4.0 to **25.5.0**
  - [bicep_linter](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter) from 0.35.1 to **0.36.1**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 1.34.2 to **1.36.0**
  - [checkstyle](https://checkstyle.org/) from 10.23.1 to **10.25.0**
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.86 to **0.1.87**
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2025.04.07 to **2025.06.05**
  - [csharpier](https://csharpier.com/) from 1.0.1 to **1.0.2**
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 8.19.4 to **9.1.1**
  - [dartanalyzer](https://dart.dev/tools/dart-analyze) from 3.7.3 to **3.8.1**
  - [devskim](https://github.com/microsoft/DevSkim) from 1.0.56 to **1.0.59**
  - [dotnet-format](https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-format) from 9.0.105 to **9.0.106**
  - [editorconfig-checker](https://editorconfig-checker.github.io/) from 3.2.1 to **3.3.0**
  - [gitleaks](https://github.com/gitleaks/gitleaks) from 8.25.1 to **8.27.2**
  - [golangci-lint](https://golangci-lint.run/) from 2.1.5 to **2.1.6**
  - [grype](https://github.com/anchore/grype) from 0.91.2 to **0.94.0**
  - [htmlhint](https://htmlhint.com/) from 1.1.4 to **1.5.1**
  - [kics](https://www.kics.io) from 2.1.7 to **2.1.10**
  - [ktlint](https://ktlint.github.io) from 1.5.0 to **1.6.0**
  - [kubeconform](https://github.com/yannh/kubeconform) from 0.6.7 to **0.7.0**
  - [lightning-flow-scanner](https://github.com/Lightning-Flow-Scanner) from 3.8.0 to **3.23.0**
  - [ls-lint](https://ls-lint.org/) from 2.3.0 to **2.3.1**
  - [markdownlint](https://github.com/DavidAnson/markdownlint) from 0.44.0 to **0.45.0**
  - [mypy](https://mypy.readthedocs.io/en/stable/) from 1.15.0 to **1.16.0**
  - [npm-groovy-lint](https://nvuillam.github.io/npm-groovy-lint/) from 15.1.0 to **15.2.0**
  - [phpcs](https://github.com/PHPCSStandards/PHP_CodeSniffer) from 3.12.2 to **3.13.1**
  - [phpstan](https://phpstan.org/) from 2.1.14 to **2.1.17**
  - [pmd](https://pmd.github.io/) from 7.13.0 to **7.14.0**
  - [protolint](https://github.com/yoheimuta/protolint) from 0.54.1 to **0.55.6**
  - [psalm](https://psalm.dev) from Psalm.6.10.2@ to **Psalm.6.12.0@**
  - [pylint](https://pylint.readthedocs.io) from 3.3.6 to **3.3.7**
  - [pyright](https://github.com/Microsoft/pyright) from 1.1.400 to **1.1.402**
  - [revive](https://revive.run/) from 1.9.0 to **1.10.0**
  - [rstcheck](https://github.com/myint/rstcheck) from 6.2.4 to **6.2.5**
  - [rubocop](https://rubocop.org/) from 1.75.4 to **1.76.1**
  - [ruff](https://github.com/astral-sh/ruff) from 0.11.8 to **0.11.13**
  - [ruff-format](https://github.com/astral-sh/ruff) from 0.11.8 to **0.11.13**
  - [scalafix](https://scalacenter.github.io/scalafix/) from 0.14.2 to **0.14.3**
  - [secretlint](https://github.com/secretlint/secretlint) from 9.3.2 to **10.1.0**
  - [semgrep](https://semgrep.dev/) from 3.12 to **3.13**
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 4.11.0 to **4.12.0**
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 4.11.0 to **4.12.0**
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 4.11.0 to **4.12.0**
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 8.27.1 to **9.5.1**
  - [sqlfluff](https://www.sqlfluff.com/) from 3.4.0 to **3.4.1**
  - [stylelint](https://stylelint.io) from 16.19.1 to **16.20.0**
  - [syft](https://github.com/anchore/syft) from 1.23.1 to **1.27.1**
  - [terraform-fmt](https://developer.hashicorp.com/terraform/cli/commands/fmt) from 1.11.4 to **1.12.2**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.78.0 to **0.81.6**
  - [tflint](https://github.com/terraform-linters/tflint) from 0.57.0 to **0.58.0**
  - [trivy](https://aquasecurity.github.io/trivy/) from 0.62.0 to **0.63.0**
  - [trivy-sbom](https://aquasecurity.github.io/trivy/) from 0.62.0 to **0.63.0**
  - [trufflehog](https://github.com/trufflesecurity/trufflehog) from 3.88.27 to **3.89.1**
  - [v8r](https://github.com/chris48s/v8r) from 4.4.0 to **5.0.0**

## [v8.7.0] - 2025-05-04

- Core
  - Replace pychalk (not maintained for 7 years) by termcolor, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/5316>
  - Update make scripts so they also work on Windows, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/5316>
  - Align number columns of markdown tables in reports, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/4835>

- Linters enhancements
  - Add new CSharpier supported file extensions, by @bdovaz in <https://github.com/oxsecurity/megalinter/pull/5292>

- Fixes
  - Exclude from sanitization the regular expressions that have awful performances, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/5308>
  - New variable SKIP_LINTER_OUTPUT_SANITIZATION to skip sanitization to improve performances if you are on a private repository with secured access, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/5308>

- Linter versions upgrades (27)
  - [ansible-lint](https://ansible-lint.readthedocs.io/) from 25.2.1 to **25.4.0**  
  - [bicep_linter](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter) from 0.34.44 to **0.35.1**  
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 1.34.1 to **1.34.2**  
  - [checkov](https://www.checkov.io/) from 3.2.404 to **3.2.413**  
  - [checkstyle](https://checkstyle.org/) from 10.23.0 to **10.23.1**  
  - [csharpier](https://csharpier.com/) from 0.30.6 to **1.0.1**  
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 8.19.2 to **8.19.4**  
  - [gitleaks](https://github.com/gitleaks/gitleaks) from 8.24.3 to **8.25.1**  
  - [golangci-lint](https://golangci-lint.run/) from 1.64.8 to **2.1.5**  
  - [lightning-flow-scanner](https://github.com/Lightning-Flow-Scanner) from 3.4.0 to **3.8.0**  
  - [phpstan](https://phpstan.org/) from 2.1.12 to **2.1.14**  
  - [pmd](https://pmd.github.io/) from 7.12.0 to **7.13.0**  
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.5.0 to **7.5.1**  
  - [protolint](https://github.com/yoheimuta/protolint) from 0.53.0 to **0.54.1**  
  - [psalm](https://psalm.dev) from 6.10.1 to **6.10.2**  
  - [rubocop](https://rubocop.org/) from 1.75.3 to **1.75.4**  
  - [ruff](https://github.com/astral-sh/ruff) from 0.11.6 to **0.11.8**  
  - [ruff-format](https://github.com/astral-sh/ruff) from 0.11.6 to **0.11.8**  
  - [secretlint](https://github.com/secretlint/secretlint) from 9.3.1 to **9.3.2**  
  - [stylelint](https://stylelint.io) from 16.19.0 to **16.19.1**  
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.77.22 to **0.78.0**  
  - [tflint](https://github.com/terraform-linters/tflint) from 0.56.0 to **0.57.0**  
  - [trivy](https://aquasecurity.github.io/trivy/) from 0.61.1 to **0.62.0**  
  - [trivy-sbom](https://aquasecurity.github.io/trivy/) from 0.61.1 to **0.62.0**  
  - [v8r](https://github.com/chris48s/v8r) from 4.3.0 to **4.4.0**  
  - [yamllint](https://yamllint.readthedocs.io/) from 1.37.0 to **1.37.1**

## [v8.6.0] - 2025-04-27

- Core
  - New config property **ENABLE_ERRORS_LINTERS**. If set, only the listed linters will be considered as blocking

- New linters
  - Add [cppcheck](https://github.com/danmar/cppcheck) linter, by @bdovaz in <https://github.com/oxsecurity/megalinter/pull/5224>

- Media
  - [Integrating MegaLinter to Automate Linting Across Multiple Codebases. A Technical Description](https://medium.com/datamindedbe/integrating-megalinter-to-automate-linting-across-multiple-codebases-a-technical-description-a200bb235b71), by [Thorsten Foltz](https://www.linkedin.com/in/thorstenfoltz/)

- Linters enhancements
  - [editorconfig_checker](https://megalinter.io/latest/descriptors/editorconfig_editorconfig_checker/) Changes default EditorConfig-Checker config filename by @llaville in <https://github.com/oxsecurity/megalinter/issues/5061>
  - [TruffleHog](https://megalinter.io/latest/descriptors/repository_trufflehog/): Ignore .git by default if not already done using --exclude-paths option

- Fixes
  - Sanitize all linter outputs by default, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/5266>

- Doc
  - Add [j2lint](https://github.com/wesley-dean/mega-linter-plugin-j2lint/) to plugins, by @wesley-dean in <https://github.com/oxsecurity/megalinter/pull/5151>
  - Add [fmlint](https://github.com/wesley-dean/mega-linter-plugin-fmlint) (frontmatter linter) to plugins list by @wesley-dean in <https://github.com/oxsecurity/megalinter/pull/5257>
  - Remove trailing spaces by @parkerbxyz in <https://github.com/oxsecurity/megalinter/pull/5185>

- CI
  - Initial Renovate automerge configuration, by @echoix in <https://github.com/oxsecurity/megalinter/pull/5057>
  - Set update schedule for checkov updates, by @echoix in <https://github.com/oxsecurity/megalinter/pull/5064>
  - Always upgrade packages from base image for updated security fixes, by @echoix in <https://github.com/oxsecurity/megalinter/pull/5152>
  - build-command: Unshallow pull or full pull before committing changes, by @echoix in <https://github.com/oxsecurity/megalinter/pull/5201>

- Linter versions upgrades (50)
  - [ansible-lint](https://ansible-lint.readthedocs.io/) from 25.1.3 to **25.2.1**
  - [bicep_linter](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter) from 0.34.1 to **0.34.44**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 1.32.0 to **1.34.1**
  - [checkov](https://www.checkov.io/) from 3.2.390 to **3.2.404**
  - [checkstyle](https://checkstyle.org/) from 10.21.4 to **10.23.0**
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.85 to **0.1.86**
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2025.02.20 to **2025.04.07**
  - [cpplint](https://github.com/cpplint/cpplint) from 2.0.0 to **2.0.2**
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 8.17.5 to **8.19.2**
  - [dartanalyzer](https://dart.dev/tools/dart-analyze) from 3.7.2 to **3.7.3**
  - [devskim](https://github.com/microsoft/DevSkim) from 1.0.52 to **1.0.56**
  - [dotnet-format](https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-format) from 9.0.104 to **9.0.105**
  - [flake8](https://flake8.pycqa.org) from 7.1.2 to **7.2.0**
  - [gitleaks](https://github.com/gitleaks/gitleaks) from 8.24.2 to **8.24.3**
  - [grype](https://github.com/anchore/grype) from 0.90.0 to **0.91.2**
  - [kics](https://www.kics.io) from 2.1.6 to **2.1.7**
  - [kubescape](https://github.com/kubescape/kubescape) from 3.0.32 to **3.0.34**
  - [lightning-flow-scanner](https://github.com/Lightning-Flow-Scanner) from 3.2.0 to **3.4.0**
  - [ls-lint](https://ls-lint.org/) from 2.2.3 to **2.3.0**
  - [phplint](https://github.com/overtrue/phplint) from 9.5.6 to **9.6.2**
  - [php-cs-fixer](https://cs.symfony.com/) from 3.73.1 to **3.75.0**
  - [phpcs](https://github.com/PHPCSStandards/PHP_CodeSniffer) from 3.12.0 to **3.12.2**
  - [phpstan](https://phpstan.org/) from 2.1.8 to **2.1.12**
  - [pmd](https://pmd.github.io/) from 7.11.0 to **7.12.0**
  - [psalm](https://psalm.dev) from Psalm.6.9.4@ to **Psalm.6.10.1@**
  - [pyright](https://github.com/Microsoft/pyright) from 1.1.397 to **1.1.400**
  - [revive](https://revive.run/) from 1.7.0 to **1.9.0**
  - [rubocop](https://rubocop.org/) from 1.74.0 to **1.75.3**
  - [ruff](https://github.com/astral-sh/ruff) from 0.11.2 to **0.11.6**
  - [ruff-format](https://github.com/astral-sh/ruff) from 0.11.2 to **0.11.6**
  - [secretlint](https://github.com/secretlint/secretlint) from 9.2.0 to **9.3.1**
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 4.10.0 to **4.11.0**
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 4.10.0 to **4.11.0**
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 4.10.0 to **4.11.0**
  - [spectral](https://docs.stoplight.io/docs/spectral/674b27b261c3c-overview) from 6.14.3 to **6.15.0**
  - [sqlfluff](https://www.sqlfluff.com/) from 3.3.1 to **3.4.0**
  - [stylelint](https://stylelint.io) from 16.16.0 to **16.19.0**
  - [swiftlint](https://github.com/realm/SwiftLint) from 0.58.2 to **0.59.1**
  - [syft](https://github.com/anchore/syft) from 1.21.0 to **1.23.1**
  - [terraform-fmt](https://developer.hashicorp.com/terraform/cli/commands/fmt) from 1.11.2 to **1.11.4**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.76.6 to **0.77.22**
  - [tflint](https://github.com/terraform-linters/tflint) from 0.55.1 to **0.56.0**
  - [trivy](https://aquasecurity.github.io/trivy/) from 0.60.0 to **0.61.1**
  - [trivy-sbom](https://aquasecurity.github.io/trivy/) from 0.60.0 to **0.61.1**
  - [trufflehog](https://github.com/trufflesecurity/trufflehog) from 3.88.18 to **3.88.25**
  - [v8r](https://github.com/chris48s/v8r) from 4.2.1 to **4.3.0**
  - [vale](https://vale.sh/) from 3.9.4 to **3.11.2**
  - [yamllint](https://yamllint.readthedocs.io/) from 1.36.2 to **1.37.0**

## [v8.5.0] - 2025-03-23

- Core
  - Addition of warnings to reporters and logic changes to surface warnings even when there are no errors. Addition of `cli_lint_warning_count` / `cli_lint_warning_regex` variables to the JSON schema. [#4476](https://github.com/oxsecurity/megalinter/issues/4476), by @bdovaz in <https://github.com/oxsecurity/megalinter/pull/4556>

- Linters enhancements
  - [kubescape](https://megalinter.io/latest/descriptors/kubernetes_kubescape/) Remove downgraded_version from kubescape, by @bdovaz in <https://github.com/oxsecurity/megalinter/pull/4712>
  - [npm-groovy-lint](https://megalinter.io/latest/descriptors/groovy_npm_groovy_lint/): Undowngrade npm-groovy-lint as there is a new release with issue fixed by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/4834>
  - [syft](https://megalinter.io/latest/descriptors/repository_syft/): Add SBOM file by default in report folder + remove useless debug statement
  - [trivy-sbom](https://megalinter.io/latest/descriptors/repository_trivy_sbom/): Add SBOM file by default in report folder + remove useless debug statement

- Fixes
  - Use npm to install pyright
  - Undowngrade npm-groovy-lint as there is a new release with issue fix
  - [jscpd](https://megalinter.io/latest/descriptors/copypaste_jscpd/): remove forced `--exitCode 1` to fix <https://github.com/oxsecurity/megalinter/issues/4631>
  - Use --with-all-dependencies to install phpcs-fixer, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/4672>
  - Remove Composer config PHP 8.3 compatibility platform for PSALM 6.0, by @llaville in <https://github.com/oxsecurity/megalinter/pull/4930>
  - Fix lychee upgrade issue (lycheeignore upgrade), by @wesley-dean in <https://github.com/oxsecurity/megalinter/pull/4964>

- Doc
  - Remove reference to R2DevOps jobs as it has been discontinued (see [#4678](https://github.com/oxsecurity/megalinter/issues/4678))
  - Improve contributing doc by adding reference to `source .venv/Scripts/activate` on Windows
  - Better apk package url, by @bdovaz in <https://github.com/oxsecurity/megalinter/pull/4707>
  - Better package version docs, by @bdovaz in <https://github.com/oxsecurity/megalinter/pull/4721>
  - Correct default SARIF_REPORTER_FILE_NAME, by @yxtay in <https://github.com/oxsecurity/megalinter/pull/4783>
  - Use github private email for megalinter-bot, by @yxtay in <https://github.com/oxsecurity/megalinter/pull/4786>
  - Update plugins.md to add raw link to JSON schema, by @wesley-dean in <https://github.com/oxsecurity/megalinter/pull/4932>

- Flavors
  - Add [syft](https://megalinter.io/latest/descriptors/repository_syft/) in all flavors

- CI
  - Update **.devcontainer** configuration, by @bdovaz in <https://github.com/oxsecurity/megalinter/pull/4843>
  - Configure Renovate for gem, cargo, pip and npm dependencies, by @bdovaz in <https://github.com/oxsecurity/megalinter/pull/4673>
  - Configure Renovate for composer dependencies,  by @bdovaz in <https://github.com/oxsecurity/megalinter/pull/4916>
  - Use packagist data source, by @bdovaz in <https://github.com/oxsecurity/megalinter/pull/4922>
  - Bring back codecov, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/4836>

- Plugins
  - Add docker-compose-linter (dclint) to plugins list, by @wesley-dean in <https://github.com/oxsecurity/megalinter/pull/4962>
  - Add repolinter to the list of plugins, by @wesley-dean in <https://github.com/oxsecurity/megalinter/pull/4972>

- Linter versions upgrades (55)
  - [ansible-lint](https://ansible-lint.readthedocs.io/) from 25.1.1 to **25.1.3**
  - [bandit](https://bandit.readthedocs.io/en/latest/) from 1.8.2 to **1.8.3**
  - [bicep_linter](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter) from 0.33.13 to **0.34.1**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 1.22.7 to **1.32.0**
  - [checkov](https://www.checkov.io/) from 3.2.360 to **3.2.390**
  - [checkstyle](https://checkstyle.org/) from 10.21.2 to **10.21.4**
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.84 to **0.1.85**
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2025.01.16 to **2025.02.20**
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 8.17.3 to **8.17.5**
  - [dartanalyzer](https://dart.dev/tools/dart-analyze) from 3.6.2 to **3.7.2**
  - [detekt](https://detekt.dev/) from 1.23.7 to **1.23.8**
  - [dotnet-format](https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-format) from 9.0.102 to **9.0.104**
  - [editorconfig-checker](https://editorconfig-checker.github.io/) from 3.2.0 to **3.2.1**
  - [flake8](https://flake8.pycqa.org) from 7.1.1 to **7.1.2**
  - [gitleaks](https://github.com/gitleaks/gitleaks) from 8.23.3 to **8.24.2**
  - [golangci-lint](https://golangci-lint.run/) from 1.63.4 to **1.64.8**
  - [grype](https://github.com/anchore/grype) from 0.87.0 to **0.90.0**
  - [isort](https://pycqa.github.io/isort/) from 6.0.0 to **6.0.1**
  - [kics](https://www.kics.io) from 2.1.3 to **2.1.6**
  - [kubescape](https://github.com/kubescape/kubescape) from 2.9.0 to **3.0.32**
  - [lightning-flow-scanner](https://github.com/Lightning-Flow-Scanner) from 2.43.0 to **3.2.0**
  - [mypy](https://mypy.readthedocs.io/en/stable/) from 1.14.1 to **1.15.0**
  - [npm-groovy-lint](https://nvuillam.github.io/npm-groovy-lint/) from 15.0.0 to **15.1.0**
  - [php-cs-fixer](https://cs.symfony.com/) from 3.68.5 to **3.73.1**
  - [phpcs](https://github.com/PHPCSStandards/PHP_CodeSniffer) from 3.11.3 to **3.12.0**
  - [phpstan](https://phpstan.org/) from 2.1.2 to **2.1.8**
  - [pmd](https://pmd.github.io/) from 7.9.0 to **7.11.0**
  - [prettier](https://prettier.io/) from 3.4.2 to **3.5.3**
  - [protolint](https://github.com/yoheimuta/protolint) from 0.52.0 to **0.53.0**
  - [psalm](https://psalm.dev) from Psalm.6.1.0@ to **Psalm.6.9.4@**
  - [puppet-lint](http://puppet-lint.com/) from 4.2.4 to **4.3.0**
  - [pylint](https://pylint.readthedocs.io) from 3.3.4 to **3.3.6**
  - [pyright](https://github.com/Microsoft/pyright) from 1.1.393 to **1.1.397**
  - [revive](https://revive.run/) from 1.6.0 to **1.7.0**
  - [roslynator](https://github.com/dotnet/Roslynator) from 0.10.0.0 to **0.10.1.0**
  - [rubocop](https://rubocop.org/) from 1.71.0 to **1.74.0**
  - [ruff-format](https://github.com/astral-sh/ruff) from 0.9.4 to **0.11.2**
  - [ruff](https://github.com/astral-sh/ruff) from 0.9.4 to **0.11.2**
  - [scalafix](https://scalacenter.github.io/scalafix/) from 0.14.0 to **0.14.2**
  - [secretlint](https://github.com/secretlint/secretlint) from 9.0.0 to **9.2.0**
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 4.9.0 to **4.10.0**
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 4.9.0 to **4.10.0**
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 4.9.0 to **4.10.0**
  - [shfmt](https://github.com/mvdan/sh) from 3.10.0 to **3.11.0**
  - [snakefmt](https://github.com/snakemake/snakefmt) from 0.10.2 to **0.11.0**
  - [spectral](https://docs.stoplight.io/docs/spectral/674b27b261c3c-overview) from 6.14.2 to **6.14.3**
  - [sqlfluff](https://www.sqlfluff.com/) from 3.3.0 to **3.3.1**
  - [stylelint](https://stylelint.io) from 16.14.1 to **16.16.0**
  - [syft](https://github.com/anchore/syft) from 1.19.0 to **1.21.0**
  - [terraform-fmt](https://developer.hashicorp.com/terraform/cli/commands/fmt) from 1.10.3 to **1.11.2**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.71.1 to **0.76.6**
  - [trivy-sbom](https://aquasecurity.github.io/trivy/) from 0.59.0 to **0.60.0**
  - [trivy](https://aquasecurity.github.io/trivy/) from 0.59.0 to **0.60.0**
  - [trufflehog](https://github.com/trufflesecurity/trufflehog) from 3.88.4 to **3.88.14**
  - [yamllint](https://yamllint.readthedocs.io/) from 1.35.1 to **1.36.2**

## [v8.4.2] - 2025-02-02

- Media
  - New video [(Brazilian) MegaLinter: Como Automatizar a Qualidade do Código para Todas Plataformas](https://www.youtube.com/watch?v=YSdZ3atC2j4) , by Codando TV

- Fixes
  - Fix .NET linters issue: Add --allow-roll-forward to dotnet tool install commands, by @bdovaz in <https://github.com/oxsecurity/megalinter/pull/4619>
  - [GH-4610](https://github.com/oxsecurity/megalinter/issues/4610) : PHP CS Fixer linter version available is not correct since running on PHP 8.4 runtime, by @llaville in <https://github.com/oxsecurity/megalinter/pull/4611>
  - Allow cspell to work with CLI_LINT_MODE=project
  - Downgrade npm-groovy-lint until it's fixed, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/4628>

- Linter versions upgrades (31)
  - [ansible-lint](https://ansible-lint.readthedocs.io/) from 25.1.0 to **25.1.1**
  - [black](https://black.readthedocs.io/en/stable/) from 24.10.0 to **25.1.0**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 1.22.7 to **1.23.1**
  - [checkov](https://www.checkov.io/) from 3.2.357 to **3.2.360**
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 8.17.2 to **8.17.3**
  - [dartanalyzer](https://dart.dev/tools/dart-analyze) from 3.6.1 to **3.6.2**
  - [devskim](https://github.com/microsoft/DevSkim) from 1.0.51 to **1.0.52**
  - [editorconfig-checker](https://editorconfig-checker.github.io/) from 3.1.2 to **3.2.0**
  - [gitleaks](https://github.com/gitleaks/gitleaks) from 8.23.2 to **8.23.3**
  - [isort](https://pycqa.github.io/isort/) from 5.13.2 to **6.0.0**
  - [lightning-flow-scanner](https://github.com/Lightning-Flow-Scanner) from 2.39.0 to **2.43.0**
  - [npm-groovy-lint](https://nvuillam.github.io/npm-groovy-lint/) from 15.0.2 to **15.0.0**
  - [php-cs-fixer](https://cs.symfony.com/) from 3.68.0 to **3.68.5**
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.4.6 to **7.5.0**
  - [powershell_formatter](https://github.com/PowerShell/PSScriptAnalyzer) from 7.4.6 to **7.5.0**
  - [psalm](https://psalm.dev) from Psalm.6.0.0@ to **Psalm.6.1.0@**
  - [pylint](https://pylint.readthedocs.io) from 3.3.3 to **3.3.4**
  - [pyright](https://github.com/Microsoft/pyright) from 1.1.392 to **1.1.393**
  - [raku](https://raku.org/) from 2024.10 to **2024.12**
  - [roslynator](https://github.com/dotnet/Roslynator) from 0.9.3.0 to **0.10.0.0**
  - [rubocop](https://rubocop.org/) from 1.71.0 to **1.71.1**
  - [ruff-format](https://github.com/astral-sh/ruff) from 0.9.3 to **0.9.4**
  - [ruff](https://github.com/astral-sh/ruff) from 0.9.3 to **0.9.4**
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 4.8.0 to **4.9.0**
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 4.8.0 to **4.9.0**
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 4.8.0 to **4.9.0**
  - [tflint](https://github.com/terraform-linters/tflint) from 0.55.0 to **0.55.1**
  - [trivy-sbom](https://aquasecurity.github.io/trivy/) from 0.58.2 to **0.59.0**
  - [trivy](https://aquasecurity.github.io/trivy/) from 0.58.2 to **0.59.0**
  - [trufflehog](https://github.com/trufflesecurity/trufflehog) from 3.88.2 to **3.88.4**

## [v8.4.1] - 2025-01-28

- Quick fix about PRE_COMMANDS crash (see <https://github.com/oxsecurity/megalinter/issues/4591>)

- Linter versions upgrades (2)
  - [checkstyle](https://checkstyle.org/) from 10.21.1 to **10.21.2**
  - [stylelint](https://stylelint.io) from 16.14.0 to **16.14.1**

## [v8.4.0] - 2025-01-26

- Core
  - PHP Linters use now the `bartlett/sarif-php-converters` first official release 1.0.0 to generate SARIF reports, by @llaville in <https://github.com/oxsecurity/megalinter/pull/4357>
  - [Upgrade PHP engine from 8.3 to 8.4](https://github.com/oxsecurity/megalinter/issues/4351) and allow Psalm 5.26 to run on this context (by @llaville)
  - Linters can specify in the pre/post commands with a `run_before_linters` / `run_after_linters` parameter whether the command is to be executed before/after the execution of the linters themselves (by @bdovaz in [#4482](https://github.com/oxsecurity/megalinter/pull/4482))
  - Bump python version to 3.12.8, by @echoix in <https://github.com/oxsecurity/megalinter/pull/4372>
  - Update to .NET 9, by @bdovaz in <https://github.com/oxsecurity/megalinter/pull/4488>
  - Upgrade PHP engine from 8.3 to 8.4, by @llaville in <https://github.com/oxsecurity/megalinter/pull/4524>

- New linters
  - Reactivate clj-style (Clojure formatter) since its bug is fixed, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/4369>
  - New python formatter: PYTHON_RUFF_FORMAT, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/4329>

- Disabled linters
  - Snakemake has been disabled, because its dependency datrie not maintained, and [issue](https://github.com/snakemake/snakemake/issues/2970) open in snakemake repo since july is still pending

- Linters enhancements
  - Add support to [phpstan/extension-installer](https://github.com/phpstan/extension-installer) Composer plugin for automatic installation of PHPStan extensions, by @llaville in <https://github.com/oxsecurity/megalinter/pull/4337>
    - Learn more about context on [GH-4328](https://github.com/oxsecurity/megalinter/issues/4328)
  - Allow Terrascan to lint in file lint mode, by @bdovaz in <https://github.com/oxsecurity/megalinter/pull/4498>
  - Add sarif output to golangci-lint, by @bdovaz in <https://github.com/oxsecurity/megalinter/pull/4557>

- Plugins
  - Add [prettier for markdown](https://github.com/liblaf/megalinter-plugins/tree/main/mega-linter-plugin-markdown-prettier), by [Qin Li](https://github.com/liblaf)

- Fixes
  - [swiftlint](https://github.com/realm/SwiftLint) Fix swiftlint error where linter is unable to find lintable files. Fixes [#440](https://github.com/oxsecurity/megalinter/issues/440), by @Noraldeno in <https://github.com/oxsecurity/megalinter/pull/4427>
  - jscpd url fixes, by @alexanderbazhenoff in <https://github.com/oxsecurity/megalinter/pull/4352>
  - Don't call get_pr_data if GitLeaks linter is not active, by @bdovaz in <https://github.com/oxsecurity/megalinter/pull/4469>
  - Fix linter disabled reason usage, by @bdovaz in <https://github.com/oxsecurity/megalinter/pull/4466>

- Doc
  - Add contributing docs on venv, by @bdovaz in <https://github.com/oxsecurity/megalinter/pull/4479>
  - Add disabled linter badge, by @bdovaz in <https://github.com/oxsecurity/megalinter/pull/4477>
  - Add AzureCommentReporter instructions, by @bdovaz in <https://github.com/oxsecurity/megalinter/pull/4480>

- CI
  - Fix up gitpod config and workflow to support uv 0.5.0+ by @echoix in #4373
  - Use uv.lock file to build docker images, by @echoix in <https://github.com/oxsecurity/megalinter/pull/4374>
  - Update Renovate schedules for uv and sfdx-hardis, by @echoix in <https://github.com/oxsecurity/megalinter/pull/4568>
  - Variabilize version and use renovate for updates for the following linters:
    - all GO linters
    - all REPOSITORY linters
    - arm-ttk
    - bash-shfmt
    - bicep
    - clj-kondo
    - cljstyle
    - csharpier
    - dart
    - ktlint
    - kubescape
    - lychee
    - luacheck
    - markdown-link-check
    - perlcritic
    - raku
    - tsqllint

- Linter versions upgrades (66)
  - [actionlint](https://rhysd.github.io/actionlint/) from 1.7.6 to **1.7.7**
  - [ansible-lint](https://ansible-lint.readthedocs.io/) from 24.12.2 to **25.1.0**
  - [bandit](https://bandit.readthedocs.io/en/latest/)to **1.8.2**
  - [bash-exec](https://www.gnu.org/software/bash/) from 5.2.26 to **5.2.37**
  - [bicep_linter](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter) from to **0.33.13**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) **1.22.7**
  - [checkov](https://www.checkov.io/) from to **3.2.357**
  - [checkstyle](https://checkstyle.org/) from 10.20.1 to **10.21.1**
  - [clang-format](https://releases.llvm.org/17.0.1/tools/clang/docs/ClangFormat.html) from 17.0.6 to **19.1.4**
  - [clippy](https://github.com/rust-lang/rust-clippy) **0.1.84**
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2024.11.14 to **2025.01.16**
  - [cljstyle](https://github.com/greglook/cljstyle) from 0.15.0 to **0.17.642**
  - [csharpier](https://csharpier.com/) from 0.30.2 to **0.30.6**
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 8.16.0 to **8.17.2**
  - [devskim](https://github.com/microsoft/DevSkim) from 1.0.44 to **1.0.51**
  - [djlint](https://djlint.com/) from 1.36.1 to **1.36.4**
  - [dotnet-format](https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-format) from 8.0.111 to **9.0.102**
  - [editorconfig-checker](https://editorconfig-checker.github.io/) from 3.0.3 to **3.1.2**
  - [git_diff](https://git-scm.com) from 2.45.2 to **2.47.2**
  - [gitleaks](https://github.com/gitleaks/gitleaks) from 8.21.2 to **8.23.2**
  - [golangci-lint](https://golangci-lint.run/) from 1.62.0 to **1.63.4**
  - [grype](https://github.com/anchore/grype) from 0.79.5 to **0.87.0**
  - [helm](https://helm.sh/docs/helm/helm_lint/) from 3.14.3 to **3.16.3**
  - [ktlint](https://ktlint.github.io) from 1.4.1 to **1.5.0**
  - [lightning-flow-scanner](https://github.com/Lightning-Flow-Scanner) from 2.36.0 to **2.39.0**
  - [lychee](https://lychee.cli.rs) from 0.17.0 to **0.18.0**
  - [markdownlint](https://github.com/DavidAnson/markdownlint) from 0.43.0 to **0.44.0**
  - [mypy](https://mypy.readthedocs.io/en/stable/) from 1.13.0 to **1.14.0**
  - [mypy](https://mypy.readthedocs.io/en/stable/) from 1.14.0 to **1.14.1**
  - [php-cs-fixer](https://cs.symfony.com/) from 3.64.0 to **7.4.0**
  - [phpcs](https://github.com/PHPCSStandards/PHP_CodeSniffer) from 3.11.1 to **3.11.3**
  - [phplint](https://github.com/overtrue/phplint) from 9.5.4 to **9.5.6**
  - [phpstan](https://phpstan.org/) from 2.0.2 to **2.1.2**
  - [pmd](https://pmd.github.io/) from 7.7.0 to **7.9.0**
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.4.2 to **7.4.6**
  - [powershell_formatter](https://github.com/PowerShell/PSScriptAnalyzer) from 7.4.2 to **7.4.6**
  - [prettier](https://prettier.io/) from 3.3.3 to **3.4.2**
  - [protolint](https://github.com/yoheimuta/protolint) from 0.50.5 to **0.52.0**
  - [psalm](https://psalm.dev) from Psalm.5.26.1@ to **Psalm.6.0.0@**
  - [pylint](https://pylint.readthedocs.io) from 3.3.1 to **3.3.3**
  - [pyright](https://github.com/Microsoft/pyright) from 1.1.389 to **1.1.392**
  - [raku](https://raku.org/) from 2020.10 to **2024.10**
  - [revive](https://revive.run/) from 1.5.1 to **1.6.0**
  - [rubocop](https://rubocop.org/) from 1.68.0 to **1.71.0**
  - [ruff-format](https://github.com/astral-sh/ruff) from 0.8.6 to **0.9.3**
  - [ruff](https://github.com/astral-sh/ruff) from 0.8.0 to **0.9.3**
  - [scalafix](https://scalacenter.github.io/scalafix/) from 0.13.0 to **0.14.0**
  - [selene](https://kampfkarren.github.io/selene/) from 0.27.1 to **0.28.0**
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 4.7.0 to **4.8.0**
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 4.7.0 to **4.8.0**
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 4.7.0 to **4.8.0**
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 8.25.3 to **8.27.1**
  - [sqlfluff](https://www.sqlfluff.com/) from 3.2.5 to **3.3.0**
  - [stylelint](https://stylelint.io) from 16.10.0 to **16.14.0**
  - [swiftlint](https://github.com/realm/SwiftLint) from 0.57.0 to **0.58.2**
  - [syft](https://github.com/anchore/syft) from 1.17.0 to **1.19.0**
  - [terraform-fmt](https://developer.hashicorp.com/terraform/cli/commands/fmt) from 1.10.0 to **1.10.3**
  - [terraform-fmt](https://developer.hashicorp.com/terraform/cli/commands/fmt) from 1.9.8 to **1.10.0**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.68.14 to **0.69.13**
  - [tflint](https://github.com/terraform-linters/tflint) from 0.54.0 to **0.55.0**
  - [trivy-sbom](https://aquasecurity.github.io/trivy/) from 0.57.1 to **0.58.2**
  - [trivy](https://aquasecurity.github.io/trivy/) from 0.57.1 to **0.58.2**
  - [trufflehog](https://github.com/trufflesecurity/trufflehog) from 3.84.1 to **3.88.2**
  - [v8r](https://github.com/chris48s/v8r) from 4.2.0 to **4.2.1**
  - [vale](https://vale.sh/) from 3.9.1 to **3.9.4**
  - [xmllint](https://gitlab.gnome.org/GNOME/libxml2/-/wikis/home) from 21207 to **21304**

## [v8.3.0] - 2024-11-23

- Core
  - Display command log (truncated to 250 chars) even when LOG_LEVEL is not DEBUG
  - Allow to replace an ENV var value with the value of another ENV var before calling a PRE_COMMAND (helps for tflint run from GitHub Enterprise)
  - Fix handling of git submodule paths

- Fixes
  - [trivy](https://megalinter.io/latest/descriptors/repository_trivy/): retry in case of BLOB_UNKNOWN  while downloading vulnerability list

- Reporters
  - Fix UpdatedSourcesReporter when `APPLY_FIXES` is list (array)
  - Fix AzureCommentReporter when the repo is not found: fallback using BUILD_REPOSITORY_ID. (+ disable space replacement in repo name with `AZURE_COMMENT_REPORTER_REPLACE_WITH_SPACES: false`)

- CI
  - Fix Docker mirroring job for release context
  - Remove max parallel jobs for release linters workflow

- Linter versions upgrades (13)
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 1.19.0 to **1.20.0**
  - [checkov](https://www.checkov.io/) from 3.2.298 to **3.2.311**
  - [csharpier](https://csharpier.com/) from 0.29.2 to **0.30.2**
  - [markdownlint](https://github.com/DavidAnson/markdownlint) from 0.42.0 to **0.43.0**
  - [phpstan](https://phpstan.org/) from 2.0.1 to **2.0.2**
  - [ruff](https://github.com/astral-sh/ruff) from 0.7.4 to **0.8.0**
  - [spectral](https://docs.stoplight.io/docs/spectral/674b27b261c3c-overview) from 6.14.1 to **6.14.2**
  - [stylua](https://github.com/JohnnyMorganz/StyLua) from 0.20.0 to **2.0.0**
  - [syft](https://github.com/anchore/syft) from 1.16.0 to **1.17.0**
  - [trivy-sbom](https://aquasecurity.github.io/trivy/) from 0.57.0 to **0.57.1**
  - [trivy](https://aquasecurity.github.io/trivy/) from 0.57.0 to **0.57.1**
  - [trufflehog](https://github.com/trufflesecurity/trufflehog) from 3.83.7 to **3.84.1**
  - [vale](https://vale.sh/) from 3.9.0 to **3.9.1**

## [v8.2.0] - 2024-11-17

- Media
  - [10 MegaLinter Tips and Tricks Unlock its Full Potential](https://flexion.us/blog/megalinter-tips-and-tricks/) by [Wes Dean](https://github.com/wesley-dean)
  - [MegaLinter Performance Tuning for Maximum Efficiency](https://flexion.us/blog/megalinter-performance-tuning/) by [Wes Dean](https://github.com/wesley-dean)

- Linters enhancements
  - [detekt](https://megalinter.io/latest/descriptors/kotlin_detekt/) Enable SARIF output + count errors
  - [lintr](https://megalinter.io/latest/descriptors/r_lintr/): Support files in subdirectories, fix unit tests
  - [phpcs](https://megalinter.io/latest/descriptors/php_phpcs/): Activate APPLY_FIXES
  - [Salesforce linters](https://megalinter.io/latest/descriptors/salesforce/): Add SF_CLI_DISABLE_AUTOUPDATE for SF CLI JIT plugins
  - [trivy](https://megalinter.io/latest/descriptors/repository_trivy/): handle retry if `failed to download Java DB` is detected
  - [tsqllint](https://github.com/tsqllint/tsqllint) Re-enabled after .net 8 and security updates

- Fixes
  - Add message in PR comment if FAIL_IF_UPDATED_SOURCES is triggered
  - Fix linting errors in GitHub Actions template

- Reporters
  - [UpdatedSourcesReporter](https://megalinter.io/latest/reporters/UpdatedSourcesReporter/) will git commit & push fixed files to source branch if APPLY_FIXES is set
  - Fix AzureCommentReporter not adding comments to PR
  - Fix AzureCommentReporter fails when target repo contains spaces

- Doc
  - Updated documentation with Azure central pipeline use case
  - Update DevSkim documentation to show a valid exclusion config file
  - Note about `risky` rules and how to fix rule violations with PHP-CS-Fixer

- CI
  - Also prune volumes before pulling and pushing to docker hub
  - Externalize mirroring from ghcr.io to docker hub in another workflow to avoid memory issues
  - Squash docker images to have less layers and size
  - Comment jobs related to GitHub Worker images, as CodeTotal is not actively maintained
  - Make gitpod workflow not blocking until uv install is fixed
  - Update stale comment
  - Try several times to embed trivy db during Docker build, as a workaround to the random failures
  - Wait 10 secondes instead of 1 before retrying a failing test method, to avoid race conditions

- Linter versions upgrades (104)
  - [actionlint](https://rhysd.github.io/actionlint/) from 1.7.3 to **1.7.4**
  - [ansible-lint](https://ansible-lint.readthedocs.io/) from 24.9.2 to **24.10.0**
  - [bicep_linter](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter) from 0.30.23 to **0.31.92**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 1.16.1 to **1.19.0**
  - [checkov](https://www.checkov.io/) from 3.2.257 to **3.2.298**
  - [checkstyle](https://checkstyle.org/) from 10.18.2 to **10.20.1**
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.81 to **0.1.82**
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2024.09.27 to **2024.11.14**
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 8.15.1 to **8.16.0**
  - [devskim](https://github.com/microsoft/DevSkim) from 1.0.33 to **1.0.44**
  - [djlint](https://djlint.com/) from 1.35.2 to **1.36.1**
  - [dotnet-format](https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-format) from 8.0.110 to **8.0.111**
  - [gitleaks](https://github.com/gitleaks/gitleaks) from 8.20.1 to **8.21.2**
  - [golangci-lint](https://golangci-lint.run/) from 1.61.0 to **1.62.0**
  - [ktlint](https://ktlint.github.io) from 1.3.1 to **1.4.1**
  - [lightning-flow-scanner](https://github.com/Lightning-Flow-Scanner) from 2.34.0 to **2.36.0**
  - [lychee](https://lychee.cli.rs) from 0.16.1 to **0.17.0**
  - [mypy](https://mypy.readthedocs.io/en/stable/) from 1.11.2 to **1.13.0**
  - [perlcritic](https://metacpan.org/pod/Perl::Critic) from 1.152 to **1.156**
  - [phpcs](https://github.com/PHPCSStandards/PHP_CodeSniffer) from 3.10.3 to **3.11.1**
  - [phplint](https://github.com/overtrue/phplint) from 9.5.3 to **9.5.4**
  - [phpstan](https://phpstan.org/) from 1.12.6 to **2.0.1**
  - [pmd](https://pmd.github.io/) from 7.6.0 to **7.7.0**
  - [pyright](https://github.com/Microsoft/pyright) from 1.1.384 to **1.1.389**
  - [revive](https://revive.run/) from 1.4.0 to **1.5.1**
  - [roslynator](https://github.com/dotnet/Roslynator) from 0.9.1.0 to **0.9.3.0**
  - [rubocop](https://rubocop.org/) from 1.66.1 to **1.68.0**
  - [ruff](https://github.com/astral-sh/ruff) from 0.6.9 to **0.7.4**
  - [secretlint](https://github.com/secretlint/secretlint) from 8.4.0 to **9.0.0**
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 4.6.0 to **4.7.0**
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 4.6.0 to **4.7.0**
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 4.6.0 to **4.7.0**
  - [shfmt](https://github.com/mvdan/sh) from 3.9.0 to **3.10.0**
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 8.21.0 to **8.25.3**
  - [spectral](https://docs.stoplight.io/docs/spectral/674b27b261c3c-overview) from 6.13.1 to **6.14.1**
  - [sqlfluff](https://www.sqlfluff.com/) from 3.2.3 to **3.2.5**
  - [syft](https://github.com/anchore/syft) from 1.14.0 to **1.16.0**
  - [terraform-fmt](https://developer.hashicorp.com/terraform/cli/commands/fmt) from 1.9.5 to **1.9.8**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.67.5 to **0.68.14**
  - [tflint](https://github.com/terraform-linters/tflint) from 0.53.0 to **0.54.0**
  - [trivy-sbom](https://aquasecurity.github.io/trivy/) from 0.56.2 to **0.57.0**
  - [trivy](https://aquasecurity.github.io/trivy/) from 0.56.2 to **0.57.0**
  - [trufflehog](https://github.com/trufflesecurity/trufflehog) from 3.82.11 to **3.83.7**
  - [tsqllint](https://github.com/tsqllint/tsqllint) from 1.15.3.0 to **1.16.0.0**
  - [v8r](https://github.com/chris48s/v8r) from 4.1.0 to **4.2.0**
  - [vale](https://vale.sh/) from 3.7.1 to **3.9.0**

## [v8.1.0] - 2024-10-13

- Core
  - Allow to tag PRE_COMMANDS to run them before loading plugins, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3944>
  - Replace usage of setup.py with a pyproject.toml package install, by @echoix in [#3893](https://github.com/oxsecurity/megalinter/pull/3893)
  - Allow to add custom messages at the end of PR / MR MegaLinter Summary using variable **JOB_SUMMARY_ADDITIONAL_MARKDOWN**

- New linters
  - New LUA linter: [**selene**](https://github.com/Kampfkarren/selene), by @AlejandroSuero in <https://github.com/oxsecurity/megalinter/pull/3978>
  - New LUA formatter: [**stylua**](https://github.com/JohnnyMorganz/StyLua), by @AlejandroSuero in <https://github.com/oxsecurity/megalinter/pull/3985>

- Linters enhancements
  - Trivy
    - Embed vulnerability database in Docker Image for running trivy on internet-free network
    - Retry 5 times after 3 seconds in case of TooManyRequests when downloading vulnerability database
    - If the retries did not succeed, call trivy with `--skip-db-update --skip-check-update` (not ideal but better than nothing)
  - Bash/Perl: Support shell scripts with no extension and only support perl shebangs at the beginning of a file in <https://github.com/oxsecurity/megalinter/pull/4076>

- Fixes
  - APPLY_FIXES and for PHP_PHPCSFIXER linter, by @llaville in [#3963](https://github.com/oxsecurity/megalinter/issues/3963)
  - Add debug traces to investigate reporters activation
  - Add more traces for ApiReporter
  - Activate ApiReporter by default

- Reporters
  - Fix ApiReporter not called in MegaLinter flavors

- Doc
  - Fix Grafana Home Dashboard to add missing criteria
  - Update PRE_COMMANDS documentation to describe all properties
  - Update Grafana documentation to fix secrets typo

- CI
  - Free space in release job to avoid no space left on device, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3914>
  - Add `pytest-rerunfailures` to improve CI control jobs success, by @AlejandroSuero in <https://github.com/oxsecurity/megalinter/pull/3993>
  - Send GITHUB_TOKEN to trivy-action
  - Workaround to avoid to reach Docker Hub rate limits: Build & push first on ghcr.io, then login to docker hub, then push to docker hub

- Linter versions upgrades
  - [actionlint](https://rhysd.github.io/actionlint/) from 1.7.1 to **1.7.3**
  - [ansible-lint](https://ansible-lint.readthedocs.io/) from 24.7.0 to **24.9.2**
  - [bandit](https://bandit.readthedocs.io/en/latest/) from 1.7.9 to **1.7.10**
  - [bicep_linter](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter) from 0.29.47 to **0.30.23**
  - [black](https://black.readthedocs.io/en/stable/) from 24.8.0 to **24.10.0**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 1.10.3 to **1.16.1**
  - [checkov](https://www.checkov.io/) from 3.2.232 to **3.2.257**
  - [checkstyle](https://checkstyle.org/) from 10.17.0 to **10.18.2**
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.80 to **0.1.81**
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2024.08.01 to **2024.09.27**
  - [cpplint](https://github.com/cpplint/cpplint) from 1.6.1 to **2.0.0**
  - [csharpier](https://csharpier.com/) from 0.29.0 to **0.29.2**
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 8.14.1 to **8.15.1**
  - [detekt](https://detekt.dev/) from 1.23.6 to **1.23.7**
  - [djlint](https://djlint.com/) from 1.34.1 to **1.35.2**
  - [dotnet-format](https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-format) from 8.0.108 to **8.0.110**
  - [eslint](https://eslint.org) from 8.57.0 to **8.57.1**
  - [gitleaks](https://github.com/gitleaks/gitleaks) from 8.18.4 to **8.20.1**
  - [golangci-lint](https://golangci-lint.run/) from 1.60.1 to **1.61.0**
  - [kics](https://www.kics.io) from 2.1.2 to **2.1.3**
  - [lightning-flow-scanner](https://github.com/Lightning-Flow-Scanner) from 2.33.0 to **2.34.0**
  - [lychee](https://lychee.cli.rs) from 0.15.1 to **0.16.1**
  - [markdownlint](https://github.com/DavidAnson/markdownlint) from 0.41.0 to **0.42.0**
  - [mypy](https://mypy.readthedocs.io/en/stable/) from 1.11.1 to **1.11.2**
  - [npm-groovy-lint](https://nvuillam.github.io/npm-groovy-lint/) from 14.6.0 to **15.0.2**
  - [php-cs-fixer](https://cs.symfony.com/) from 3.62.0 to **3.64.0**
  - [phpcs](https://github.com/PHPCSStandards/PHP_CodeSniffer) from 3.10.2 to **3.10.3**
  - [phplint](https://github.com/overtrue/phplint) from 9.4.1 to **9.5.3**
  - [phpstan](https://phpstan.org/) from 1.11.11 to **1.12.6**
  - [pmd](https://pmd.github.io/) from 7.4.0 to **7.6.0**
  - [psalm](https://psalm.dev) from Psalm.5.25.0@ to **Psalm.5.26.1@**
  - [pylint](https://pylint.readthedocs.io) from 3.2.6 to **3.3.1**
  - [pyright](https://github.com/Microsoft/pyright) from 1.1.376 to **1.1.384**
  - [revive](https://revive.run/) from 1.3.9 to **1.4.0**
  - [roslynator](https://github.com/dotnet/Roslynator) from 0.8.9.0 to **0.9.1.0**
  - [rubocop](https://rubocop.org/) from 1.65.1 to **1.66.1**
  - [ruff](https://github.com/astral-sh/ruff) from 0.6.1 to **0.6.9**
  - [scalafix](https://scalacenter.github.io/scalafix/) from 0.12.1 to **0.13.0**
  - [secretlint](https://github.com/secretlint/secretlint) from 8.2.4 to **8.4.0**
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 4.4.0 to **4.6.0**
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 4.4.0 to **4.6.0**
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 4.4.0 to **4.6.0**
  - [shfmt](https://github.com/mvdan/sh) from 3.8.0 to **3.9.0**
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 8.18.1 to **8.21.0**
  - [spectral](https://docs.stoplight.io/docs/spectral/674b27b261c3c-overview) from 6.11.1 to **6.13.1**
  - [sqlfluff](https://www.sqlfluff.com/) from 3.1.0 to **3.2.3**
  - [standard](https://standardjs.com/) from 17.1.0 to **17.1.2**
  - [stylelint](https://stylelint.io) from 16.8.2 to **16.10.0**
  - [swiftlint](https://github.com/realm/SwiftLint) from 0.56.1 to **0.57.0**
  - [syft](https://github.com/anchore/syft) from 1.11.0 to **1.14.0**
  - [terraform-fmt](https://developer.hashicorp.com/terraform/cli/commands/fmt) from 1.9.4 to **1.9.5**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.66.8 to **0.67.5**
  - [terrascan](https://runterrascan.io/) from 1.18.11 to **1.19.9**
  - [trivy-sbom](https://aquasecurity.github.io/trivy/) from 0.54.1 to **0.56.2**
  - [trivy](https://aquasecurity.github.io/trivy/) from 0.54.1 to **0.56.2**
  - [trufflehog](https://github.com/trufflesecurity/trufflehog) from 3.81.10 to **3.82.8**
  - [v8r](https://github.com/chris48s/v8r) from 4.0.1 to **4.1.0**
  - [vale](https://vale.sh/) from 3.7.0 to **3.7.1**

## [v8.0.0] - 2024-08-19

- Reporters
  - New [**ApiReporter**](https://megalinter.io/beta/reporters/ApiReporter/) (can be used to build Grafana dashboards), by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3540>

[![Upgrade to v8 Video](https://img.youtube.com/vi/vbx-ifa1oXE/0.jpg)](https://www.youtube.com/watch?v=vbx-ifa1oXE)

- Removed deprecated linters, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3854>
  - CSS_SCSSLINT: [Project discontinued and advising to use stylelint](https://github.com/sds/scss-lint#notice-consider-other-tools-before-adopting-scss-lint)
  - OPENAPI_SPECTRAL: Replaced by [API_SPECTRAL](https://megalinter.io/latest/descriptors/api_spectral/) (same linter but more formats handled)
  - SQL_SQL_LINT: [Project no longer maintained](https://github.com/joereynolds/sql-lint/issues/262)

- Core
  - Hide to linters by default all environment variables that contain **TOKEN**, **USERNAME** or **PASSWORD**, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3881>
  - Allow to override CLI_LINT_MODE when defined as project, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3772>
  - Allow to use absolute paths for LINTER_RULES_PATH, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3775>
  - Allow to update variables from [PRE/POST Commands](https://megalinter.io/latest/config-precommands/) using `output_variables` property, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3861>

- Media
  - [MegaLinter: un linter pour les gouverner tous](https://blog.wescale.fr/megalinter-un-linter-pour-les-gouverner-tous) (FR), by [Guillaume Arnaud](https://www.linkedin.com/in/guillaume-arnaud/) from [WeScale](https://www.wescale.fr/)
  - [MegaLinter](https://blog.stephane-robert.info/docs/developper/autres-outils/linters/megalinter/), by [Stéphane Robert](https://www.linkedin.com/in/stephanerobert1/), from [3DS OutScale](https://fr.outscale.com/)
  - [30 Seconds to Setup MegaLinter: Your Go-To Tool for Automated Code Quality](https://medium.com/@caodanju/30-seconds-to-setup-megalinter-your-go-to-tool-for-automated-code-quality-and-iac-security-969d90a5a99c), by [Peng Cao](https://www.linkedin.com/in/peng-cao-83b6a2103/) |

- Linters enhancements
  - [bandit](https://megalinter.io/latest/descriptors/python_bandit/) Call bandit with quiet mode to generate less logs, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3892>
  - [grype](https://megalinter.io/latest/descriptors/repository_grype/) Count number of errors returned by Grype,  by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3906>
  - [yamllint](https://megalinter.io/latest/descriptors/yaml_yamllint) Fix yamllint default format to avoid special characters or GitHub sections in text logs, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3898>

- Fixes
  - [terrascan](https://runterrascan.io/) fixed errors and removed redundant code, by @TommyE123 in <https://github.com/oxsecurity/megalinter/pull/3767>
  - [dotnet-format](https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-format) various performance improvements and ability to specify sln or proj paths, by @TommyE123 in <https://github.com/oxsecurity/megalinter/pull/3741>
  - [swiftlint](https://github.com/realm/SwiftLint) Remove deprecated argument --path
  - Salesforce linters: Disable SF CLI auto update warning, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3883>

- Doc
  - Add images and links to Git, CI/CD & other tools integrations at the beginning of the README, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3885>
  - Create README animated GIF presentation of MegaLinter, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3910>
  - Format mkdocs search index in place, by @echoix in <https://github.com/oxsecurity/megalinter/pull/3890>
  - Use consistent spelling of 'flavor', by @InputUsername in <https://github.com/oxsecurity/megalinter/pull/3789>

- CI
  - Fix docker warnings, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3853>
    - FromAsCasing: 'as' and 'FROM' keywords' casing do not match
    - NoEmptyContinuation: Empty continuation line
    - SecretsUsedInArgOrEnv: Do not use ARG or ENV instructions for sensitive data
  - Port Beta workflows to use docker/metadata-action, by @echoix in <https://github.com/oxsecurity/megalinter/pull/3860>
  - AutoUpdate linters: Always create a PR if the job has been started manually, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3863>
  - Add `skip_checkout: true` to default MegaLinter GitHub Action template
  - Remove path filters in deploy-DEV workflow as it is a required check by @echoix in <https://github.com/oxsecurity/megalinter/pull/3894>

- mega-linter-runner
  - Add new rules to upgrade to MegaLinter v8, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3896>
  - Replace glob-promise by glob library, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3902>
    - **Minimum NodeJs version is now 20.x**

- Linter versions upgrades
  - [ansible-lint](https://ansible-lint.readthedocs.io/) from 24.6.1 to **24.7.0**
  - [bicep_linter](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter) from 0.28.1 to **0.29.47**
  - [black](https://black.readthedocs.io/en/stable/) from 24.4.2 to **24.8.0**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 1.5.0 to **1.10.3**
  - [checkov](https://www.checkov.io/) from 3.2.174 to **3.2.232**
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.79 to **0.1.80**
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2024.05.24 to **2024.08.01**
  - [csharpier](https://csharpier.com/) from 0.28.2 to **0.29.0**
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 8.10.4 to **8.14.1**
  - [dotnet-format](https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-format) from 8.0.106 to **8.0.108**
  - [flake8](https://flake8.pycqa.org) from 7.1.0 to **7.1.1**
  - [golangci-lint](https://golangci-lint.run/) from 1.59.1 to **1.60.1**
  - [grype](https://github.com/anchore/grype) from 0.79.2 to **0.79.5**
  - [jsonlint](https://github.com/prantlf/jsonlint) from 14.0.3 to **16.0.0**
  - [kics](https://www.kics.io) from 2.1.1 to **2.1.2**
  - [kubeconform](https://github.com/yannh/kubeconform) from 0.6.6 to **0.6.7**
  - [lightning-flow-scanner](https://github.com/Lightning-Flow-Scanner) from 2.28.0 to **2.33.0**
  - [mypy](https://mypy.readthedocs.io/en/stable/) from 1.10.1 to **1.11.1**
  - [php-cs-fixer](https://cs.symfony.com/) from 3.59.3 to **3.62.0**
  - [phpcs](https://github.com/PHPCSStandards/PHP_CodeSniffer) from 3.10.1 to **3.10.2**
  - [phpstan](https://phpstan.org/) from 1.11.9 to **1.11.11**
  - [pmd](https://pmd.github.io/) from 7.3.0 to **7.4.0**
  - [prettier](https://prettier.io/) from 3.3.2 to **3.3.3**
  - [protolint](https://github.com/yoheimuta/protolint) from 0.50.2 to **0.50.5**
  - [pylint](https://pylint.readthedocs.io) from 3.2.5 to **3.2.6**
  - [pyright](https://github.com/Microsoft/pyright) from 1.1.370 to **1.1.376**
  - [revive](https://revive.run/) from 1.3.7 to **1.3.9**
  - [rstcheck](https://github.com/myint/rstcheck) from 6.2.1 to **6.2.4**
  - [rubocop](https://rubocop.org/) from 1.64.1 to **1.65.1**
  - [ruff](https://github.com/astral-sh/ruff) from 0.5.1 to **0.6.1**
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 4.3.2 to **4.4.0**
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 4.3.2 to **4.4.0**
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 4.3.2 to **4.4.0**
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 8.15.2 to **8.18.1**
  - [stylelint](https://stylelint.io) from 16.6.1 to **16.8.2**
  - [swiftlint](https://github.com/realm/SwiftLint) from 0.55.1 to **0.56.1**
  - [syft](https://github.com/anchore/syft) from 1.8.0 to **1.11.0**
  - [terraform-fmt](https://developer.hashicorp.com/terraform/cli/commands/fmt) from 1.9.0 to **1.9.4**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.59.6 to **0.66.8**
  - [tflint](https://github.com/terraform-linters/tflint) from 0.52.0 to **0.53.0**
  - [trivy-sbom](https://aquasecurity.github.io/trivy/) from 0.53.0 to **0.54.1**
  - [trivy](https://aquasecurity.github.io/trivy/) from 0.53.0 to **0.54.1**
  - [trufflehog](https://github.com/trufflesecurity/trufflehog) from 3.79.0 to **3.81.9**
  - [v8r](https://github.com/chris48s/v8r) from 3.1.0 to **4.0.1**
  - [vale](https://vale.sh/) from 3.6.0 to **3.7.0**

## [v7.13.0] - 2024-07-06

- New linters
  - Add [**ls-lint**](https://ls-lint.org/), file and folder linter, by @scolladon in <https://github.com/oxsecurity/megalinter/pull/3681>

- Core
  - Handle renovate version comments in build script, by @echoix in <https://github.com/oxsecurity/megalinter/pull/3617> ,  <https://github.com/oxsecurity/megalinter/pull/3627> , <https://github.com/oxsecurity/megalinter/pull/3643> , <https://github.com/oxsecurity/megalinter/pull/3699> , <https://github.com/oxsecurity/megalinter/pull/3700>
  - Update base image to python:3.12.4-alpine3.20
  - Use `dotnet8-sdk` available in the main repository, by @TommyE123 in <https://github.com/oxsecurity/megalinter/pull/3696>

- Media
  - [Introducing MegaLinter: Streamlining Code Quality Checks Across Multiple Languages](https://cloudtuned.hashnode.dev/introducing-megalinter-streamlining-code-quality-checks-across-multiple-languages), by Cloud Tuned
  - [Infrastructure as Code GitHub Codespace Template](https://luke.geek.nz/azure/iac-github-codespace/), by [Luke Murray](https://www.linkedin.com/in/ljmurray/)
  - [Video: How to: Secrets scanning](https://youtu.be/iBMWAk5QIfM?si=EVcJilkz7Y2jdn6e&t=649), by [Hackitect's playground](https://www.youtube.com/@hackitectsplayground)

- Linters enhancements
  - Add SARIF support (v2) for all PHP linters by @llaville in <https://github.com/oxsecurity/megalinter/pull/3745> , <https://github.com/oxsecurity/megalinter/pull/3729>
  - Add python package Pygments to rst-lint venv, by @bobidle in <https://github.com/oxsecurity/megalinter/pull/3631>
  - [CSharpier](https://csharpier.com) added ability to override config filename and path, by @TommyE123 in <https://github.com/oxsecurity/megalinter/pull/3664>
  - [xmllint](https://gnome.pages.gitlab.gnome.org/libxml2/xmllint.html) added support for `xsd` files, by @TommyE123 in <https://github.com/oxsecurity/megalinter/pull/3665>

- Fixes
  - Improve support for single argument in `get_list_args` function, by @TommyE123 in <https://github.com/oxsecurity/megalinter/pull/3589>
  - [ansible-lint](https://ansible-lint.readthedocs.io) Improved activation by checking for `.ansible-lint` config file, by @TommyE123 in <https://github.com/oxsecurity/megalinter/pull/3697>
  - [DevSkim](https://github.com/microsoft/DevSkim) fixed fatal errors when scanning and ability to override config path, by @TommyE123 in <https://github.com/oxsecurity/megalinter/pull/3673>
  - [GitLeaks](https://github.com/gitleaks/gitleaks) add missing schema properties, by @TommyE123 in <https://github.com/oxsecurity/megalinter/pull/3675>
  - [Powershell](https://github.com/PowerShell/PSScriptAnalyzer#readme) Error table truncation improvements, by @TommyE123 in <https://github.com/oxsecurity/megalinter/pull/3620>
  - [Powershell](https://github.com/PowerShell/PSScriptAnalyzer#readme) added missing schema property `POWERSHELL_POWERSHELL_FORMATTER_OUTPUT_ENCODING`, by @TommyE123 in <https://github.com/oxsecurity/megalinter/pull/3678>
  - [syft](https://github.com/anchore/syft) use `scan` instead of deprecated `packages` arg, by @TommyE123 in <https://github.com/oxsecurity/megalinter/pull/3613>
  - [tflint](https://github.com/terraform-linters/tflint) added missing schema property `TERRAFORM_TFLINT_SECURED_ENV`, by @TommyE123 in <https://github.com/oxsecurity/megalinter/pull/3679>
  - [tflint](https://github.com/terraform-linters/tflint) fixed deprecated argument and other improvements to default `.tflint.hcl` template, by @TommyE123 in <https://github.com/oxsecurity/megalinter/pull/3688>
  - [xmllint](https://gitlab.gnome.org/GNOME/libxml2/-/wikis/home) added missing schema properties `XML_XMLLINT_AUTOFORMAT` and `XML_XMLLINT_INDENT`, by @TommyE123 in <https://github.com/oxsecurity/megalinter/pull/3677>
  - [yamllint](https://github.com/adrienverge/yamllint) fix error/warning count to work with different log output formats, by @TommyE123 in <https://github.com/oxsecurity/megalinter/pull/3612>

- Doc
  - Update documentation icons by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3625>

- Flavors
  - Add gherkin-lint in c_cpp flavor, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3698>

- CI
  - Bump actions/checkout from 3 to 4, by @KristjanESPERANTO in <https://github.com/oxsecurity/megalinter/pull/2994>
  - Reduce dependabot PR frequency to weekly by @echoix in <https://github.com/oxsecurity/megalinter/pull/3642>

- Linter versions upgrades
  - [ansible-lint](https://ansible-lint.readthedocs.io/) from 24.2.3 to **24.6.1**
  - [bandit](https://bandit.readthedocs.io/en/latest/) from 1.7.8 to **1.7.9**
  - [bash-exec](https://www.gnu.org/software/bash/) from 5.2.21 to **5.2.26**
  - [bicep_linter](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter) from 0.27.1 to **0.28.1**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 0.87.4 to **1.5.0**
  - [checkov](https://www.checkov.io/) from 3.2.122 to **3.2.174**
  - [clang-format](https://releases.llvm.org/17.0.1/tools/clang/docs/ClangFormat.html) from 17.0.5 to **17.0.6**
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.78 to **0.1.79**
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 8.8.3 to **8.10.4**
  - [editorconfig-checker](https://editorconfig-checker.github.io/) from 3.0.1 to **3.0.3**
  - [flake8](https://flake8.pycqa.org) from 7.0.0 to **7.1.0**
  - [git_diff](https://git-scm.com) from 2.43.4 to **2.45.2**
  - [gitleaks](https://github.com/gitleaks/gitleaks) from 8.18.2 to **8.18.4**
  - [golangci-lint](https://golangci-lint.run/) from 1.59.0 to **1.59.1**
  - [grype](https://github.com/anchore/grype) from 0.78.0 to **0.79.2**
  - [helm](https://helm.sh/docs/helm/helm_lint/) from 3.14.2 to **3.14.3**
  - [jscpd](https://github.com/kucherenko/jscpd/tree/master/packages/jscpd) from 4.0.4 to **4.0.5**
  - [kics](https://www.kics.io) from 2.0.1 to **2.1.1**
  - [ktlint](https://ktlint.github.io) from 1.2.1 to **1.3.1**
  - [lightning-flow-scanner](https://github.com/Lightning-Flow-Scanner) from 2.26.0 to **2.28.0**
  - [markdown-table-formatter](https://www.npmjs.com/package/markdown-table-formatter) from 1.6.0 to **1.6.1**
  - [mypy](https://mypy.readthedocs.io/en/stable/) from 1.10.0 to **1.10.1**
  - [npm-package-json-lint](https://npmpackagejsonlint.org/) from 7.1.0 to **8.0.0**
  - [php-cs-fixer](https://cs.symfony.com/) from 3.58.1 to **3.59.3**
  - [phplint](https://github.com/overtrue/phplint) from 9.3.1 to **9.4.1**
  - [phpstan](https://phpstan.org/) from 1.11.3 to **1.11.7**
  - [pmd](https://pmd.github.io/) from 7.1.0 to **7.3.0**
  - [prettier](https://prettier.io/) from 3.3.0 to **3.3.2**
  - [protolint](https://github.com/yoheimuta/protolint) from 0.49.7 to **0.50.2**
  - [psalm](https://psalm.dev) from Psalm.5.24.0@ to **Psalm.5.25.0@**
  - [pylint](https://pylint.readthedocs.io) from 3.2.2 to **3.2.5**
  - [pyright](https://github.com/Microsoft/pyright) from 1.1.365 to **1.1.370**
  - [ruff](https://github.com/astral-sh/ruff) from 0.4.10 to **0.5.1**
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 3.25.0 to **4.3.2**
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 3.25.0 to **4.3.2**
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 3.25.0 to **4.3.2**
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 8.12.0 to **8.15.2**
  - [sqlfluff](https://www.sqlfluff.com/) from 3.0.7 to **3.1.0**
  - [swiftlint](https://github.com/realm/SwiftLint) from 0.54.0 to **0.55.1**
  - [syft](https://github.com/anchore/syft) from 1.5.0 to **1.8.0**
  - [terraform-fmt](https://developer.hashicorp.com/terraform/cli/commands/fmt) from 1.8.4 to **1.9.0**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.58.13 to **0.59.6**
  - [tflint](https://github.com/terraform-linters/tflint) from 0.51.1 to **0.52.0**
  - [trivy-sbom](https://aquasecurity.github.io/trivy/) from 0.51.4 to **0.53.0**
  - [trivy](https://aquasecurity.github.io/trivy/) from 0.51.4 to **0.53.0**
  - [trufflehog](https://github.com/trufflesecurity/trufflehog) from 3.77.0 to **3.79.0**
  - [v8r](https://github.com/chris48s/v8r) from 3.0.0 to **3.1.0**
  - [vale](https://vale.sh/) from 3.4.2 to **3.6.0**
  - [xmllint](https://gitlab.gnome.org/GNOME/libxml2/-/wikis/home) from 21108 to **21207**

## [v7.12.0] - 2024-06-02

- Core
  - Add new logs (at debug level) on each linter activation/deactivation
  - Clean MegaLinter own CVE exceptions and order the remaining ones with links to related issues
  - Upgrade to Java 21 except for npm-groovy-lint that requires Java 17

- Media
  - Add blog post [5 ways MegaLinter upped our DevSecOps game](https://flexion.us/blog/5-ways-megalinter-upped-our-devsecops-game/) to the list of English articles by @wesley-dean-flexion in <https://github.com/oxsecurity/megalinter/pull/3596>

- Linters
  - Add PHP fixer by @llaville in <https://github.com/oxsecurity/megalinter/pull/3598>
  - `API_SPECTRAL` was added as replacement for `OPENAPI_SPECTRAL` (deprecated), supporting AsyncAPI and OpenAPI by default. Uses Spectral's standard config file name `.spectral.yaml` instead of `.openapirc.yml` with a default config with rulesets for AsyncAPI and OpenAPI enabled. Fixes [#3387](https://github.com/oxsecurity/megalinter/issues/3387)
  - Disable SQL_TSQLLINT until security issues are solved. Related to <https://github.com/tsqllint/tsqllint/issues/333>
  - PHP linters (PHP_PHPCS, PHP_PHPLINT, PHP_PHPSTAN) add support to SARIF report output format with help of <https://github.com/llaville/sarif-php-sdk>
  - Php psalm improvement by @llaville in <https://github.com/oxsecurity/megalinter/pull/3541>
  - `KOTLIN_KTLINT` now supports `list_of_files` mode, and has better error counting
  - Upgrade `KOTLIN_DETEKT` and make it work with cli_lint_mode = project

- Fixes
  - Change `golangci-lint` lint mode to `project`, by @wandering-tales in <https://github.com/oxsecurity/megalinter/pull/3509>
  - Disable sql-lint as it is no longer maintained
  - Add new entries `findUnusedCode` and `findUnusedBaselineEntry` in default `psalm.xml` configuration file for PHP_PSALM linter. Related to <https://github.com/oxsecurity/megalinter/issues/3538>
  - fix(pylint): overgeneral-exceptions fully qualified name by @gardar in <https://github.com/oxsecurity/megalinter/pull/3576>
  - Update `ktlint` descriptor to support `list_of_files` and better error counting by @Yann-J in <https://github.com/oxsecurity/megalinter/pull/3575>
  - Sync PowerShell version in arm.megalinter-descriptor.yml by @echoix in <https://github.com/oxsecurity/megalinter/pull/3586>
  - Adjust find commands to clean up files in same step by @echoix in <https://github.com/oxsecurity/megalinter/pull/3588>
  - Upgrade KOTLIN_DETEKT and make it work with cli_lint_mode = project by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3590>

- Doc
  - Handle disabled_reason property in descriptors
  - Sort enums in json schema, by @echoix in <https://github.com/oxsecurity/megalinter/pull/3595>

- Flavors

- CI
  - Build: take in account disabled linters for workflow auto-update
  - Remove useless package-lock.json that was in python tests folder
  - Fix SARIF_REPORTER that was wrongly sent to `true` to format & fix test methods
  - Build: Write ARG lines at the top of Dockerfiles if they are used by FROM variables
  - Remove Github Actions Workflow telemetry to improve performances
  - Update Docker image for Gitpod to run on Ubuntu Noble, by @echoix
  - Update makefile bootstrap config (gitpod or local) to use uv for package installation, by @echoix
  - Use uv to install Python deps for CI by @echoix in <https://github.com/oxsecurity/megalinter/pull/3561>
  - Use a single find command to delete pycache files by @echoix in <https://github.com/oxsecurity/megalinter/pull/3562>
  - Sort schema enums by @echoix in <https://github.com/oxsecurity/megalinter/pull/3595>

- Linter versions upgrades
  - [actionlint](https://rhysd.github.io/actionlint/) from 1.6.27 to **1.7.1**
  - [ansible-lint](https://ansible-lint.readthedocs.io/) from 24.2.2 to **24.2.3**
  - [bicep_linter](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter) from 0.26.170 to **0.27.1**
  - [black](https://black.readthedocs.io/en/stable/) from 24.4.0 to **24.4.2**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 0.86.4 to **0.87.4**
  - [checkov](https://www.checkov.io/) from 3.2.74 to **3.2.122**
  - [checkstyle](https://checkstyle.org/) from 10.15.0 to **10.17.0**
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.77 to **0.1.78**
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2024.03.13 to **2024.05.24**
  - [csharpier](https://csharpier.com/) from 0.28.1 to **0.28.2**
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 8.7.0 to **8.8.3**
  - [detekt](https://detekt.dev/) from 1.23.5 to **1.23.6**
  - [dotnet-format](https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-format) from 8.0.104 to **8.0.106**
  - [editorconfig-checker](https://editorconfig-checker.github.io/) from 2.7.2 to **3.0.1**
  - [git_diff](https://git-scm.com) from 2.43.0 to **2.43.4**
  - [golangci-lint](https://golangci-lint.run/) from 1.57.2 to **1.59.0**
  - [grype](https://github.com/anchore/grype) from 0.77.0 to **0.78.0**
  - [jscpd](https://github.com/kucherenko/jscpd/tree/master/packages/jscpd) from 3.5.10 to **4.0.4**
  - [kics](https://www.kics.io) from 2.0.0 to **2.0.1**
  - [kubeconform](https://github.com/yannh/kubeconform) from 0.6.4 to **0.6.6**
  - [lightning-flow-scanner](https://github.com/Lightning-Flow-Scanner) from 2.22.0 to **2.24.0**
  - [luacheck](https://luacheck.readthedocs.io) from 1.1.2 to **1.2.0**
  - [lychee](https://lychee.cli.rs) from 0.14.3 to **0.15.1**
  - [markdown-link-check](https://github.com/tcort/markdown-link-check) from 3.12.1 to **3.12.2**
  - [markdown-table-formatter](https://www.npmjs.com/package/markdown-table-formatter) from 1.5.0 to **1.6.0**
  - [markdownlint](https://github.com/DavidAnson/markdownlint) from 0.39.0 to **0.41.0**
  - [mypy](https://mypy.readthedocs.io/en/stable/) from 1.9.0 to **1.10.0**
  - [npm-groovy-lint](https://nvuillam.github.io/npm-groovy-lint/) from 14.4.1 to **14.6.0**
  - [phpcs](https://github.com/PHPCSStandards/PHP_CodeSniffer) from 3.9.1 to **3.10.1**
  - [phplint](https://github.com/overtrue/phplint) from 9.1.2 to **9.3.1**
  - [phpstan](https://phpstan.org/) from 1.10.67 to **1.11.0** to **1.11.3**
  - [pmd](https://pmd.github.io/) from 6.55.0 to **7.1.0**
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.4.1 to **7.4.2**
  - [powershell_formatter](https://github.com/PowerShell/PSScriptAnalyzer) from 7.4.1 to **7.4.2**
  - [prettier](https://prettier.io/) from 3.2.5 to **3.3.0**
  - [proselint](https://github.com/amperser/proselint) from 0.13.0 to **0.14.0**
  - [protolint](https://github.com/yoheimuta/protolint) from 0.49.6 to **0.49.7**
  - [psalm](https://psalm.dev) from Psalm.5.23.1@ to **Psalm.5.24.0@**
  - [pylint](https://pylint.readthedocs.io) from 3.1.0 to **3.2.2**
  - [pyright](https://github.com/Microsoft/pyright) from 1.1.359 to **1.1.365**
  - [roslynator](https://github.com/dotnet/Roslynator) from 0.8.6.0 to **0.8.9.0**
  - [rubocop](https://rubocop.org/) from 1.63.3 to **1.64.1**
  - [ruff](https://github.com/astral-sh/ruff) from 0.4.1 to **0.4.7**
  - [scalafix](https://scalacenter.github.io/scalafix/) from 0.12.0 to **0.12.1**
  - [secretlint](https://github.com/secretlint/secretlint) from 8.2.3 to **8.2.4**
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 3.23.0 to **3.25.0**
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 3.23.0 to **3.25.0**
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 3.23.0 to **3.25.0**
  - [snakefmt](https://github.com/snakemake/snakefmt) from 0.10.1 to **0.10.2**
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 8.10.8 to **8.12.0**
  - [sqlfluff](https://www.sqlfluff.com/) from 3.0.5 to **3.0.7**
  - [stylelint](https://stylelint.io) from 16.4.0 to **16.6.1**
  - [syft](https://github.com/anchore/syft) from 1.2.0 to **1.5.0**
  - [tekton-lint](https://github.com/IBM/tekton-lint) from 1.0.2 to **1.1.0**
  - [terraform-fmt](https://developer.hashicorp.com/terraform/cli/commands/fmt) from 1.8.1 to **1.8.4**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.57.5 to **0.58.10**
  - [tflint](https://github.com/terraform-linters/tflint) from 0.50.3 to **0.51.1**
  - [trivy-sbom](https://aquasecurity.github.io/trivy/) from 0.50.2 to **0.51.4**
  - [trivy](https://aquasecurity.github.io/trivy/) from 0.50.2 to **0.51.4**
  - [trufflehog](https://github.com/trufflesecurity/trufflehog) from 3.73.0 to **3.77.0**
  - [vale](https://vale.sh/) from 3.4.0 to **3.4.2**
  - [xmllint](https://gitlab.gnome.org/GNOME/libxml2/-/wikis/home) from 21107 to **21108**

## [v7.11.1] - 2024-04-23

- Fixes
  - Implement fallback in case git diff does not work with merge-base

- Linter versions upgrades
  - [stylelint](https://stylelint.io) from 16.3.1 to **16.4.0**

## [v7.11.0] - 2024-04-23

- Core
  - Allow to override the number of parallel cores used, with variable **PARALLEL_PROCESS_NUMBER**, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3428>
  - Upgrade base python image from 3.12.2-alpine3.19 to 3.12.3-alpine3.19
  - Upgrade PHP 8.1 to 8.3 by @llaville in <https://github.com/oxsecurity/megalinter/pull/3464>
  - Add descriptor pre / post commands, by @bdovaz in <https://github.com/oxsecurity/megalinter/pull/3468>
  - Allow merge lists with **EXTENDS**, by @bdovaz in <https://github.com/oxsecurity/megalinter/pull/3469>

- Media

- New linters
  - Add Kotlin detekt linter, by @enciyo in <https://github.com/oxsecurity/megalinter/pull/3408>

- Reporters
  - Add ruff sarif support, by @Skitionek in <https://github.com/oxsecurity/megalinter/pull/3486>

- Fixes
  - Fix listing of modified files, by @vkucera in <https://github.com/oxsecurity/megalinter/pull/3472>. Fixes <https://github.com/oxsecurity/megalinter/issues/2125>.
  - Fix conflict between prettier and yamllint about spaces, by @apeyrat in <https://github.com/oxsecurity/megalinter/pull/3426>
  - Ensure [trufflehog](https://github.com/trufflesecurity/trufflehog) does not auto-update itself,  by @wandering-tales in <https://github.com/oxsecurity/megalinter/pull/3430>
  - Salesforce linters: use sf + default Flow Scanner rules, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3435>
  - Disable JSON_ESLINT_PLUGIN_JSONC until <https://github.com/ota-meshi/eslint-plugin-jsonc/issues/328> is fixed
  - Upgrade tar in mega-linter-runner
  - secretlint: remove default `.secretlintignore` that was never used but `.gitignore` is used instead. Fixes [#3328](https://github.com/oxsecurity/megalinter/issues/3328)
  - Add jpeg, xlsx to .gitleaks.toml, by @rasa in <https://github.com/oxsecurity/megalinter/pull/3434>
  - Fix Json Schema, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3470>
  - Remove `TEMPLATES/.secretlintignore`, by @pjungermann in <https://github.com/oxsecurity/megalinter/pull/3476>

- Doc
  - Update R2DevOps logo, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3436>
  - Update [Roslynator](https://github.com/dotnet/roslynator) repo url and logo, by @TommyE123 in <https://github.com/oxsecurity/megalinter/pull/3444>
  - Fix clang-format documentation links to point to the correct version. Fixes [#3452](https://github.com/oxsecurity/megalinter/issues/3452), by @daltonv in <https://github.com/oxsecurity/megalinter/pull/3453>
  - Add copy to clipboard button in code block (documentation), by @nikkii86 in <https://github.com/oxsecurity/megalinter/pull/3491>

- Flavors
  - Add C & C++ linters in Python flavor by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3456>

- CI
  - Make SPELL_LYCHEE non blocking for internal CI jobs
  - Remove old unused automerge workflows by @echoix in <https://github.com/oxsecurity/megalinter/pull/3432>
  - Add consistent python3/python handling at build.sh, by @pjungermann in <https://github.com/oxsecurity/megalinter/pull/3475>

- Linter versions upgrades
  - [ansible-lint](https://ansible-lint.readthedocs.io/) from 24.2.0 to **24.2.2**
  - [bicep_linter](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter) from 0.25.53 to **0.26.170**
  - [black](https://black.readthedocs.io/en/stable/) from 24.2.0 to **24.4.0**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 0.86.0 to **0.86.4**
  - [checkov](https://www.checkov.io/) from 3.2.34 to **3.2.74**
  - [checkstyle](https://checkstyle.org/) from 10.14.0 to **10.15.0**
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.76 to **0.1.77**
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2024.03.05 to **2024.03.13**
  - [csharpier](https://csharpier.com/) from 0.27.3 to **0.28.1**
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 8.6.0 to **8.7.0**
  - [devskim](https://github.com/microsoft/DevSkim) from 1.0.32 to **1.0.33**
  - [dotnet-format](https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-format) from 8.0.102 to **8.0.104**
  - [eslint-plugin-jsonc](https://ota-meshi.github.io/eslint-plugin-jsonc/) from 2.13.0 to **2.15.1**
  - [golangci-lint](https://golangci-lint.run/) from 1.56.2 to **1.57.2**
  - [grype](https://github.com/anchore/grype) from 0.74.7 to **0.77.0**
  - [kics](https://www.kics.io) from 1.7.13 to **2.0.0**
  - [lightning-flow-scanner](https://github.com/Lightning-Flow-Scanner) from 2.18.0 to **2.22.0**
  - [markdown-link-check](https://github.com/tcort/markdown-link-check) from 3.11.2 to **3.12.1**
  - [npm-groovy-lint](https://nvuillam.github.io/npm-groovy-lint/) from 14.2.3 to **14.4.1**
  - [phpcs](https://github.com/PHPCSStandards/PHP_CodeSniffer) from 3.9.0 to **3.9.1**
  - [phpstan](https://phpstan.org/) from 1.10.60 to **1.10.67**
  - [protolint](https://github.com/yoheimuta/protolint) from 0.48.0 to **0.49.6**
  - [psalm](https://psalm.dev) from Psalm.5.23.0@ to **Psalm.5.23.1@**
  - [pyright](https://github.com/Microsoft/pyright) from 1.1.353 to **1.1.359**
  - [roslynator](https://github.com/dotnet/Roslynator) from 0.8.3.0 to **0.8.6.0**
  - [rstcheck](https://github.com/myint/rstcheck) from 6.2.0 to **6.2.1**
  - [rubocop](https://rubocop.org/) from 1.62.0 to **1.63.3**
  - [ruff](https://github.com/astral-sh/ruff) from 0.3.2 to **0.4.1**
  - [secretlint](https://github.com/secretlint/secretlint) from 8.1.2 to **8.2.3**
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 3.21.0 to **3.23.0**
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 3.21.0 to **3.23.0**
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 3.21.0 to **3.23.0**
  - [snakefmt](https://github.com/snakemake/snakefmt) from 0.10.0 to **0.10.1**
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 8.5.5 to **8.10.8**
  - [spectral](https://docs.stoplight.io/docs/spectral/674b27b261c3c-overview) from 6.11.0 to **6.11.1**
  - [sqlfluff](https://www.sqlfluff.com/) from 2.3.5 to **3.0.5**
  - [stylelint](https://stylelint.io) from 16.2.1 to **16.3.1**
  - [syft](https://github.com/anchore/syft) from 1.0.1 to **1.2.0**
  - [tekton-lint](https://github.com/IBM/tekton-lint) from 1.0.0 to **1.0.2**
  - [terraform-fmt](https://developer.hashicorp.com/terraform/cli/commands/fmt) from 1.7.4 to **1.8.1**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.55.13 to **0.57.5**
  - [trivy-sbom](https://aquasecurity.github.io/trivy/) from 0.49.1 to **0.50.2**
  - [trivy](https://aquasecurity.github.io/trivy/) from 0.49.1 to **0.50.2**
  - [trufflehog](https://github.com/trufflesecurity/trufflehog) from 3.69.0 to **3.73.0**
  - [vale](https://vale.sh/) from 3.2.2 to **3.4.0**

## [v7.10.0] - 2024-03-10

- Core
  - Update dotnet linters to .NET 8, by @bdovaz in <https://github.com/oxsecurity/megalinter/pull/3182>

- Media
  - [How to use MegaLinter with Jenkins](https://www.youtube.com/watch?v=KhkNf2tQ3hM), by [Darin Pope](https://www.linkedin.com/in/darinpope/) / [Cloudbees](https://www.cloudbees.com/)

- Fixes
  - Trivy: use `misconfig` instead of the deprecated `config` scanner, updating the default arguments, by @pjungermann in <https://github.com/oxsecurity/megalinter/pull/3376>
  - Update calls to sfdx-scanner to output a CSV file for Aura & LWC, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3398>
  - Kics: fixed error count in the summary table, by @TommyE123 in <https://github.com/oxsecurity/megalinter/pull/3402>
  - Fix issue with EXTENDS using private repository by sending GITHUB_TOKEN as HTTP auth header, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3404>
  - Fix SPELL_VALE_CONFIG_FILE not working (handle the override of linter CONFIG_FILE if the linter is activated only if some files are found), by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3409>

- CI
  - Enable dependabot updates for devcontainer and other Docker directories, by @echoix in <https://github.com/oxsecurity/megalinter/pull/3390>

- Doc
  - Removed obsolete warning for semgrep as the issue has been fixed, by @Jayllyz in <https://github.com/oxsecurity/megalinter/pull/3374>
  - docs: fix docs in TrivySbomLinter.py, by @pjungermann in <https://github.com/oxsecurity/megalinter/pull/3377S>

- Linter versions upgrades
  - [actionlint](https://rhysd.github.io/actionlint/) from 1.6.26 to **1.6.27**
  - [bandit](https://bandit.readthedocs.io/en/latest/) from 1.7.7 to **1.7.8**
  - [bicep_linter](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter) from 0.25.3 to **0.25.53**
  - [black](https://black.readthedocs.io/en/stable/) from 24.1.1 to **24.2.0**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 0.85.1 to **0.86.0**
  - [checkov](https://www.checkov.io/) from 3.2.20 to **3.2.21**
  - [checkstyle](https://checkstyle.org/) from 10.13.0 to **10.14.0**
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2023.12.15 to **2024.03.05**
  - [csharpier](https://csharpier.com/) from 0.27.2 to **0.27.3**
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 8.3.2 to **8.6.0**
  - [devskim](https://github.com/microsoft/DevSkim) from 1.0.28 to **1.0.32**
  - [dotnet-format](https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-format) from 7.0.115 to **8.0.102**
  - [eslint](https://eslint.org) from 8.56.0 to **8.57.0**
  - [golangci-lint](https://golangci-lint.run/) from 1.56.1 to **1.56.2**
  - [grype](https://github.com/anchore/grype) from 0.74.5 to **0.74.7**
  - [helm](https://helm.sh/docs/helm/helm_lint/) from 3.13.2 to **3.14.2**
  - [kics](https://www.kics.io) from 1.7.12 to **1.7.13**
  - [ktlint](https://ktlint.github.io) from 1.1.1 to **1.2.1**
  - [lightning-flow-scanner](https://github.com/Lightning-Flow-Scanner) from 2.16.0 to **2.18.0**
  - [mypy](https://mypy.readthedocs.io/en/stable/) from 1.8.0 to **1.9.0**
  - [npm-groovy-lint](https://nvuillam.github.io/npm-groovy-lint/) from 14.2.1 to **14.2.3**
  - [phpcs](https://github.com/PHPCSStandards/PHP_CodeSniffer) from 3.8.1 to **3.9.0**
  - [phpstan](https://phpstan.org/) from 1.10.57 to **1.10.60**
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.4.0 to **7.4.1**
  - [powershell_formatter](https://github.com/PowerShell/PSScriptAnalyzer) from 7.4.0 to **7.4.1**
  - [protolint](https://github.com/yoheimuta/protolint) from 0.47.5 to **0.48.0**
  - [psalm](https://psalm.dev) from Psalm.5.21.1@ to **Psalm.5.23.0@**
  - [pylint](https://pylint.readthedocs.io) from 3.0.3 to **3.1.0**
  - [pyright](https://github.com/Microsoft/pyright) from 1.1.350 to **1.1.353**
  - [rubocop](https://rubocop.org/) from 1.60.2 to **1.62.0**
  - [ruff](https://github.com/astral-sh/ruff) from 0.2.1 to **0.3.2**
  - [scalafix](https://scalacenter.github.io/scalafix/) from 0.11.1 to **0.12.0**
  - [secretlint](https://github.com/secretlint/secretlint) from 8.1.1 to **8.1.2**
  - [shellcheck](https://github.com/koalaman/shellcheck) from 0.9.0 to **0.10.0**
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 8.4.8 to **8.5.5**
  - [syft](https://github.com/anchore/syft) from 0.104.0 to **1.0.1**
  - [terraform-fmt](https://developer.hashicorp.com/terraform/cli/commands/fmt) from 1.7.3 to **1.7.4**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.55.1 to **0.55.13**
  - [trufflehog](https://github.com/trufflesecurity/trufflehog) from 3.67.5 to **3.69.0**
  - [vale](https://vale.sh/) from 3.0.5 to **3.2.2**
  - [xmllint](https://gitlab.gnome.org/GNOME/libxml2/-/wikis/home) from 21106 to **21107**
  - [yamllint](https://yamllint.readthedocs.io/) from 1.34.0 to **1.35.1**

## [v7.9.0] - 2024-02-11

- Core
  - Upgrade actions/checkout and stefanzweifel/git-auto-commit-action in generator template workflow, by @Jayllyz in [#3327](https://github.com/oxsecurity/megalinter/pull/3327)
  - Upgrade base python image to python:3.12.2-alpine3.19

- Fixes
  - Format powershell linter output into terminal-wide table, and count errors, by @efrecon in [#3318](https://github.com/oxsecurity/megalinter/pull/3318)
  - Allow active_only_if_file_found to work in specified subdirectory (_DIRECTORY), fixes [#2873](https://github.com/oxsecurity/megalinter/issues/2873), by @TimothyEarley in [#3323](https://github.com/oxsecurity/megalinter/pull/3323)
  - Activate CI servers reporters only if we find a related default env variable, by @nvuillam in [#3321](https://github.com/oxsecurity/megalinter/pull/3321)

- Doc
  - Update copyright year to 2024, by @Jayllyz in [#3339](https://github.com/oxsecurity/megalinter/pull/3339)

- CI
  - Free more disk space before docker build
  - Upgrade peter-evans/create-pull-request from v5 to v6 in GitHub Actions workflows

- Linter versions upgrades
  - [ansible-lint](https://ansible-lint.readthedocs.io/) from 6.22.2 to **24.2.0**
  - [bandit](https://bandit.readthedocs.io/en/latest/) from 1.7.6 to **1.7.7**
  - [bicep_linter](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter) from 0.24.24 to **0.25.3**
  - [black](https://black.readthedocs.io/en/stable/) from 23.12.1 to **24.1.1**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 0.84.0 to **0.85.1**
  - [checkov](https://www.checkov.io/) from 3.1.67 to **3.2.20**
  - [checkstyle](https://checkstyle.sourceforge.io) from 10.12.7 to **10.13.0**
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.75 to **0.1.76**
  - [csharpier](https://csharpier.com/) from 0.27.0 to **0.27.2**
  - [eslint-plugin-jsonc](https://ota-meshi.github.io/eslint-plugin-jsonc/) from 2.12.2 to **2.13.0**
  - [gitleaks](https://github.com/gitleaks/gitleaks) from 8.18.1 to **8.18.2**
  - [golangci-lint](https://golangci-lint.run/) from 1.55.2 to **1.56.1**
  - [grype](https://github.com/anchore/grype) from 0.63.1 to **0.74.5**
  - [lychee](https://lychee.cli.rs) from 0.14.1 to **0.14.3**
  - [markdownlint](https://github.com/DavidAnson/markdownlint) from 0.38.0 to **0.39.0**
  - [npm-groovy-lint](https://nvuillam.github.io/npm-groovy-lint/) from 14.2.0 to **14.2.1**
  - [phplint](https://github.com/overtrue/phplint) from 9.1.0 to **9.1.2**
  - [phpstan](https://phpstan.org/) from 1.10.56 to **1.10.57**
  - [prettier](https://prettier.io/) from 3.2.4 to **3.2.5**
  - [psalm](https://psalm.dev) from Psalm.5.20.0@ to **Psalm.5.21.1@**
  - [puppet-lint](http://puppet-lint.com/) from 4.2.3 to **4.2.4**
  - [pyright](https://github.com/Microsoft/pyright) from 1.1.347 to **1.1.350**
  - [revive](https://revive.run/) from 1.3.6 to **1.3.7**
  - [roslynator](https://github.com/JosefPihrt/Roslynator) from 0.8.2.0 to **0.8.3.0**
  - [rubocop](https://rubocop.org/) from 1.60.1 to **1.60.2**
  - [ruff](https://github.com/astral-sh/ruff) from 0.1.14 to **0.2.1**
  - [secretlint](https://github.com/secretlint/secretlint) from 8.1.0 to **8.1.1**
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 3.20.0 to **3.21.0**
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 3.20.0 to **3.21.0**
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 3.20.0 to **3.21.0**
  - [shfmt](https://github.com/mvdan/sh) from 3.7.0 to **3.8.0**
  - [snakefmt](https://github.com/snakemake/snakefmt) from 0.9.0 to **0.10.0**
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 8.2.3 to **8.4.8**
  - [stylelint](https://stylelint.io) from 16.2.0 to **16.2.1**
  - [syft](https://github.com/anchore/syft) from 0.101.1 to **0.104.0**
  - [terraform-fmt](https://developer.hashicorp.com/terraform/cli/commands/fmt) from 1.7.0 to **1.7.3**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.54.20 to **0.55.1**
  - [tflint](https://github.com/terraform-linters/tflint) from 0.50.1 to **0.50.3**
  - [trivy-sbom](https://aquasecurity.github.io/trivy/) from 0.48.3 to **0.49.1**
  - [trivy](https://aquasecurity.github.io/trivy/) from 0.48.3 to **0.49.1**
  - [trufflehog](https://github.com/trufflesecurity/trufflehog) from 3.63.10 to **3.67.5**
  - [v8r](https://github.com/chris48s/v8r) from 2.1.0 to **3.0.0**
  - [yamllint](https://yamllint.readthedocs.io/) from 1.33.0 to **1.34.0**

## [v7.8.0] - 2024-01-21

- Reporters
  - New reporter **MARKDOWN_SUMMARY_REPORTER**, allows saving MegaLinter results summary as a markdown file. This file can be further utilised to add comments on the pull request (PR) from Jenkins and other continuous integration (CI) tools by @saishivarcr in <https://github.com/oxsecurity/megalinter/pull/3250>
  - New reporter **BITBUCKET_COMMENT_REPORTER** allowing to post MegaLinter results as comments on Bitbucket pull requests  by @saishivarcr in <https://github.com/oxsecurity/megalinter/pull/3256>

- Core
  - mega-linter-runner: Remove container by default, except of `no-remove-container` option is sent by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3203>
  - Upgrade base image from python:3.11.6-alpine3.18 to python:3.11.7-alpine3.18, by @echoix in [#3212](https://github.com/oxsecurity/megalinter/pull/3212)
  - Upgrade to python 3.12.0 by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3006>
  - Upgrade actions/upload-artifact@v3 to actions/upload-artifact@v4 in default workflows by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3225>
  - mega-linter-runner: Improve check if running as script or module, by @echoix in [#3233](https://github.com/oxsecurity/megalinter/pull/3233)

- Media
  - (FR) MegaLinter presentation at [DevCon 20 / Programmez Magazine](https://www.programmez.com/page-devcon/devcon-20-100-securite-qualite-du-code), by [Nicolas Vuillamy](https://github.com/nvuillam)

<div style="text-align:center"><iframe width="560" height="315" src="https://www.youtube.com/embed/SlKurrIsUls" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>

- Fixes
  - tekton-lint is now published as @ibm/tekton-lint, by @echoix in [#3210](https://github.com/oxsecurity/megalinter/pull/3210)
  - PHP PHIVE: Use keys.openpgp.org and fingerprint for phive key verification, by @echoix in [#3230](https://github.com/oxsecurity/megalinter/pull/3230)
  - Undowngrade sass linters, by @echoix in [#3260](https://github.com/oxsecurity/megalinter/pull/3260)
  - Upgrade lychee default configuration to handle [breaking change between 0.13.0 and 0.14.0](https://github.com/lycheeverse/lychee/issues/1338)
  - Hadolint: support both `Containerfile` and `Dockerfile` by @sanmai-NL in <https://github.com/oxsecurity/megalinter/pull/3217>

- Doc
  - Upgrade url to [PHP CodeSniffer](https://github.com/PHPCSStandards/PHP_CodeSniffer), as now the original repo is not maintained anymore by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3201>

- CI
  - Use docker/metadata-action for deploy-DEV.yml workflow, by @echoix in [#3193](https://github.com/oxsecurity/megalinter/pull/3193)

- Linter versions upgrades
  - [ansible-lint](https://ansible-lint.readthedocs.io/) from 6.22.1 to **6.22.2**
  - [bash-exec](https://www.gnu.org/software/bash/) from 5.2.15 to **5.2.21**
  - [bicep_linter](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter) from 0.23.1 to **0.24.24** on 2023-12-14
  - [black](https://black.readthedocs.io/en/stable/) from 23.11.0 to **23.12.1** on 2023-12-23
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 0.83.4 to **0.84.0**
  - [checkov](https://www.checkov.io/) from 3.1.27 to **3.1.67**
  - [checkstyle](https://checkstyle.sourceforge.io) from 10.12.6 to **10.12.7**
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.74 to **0.1.75** on 2023-12-28
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2023.10.20 to **2023.12.15** on 2023-12-15
  - [csharpier](https://csharpier.com/) from 0.26.4 to **0.27.0**
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 8.1.3 to **8.3.2**
  - [devskim](https://github.com/microsoft/DevSkim) from 1.0.23 to **1.0.28**
  - [djlint](https://djlint.com/) from 1.34.0 to **1.34.1** on 2023-12-22
  - [dotnet-format](https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-format) from 7.0.114 to **7.0.115**
  - [eslint-plugin-jsonc](https://ota-meshi.github.io/eslint-plugin-jsonc/) from 2.10.0 to **2.12.2**
  - [eslint](https://eslint.org) from 8.55.0 to **8.56.0** on 2023-12-16
  - [flake8](https://flake8.pycqa.org) from 6.1.0 to **7.0.0**
  - [git_diff](https://git-scm.com) from 2.40.1 to **2.43.0**
  - [helm](https://helm.sh/docs/helm/helm_lint/) from 3.11.3 to **3.13.2**
  - [isort](https://pycqa.github.io/isort/) from 5.13.0 to **5.13.2** on 2023-12-13
  - [kics](https://www.kics.io) from 1.7.11 to **1.7.12** on 2023-12-22
  - [ktlint](https://ktlint.github.io) from 1.0.1 to **1.1.1**
  - [lychee](https://lychee.cli.rs) from 0.13.0 to **0.14.1**
  - [mypy](https://mypy.readthedocs.io/en/stable/) from 1.7.1 to **1.8.0** on 2023-12-22
  - [npm-groovy-lint](https://nvuillam.github.io/npm-groovy-lint/) from 13.0.2 to **14.2.0**
  - [phpcs](https://github.com/PHPCSStandards/PHP_CodeSniffer) from 3.8.0 to **3.8.1**
  - [phplint](https://github.com/overtrue/phplint) from 9.0.6 to **9.1.0** on 2023-12-17
  - [phpstan](https://phpstan.org/) from 1.10.48 to **1.10.56**
  - [prettier](https://prettier.io/) from 3.1.0 to **3.2.4**
  - [protolint](https://github.com/yoheimuta/protolint) from 0.46.3 to **0.47.5**
  - [psalm](https://psalm.dev) from Psalm.5.17.0@ to **Psalm.5.20.0@**
  - [pylint](https://pylint.readthedocs.io) from 3.0.2 to **3.0.3** on 2023-12-13
  - [pyright](https://github.com/Microsoft/pyright) from 1.1.339 to **1.1.347**
  - [revive](https://revive.run/) from 1.3.4 to **1.3.6**
  - [roslynator](https://github.com/JosefPihrt/Roslynator) from 0.8.1.0 to **0.8.2.0**
  - [rubocop](https://rubocop.org/) from 1.58.0 to **1.60.1**
  - [ruff](https://github.com/astral-sh/ruff) from 0.1.7 to **0.1.14** on 2023-12-13
  - [secretlint](https://github.com/secretlint/secretlint) from 8.0.0 to **8.1.0** on 2023-12-28
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 3.19.0 to **3.20.0**
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 3.19.0 to **3.20.0**
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 3.19.0 to **3.20.0**
  - [snakefmt](https://github.com/snakemake/snakefmt) from 0.8.5 to **0.9.0**
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.32.4 to **8.2.3**
  - [stylelint](https://stylelint.io) from 15.11.0 to **16.2.0**
  - [syft](https://github.com/anchore/syft) from 0.98.0 to **0.101.1** on 2023-12-22
  - [tekton-lint](https://github.com/IBM/tekton-lint) from 0.6.0 to **1.0.0**
  - [terraform-fmt](https://developer.hashicorp.com/terraform/cli/commands/fmt) from 1.6.5 to **1.7.0**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.54.0 to **0.54.20**
  - [terrascan](https://runterrascan.io/) from 1.18.3 to **1.18.8** on 2023-12-16
  - [terrascan](https://runterrascan.io/) from 1.18.8 to **1.18.11** on 2023-12-30
  - [tflint](https://github.com/terraform-linters/tflint) from 0.49.0 to **0.50.0** on 2023-12-30
  - [tflint](https://github.com/terraform-linters/tflint) from 0.50.0 to **0.50.1**
  - [trivy-sbom](https://aquasecurity.github.io/trivy/) from 0.48.0 to **0.48.1** on 2023-12-18
  - [trivy-sbom](https://aquasecurity.github.io/trivy/) from 0.48.1 to **0.48.2**
  - [trivy-sbom](https://aquasecurity.github.io/trivy/) from 0.48.2 to **0.48.3**
  - [trivy](https://aquasecurity.github.io/trivy/) from 0.48.0 to **0.48.1** on 2023-12-18
  - [trivy](https://aquasecurity.github.io/trivy/) from 0.48.1 to **0.48.2**
  - [trivy](https://aquasecurity.github.io/trivy/) from 0.48.2 to **0.48.3**
  - [trufflehog](https://github.com/trufflesecurity/trufflehog) from 3.63.2 to **3.63.3** on 2023-12-14
  - [trufflehog](https://github.com/trufflesecurity/trufflehog) from 3.63.3 to **3.63.4** on 2023-12-15
  - [trufflehog](https://github.com/trufflesecurity/trufflehog) from 3.63.4 to **3.63.6** on 2023-12-22
  - [trufflehog](https://github.com/trufflesecurity/trufflehog) from 3.63.6 to **3.63.7** on 2023-12-23
  - [trufflehog](https://github.com/trufflesecurity/trufflehog) from 3.63.7 to **3.63.9**
  - [trufflehog](https://github.com/trufflesecurity/trufflehog) from 3.63.9 to **3.63.10**
  - [vale](https://vale.sh/) from 2.30.0 to **3.0.5**

## [v7.7.0] - 2023-12-09

- Core
  - Update base java apk package to openjdk 17 by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3160>
  - Update dotnet linters to .NET 7 by @bdovaz in <https://github.com/oxsecurity/megalinter/pull/2402>

- Media
  - [Try using MegaLinter (article in japanese)](https://future-architect.github.io/articles/20231129a/?s=03) by [Takashi Minayaga](https://future-architect.github.io/authors/%E5%AE%AE%E6%B0%B8%E5%B4%87%E5%8F%B2)

- New linters
  - Add [clang-format](https://releases.llvm.org/16.0.0/tools/clang/docs/ClangFormat.html) c & cpp formatting linter including "apply fix" support
  - Add [Roslynator](https://github.com/dotnet/roslynator) C# linter by @bdovaz in <https://github.com/oxsecurity/megalinter/pull/3155>

- Fixes
  - Call jscpd with `--gitignore` to ignore copy-pastes in files matching `.gitignore`
  - cpplint: Dynamically add the list of extensions from list of files in --extensions parameter
  - Fix mkdocs generation + CI control job by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3135>
  - Add semgrep ruleset to validation schema by @wesley-dean-flexion in <https://github.com/oxsecurity/megalinter/pull/3164>
  - Downgrade stylelint to avoid crash with not v16 compliant dependencies
  - Fix count of yaml-lint errors
  - Remove openssl reinstall, as base image has updated version from alpine 3.18.5 by @echoix in <https://github.com/oxsecurity/megalinter/pull/3181>

- CI
  - Add arguments to make use of pytest-xdist, by @echoix

- Linter versions upgrades
  - [ansible-lint](https://ansible-lint.readthedocs.io/) from 6.22.0 to **6.22.1**
  - [bandit](https://bandit.readthedocs.io/en/latest/) from 1.7.5 to **1.7.6**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 0.83.3 to **0.83.4**
  - [checkov](https://www.checkov.io/) from 3.0.39 to **3.1.25**
  - [checkstyle](https://checkstyle.sourceforge.io) from 10.12.5 to **10.12.6**
  - [csharpier](https://csharpier.com/) from 0.26.2 to **0.26.4**
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 8.0.0 to **8.1.3**
  - [dotnet-format](https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-format) from 6.0.417 to **7.0.114**
  - [eslint](https://eslint.org) from 8.54.0 to **8.55.0**
  - [gitleaks](https://github.com/gitleaks/gitleaks) from 8.18.0 to **8.18.1**
  - [isort](https://pycqa.github.io/isort/) from 5.12.0 to **5.13.0**
  - [lightning-flow-scanner](https://github.com/Lightning-Flow-Scanner) from 2.15.0 to **2.16.0**
  - [luacheck](https://luacheck.readthedocs.io) from 1.1.1 to **1.1.2**
  - [markdown-table-formatter](https://www.npmjs.com/package/markdown-table-formatter) from 1.4.0 to **1.5.0**
  - [markdownlint](https://github.com/DavidAnson/markdownlint) from 0.37.0 to **0.38.0**
  - [mypy](https://mypy.readthedocs.io/en/stable/) from 1.7.0 to **1.7.1**
  - [npm-groovy-lint](https://nvuillam.github.io/npm-groovy-lint/) from 12.1.0 to **13.0.2**
  - [phpcs](https://github.com/squizlabs/PHP_CodeSniffer) from 3.7.2 to **3.8.0**
  - [phplint](https://github.com/overtrue/phplint) from 9.0.4 to **9.0.6**
  - [phpstan](https://phpstan.org/) from 1.10.42 to **1.10.48**
  - [psalm](https://psalm.dev) from Psalm.5.15.0@ to **Psalm.5.17.0@**
  - [puppet-lint](http://puppet-lint.com/) from 4.2.1 to **4.2.3**
  - [pyright](https://github.com/Microsoft/pyright) from 1.1.336 to **1.1.339**
  - [roslynator](https://github.com/JosefPihrt/Roslynator) from 0.8.0.0 to **0.8.1.0**
  - [rubocop](https://rubocop.org/) from 1.57.2 to **1.58.0**
  - [ruff](https://github.com/astral-sh/ruff) from 0.1.6 to **0.1.7**
  - [secretlint](https://github.com/secretlint/secretlint) from 7.1.0 to **8.0.0**
  - [semgrep](https://semgrep.dev/) from 1.50.0 to **1.52.0**
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 3.18.0 to **3.19.0**
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 3.18.0 to **3.19.0**
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 3.18.0 to **3.19.0**
  - [syft](https://github.com/anchore/syft) from 0.97.1 to **0.98.0**
  - [terraform-fmt](https://developer.hashicorp.com/terraform/cli/commands/fmt) from 1.6.4 to **1.6.5**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.53.4 to **0.54.0**
  - [trivy](https://aquasecurity.github.io/trivy/) from 0.47.0 to **0.48.0**
  - [trufflehog](https://github.com/trufflesecurity/trufflehog) from 3.63.0 to **3.63.2**
  - [vale](https://vale.sh/) from 2.29.7 to **2.30.0**

## [v7.6.0] - 2023-11-19

- Major enhancements
  - New flavor [**c_cpp**](https://megalinter.io/latest/flavors/c_cpp/): New flavor for pure C/C++ projects, by @daltonv in <https://github.com/oxsecurity/megalinter/pull/3067>
  - New flavor [**formatters**](https://megalinter.io/beta/flavors/formatters/): Contains only formatter linters, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3071>
  - Add [**Salesforce Lightning Flow Scanner**](https://github.com/Lightning-Flow-Scanner), by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3092>

- Core
  - Allow to use value `any` to always activate a linter who as a **_DIRECTORY** variable. Example: `KUBERNETES_DIRECTORY: any`, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3058>
  - Update base Docker image to `python:3.11.6-alpine3.18`

- Fixes
  - Fix issue Gitleaks `--no-git` does not work anymore, [#2945](https://github.com/oxsecurity/megalinter/issues/2945), in [#3112](https://github.com/oxsecurity/megalinter/pull/3112)
  - Fix way to install powershell on Alpine linux image
  - Fix issue with VS Code devcontainer not building [#3114](https://github.com/oxsecurity/megalinter/issues/3114)
  - Fix Default Workflow to handle latest ActionLint rules, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3130>
  - Write checkov SARIF report `results_sarif.sarif` in `REPORT_FOLDER`, by @gmeligio in <https://github.com/oxsecurity/megalinter/pull/3121>
  - Updated lintr config template to use `linters_with_defaults()` (formerly `with_defaults()`)
  - Fix csharp installation dependencies, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3075>
  - Fix powershell installation by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3126>

- Doc
  - Update lintr links to their current locations, by @echoix in [#3122](https://github.com/oxsecurity/megalinter/issues/3122)
  - Update Pylint links to their current locations, by @echoix in [#3116](https://github.com/oxsecurity/megalinter/issues/3116)
  - Add R2DevOps way to setup MegaLinter on Gitlab, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/3129>

- CI
  - Upgrade pymdown-extensions and markdown, by @BryanQuigley in [#3053](https://github.com/oxsecurity/megalinter/pull/3053)
  - Use docker/metadata-action for some internal CI, by @echoix in [#3110](https://github.com/oxsecurity/megalinter/pull/3110)
  - Call docker buildx prune instead of docker builder prune, by @echoix in [#3127](https://github.com/oxsecurity/megalinter/pull/3127)
  - Set schedule earlier for auto-update-linters.yml, allow manual runs, by @echoix in <https://github.com/oxsecurity/megalinter/pull/3066>
  - Add mike to dev/requirements.txt, by @echoix in <https://github.com/oxsecurity/megalinter/pull/3070>
  - Modernize dependabot.yml in correct directories, by @echoix in <https://github.com/oxsecurity/megalinter/pull/3093>
  - Fix devcontainer Dockerfile typo (fixes #3114) by @daltonv in <https://github.com/oxsecurity/megalinter/pull/3115>

- Linter versions upgrades
  - [ansible-lint](https://ansible-lint.readthedocs.io/) from 6.21.1 to **6.22.0**
  - [bicep_linter](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter) from 0.22.6 to **0.23.1**
  - [black](https://black.readthedocs.io/en/stable/) from 23.10.1 to **23.11.0**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 0.83.0 to **0.83.3**
  - [checkov](https://www.checkov.io/) from 3.0.12 to **3.0.39**
  - [checkstyle](https://checkstyle.sourceforge.io) from 10.12.4 to **10.12.5**
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.73 to **0.1.74**
  - [csharpier](https://csharpier.com/) from 0.25.0 to **0.26.2**
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 7.3.8 to **8.0.0**
  - [dotnet-format](https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-format) from 6.0.416 to **6.0.417**
  - [eslint](https://eslint.org) from 8.52.0 to **8.54.0**
  - [golangci-lint](https://golangci-lint.run/) from 1.55.1 to **1.55.2**
  - [kics](https://www.kics.io) from 1.7.10 to **1.7.11**
  - [kubeconform](https://github.com/yannh/kubeconform) from 0.6.3 to **0.6.4**
  - [mypy](https://mypy.readthedocs.io/en/stable/) from 1.6.1 to **1.7.0**
  - [npm-groovy-lint](https://nvuillam.github.io/npm-groovy-lint/) from 11.1.1 to **12.1.0**
  - [npm-package-json-lint](https://npmpackagejsonlint.org/) from 7.0.0 to **7.1.0**
  - [phpstan](https://phpstan.org/) from 1.10.39 to **1.10.42**
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.3.9 to **7.4.0**
  - [powershell_formatter](https://github.com/PowerShell/PSScriptAnalyzer) from 7.3.9 to **7.4.0**
  - [prettier](https://prettier.io/) from 3.0.3 to **3.1.0**
  - [protolint](https://github.com/yoheimuta/protolint) from 0.46.2 to **0.46.3**
  - [pyright](https://github.com/Microsoft/pyright) from 1.1.333 to **1.1.336**
  - [ruff](https://github.com/astral-sh/ruff) from 0.1.3 to **0.1.6**
  - [secretlint](https://github.com/secretlint/secretlint) from 7.0.7 to **7.1.0**
  - [semgrep](https://semgrep.dev/) from 1.46.0 to **1.50.0**
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 3.17.0 to **3.18.0**
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 3.17.0 to **3.18.0**
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 3.17.0 to **3.18.0**
  - [swiftlint](https://github.com/realm/SwiftLint) from 0.53.0 to **0.54.0**
  - [syft](https://github.com/anchore/syft) from 0.94.0 to **0.97.1**
  - [terraform-fmt](https://developer.hashicorp.com/terraform/cli/commands/fmt) from 1.6.2 to **1.6.4**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.53.0 to **0.53.4**
  - [tflint](https://github.com/terraform-linters/tflint) from 0.48.0 to **0.49.0**
  - [trivy-sbom](https://aquasecurity.github.io/trivy/) from 0.46.1 to **0.47.0**
  - [trivy](https://aquasecurity.github.io/trivy/) from 0.46.1 to **0.47.0**
  - [trufflehog](https://github.com/trufflesecurity/trufflehog) from 3.61.0 to **3.63.0**
  - [vale](https://vale.sh/) from 2.29.5 to **2.29.7**
  - [xmllint](https://gitlab.gnome.org/GNOME/libxml2/-/wikis/home) from 21104 to **21106**
  - [yamllint](https://yamllint.readthedocs.io/) from 1.32.0 to **1.33.0**

## [v7.5.0] - 2023-10-29

- Core
  - mega-linter-runner: Convert to ES6 and upgrade npm dependencies. Node 18 minimum version is now required.
  - Allow to define `COMPILER_ONLY` virtual package as cargo dependency in descriptors to embed rust compiler in the Dockerfile
  - Optimize `@generated` marker scanning ([#2654](https://github.com/oxsecurity/megalinter/pull/2654))
  - Upgrade to python 3.12.0

- Media
  - [Achieve Code Consistency: MegaLinter Integration in Azure DevOps](https://techcommunity.microsoft.com/t5/azure-devops-blog/achieve-code-consistency-megalinter-integration-in-azure-devops/ba-p/3939448), by [Don Koning](https://techcommunity.microsoft.com/t5/user/viewprofilepage/user-id/2039143#profile) on [Microsoft Tech Community](https://techcommunity.microsoft.com/)

- Fixes
  - build.py: Remove exclusivity between pip, gem & cargo packages
  - Salesforce linters: Switch sfdx-cli to @salesforce/cli
  - Fixed issue with `actionlint` throwing an error on `if` statements in the generated workflow file
  - Added default `.devskim.json` to mitigate errors introduced when no config exists

- Doc
  - Display list of articles from newest to oldest
  - Fix incorrect environment variable in djlint docs
  - Improve lychee documentation to add an example of `.lycheeignore`

- CI
  - Add the other maintainers globally to the CODEOWNERS file ([#3008](https://github.com/oxsecurity/megalinter/pull/3008))
  - Free disk space earlier in the process to avoid failure during docker build
  - Set flavors-stats.json as a generated file in .gitattributes ([#3023](https://github.com/oxsecurity/megalinter/pull/3023))
  - Update and fix our ChatOps automations to only run on pull request comments, by @echoix in [#3034](https://github.com/oxsecurity/megalinter/pull/3034)
  - Use App::cpm to install perlcritic faster, and clean `.perl-cpm` cache, by @echoix in [#3036](https://github.com/oxsecurity/megalinter/pull/3036)
  - Add failure message in ChatOps build-command and Slash dispatcher, by @echoix in [#3037](https://github.com/oxsecurity/megalinter/pull/3037)

- Linter versions upgrades
  - [ansible-lint](https://ansible-lint.readthedocs.io/) from 6.20.0 **6.21.1**
  - [bicep_linter](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter) from 0.21.1 to **0.22.6**
  - [black](https://black.readthedocs.io/en/stable/) from 23.9.1 to **23.10.1**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 0.80.2 to **0.83.0**
  - [checkov](https://www.checkov.io/) from 2.4.48 to **3.0.12**
  - [checkstyle](https://checkstyle.sourceforge.io) from 10.12.3 to **10.12.4**
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.72 to **0.1.73**
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2023.09.07 to **2023.10.20**
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 7.3.6 to **7.3.8**
  - [devskim](https://github.com/microsoft/DevSkim) from 1.0.22 to **1.0.23**
  - [dotnet-format](https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-format) from 6.0.414 to **6.0.416**
  - [editorconfig-checker](https://editorconfig-checker.github.io/) from 2.7.1 to **2.7.2**
  - [eslint-plugin-jsonc](https://ota-meshi.github.io/eslint-plugin-jsonc/) from 2.9.0 to **2.10.0**
  - [eslint](https://eslint.org) from 8.49.0 to **8.52.0**
  - [golangci-lint](https://golangci-lint.run/) from 1.54.2 to **1.55.1**
  - [kics](https://www.kics.io) from 1.7.8 to **1.7.10**
  - [ktlint](https://ktlint.github.io) from 1.0.0 to **1.0.1**
  - [mypy](https://mypy.readthedocs.io/en/stable/) from 1.5.1 to **1.6.1**
  - [perlcritic](https://metacpan.org/pod/Perl::Critic) from 1.150 to **1.152**
  - [phpstan](https://phpstan.org/) from 1.10.35 to **1.10.39**
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.3.7 to **7.3.9**
  - [powershell_formatter](https://github.com/PowerShell/PSScriptAnalyzer) from 7.3.7 to **7.3.9**
  - [protolint](https://github.com/yoheimuta/protolint) from 0.46.0 to **0.46.2**
  - [puppet-lint](http://puppet-lint.com/) from 4.2.0 to **4.2.1**
  - [pylint](https://pylint.pycqa.org) from 2.17.5 to **3.0.2**
  - [pyright](https://github.com/Microsoft/pyright) from 1.1.327 to **1.1.333**
  - [rubocop](https://rubocop.org/) from 1.56.3 to **1.57.2**
  - [ruff](https://github.com/astral-sh/ruff) from 0.1.2 to **0.1.3**
  - [ruff](https://github.com/charliermarsh/ruff) from 0.0.290 to **0.1.2**
  - [semgrep](https://semgrep.dev/) from 1.41.0 to **1.46.0**
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 3.16.0 to **3.17.0**
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 3.16.0 to **3.17.0**
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 3.16.0 to **3.17.0**
  - [snakefmt](https://github.com/snakemake/snakefmt) from 0.8.4 to **0.8.5**
  - [sqlfluff](https://www.sqlfluff.com/) from 2.3.2 to **2.3.5**
  - [stylelint](https://stylelint.io) from 15.10.3 to **15.11.0**
  - [swiftlint](https://github.com/realm/SwiftLint) from 0.52.4 to **0.53.0**
  - [syft](https://github.com/anchore/syft) from 0.91.0 to **0.94.0**
  - [terraform-fmt](https://developer.hashicorp.com/terraform/cli/commands/fmt) from 1.5.7 to **1.6.2**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.51.4 to **0.53.0**
  - [trivy-sbom](https://aquasecurity.github.io/trivy/) from 0.45.1 to **0.46.1**
  - [trivy](https://aquasecurity.github.io/trivy/) from 0.45.1 to **0.46.1**
  - [trufflehog](https://github.com/trufflesecurity/trufflehog) from 3.56.1 to **3.61.0**
  - [v8r](https://github.com/chris48s/v8r) from 2.0.0 to **2.1.0**
  - [vale](https://vale.sh/) from 2.29.0 to **2.29.5**

## [v7.4.0] - 2023-09-22

- Core
  - Upgrade python to 3.11.5

- Media
  - [Maximize your code consistency with Megalinter](https://codewithme.cloud/posts/2023/08/maximize-your-code-consistency-with-megalinter/) by [Tor Ivar Asbølmo](https://www.linkedin.com/in/torivara/) on [codewithme.cloud](https://codewithme.cloud)
  - [MegaLinter in Azure DevOps](https://jamescook.dev/megalinter-in-azure-devops) by [James Cook](https://www.linkedin.com/in/cookjames/)

- Fixes
  - Fix [IGNORE_GITIGNORED_FILES not working anymore](https://github.com/oxsecurity/megalinter/issues/2955) , by @iisisrael
  - Fix [v7 issue when using MEGALINTER_FILES_TO_LINT](https://github.com/oxsecurity/megalinter/issues/2744) ( thanks @pfiaux !)
  - Fix [Ignore symlink files when VALIDATE_ALL_CODEBASE is false](https://github.com/oxsecurity/megalinter/issues/2944)
  - Fix rstcheck options & install

- Doc
  - Secretlint logo - reduce size to 150 and remove background
  - Replace `https://megalinter.io/flavors` with `https://megalinter.io/latest/flavors` to avoid lychee 404 error

- CI
  - Workflow job name changed from `build` to `megalinter` to prevent conflicts with other workflows
  - Add support for master branch in TEMPLATES/mega-linter.yml, by @rasa

- Deprecations
  - Deprecate SCSS LINT as not maintained anymore (<https://github.com/sds/scss-lint#notice-consider-other-tools-before-adopting-scss-lint>)

- Linter versions upgrades
  - [actionlint](https://rhysd.github.io/actionlint/) from 1.6.25 to **1.6.26**
  - [ansible-lint](https://ansible-lint.readthedocs.io/) from 6.17.2 to **6.20.0**
  - [bicep_linter](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter) from 0.20.4 to **0.21.1**
  - [black](https://black.readthedocs.io/en/stable/) from 23.7.0 to **23.9.1**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 0.79.6 to **0.80.2**
  - [checkov](https://www.checkov.io/) from 2.3.360 to **2.4.10**
  - [checkstyle](https://checkstyle.sourceforge.io) from 10.12.2 to **10.12.3**
  - [chktex](https://www.nongnu.org/chktex) from 1.7.6 to **1.7.8**
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.71 to **0.1.72**
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2023.07.13 to **2023.09.07**
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 6.31.3 to **7.3.6**
  - [devskim](https://github.com/microsoft/DevSkim) from 1.0.18 to **1.0.22**
  - [djlint](https://djlint.com/) from 1.32.1 to **1.34.0**
  - [dotnet-format](https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-format) from 6.0.413 to **6.0.414**
  - [editorconfig-checker](https://editorconfig-checker.github.io/) from 2.7.0 to **2.7.1**
  - [eslint](https://eslint.org) from 8.46.0 to **8.49.0**
  - [git_diff](https://git-scm.com) from 2.38.5 to **2.40.1**
  - [gitleaks](https://github.com/gitleaks/gitleaks) from 8.17.0 to **8.18.0**
  - [golangci-lint](https://golangci-lint.run/) from 1.54.0 to **1.54.2**
  - [helm](https://helm.sh/docs/helm/helm_lint/) from 3.10.2 to **3.11.3**
  - [jscpd](https://github.com/kucherenko/jscpd/tree/master/packages/jscpd) from 3.5.9 to **3.5.10**
  - [kics](https://www.kics.io) from 1.7.5 to **1.7.8**
  - [ktlint](https://ktlint.github.io) from 0.50.0 to **1.0.0**
  - [kubescape](https://github.com/kubescape/kubescape) from 2.3.6 to **2.9.0**
  - [markdownlint](https://github.com/DavidAnson/markdownlint) from 0.35.0 to **0.36.0**
  - [mypy](https://mypy.readthedocs.io/en/stable/) from 1.4.1 to **1.5.1**
  - [phpstan](https://phpstan.org/) from 1.10.28 to **1.10.35**
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.3.6 to **7.3.7**
  - [powershell_formatter](https://github.com/PowerShell/PSScriptAnalyzer) from 7.3.6 to **7.3.7**
  - [prettier](https://prettier.io/) from 3.0.1 to **3.0.3**
  - [protolint](https://github.com/yoheimuta/protolint) from 0.45.0 to **0.46.0**
  - [psalm](https://psalm.dev) from Psalm.5.14.1@ to **Psalm.5.15.0@**
  - [puppet-lint](http://puppet-lint.com/) from 4.0.1 to **4.2.0**
  - [pyright](https://github.com/Microsoft/pyright) from 1.1.321 to **1.1.327**
  - [revive](https://revive.run/) from 1.3.2 to **1.3.4**
  - [rstcheck](https://github.com/myint/rstcheck) from 6.1.2 to **6.2.0**
  - [rstfmt](https://github.com/dzhu/rstfmt) from 0.0.13 to **0.0.14**
  - [rubocop](https://rubocop.org/) from 1.56.0 to **1.56.3**
  - [ruff](https://github.com/charliermarsh/ruff) from 0.0.284 to **0.0.290**
  - [scalafix](https://scalacenter.github.io/scalafix/) from 0.11.0 to **0.11.1**
  - [semgrep](https://semgrep.dev/) from 1.34.1 to **1.41.0**
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 3.15.0 to **3.16.0**
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 3.15.0 to **3.16.0**
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 3.15.0 to **3.16.0**
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.32.3 to **7.32.4**
  - [spectral](https://meta.stoplight.io/docs/spectral/README.md) from 6.10.1 to **6.11.0**
  - [sqlfluff](https://www.sqlfluff.com/) from 2.2.1 to **2.3.2**
  - [stylelint](https://stylelint.io) from 15.10.2 to **15.10.3**
  - [syft](https://github.com/anchore/syft) from 0.86.1 to **0.91.0**
  - [terraform-fmt](https://developer.hashicorp.com/terraform/cli/commands/fmt) from 1.5.4 to **1.5.7**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.48.6 to **0.51.3**
  - [terrascan](https://runterrascan.io/) from 1.18.2 to **1.18.3**
  - [tflint](https://github.com/terraform-linters/tflint) from 0.47.0 to **0.48.0**
  - [trivy-sbom](https://aquasecurity.github.io/trivy/) from 0.44.0 to **0.45.1**
  - [trivy](https://aquasecurity.github.io/trivy/) from 0.44.0 to **0.45.1**
  - [trufflehog](https://github.com/trufflesecurity/trufflehog) from 3.47.0 to **3.56.1**
  - [vale](https://vale.sh/) from 2.28.1 to **2.29.0**
  - [xmllint](https://gitlab.gnome.org/GNOME/libxml2/-/wikis/home) from 21004 to **21104**

## [v7.3.0] - 2023-08-10

- Features
  - Allow to define linter_key**_COMMAND_REMOVE_ARGUMENTS** to remove a command line argument internally added by MegaLinter

- Fixes
  - Replace `https://megalinter.io/config-file` by `https://megalinter.io/latest/config-file` to avoid lychee 404 detection
  - Improve docs for posting comments to PRs in GitHub Enterprise

- [CodeTotal](https://codetotal.io)
  - Redis reporter: Return URL of linter icons when available, in property `iconPngUrl`
  - Allow to run CodeTotal with a single command `npx mega-linter-runner@latest --codetotal` , that opens CodeTotal in Web Browser once started

- Linter versions upgrades
  - [bicep_linter](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter) from 0.19.5 to **0.20.4**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 0.79.2 to **0.79.6**
  - [checkov](https://www.checkov.io/) from 2.3.343 to **2.3.360**
  - [checkstyle](https://checkstyle.sourceforge.io) from 10.12.1 to **10.12.2**
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 6.31.2 to **6.31.3**
  - [devskim](https://github.com/microsoft/DevSkim) from 1.0.1 to **1.0.18**
  - [dotnet-format](https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-format) from 6.0.412 to **6.0.413**
  - [eslint](https://eslint.org) from 8.45.0 to **8.46.0**
  - [flake8](https://flake8.pycqa.org) from 6.0.0 to **6.1.0**
  - [golangci-lint](https://golangci-lint.run/) from 1.53.3 to **1.54.0**
  - [kics](https://www.kics.io) from 1.7.4 to **1.7.5**
  - [phpstan](https://phpstan.org/) from 1.10.26 to **1.10.28**
  - [prettier](https://prettier.io/) from 3.0.0 to **3.0.1**
  - [psalm](https://psalm.dev) from Psalm.5.13.1@ to **Psalm.5.14.1@**
  - [puppet-lint](http://puppet-lint.com/) from 4.0.0 to **4.0.1**
  - [pyright](https://github.com/Microsoft/pyright) from 1.1.318 to **1.1.321**
  - [rubocop](https://rubocop.org/) from 1.55.0 to **1.56.0**
  - [ruff](https://github.com/charliermarsh/ruff) from 0.0.280 to **0.0.284**
  - [secretlint](https://github.com/secretlint/secretlint) from 7.0.3 to **7.0.7**
  - [semgrep](https://semgrep.dev/) from 1.33.2 to **1.34.1**
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 3.14.0 to **3.15.0**
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 3.14.0 to **3.15.0**
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 3.14.0 to **3.15.0**
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.31.0 to **7.32.3**
  - [spectral](https://meta.stoplight.io/docs/spectral/README.md) from 6.10.0 to **6.10.1**
  - [sqlfluff](https://www.sqlfluff.com/) from 2.1.4 to **2.2.1**
  - [syft](https://github.com/anchore/syft) from 0.85.0 to **0.86.1**
  - [terraform-fmt](https://developer.hashicorp.com/terraform/cli/commands/fmt) from 1.5.3 to **1.5.4**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.48.4 to **0.48.6**
  - [terrascan](https://runterrascan.io/) from 1.18.1 to **1.18.2**
  - [trivy-sbom](https://aquasecurity.github.io/trivy/) from 0.43.1 to **0.44.0**
  - [trivy](https://aquasecurity.github.io/trivy/) from 0.43.1 to **0.44.0**
  - [trufflehog](https://github.com/trufflesecurity/trufflehog) from 3.45.1 to **3.47.0**

## [v7.2.1] - 2023-07-26

- Fixes
  - Fix TAP reporter (3 real dots instead if 3 dots character)
  - Call trufflehog with `--only-verified` to avoid false positives in .git/config

- Linter versions upgrades
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 0.78.2 to **0.79.2**
  - [checkov](https://www.checkov.io/) from 2.3.340 to **2.3.343**
  - [pylint](https://pylint.pycqa.org) from 2.17.4 to **2.17.5**
  - [rubocop](https://rubocop.org/) from 1.54.2 to **1.55.0**
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.30.2 to **7.31.0**
  - [spectral](https://meta.stoplight.io/docs/spectral/README.md) from 6.8.0 to **6.10.0**
  - [sqlfluff](https://www.sqlfluff.com/) from 2.1.3 to **2.1.4**
  - [trufflehog](https://github.com/trufflesecurity/trufflehog) from 3.44.0 to **3.45.1**

## [v7.2.0] - 2023-07-25

- New linters
  - Add [Lychee](https://github.com/lycheeverse/lychee) - links and email addresses checker, by @DariuszPorowski in [#2673](https://github.com/oxsecurity/megalinter/pull/2673)
  - Add [grype](https://github.com/anchore/grype) security linter
  - Add [trufflehog](https://github.com/trufflesecurity/trufflehog) security linter

- New flavor **dotnetweb**: dotnet flavor linters + Javascript & Typescript linters

- Media
  - [8 Tools to Scan Node.js Applications for Security Vulnerability](https://geekflare.com/nodejs-security-scanner/), by [Chandan Kumar](https://www.linkedin.com/in/chandank){target=_blank} on [GeekFlare.com](https://geekflare.com/)
  - [Shift Left Just Become Easier (Black Hat Arsenal Session)](https://www.blackhat.com/us-23/arsenal/schedule/index.html#codetotal-shift-left-just-became-easier-33596)

- Core
  - MegaLinter Server for [CodeTotal](https://www.blackhat.com/us-23/arsenal/schedule/index.html#codetotal-shift-left-just-became-easier-33596)
  - Improvements to Gitpod workspace and addition of Makefile for automation, by @ThomasSanson in <https://github.com/oxsecurity/megalinter/pull/2737>

- Fixes
  - Handle reporter crashes without making all ML crash
  - Devskim: Remove default --ignore-globs argument
  - mypy: Use /tmp as cache folder by default with ENV MYPY_CACHE_DIR=/tmp in Dockerfile
  - Fix `hadolint` to use its default configuration file properly, by @KihyeokK in <https://github.com/oxsecurity/megalinter/pull/2763>
  - Remove linters not in flavor before calling reporters
  - Undowngrade devskim, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/2748>
  - Add ts-standard linter for ts standard, by @janderssonse in <https://github.com/oxsecurity/megalinter/pull/2746>
  - Remove additional `--update` for apk in Dockerfile by @PeterDaveHello in <https://github.com/oxsecurity/megalinter/pull/2619>
  - Fix V8R config arg usage (#2756), by @bdovaz in <https://github.com/oxsecurity/megalinter/pull/2819>

- Reporters
  - New Redis reporter (beta)

- CI
  - Clean docker build cache to avoid no space left on device during Build Dev job

- Linter versions upgrades
  - [actionlint](https://rhysd.github.io/actionlint/) from 1.6.24 to **1.6.25**
  - [ansible-lint](https://ansible-lint.readthedocs.io/) from 6.16.2 to **6.17.2**
  - [bicep_linter](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter) from 0.17.1 to **0.19.5**
  - [black](https://black.readthedocs.io/en/stable/) from 23.3.0 to **23.7.0**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 0.77.10 to **0.78.2**
  - [checkov](https://www.checkov.io/) from 2.3.285 to **2.3.340**
  - [checkstyle](https://checkstyle.sourceforge.io) from 10.12.0 to **10.12.1**
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.70 to **0.1.71**
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2023.05.26 to **2023.07.13**
  - [csharpier](https://csharpier.com/) from 0.24.2 to **0.25.0**
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 6.31.1 to **6.31.2**
  - [devskim](https://github.com/microsoft/DevSkim) from 0.7.104 to **1.0.11**
  - [djlint](https://djlint.com/) from 1.30.2 to **1.32.1**
  - [dotnet-format](https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-format) from 6.0.408 to **6.0.412**
  - [eslint-plugin-jsonc](https://ota-meshi.github.io/eslint-plugin-jsonc/) from 2.8.0 to **2.9.0**
  - [eslint](https://eslint.org) from 8.42.0 to **8.45.0**
  - [gitleaks](https://github.com/gitleaks/gitleaks) from 8.16.4 to **8.17.0**
  - [golangci-lint](https://golangci-lint.run/) from 1.53.2 to **1.53.3**
  - [grype](https://github.com/anchore/grype) from 0.63.1 to **0.63.1**
  - [kics](https://www.kics.io) from 1.7.1 to **1.7.4**
  - [ktlint](https://ktlint.github.io) from 0.49.1 to **0.50.0**
  - [kubeconform](https://github.com/yannh/kubeconform) from 0.6.2 to **2.3.6**
  - [markdownlint](https://github.com/DavidAnson/markdownlint) from 0.34.0 to **0.37.0**
  - [mypy](https://mypy.readthedocs.io/en/stable/) from 1.3.0 to **1.4.1**
  - [npm-package-json-lint](https://npmpackagejsonlint.org/) from 6.4.0 to **7.0.0**
  - [phpstan](https://phpstan.org/) from 1.10.18 to **1.10.26**
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.3.4 to **7.3.6**
  - [powershell_formatter](https://github.com/PowerShell/PSScriptAnalyzer) from 7.3.4 to **7.3.6**
  - [prettier](https://prettier.io/) from 2.8.8 to **3.0.0**
  - [protolint](https://github.com/yoheimuta/protolint) from 0.44.0 to **0.45.0**
  - [psalm](https://psalm.dev) from Psalm.5.12.0@ to **Psalm.5.13.1@**
  - [pyright](https://github.com/Microsoft/pyright) from 1.1.313 to **1.1.318**
  - [rubocop](https://rubocop.org/) from 1.52.0 to **1.54.2**
  - [ruff](https://github.com/charliermarsh/ruff) from 0.0.272 to **0.0.280**
  - [secretlint](https://github.com/secretlint/secretlint) from 6.2.3 to **7.0.3**
  - [semgrep](https://semgrep.dev/) from 1.26.0 to **1.33.2**
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 3.13.0 to **3.14.0**
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 3.13.0 to **3.14.0**
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 3.13.0 to **3.14.0**
  - [shfmt](https://github.com/mvdan/sh) from 3.6.0 to **3.7.0**
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.26.0 to **7.30.2**
  - [sqlfluff](https://www.sqlfluff.com/) from 2.1.1 to **2.1.3**
  - [stylelint](https://stylelint.io) from 15.10.0 to **15.10.0**
  - [swiftlint](https://github.com/realm/SwiftLint) from 0.52.2 to **0.52.4**
  - [syft](https://github.com/anchore/syft) from 0.83.0 to **0.85.0**
  - [terraform-fmt](https://developer.hashicorp.com/terraform/cli/commands/fmt) from 1.4.6 to **1.5.3**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.46.3 to **0.51.4**
  - [tflint](https://github.com/terraform-linters/tflint) from 0.46.1 to **0.47.0**
  - [trivy](https://aquasecurity.github.io/trivy/) from 0.42.1 to **0.43.1**
  - [vale](https://vale.sh/) from 2.27.0 to **2.28.1**

## [v7.1.0] - 2023-06-11

- Core
  - Upgrade base image to **python:3.11.4-alpine3.17**, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/2738>

- Linter enhancements & fixes
  - cljstyle: Remove default value for configuration file name, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/2717>
  - golangci-lint : Add autofix capability using **--fix** argument, by @seaneagan in <https://github.com/oxsecurity/megalinter/pull/2700>

- Linter versions upgrades
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 0.77.5 to **0.77.7**
  - [checkov](https://www.checkov.io/) from 2.3.267 to **2.3.285**
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.69 to **0.1.70**
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2023.05.18 to **2023.05.26**
  - [djlint](https://djlint.com/) from 1.30.0 to **1.30.2**
  - [eslint](https://eslint.org) from 8.41.0 to **8.42.0**
  - [gitleaks](https://github.com/gitleaks/gitleaks) from 8.16.3 to **8.16.4**
  - [golangci-lint](https://golangci-lint.run/) from 1.52.2 to **1.53.2**
  - [kubeconform](https://github.com/yannh/kubeconform) from 0.6.1 to **0.6.2**
  - [kubescape](https://github.com/kubescape/kubescape) from 2.3.4 to **2.3.5**
  - [luacheck](https://luacheck.readthedocs.io) from 1.1.0 to **1.1.1**
  - [markdownlint](https://github.com/DavidAnson/markdownlint) from 0.33.0 to **0.34.0**
  - [phpstan](https://phpstan.org/) from 1.10.15 to **1.10.18**
  - [pyright](https://github.com/Microsoft/pyright) from 1.1.311 to **1.1.313**
  - [rubocop](https://rubocop.org/) from 1.51.0 to **1.52.0**
  - [ruff](https://github.com/charliermarsh/ruff) from 0.0.270 to **0.0.272**
  - [scalafix](https://scalacenter.github.io/scalafix/) from 0.10.4 to **0.11.0**
  - [semgrep](https://semgrep.dev/) from 1.24.0 to **1.26.0**
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 3.12.0 to **3.13.0**
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 3.12.0 to **3.13.0**
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 3.12.0 to **3.13.0**
  - [stylelint](https://stylelint.io) from 15.6.2 to **15.7.0**
  - [syft](https://github.com/anchore/syft) from 0.82.0 to **0.83.0**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.45.17 to **0.46.3**
  - [trivy](https://aquasecurity.github.io/trivy/) from 0.41.0 to **0.42.1**

## [v7.0.4] - 2023-05-31

- Core
  - Allow to define `linterkey_UNSECURED_ENV_VARIABLES` for specific linters to make them visible when necessary (ex: GITHUB_TOKEN for TERRAFORM_TFLINT)

- Documentation
  - Add note to terraform_tflint about TERRAFORM_TFLINT_UNSECURED_ENV_VARIABLES by @ruzickap in <https://github.com/oxsecurity/megalinter/pull/2706>

- Linter versions upgrades
  - [checkov](https://www.checkov.io/) from 2.3.261 to **2.3.267**
  - [djlint](https://djlint.com/) from 1.29.0 to **1.30.0**
  - [pyright](https://github.com/Microsoft/pyright) from 1.1.310 to **1.1.311**
  - [semgrep](https://semgrep.dev/) from 1.23.0 to **1.24.0**
  - [standard](https://standardjs.com/) from 17.0.0 to **17.1.0**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.45.16 to **0.45.17**

## [v7.0.3] - 2023-05-29

- Linter enhancements & fixes
  - New variable **TERRAFORM_TFLINT_SECURED_ENV** with default value `true`. Set to `false` to allow `tflint --init` to access your env vars.

- Core
  - Secure PRE_COMMANDS and POST_COMMANDS by default
  - Can be disabled with **secured_env: false** in the command definition
  - Manage v6 retrocompatibility with FILTER_REGEX_INCLUDE and FILTER_REGEX_EXCLUDE expression

- Linter versions upgrades
  - [checkstyle](https://checkstyle.sourceforge.io) from 10.11.0 to **10.12.0**
  - [kubescape](https://github.com/kubescape/kubescape) from 2.3.3 to **2.3.4**
  - [checkov](https://www.checkov.io/) from 2.3.259 to **2.3.261**

## [v7.0.2] - 2023-05-27

- Quick Fix mega-linter-runner --upgrade (Warning: bug with npm, not publish yet in mega-linter-runner)
  - Dead link to configuration.md
  - Regex issue with megalinter-reports

## [v7.0.0] - 2023-05-27

To upgrade to MegaLinter v7, run `npx mega-linter-runner@latest --upgrade` , comment [here](https://github.com/oxsecurity/megalinter/issues/2692) if you have any issue :)

- MAJOR Updates
  - [SECURED_ENV_VARIABLES](https://megalinter.io/latest/config-variables-security/) & core scoped configuration by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/2601>
    - New configuration variables **SECURED_ENV_VARIABLES** and SECURED_ENV_VARIABLES_DEFAULT to hide your environment sensitive variables to the linters called by MegaLinter
    - Read [documentation](https://megalinter.io/latest/config-variables-security/) to enhance security using MegaLinter
  - Use **relative file paths** to call linters by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/1877>
    - This can be a breaking change for customizations, post an issue if you see a problem !

- New linters
  - Add linter [cljstyle](https://github.com/greglook/cljstyle), Clojure formatter, by @practicalli-john in <https://github.com/oxsecurity/megalinter/pull/2115>
  - Add [kubescape](https://github.com/kubescape/kubescape), kubernetes linter, by @muandane in <https://github.com/oxsecurity/megalinter/pull/2531>
  - Add [Vale](https://vale.sh/), a powerful enforcer of writing style, by @wesley-dean-flexion in <https://github.com/oxsecurity/megalinter/pull/2406>

- Removed linters
  - KUBERNETES_KUBEVAL: Not maintained anymore (kubeconform recommended by the authors)
  - REPOSITORY_GOODCHECK: Not open-source anymore
  - SPELL_MISSPELL: Not maintained anymore (last commit in 2018)
  - TERRAFORM_CHECKOV: Replaced by REPOSITORY_CHECKOV
  - TERRAFORM_KICS: Replaced by REPOSITORY_KICS

- Media
  - Article: [Use the Workflows JSON schema in your IDE](https://cloud.google.com/workflows/docs/use-workflows-json-schema-with-ide), by [Google Cloud](https://cloud.google.com/)
  - Video: [Ortelius Architecture Meeting](https://www.youtube.com/watch?v=oegOSmVegiQ&t=1510s), with a review of MegaLinter, by [Steve Taylor](https://github.com/sbtaylor15) from [Ortelius](https://ortelius.io/)
  - Web site: [my-devops-lab.com](https://www.my-devops-lab.com/tools)

- Linter enhancements & fixes
  - [cspell](https://megalinter.io/latest/descriptors/spell_cspell/)
    - Fix corrective .cspell.json file generated from cspell output by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/2562>
  - [eslint](https://megalinter.io/latest/descriptors/javascript_eslint/)
    - Ensure ESLint actually runs in project mode (#1572) by @Kurt-von-Laven in <https://github.com/oxsecurity/megalinter/pull/2455>
  - [jscpd](https://megalinter.io/latest/descriptors/copypaste_jscpd/)
    - Prevent jscpd to create output folder if the repo is not writable by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/2556>
  - [Gitleaks](https://megalinter.io/latest/descriptors/repository_gitleaks/)
    - Add support to scan PR commits only on PRs when `VALIDATE_ALL_CODEBASE` is set to `false`, by @DariuszPorowski [#2504](https://github.com/oxsecurity/megalinter/pull/2504)
  - [KICS](https://megalinter.io/latest/descriptors/repository_kics/)
    - Move KICS to REPOSITORY descriptor, so it can analyze all types of files, not terraform only,  by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/2689>
    - KICS can now output SARIF
    - The new version can have performance issues: customize of disable REPOSITORY_KICS if necessary
  - [KubeConform](https://megalinter.io/latest/descriptors/kubernetes_kubeconform/)
    - Simplify kubeconform install & get version by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/2629>
  - [PHPLint](https://megalinter.io/latest/descriptors/php_phplint/)
    - Upgrade PHPLint to v9 by @bdovaz in <https://github.com/oxsecurity/megalinter/pull/2638>
  - [sqlfluff](https://megalinter.io/latest/descriptors/sql_sqlfluff/)
    - Remove old options from SQLFluff config file by @tunetheweb in <https://github.com/oxsecurity/megalinter/pull/2560>
  - [v8r](https://megalinter.io/latest/descriptors/json_v8r/)
    - Allow use of configuration files with v8r by @bdovaz in <https://github.com/oxsecurity/megalinter/pull/1982>

- Core
  - Upgrade base Docker image to python:3.11.3-alpine3.17 by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/2537>
  - Allow simultaneous regex filtering at descriptor and linter levels by @nvuillam & @seaneagan in <https://github.com/oxsecurity/megalinter/pull/2669>
  - Allow MEGALINTER_CONFIG to contain a full path to a MegaLinter config file by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/2649>
  - Fix issue preventing plugins to work with flavors by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/2532>
  - Fix crash in case of unreachable symlinks by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/2538>
  - mega-linter-runner: Use --platform also for docker run by @nvuillam , @Kurt-Von-Laven & @cam-barts in <https://github.com/oxsecurity/megalinter/pull/2690>
  - Replace deprecated distutils.copy_tree by shutil.copytree

- Reporters
  - [SARIF_REPORTER](https://megalinter.io/latest/reporters/SarifReporter/)
    - Add option to skip def_ws prefix in sarif reports by @janderssonse in <https://github.com/oxsecurity/megalinter/pull/2383>
    - update schema to pass official SARIF validator by @DariuszPorowski in <https://github.com/oxsecurity/megalinter/pull/2645>
  - [CONFIG_REPORTER](https://megalinter.io/latest/reporters/ConfigReporter/)
    - Add support for idea plugins auto-install by @waterfoul in <https://github.com/oxsecurity/megalinter/pull/2553>
  - [CONSOLE_REPORTER](https://megalinter.io/latest/reporters/ConsoleReporter/)
    - Updated cases in console/log output to use ⚠ `Warning Sign (U+26A0)` instead of ◬ `White Up-Pointing Triangle with Dot (U+25EC)`, by @Doommius
  - [GITLAB_COMMENT_REPORTER](https://megalinter.io/latest/reporters/GitlabCommentReporter/)
    - Enhancement & fixes for GitlabCommentReporter by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/2564>
      - New var GITLAB_COMMENT_REPORTER_OVERWRITE_COMMENT to allow to disable the overwrite of existing MegaLinter comment in case of new run
      - In case of overwrite activated (by default), fetch all Merge Request comments, not the first 20.
      - Display a different message in log when a Merge Request comment is created or updated.
  - [AZURE_COMMENT_REPORTER](https://megalinter.io/latest/reporters/AzureCommentReporter/)
    - Downgrade Azure DevOps pipy package to avoid crash by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/2576>

- Documentation
  - Improve documentation pages split by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/2688>
    - Now Installation and Configuration menus have their own child menus
  - Doc about how to use fine grained PAT by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/2662>
  - Fixed incorrect link in Azure to Gitlab reporters pages. by @Doommius in <https://github.com/oxsecurity/megalinter/pull/2613>
  - Added bitbucket job template + Fix icon in console logs by @Doommius in <https://github.com/oxsecurity/megalinter/pull/2617>
  - Exclude licenses pages from online search results by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/2665>
  - Improve HTML tables display by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/2670>
  - Remove ASCII characters from linters helps displayed in MegaLinter documentation

- Internal CI
  - Upgrade GitHub Actions to change automated comments and increase timeout by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/2536>
  - Use Github Permissions instead of PAT by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/2652>
  - Update GitHub Actions workflows environments by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/2657>
  - Automate External Plugins table generation using **.automation/plugins.yml** file by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/2667>
  - Fix MegaLinter build issue by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/2539>
  - Fix for trivy-action (new naming for input) by @DariuszPorowski in <https://github.com/oxsecurity/megalinter/pull/2541>
  - Fix `/build` slash command to checkout the correct PR branch by @echoix in <https://github.com/oxsecurity/megalinter/pull/2542>
  - Fix local run of python test cases by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/2565>
  - Fix mkdocs documentation generation by downgrading mkdocs-glightbox to 0.3.2 by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/2582>
  - Do not push to docker from dev PRs by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/2639>
  - Update stale workflow: remove trigger on comments and explicit permissions by @echoix in <https://github.com/oxsecurity/megalinter/pull/2641>
  - Decouple updating docker pull stats from building docs by @echoix in <https://github.com/oxsecurity/megalinter/pull/2677>
  - Review MegaLinter's own cspell word list for outdated exclusions by @echoix in <https://github.com/oxsecurity/megalinter/pull/2676>
  - Run stale workflow only on schedule, by @echoix in <https://github.com/oxsecurity/megalinter/pull/2641>
  - Add explicit permissions to stale workflow, by @echoix in <https://github.com/oxsecurity/megalinter/pull/2641>

- Linter versions upgrades
  - [actionlint](https://rhysd.github.io/actionlint/) from 1.6.23 to **1.6.24**
  - [ansible-lint](https://ansible-lint.readthedocs.io/) from 6.14.4 to **6.16.2**
  - [bicep_linter](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter) from 0.15.31 to **0.17.1**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 0.76.1 to **0.77.5**
  - [checkov](https://www.checkov.io/) from 2.3.149 to **2.3.259**
  - [checkstyle](https://checkstyle.sourceforge.io) from 10.9.3 to **10.11.0**
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.68 to **0.1.69**
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2023.03.17 to **2023.05.18**
  - [csharpier](https://csharpier.com/) from 0.23.0 to **0.24.2**
  - [djlint](https://djlint.com/) from 1.19.16 to **1.29.0**
  - [dotnet-format](https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-format) from 6.0.407 to **6.0.408**
  - [eslint-plugin-jsonc](https://ota-meshi.github.io/eslint-plugin-jsonc/) from 2.7.0 to **2.8.0**
  - [eslint](https://eslint.org) from 8.37.0 to **8.41.0**
  - [git_diff](https://git-scm.com) from 2.38.4 to **2.38.5**
  - [gitleaks](https://github.com/zricethezav/gitleaks) from 8.16.1 to **8.16.3**
  - [jscpd](https://github.com/kucherenko/jscpd/tree/master/packages/jscpd) from 3.5.4 to **3.5.9**
  - [jsonlint](https://github.com/prantlf/jsonlint) from 14.0.2 to **14.0.3**
  - [kics](https://www.kics.io) from 1.6.13 to **1.7.1**
  - [ktlint](https://ktlint.github.io) from 0.48.2 to **0.49.1**
  - [kubeconform](https://github.com/yannh/kubeconform) from 0.5.0 to **0.6.1**
  - [kubescape](https://github.com/kubescape/kubescape) from 2.3.1 to **2.3.3**
  - [markdown-link-check](https://github.com/tcort/markdown-link-check) from 3.10.3 to **3.11.2**
  - [mypy](https://mypy.readthedocs.io/en/stable/) from 1.1.1 to **1.3.0**
  - [phplint](https://github.com/overtrue/phplint) from 5.5 to **9.0.4**
  - [phpstan](https://phpstan.org/) from 1.10.10 to **1.10.15**
  - [pmd](https://pmd.github.io/) from 6.48.0 to **6.55.0**
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.3.3 to **7.3.4**
  - [powershell_formatter](https://github.com/PowerShell/PSScriptAnalyzer) from 7.3.3 to **7.3.4**
  - [prettier](https://prettier.io/) from 2.8.7 to **2.8.8**
  - [protolint](https://github.com/yoheimuta/protolint) from 0.43.1 to **0.44.0**
  - [psalm](https://psalm.dev) from Psalm.5.9.0@ to **Psalm.5.12.0@**
  - [puppet-lint](http://puppet-lint.com/) from 3.3.0 to **4.0.0**
  - [pylint](https://pylint.pycqa.org) from 2.17.2 to **2.17.4**
  - [pyright](https://github.com/Microsoft/pyright) from 1.1.301 to **1.1.310**
  - [revive](https://revive.run/) from 1.3.1 to **1.3.2**
  - [rubocop](https://rubocop.org/) from 1.49.0 to **1.51.0**
  - [ruff](https://github.com/charliermarsh/ruff) from 0.0.260 to **0.0.270**
  - [semgrep](https://semgrep.dev/) from 1.16.0 to **1.23.0**
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 3.11.0 to **3.12.0**
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 3.11.0 to **3.12.0**
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 3.11.0 to **3.12.0**
  - [snakefmt](https://github.com/snakemake/snakefmt) from 0.8.3 to **0.8.4**
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.25.0 to **7.26.0**
  - [spectral](https://meta.stoplight.io/docs/spectral/README.md) from 6.6.0 to **6.8.0**
  - [sqlfluff](https://www.sqlfluff.com/) from 2.0.2 to **2.1.1**
  - [stylelint](https://stylelint.io) from 15.4.0 to **15.6.2**
  - [swiftlint](https://github.com/realm/SwiftLint) from 0.51.0 to **0.52.2**
  - [syft](https://github.com/anchore/syft) from 0.76.0 to **0.82.0**
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.4.4 to **1.4.6**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.45.0 to **0.45.11**
  - [terrascan](https://www.accurics.com/products/terrascan/) from 1.18.0 to **1.18.1**
  - [tflint](https://github.com/terraform-linters/tflint) from 0.45.0 to **0.46.1**
  - [trivy](https://aquasecurity.github.io/trivy/) from 0.39.0 to **0.41.0**
  - [v8r](https://github.com/chris48s/v8r) from 1.0.0 to **2.0.0**
  - [vale](https://vale.sh/) from 2.24.0 to **2.27.0**
  - [xmllint](https://gitlab.gnome.org/GNOME/libxml2/-/wikis/home) from 21003 to **21004**
  - [yamllint](https://yamllint.readthedocs.io/) from 1.30.0 to **1.32.0**

## [v6.22.2] - 2023-04-03

- Core
  - Fix failure of AzureCommentReporter when there is no pull request found in ENV vars
  - Fix HTML comment appearing in Azure Pull Request mail notifications

- Linter versions upgrades
  - [ansible-lint](https://ansible-lint.readthedocs.io/) from 6.14.3 to **6.14.4**
  - [checkov](https://www.checkov.io/) from 2.3.145 to **2.3.149**
  - [pylint](https://pylint.pycqa.org) from 2.17.1 to **2.17.2**
  - [rubocop](https://rubocop.org/) from 1.48.1 to **1.49.0**

## [v6.22.1] - 2023-04-02

- Core
  - Changed vars in AzureCommentReporter to reflects official Azure DevOps naming convention + fallback to keep backward compatibility, see [#2509](https://github.com/oxsecurity/megalinter/issues/2509)
  - Update AzureCommentReport to have only one MegaLinter thread instead of a new one for each run of MegaLinter

- Documentation
  - Updated usage scenario for Azure DevOps, see [#2509](https://github.com/oxsecurity/megalinter/issues/2509)

- Linter versions upgrades
  - [checkov](https://www.checkov.io/) from 2.3.141 to **2.3.145**
  - [phpstan](https://phpstan.org/) from 1.10.9 to **1.10.10**
  - [rstfmt](https://github.com/dzhu/rstfmt) from 0.0.12 to **0.0.13**

## [v6.22.0] - 2023-04-01

- New linters
  - Add [**ruff**](https://github.com/charliermarsh/ruff), by @lars-reimann in <https://github.com/oxsecurity/megalinter/pull/2458>

- Linter enhancements & fixes
  - Pin markdown-link-check to 3.10.3 until [tcort/markdown-link-check#246](https://github.com/tcort/markdown-link-check/issues/246) is fixed, by @Kurt-von-Laven ([#2498](https://github.com/oxsecurity/megalinter/issues/2498)).

- Core
  - Fix MegaLinter doc version & url displayed in logs, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/2485>
  - Use [megalinter-bot](https://github.com/megalinter-bot) to create apply fixes commits, by @lars-reimann, @nvuillam and @megalinter-bot :)
    - If you are an existing user of MegaLinter, you must update your github actions workflows to add the following parameters to **stefanzweifel/git-auto-commit-action@v4** :

    ```yaml
    commit_user_name: megalinter-bot
    commit_user_email: nicolas.vuillamy@ox.security
    ```

    - You can also use any github username and email you like :)

- Documentation
  - Close parentheses in ci_light flavour doc by @moverperfect in <https://github.com/oxsecurity/megalinter/pull/2494>

- Linter versions upgrades
  - [black](https://black.readthedocs.io/en/stable/) from 23.1.0 to **23.3.0**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 0.75.1 to **0.76.1**
  - [checkov](https://www.checkov.io/) from 2.3.120 to **2.3.141**
  - [eslint](https://eslint.org) from 8.36.0 to **8.37.0**
  - [kics](https://www.kics.io) from 1.6.12 to **1.6.13**
  - [markdown-link-check](https://github.com/tcort/markdown-link-check) from 3.11.0 to **3.10.3**
  - [phpstan](https://phpstan.org/) from 1.10.8 to **1.10.9**
  - [psalm](https://psalm.dev) from Psalm.5.8.0@ to **Psalm.5.9.0@**
  - [pyright](https://github.com/Microsoft/pyright) from 1.1.300 to **1.1.301**
  - [ruff](https://github.com/charliermarsh/ruff) from 0.0.255 to **0.0.260**
  - [semgrep](https://semgrep.dev/) from 1.15.0 to **1.16.0**
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 3.10.0 to **3.11.0**
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 3.10.0 to **3.11.0**
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 3.10.0 to **3.11.0**
  - [stylelint](https://stylelint.io) from 15.3.0 to **15.4.0**
  - [swiftlint](https://github.com/realm/SwiftLint) from 0.50.3 to **0.51.0**
  - [syft](https://github.com/anchore/syft) from 0.75.0 to **0.76.0**
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.4.2 to **1.4.4**
  - [trivy](https://aquasecurity.github.io/trivy/) from 0.38.3 to **0.39.0**

## [v6.21.0] - 2023-03-26

- New linters
  - Add [**helm lint**](https://helm.sh/docs/helm/helm_lint/), by @ThomasSanson in <https://github.com/oxsecurity/megalinter/pull/2386>

<!-- /* cspell:disable */ -->

- Media
  - Video: [Code quality - Ep01 - MegaLinter, one linter to rule them all](https://www.youtube.com/watch?v=NauVD4z-cMA), by @devpro
  - Video: [DevSecOps Webinar using MegaLinter](https://www.youtube.com/watch?v=hk950RUwIUA), by [5.15 Technologies](https://www.515tech.com/)
  - Video: (FR) [Coding Tech - L'importance de la CI/CD dans le développement de logiciels](https://www.youtube.com/watch?v=raCDpsP9O78), by @GridexX from [R2DevOps](https://r2devops.io/)
  - Article: (FR) [MegaLinter, votre meilleur ami pour un code de qualité](https://www.neosoft.fr/nos-publications/blog-tech/mega-linter-votre-meilleur-ami-pour-un-code-de-qualite/?utm_source=twitter&utm_medium=organic&utm_campaign=article-mega-linter), by @ThomasSanson

<!-- /* cspell:enable */ -->

- Linter enhancements & fixes
  - [phpcs](https://megalinter.io/latest/descriptors/php_phpcs/): Add regex in descriptor to be able to extract the number of found errors, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/2453>
  - Replace babel-eslint with @babel/eslint-parser, by @bdovaz in <https://github.com/oxsecurity/megalinter/pull/2445>
  - Use docker image to install phpstan, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/2469>
  - Avoid cspell error on readonly workspaces, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/2474>
  - Allow bandit to use pyproject.toml, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/2475>
  - Bring back stylelint-config-sass-guidelines package, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/2477>
  - Display only errors in markdown-link-check logs for better readability, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/2479>

- Core
  - Run CI linter jobs only on Pull requests to avoid doubling jobs

- Documentation
  - mega-linter-runner: doc fix for env list of values, see [#2448](https://github.com/oxsecurity/megalinter/issues/2448), by @DariuszPorowski in <https://github.com/oxsecurity/megalinter/pull/2449>

- Linter versions upgrades
  - [ansible-lint](https://ansible-lint.readthedocs.io/) from 6.14.1 to **6.14.3**
  - [bandit](https://bandit.readthedocs.io/en/latest/) from 1.7.4 to **1.7.5**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 0.74.1 to **0.75.1**
  - [checkov](https://www.checkov.io/) from 2.3.70 to **2.3.120**
  - [checkstyle](https://checkstyle.sourceforge.io) from 10.8.0 to **10.9.3**
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.67 to **0.1.68**
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2023.02.17 to **2023.03.17**
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 6.28.0 to **6.31.1**
  - [dotnet-format](https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-format) from 6.0.406 to **6.0.407**
  - [eslint-plugin-jsonc](https://ota-meshi.github.io/eslint-plugin-jsonc/) from 2.6.0 to **2.7.0**
  - [eslint](https://eslint.org) from 8.35.0 to **8.36.0**
  - [gitleaks](https://github.com/zricethezav/gitleaks) from 8.16.0 to **8.16.1**
  - [jscpd](https://github.com/kucherenko/jscpd/tree/master/packages/jscpd) from 3.5.3 to **3.5.4**
  - [jsonlint](https://github.com/prantlf/jsonlint) from 14.0.1 to **14.0.2**
  - [kics](https://www.kics.io) from 1.6.11 to **1.6.12**
  - [markdown-link-check](https://github.com/tcort/markdown-link-check) from 3.10.3 to **3.11.0**
  - [phpstan](https://phpstan.org/) from 1.10.5 to **1.10.8**
  - [prettier](https://prettier.io/) from 2.8.4 to **2.8.7**
  - [psalm](https://psalm.dev) from Psalm.5.7.7@ to **Psalm.5.8.0@**
  - [pylint](https://pylint.pycqa.org) from 2.16.4 to **2.17.1**
  - [pyright](https://github.com/Microsoft/pyright) from 1.1.296 to **1.1.300**
  - [revive](https://revive.run/) from 1.2.5 to **1.3.1**
  - [rstcheck](https://github.com/myint/rstcheck) from 6.1.1 to **6.1.2**
  - [rubocop](https://rubocop.org/) from 1.48.0 to **1.48.1**
  - [semgrep](https://semgrep.dev/) from 1.14.0 to **1.15.0**
  - [snakefmt](https://github.com/snakemake/snakefmt) from 0.8.1 to **0.8.3**
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.24.0 to **7.25.0**
  - [sqlfluff](https://www.sqlfluff.com/) from 1.4.5 to **2.0.2**
  - [stylelint](https://stylelint.io) from 15.2.0 to **15.3.0**
  - [syft](https://github.com/anchore/syft) from 0.74.0 to **0.75.0**
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.3.9 to **1.4.2**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.44.4 to **0.45.0**
  - [trivy](https://aquasecurity.github.io/trivy/) from 0.38.1 to **0.38.3**
  - [v8r](https://github.com/chris48s/v8r) from 0.14.0 to **1.0.0**
  - [yamllint](https://yamllint.readthedocs.io/) from 1.29.0 to **1.30.0**

## [v6.20.1] - 2023-03-07

- Fixes
  - Fix [issue with running on Mac m1 no longer working](https://github.com/oxsecurity/megalinter/issues/2427), by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/2430>
  - Fix [Container images errors when pulling](https://github.com/oxsecurity/megalinter/issues/2348), by @echoix in <https://github.com/oxsecurity/megalinter/pull/2435>
  - Fix [Pre npm install not resolving](https://github.com/oxsecurity/megalinter/issues/2428), by @echoix in <https://github.com/oxsecurity/megalinter/pull/2435>
  - Add build date in Beta docker images, by @nvuillam
  - Correct misleading error message in **GitlabCommentReporter.py**, see [#2420](https://github.com/oxsecurity/megalinter/issues/2420)
  - Fix **GitlabCommentReporter** wrong variables names, check [#2423](https://github.com/oxsecurity/megalinter/issues/2423)

- Core
  - Improve config test, by @bdovaz in <https://github.com/oxsecurity/megalinter/pull/2426>

- Doc
  - Add article [Level up your Unity Packages with CI/CD](https://medium.com/@RunningMattress/level-up-your-unity-packages-with-ci-cd-9498d2791211), by @RunningMattress in <https://github.com/oxsecurity/megalinter/pull/2436>
  - Correct minor docs error by @moverperfect in <https://github.com/oxsecurity/megalinter/pull/2440>

- Linter versions upgrades
  - [ansible-lint](https://ansible-lint.readthedocs.io/) from 6.14.0 to **6.14.1**
  - [bicep_linter](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter) from 0.14.85 to **0.15.31**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 0.74.0 to **0.74.1**
  - [checkov](https://www.checkov.io/) from 2.3.59 to **2.3.70**
  - [csharpier](https://csharpier.com/) from 0.22.1 to **0.23.0**
  - [jsonlint](https://github.com/prantlf/jsonlint) from 13.0.1 to **14.0.1**
  - [mypy](https://mypy.readthedocs.io/en/stable/) from 1.0.1 to **1.1.1**
  - [phpstan](https://phpstan.org/) from 1.10.3 to **1.10.5**
  - [protolint](https://github.com/yoheimuta/protolint) from 0.43.0 to **0.43.1**
  - [puppet-lint](http://puppet-lint.com/) from 3.2.0 to **3.3.0**
  - [pylint](https://pylint.pycqa.org) from 2.16.3 to **2.16.4**
  - [rubocop](https://rubocop.org/) from 1.47.0 to **1.48.0**
  - [stylelint](https://stylelint.io) from 14.16.1 to **15.2.0**

## [v6.20.0] - 2023-03-05

- Core
  - Upgrade base docker image from python:3.10.4-alpine3.16 to python:3.11.1-alpine3.17
  - Build: remove folder contents before generating Dockerfile files for each linter in generate_linter_dockerfiles(), by @bdovaz in [#2294](https://github.com/oxsecurity/megalinter/pull/2294)
  - Build: remove folder contents before generating test classes for each linter in generate_linter_test_classes(), by @bdovaz in [#2294](https://github.com/oxsecurity/megalinter/pull/2294)
  - Build: automatically update the linter list used in the matrix of several of the workflows, by @bdovaz in [#2294](https://github.com/oxsecurity/megalinter/pull/2294)
  - Test: create a testing architecture for format/autofix linters, by @bdovaz in [#2294](https://github.com/oxsecurity/megalinter/pull/2294)
  - Test: create or adapt input files for format/autofix tests, by @bdovaz in [#2294](https://github.com/oxsecurity/megalinter/pull/2294)
  - Test: created specific test folders for linters that need them because they can't share them, by @bdovaz in [#2294](https://github.com/oxsecurity/megalinter/pull/2294)
  - Added rubocop-rake RubyGem for linting Rake files with RuboCop

- Fixes
  - Correctly generate class names and test class files for each linter when the linter descriptor defines the attribute "name", by @bdovaz in [#2294](https://github.com/oxsecurity/megalinter/pull/2294)
  - Removed the default **powershell** templates TEMPLATES/.powershell-formatter.psd1 and TEMPLATES/.powershell-psscriptanalyzer.psd1. Having these templates caused all rules to be ignored as the settings aren't incremental but absolute, by @bdovaz in [#2294](https://github.com/oxsecurity/megalinter/pull/2294)
  - Added **cli_lint_fix_arg_name** parameter to **dotnet format** descriptor as without it, autofix doesn't work, by @bdovaz in [#2294](https://github.com/oxsecurity/megalinter/pull/2294)
  - Created **BicepLinter** class to add **DOTNET_SYSTEM_GLOBALIZATION_INVARIANT** environment variable to avoid problems with ICU packages, by @bdovaz in [#2294](https://github.com/oxsecurity/megalinter/pull/2294)
  - Modified **npm-groovy-lint** descriptor to add **--failon** parameter to only fail with error and not info which is the default value, by @bdovaz in [#2294](https://github.com/oxsecurity/megalinter/pull/2294)
  - Added **cli_lint_fix_arg_name** parameter to **powershell formatter** descriptor as without it, autofix doesn't work, by @bdovaz in [#2294](https://github.com/oxsecurity/megalinter/pull/2294)
  - Created **ProtolintLinter** class to fix the problem that returns exit code 1 when it encounters a problem to correct even though it corrects it correctly, by @bdovaz in [#2294](https://github.com/oxsecurity/megalinter/pull/2294)
  - Concatenate **--output** parameter correctly to **xmllint** linter, by @bdovaz in [#2294](https://github.com/oxsecurity/megalinter/pull/2294)
  - Modified the .pre-commit-hooks.yaml for megalinter-full so the containername argument is correctly split between two lines, by @drbothen [#2411](https://github.com/oxsecurity/megalinter/pull/2411)
  - Avoid [jscpd](https://megalinter.io/v6/descriptors/copypaste_jscpd/) default config to detect copy pastes in image files
  - Move utilstest to megalinter folder to avoid import issues
  - Replace deprecated spectral package, by @bdovaz in by @bdovaz in <https://github.com/oxsecurity/megalinter/pull/2340>
  - Generate correct urls for packages with fixed versions, by @bdovaz in <https://github.com/oxsecurity/megalinter/pull/2339>

- Documentation
  - Change **swiftlint** example that did not correctly reflect the **--fix** parameter, by @bdovaz in [#2294](https://github.com/oxsecurity/megalinter/pull/2294)
  - Change in TSX **eslint** descriptor the urls as they were not correct, by @bdovaz in [#2294](https://github.com/oxsecurity/megalinter/pull/2294)
  - Change in TYPESCRIPT **eslint** descriptor the urls as they were not correct, by @bdovaz on [#2294](https://github.com/oxsecurity/megalinter/pull/2294)
  - Use mkdocs-glightbox to allow to click on images and display them in full screen

- CI
  - Use docker/build-push-action to build docker images and akhilerm/tag-push-action to release by retagging and pushing beta images instead of rebuilding them
  - Authenticate to GitHub API during docker build to avoid reaching limits
  - Remove apk go package install in images where possible to decrease image sizes, by @echoix in <https://github.com/oxsecurity/megalinter/pull/2318>
  - Create a slash PR bot to run `./build.sh` command manually on PRs, by @echoix in [#2353](https://github.com/oxsecurity/megalinter/pull/2353) and [#2381](https://github.com/oxsecurity/megalinter/pull/2381)
  - Limit parallel execution of large job matrix in the workflows with max-parallel in order to keep runners available for other jobs, by @echoix in [#2397](https://github.com/oxsecurity/megalinter/pull/2397)

- Linter versions upgrades
  - [ansible-lint](https://ansible-lint.readthedocs.io/) from 6.12.1 to **6.14.0**
  - [bash-exec](https://www.gnu.org/software/bash/) from 5.1.16 to **5.2.15**
  - [bicep_linter](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter) from 0.14.46 to **0.14.85**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 0.72.10 to **0.74.0**
  - [checkmake](https://github.com/mrtazz/checkmake) from 0.2.1 to **0.2.0**
  - [checkov](https://www.checkov.io/) from 2.1.244 to **2.3.18**
  - [checkstyle](https://checkstyle.sourceforge.io) from 10.7.0 to **10.8.0**
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2023.01.20 to **2023.02.17**
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 6.21.0 to **6.28.0**
  - [djlint](https://djlint.com/) from 1.19.13 to **1.19.16**
  - [dotnet-format](https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-format) from 6.0.405 to **6.0.406**
  - [dustilock](https://github.com/Checkmarx/dustilock) from 0.0.0 to **1.2.0**
  - [editorconfig-checker](https://editorconfig-checker.github.io/) from 2.4.0 to **2.7.0**
  - [eslint](https://eslint.org) from 8.33.0 to **8.35.0**
  - [git_diff](https://git-scm.com) from 2.36.4 to **2.38.4**
  - [gitleaks](https://github.com/zricethezav/gitleaks) from 8.15.3 to **8.16.0**
  - [golangci-lint](https://golangci-lint.run/) from 1.51.0 to **1.51.2**
  - [jscpd](https://github.com/kucherenko/jscpd/tree/master/packages/jscpd) from 3.3.26 to **3.5.3**
  - [jsonlint](https://github.com/prantlf/jsonlint) from 11.7.0 to **13.0.1**
  - [kics](https://www.kics.io) from 1.6.9 to **1.6.11**
  - [mypy](https://mypy.readthedocs.io/en/stable/) from 0.991 to **1.0.1**
  - [perlcritic](https://metacpan.org/pod/Perl::Critic) from 1.148 to **1.150**
  - [phpcs](https://github.com/squizlabs/PHP_CodeSniffer) from 3.7.1 to **3.7.2**
  - [phpstan](https://phpstan.org/) from 1.9.14 to **1.10.3**
  - [powershell_formatter](https://github.com/PowerShell/PSScriptAnalyzer) from 7.3.2 to **7.3.3**
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.3.2 to **7.3.3**
  - [prettier](https://prettier.io/) from 2.8.3 to **2.8.4**
  - [protolint](https://github.com/yoheimuta/protolint) from 0.42.2 to **0.43.0**
  - [psalm](https://psalm.dev) from Psalm.5.6.0@ to **Psalm.5.7.7@**
  - [puppet-lint](http://puppet-lint.com/) from 3.0.1 to **3.2.0**
  - [pylint](https://pylint.pycqa.org) from 2.16.1 to **2.16.3**
  - [pyright](https://github.com/Microsoft/pyright) from 1.1.270 to **1.1.296**
  - [rubocop](https://rubocop.org/) from 1.44.1 to **1.47.0**
  - [secretlint](https://github.com/secretlint/secretlint) from 6.2.0 to **6.2.3**
  - [semgrep](https://semgrep.dev/) from 1.9.0 to **1.14.0**
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 3.8.0 to **3.10.0**
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 3.8.0 to **3.10.0**
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 3.8.0 to **3.10.0**
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.21.0 to **7.24.0**
  - [spectral](https://meta.stoplight.io/docs/spectral/README.md) from 5.9.2 to **6.6.0**
  - [syft](https://github.com/anchore/syft) from 0.70.0 to **0.74.0**
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.3.7 to **1.3.9**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.43.2 to **0.44.4**
  - [terrascan](https://www.accurics.com/products/terrascan/) from 1.16.0 to **1.18.0**
  - [tflint](https://github.com/terraform-linters/tflint) from 0.44.1 to **0.45.0**
  - [trivy](https://aquasecurity.github.io/trivy/) from 0.35.0 to **0.38.1**
  - [xmllint](https://gitlab.gnome.org/GNOME/libxml2/-/wikis/home) from 20914 to **21003**

## [v6.19.0] - 2023-02-05

- Core
  - Deploy additional Docker images to GitHub Container Registry, by @lars-reimann in [#2117](https://github.com/oxsecurity/megalinter/pull/2117)
  - Build: Disable generate_documentation_all_users as we use github-dependents-info

- Evolutions
  - Support xmllint autofix, by @bdovaz in <https://github.com/oxsecurity/megalinter/pull/2244> (requires definition of `XML_XMLLINT_AUTOFORMAT: true`)

- Fixes
  - Change name of config file for powershell formatter to avoid collision with powershell linter config, by @nvuillam in <https://github.com/oxsecurity/megalinter/pull/2231>
  - Enhance find SARIF json in stdout output
  - Pass --show-context, --show-suggestions, and --no-must-find-files to CSpell for friendlier UX, by @Kurt-von-Laven in [#2275](https://github.com/oxsecurity/megalinter/pull/2275).
  - Only run npm-package-json-lint when package.json is present, by @Kurt-von-Laven in [#2280](https://github.com/oxsecurity/megalinter/pull/2280).
  - Fix local files with extends, by @bdovaz in <https://github.com/oxsecurity/megalinter/pull/2236>
  - Remove downgrading of ansible-lint, by @gotit96 in <https://github.com/oxsecurity/megalinter/pull/2257>
  - Tag some automatically updated files as generated files, by @echoix in <https://github.com/oxsecurity/megalinter/pull/2285>
  - Fix Sarif Reporter in Azure Devops with space in project name, by @EtienneDeneuve in <https://github.com/oxsecurity/megalinter/pull/2301>
  - Pass extra args for friendlier CSpell UX (#2271), by @Kurt-von-Laven in <https://github.com/oxsecurity/megalinter/pull/2275>

- Documentation
  - Configure jsonschema documentation formatting (see [Descriptor schema](https://megalinter.io/latest/json-schemas/descriptor.html), [Configuration schema](https://megalinter.io/latest/json-schemas/configuration.html)), by @echoix in [#2270](https://github.com/oxsecurity/megalinter/pull/2270)
  - Update CONTRIBUTING.md and add documentation improvements hints, by @bdovaz in <https://github.com/oxsecurity/megalinter/pull/2228>
  - Add Powershell linters rules url, by @bdovaz in <https://github.com/oxsecurity/megalinter/pull/2242>
  - Fix syft logo, by @pjungermann in <https://github.com/oxsecurity/megalinter/pull/2282>
  - Fix docker run documentation, by @davidjeddy in <https://github.com/oxsecurity/megalinter/pull/2258>

- Linter versions upgrades
  - [actionlint](https://rhysd.github.io/actionlint/) from 1.6.22 to **1.6.23**
  - [ansible-lint](https://ansible-lint.readthedocs.io/) from 6.7.0 to **6.12.1**
  - [bicep_linter](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter) from 0.13.1 to **0.14.6**
  - [black](https://black.readthedocs.io/en/stable/) from 22.12.0 to **23.1.0**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 0.72.6 to **0.72.10**
  - [checkstyle](https://checkstyle.sourceforge.io) from 10.6.0 to **10.7.0**
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.66 to **0.1.67**
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2022.12.10 to **2023.01.20**
  - [csharpier](https://csharpier.com/) from 0.21.0 to **0.22.1**
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 6.18.1 to **6.21.0**
  - [devskim](https://github.com/microsoft/DevSkim) from 0.7.101 to **0.7.104**
  - [djlint](https://djlint.com/) from 1.19.11 to **1.19.13**
  - [dotnet-format](https://docs.microsoft.com/en-us/dotnet/core/tools/dotnet-format) from 000 to **6.0.405**
  - [eslint](https://eslint.org) from 8.31.0 to **8.33.0**
  - [git_diff](https://git-scm.com) from 2.36.3 to **2.36.4**
  - [gitleaks](https://github.com/zricethezav/gitleaks) from 8.15.2 to **8.15.3**
  - [golangci-lint](https://golangci-lint.run/) from 1.50.1 to **1.51.0**
  - [isort](https://pycqa.github.io/isort/) from 5.11.4 to **5.12.0**
  - [kics](https://www.kics.io) from 1.6.7 to **1.6.9**
  - [ktlint](https://ktlint.github.io) from 0.48.1 to **0.48.2**
  - [perlcritic](https://metacpan.org/pod/Perl::Critic) from 1.146 to **1.148**
  - [phpstan](https://phpstan.org/) from 1.9.7 to **1.9.14**
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.3.1 to **7.3.2**
  - [powershell_formatter](https://github.com/PowerShell/PSScriptAnalyzer) from 7.3.1 to **7.3.2**
  - [prettier](https://prettier.io/) from 2.8.1 to **2.8.3**
  - [psalm](https://psalm.dev) from Psalm.dev-master@ to **Psalm.5.6.0@**
  - [pylint](https://pylint.pycqa.org) from 2.15.10 to **2.16.1**
  - [revive](https://revive.run/) from 1.2.4 to **1.2.5**
  - [rstfmt](https://github.com/dzhu/rstfmt) from 0.0.11 to **0.0.12**
  - [rubocop](https://rubocop.org/) from 1.42.0 to **1.44.1**
  - [scss-lint](https://github.com/sds/scss-lint) from 0.59.0 to **0.60.0**
  - [secretlint](https://github.com/secretlint/secretlint) from 6.0.2 to **6.2.0**
  - [semgrep](https://semgrep.dev/) from 1.3.0 to **1.9.0**
  - [snakefmt](https://github.com/snakemake/snakefmt) from 0.8.0 to **0.8.1**
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.19.1 to **7.21.0**
  - [syft](https://github.com/anchore/syft) from 0.65.0 to **0.70.0**
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.3.6 to **1.3.7**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.42.3 to **0.43.2**
  - [tflint](https://github.com/terraform-linters/tflint) from 0.44.0 to **0.44.1**
  - [tsqllint](https://github.com/tsqllint/tsqllint) from 1.15.1.0 to **1.15.3.0**
  - [v8r](https://github.com/chris48s/v8r) from 0.13.1 to **0.14.0**
  - [yamllint](https://yamllint.readthedocs.io/) from 1.28.0 to **1.29.0**

## [v6.18.0] - 2023-01-07

- New linters
  - Add [CSharpier](https://csharpier.com/) linter, by @bdovaz in [#2185](https://github.com/oxsecurity/megalinter/pull/2185) and [#2198](https://github.com/oxsecurity/megalinter/pull/2198)

- Core
  - Upgrade to dotnet 6.0, by @lexstatic in [#1680](https://github.com/oxsecurity/megalinter/pull/1680)
    - dotnet-format requires `.sln`, `.csproj` or `.vbproj` in the repo
  - Switch to docker buildx, by @bdovaz in [#2199](https://github.com/oxsecurity/megalinter/pull/2199)
  - Drone CI enhancements, by @NebulaOnion in [#2195](https://github.com/oxsecurity/megalinter/pull/2195)
    - Config generator tool now supports Drone CI
    - Added information about how to change trigger rules for Drone CI workflow
  - Unify the drawing of badges in documentation, by @bdovaz in [#2220](https://github.com/oxsecurity/megalinter/pull/2220)

- Fixes
  - Don't write output files if REPORT_OUTPUT_FOLDER is none
  - Fix Perl linter skipping files

- New MegaLinter plugins
  - [linkcheck](https://github.com/shiranr/linkcheck): Plugin to check and validate Markdown links, by @shiranr
  - [salt-lint](https://github.com/ssc-services/mega-linter-plugin-salt): Checks Salt State files (SLS) for best practices and behavior that could potentially be improved, by @grimmjo

- New article talking about MegaLinter: Writing documentation as a champ in engineering teams (deleted), by @gijsreyn

- Linter versions upgrades
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 0.72.5 to **0.72.6**
  - [checkstyle](https://checkstyle.sourceforge.io) from 10.5.0 to **10.6.0**
  - [csharpier](https://csharpier.com/) from 0.16.0 to **0.21.0**
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 6.18.0 to **6.18.1**
  - [devskim](https://github.com/microsoft/DevSkim) from 0.6.9 to **0.7.101**
  - [djlint](https://djlint.com/) from 1.19.10 to **1.19.11**
  - [eslint-plugin-jsonc](https://ota-meshi.github.io/eslint-plugin-jsonc/) from 2.5.0 to **2.6.0**
  - [eslint](https://eslint.org) from 8.30.0 to **8.31.0**
  - [kics](https://www.kics.io) from 1.6.6 to **1.6.7**
  - [ktlint](https://ktlint.github.io) from 0.48.0 to **0.48.1**
  - [markdownlint](https://github.com/DavidAnson/markdownlint) from 0.32.2 to **0.33.0**
  - [phplint](https://github.com/overtrue/phplint) from 5.4 to **5.5**
  - [phpstan](https://phpstan.org/) from 1.9.4 to **1.9.7**
  - [rubocop](https://rubocop.org/) from 1.41.1 to **1.42.0**
  - [secretlint](https://github.com/secretlint/secretlint) from 5.3.0 to **6.0.2**
  - [semgrep](https://semgrep.dev/) from 1.2.1 to **1.3.0**
  - [sfdx-scanner](https://forcedotcom.github.io/sfdx-scanner/) from 3.7.1 to **3.8.0**
  - [stylelint](https://stylelint.io) from 14.16.0 to **14.16.1**
  - [syft](https://github.com/anchore/syft) from 0.64.0 to **0.65.0**
  - [tsqllint](https://github.com/tsqllint/tsqllint) from 1.14.5.0 to **1.15.1.0**

## [v6.17.0] - 2022-12-27

- New linters
  - Add PowerShell formatter, by @bdovaz ([#2176](https://github.com/oxsecurity/megalinter/pull/2176))

- Documentation
  - Improve meta tags in HTML documentation
  - Clarify how npm-package-json-lint files can be ignored, by @bdovaz ([#2184](https://github.com/oxsecurity/megalinter/pull/2184))

- Linter versions upgrades
  - [djlint](https://djlint.com/) from 1.19.9 to **1.19.10**
  - [dotenv-linter](https://dotenv-linter.github.io/) from 3.2.0 to **3.3.0**
  - [powershell_formatter](https://github.com/PowerShell/PSScriptAnalyzer) from 5.1.22621 to **7.3.1**
  - [tflint](https://github.com/terraform-linters/tflint) from 0.43.0 to **0.44.0**

## [v6.16.0] - 2022-12-24

- New linters
  - Add [npm-package-json-lint](https://github.com/tclindner/npm-package-json-lint) linter, by @bdovaz ([#2150](https://github.com/oxsecurity/megalinter/pull/2150))

- Evolutions
  - Upgrade to alpine 3.16
  - Disable php7 & upgrade php8 to php81
  - Add Makefile linters to documentation flavor
  - PowershellLinter autofix capability, by @bdovaz ([#2175](https://github.com/oxsecurity/megalinter/pull/2175))
  - Allow local files with EXTENDS configuration, by @bdovaz ([#2151](https://github.com/oxsecurity/megalinter/pull/2151))
  - Add Trivy config file parameters, by @bdovaz ([#2154](https://github.com/oxsecurity/megalinter/pull/2154))

- Fixes
  - Change reporter text for better UX, by @ashokm ([#2168](https://github.com/oxsecurity/megalinter/pull/2168))
  - Remove workspace prefix from aggregate sarif report, by @janderssonse ([#2119](https://github.com/oxsecurity/megalinter/pull/2119))
  - CSpell file name linting doesn't use (custom) CSpell configuration ([#2058](https://github.com/oxsecurity/megalinter/issues/2058))
  - HTML email not rendering correctly ([#2120](https://github.com/oxsecurity/megalinter/issues/2120)). Set `REPORTERS_MARKDOWN_TYPE` to `simple` to avoid external images in PR/MR markdown comments.
  - mega-linter-runner: Fix Value for container-name of type String required, by @AlbanAndrieu ([#2123](https://github.com/oxsecurity/megalinter/pull/2123)
  - Use warning emoji in reporters, by @ashokm ([#2156](https://github.com/oxsecurity/megalinter/pull/2156))
  - Fix branding to use the correct 'OX Security' name, by @ashokm

- Doc
  - Enclose System.TeamProject in Azure Pipelines, by @ashokm ([#2131](https://github.com/oxsecurity/megalinter/pull/2131))
  - Better contributing docs, by @bdovaz ([#2162](https://github.com/oxsecurity/megalinter/pull/2162))

- Linter versions upgrades
  - [bicep_linter](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter) from 0.12.40 to **0.13.1**
  - [black](https://black.readthedocs.io/en/stable/) from 22.10.0 to **22.12.0**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 0.72.0 to **0.72.5**
  - [checkstyle](https://checkstyle.sourceforge.io) from 10.4 to **10.5.0**
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.65 to **0.1.66**
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2022.10.14 to **2022.12.10**
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 6.14.3 to **6.18.0**
  - [djlint](https://djlint.com/) from 1.19.7 to **1.19.9**
  - [eslint](https://eslint.org) from 8.28.0 to **8.29.0** to **8.30.0**
  - [git_diff](https://git-scm.com) from 2.34.5 to **2.36.3**
  - [gitleaks](https://github.com/zricethezav/gitleaks) from 8.15.0 to **8.15.2**
  - [isort](https://pycqa.github.io/isort/) from 5.10.1 to **5.11.4**
  - [kics](https://www.kics.io) from 1.6.5 to **1.6.6**
  - [ktlint](https://ktlint.github.io) from 0.47.1 to **0.48.0**
  - [luacheck](https://luacheck.readthedocs.io) from 1.0.0 to **1.1.0**
  - [perlcritic](https://metacpan.org/pod/Perl::Critic) from 1.140 to **1.146**
  - [phplint](https://github.com/overtrue/phplint) from 3.0 to **5.4**
  - [phpstan](https://phpstan.org/) from 1.9.2 to **1.9.4**
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.3.0 to **7.3.1**
  - [prettier](https://prettier.io/) from 2.8.0 to **2.8.1**
  - [psalm](https://psalm.dev) from Psalm.4.x-dev@ to **Psalm.dev-master@**
  - [pylint](https://pylint.pycqa.org) from 2.15.6 to **2.15.9**
  - [rubocop](https://rubocop.org/) from 1.39.0 to **1.41.1**
  - [semgrep](https://semgrep.dev/) from 0.122.0 to **1.2.1**
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 3.6.2 to **3.7.1**
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 3.6.2 to **3.7.1**
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 3.6.2 to **3.7.1**
  - [shellcheck](https://github.com/koalaman/shellcheck) from 0.8.0 to **0.9.0**
  - [snakefmt](https://github.com/snakemake/snakefmt) from 0.7.0 to **0.8.0**
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.18.2 to **7.19.1**
  - [sqlfluff](https://www.sqlfluff.com/) from 1.4.2 to **1.4.5**
  - [stylelint](https://stylelint.io) from 14.15.0 to **14.16.0**
  - [swiftlint](https://github.com/realm/SwiftLint) from 0.50.0 to **0.50.3**
  - [syft](https://github.com/anchore/syft) from 0.62.1 to **0.64.0**
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.3.5 to **1.3.6**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.40.2 to **0.42.3**
  - [terrascan](https://www.accurics.com/products/terrascan/) from 1.17.0 to **1.16.0**
  - [tflint](https://github.com/terraform-linters/tflint) from 0.42.1 to **0.43.0**
  - [trivy](https://aquasecurity.github.io/trivy/) from 0.29.2 to **0.35.0**
  - [v8r](https://github.com/chris48s/v8r) from 0.13.0 to **0.13.1**

## [v6.15.0] - 2022-11-23

- Switch to <https://megalinter.io>
- Initial Drone CI documentation
- Automatically generate "Used by" markdown documentation with [github-dependents-info](https://github.com/nvuillam/github-dependents-info)
- Add Docker container documentation

- Linter versions upgrades
  - [bicep_linter](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter) from 0.12.1 to **0.12.40**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 0.70.1 to **0.72.0**
  - [coffeelint](http://www.coffeelint.org) from 5.2.10 to **5.2.11**
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 6.14.0 to **6.14.3**
  - [djlint](https://djlint.com/) from 1.19.4 to **1.19.7**
  - [eslint](https://eslint.org) from 8.27.0 to **8.28.0**
  - [flake8](https://flake8.pycqa.org) from 5.0.4 to **6.0.0**
  - [hadolint](https://github.com/hadolint/hadolint) from 2.10.0 to **2.12.0**
  - [kics](https://www.kics.io) from 1.6.3 to **1.6.5**
  - [mypy](https://mypy.readthedocs.io/en/stable/) from 0.982 to **0.991**
  - [phpstan](https://phpstan.org/) from 1.9.1 to **1.9.2**
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.2.7 to **7.3.0**
  - [prettier](https://prettier.io/) from 2.7.1 to **2.8.0**
  - [protolint](https://github.com/yoheimuta/protolint) from 0.41.0 to **0.42.2**
  - [psalm](https://psalm.dev) from Psalm.5.x-dev@ to **Psalm.4.x-dev@**
  - [pylint](https://pylint.pycqa.org) from 2.15.5 to **2.15.6**
  - [rstcheck](https://github.com/myint/rstcheck) from 6.1.0 to **6.1.1**
  - [rubocop](https://rubocop.org/) from 1.38.0 to **1.39.0**
  - [semgrep](https://semgrep.dev/) from 0.120.0 to **0.122.0**
  - [snakefmt](https://github.com/snakemake/snakefmt) from 0.6.1 to **0.7.0**
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.18.1 to **7.18.2**
  - [sqlfluff](https://www.sqlfluff.com/) from 1.4.1 to **1.4.2**
  - [stylelint](https://stylelint.io) from 14.14.1 to **14.15.0**
  - [swiftlint](https://github.com/realm/SwiftLint) from 0.46.5 to **0.50.0**
  - [syft](https://github.com/anchore/syft) from 0.60.3 to **0.62.1**
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.3.4 to **1.3.5**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.40.0 to **0.40.2**
  - [terrascan](https://www.accurics.com/products/terrascan/) from 1.16.0 to **1.17.0**

## [v6.14.0] - 2022-11-06

- Core
  - Replace `set-output` usage with `GITHUB_OUTPUT` to handle [Github deprecation notice](https://github.blog/changelog/2022-10-11-github-actions-deprecating-save-state-and-set-output-commands/)
  - Allow [PRE_COMMANDS](https://oxsecurity.github.io/megalinter/latest/configuration/#pre-commands) to be defined within a python venv ([#2017](https://github.com/oxsecurity/megalinter/issues/2017))
  - Correct behavior of `EXTENDS` property in `.megalinter.yml` config file ([#1516](https://github.com/oxsecurity/megalinter/issues/1516))
  - Fix flavor suggestion message in reporters

- New MegaLinter plugin: [mustache](https://github.com/one-acre-fund/mega-linter-plugin-logstash): Plugin to validate [Logstash](https://www.elastic.co/guide/en/logstash/current/configuration.html) pipeline definition files using [mustache](https://github.com/breml/logstash-config), by [Yann Jouanique](https://github.com/Yann-J)

- Linters
  - Bring back [rstfmt](https://oxsecurity.github.io/megalinter/latest/descriptors/rst_rstfmt/) RestructuredText formatter
  - Add the SPELL_*_FILE_EXTENSIONS parameter for each SPELL type linter. If set, it will use this value to filter instead of the default behavior which is to parse the files of all other linters executed ([#1997](https://github.com/oxsecurity/megalinter/issues/1997)).
  - Allow cspell to also analyze file names (new variable SPELL_CSPELL_ANALYZE_FILE_NAMES) ([#2009](https://github.com/oxsecurity/megalinter/issues/2009))
  - Fix bicep version regex

- Linter versions upgrades
  - [actionlint](https://rhysd.github.io/actionlint/) from 1.6.21 to **1.6.22**
  - [bicep_linter](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter) from 0.11.1 to to **0.12.1**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 0.68.1 to **0.70.1**
  - [checkstyle](https://checkstyle.sourceforge.io) from 10.3.4 to **10.4**
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.64 to **0.1.65**
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 6.12.0 to **6.14.0**
  - [djlint](https://djlint.com/) from 1.19.2 to **1.19.4**
  - [eslint-plugin-jsonc](https://ota-meshi.github.io/eslint-plugin-jsonc/) from 2.4.0 to **2.5.0**
  - [eslint](https://eslint.org) from 8.26.0 to **8.27.0**
  - [kics](https://www.kics.io) from 1.6.2 to **1.6.3**
  - [kubeconform](https://github.com/yannh/kubeconform) from 0.4.12 to **0.5.0**
  - [npm-groovy-lint](https://nvuillam.github.io/npm-groovy-lint/) from 11.0.0 to **11.1.1**
  - [phpstan](https://phpstan.org/) from 1.8.10 to **1.9.1**
  - [revive](https://revive.run/) from 0.0.0 to **1.2.4**
  - [rstfmt](https://github.com/dzhu/rstfmt) from 0.0.10 to **0.0.11**
  - [rubocop](https://rubocop.org/) from 1.37.0 to **1.38.0**
  - [secretlint](https://github.com/secretlint/secretlint) from 5.2.4 to **5.3.0**
  - [semgrep](https://semgrep.dev/) from 0.118.0 to **0.120.0**
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 2.13.9 to **3.6.2**
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 2.13.9 to **3.6.2**
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 2.13.9 to **3.6.2**
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.16.1 to **7.18.1**
  - [sqlfluff](https://www.sqlfluff.com/) from 1.3.2 to **1.4.1**
  - [stylelint](https://stylelint.io) from 14.14.0 to **14.14.1**
  - [syft](https://github.com/anchore/syft) from 0.59.0 to **0.60.3**
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.3.3 to **1.3.4**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.39.2 to **0.40.0**
  - [tflint](https://github.com/terraform-linters/tflint) from 0.41.0 to **0.42.1**
  - [yamllint](https://yamllint.readthedocs.io/) from 1.26.3 to **1.26.3**

## [v6.13.0] - 2022-10-24

- New [cupcake flavor](https://oxsecurity.github.io/megalinter/beta/flavors/cupcake/#readme) with 78 instead of 108 linters
- Don't add literal double quote character to filenames in mega-linter-runner ([#1942](https://github.com/oxsecurity/megalinter/issues/1942)).
- Remove default npm-groovy-lint extra arguments ([#1872](https://github.com/oxsecurity/megalinter/issues/1872))
- Replace yaml.load by yaml.safe_load for better security

- Linter versions upgrades
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 0.67.0 to **0.68.1**
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2022.10.05 to **2022.10.14**
  - [djlint](https://djlint.com/) from 1.19.1 to **1.19.2**
  - [eslint](https://eslint.org) from 8.25.0 to **8.26.0**
  - [git_diff](https://git-scm.com) from 2.34.4 to **2.34.5**
  - [gitleaks](https://github.com/zricethezav/gitleaks) from 8.14.1 to **8.15.0**
  - [golangci-lint](https://golangci-lint.run/) from 1.50.0 to **1.50.1**
  - [phpstan](https://phpstan.org/) from 1.8.9 to **1.8.10**
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.2.6 to **7.2.7**
  - [puppet-lint](http://puppet-lint.com/) from 3.0.0 to **3.0.1**
  - [pylint](https://pylint.pycqa.org) from 2.15.4 to **2.15.5**
  - [rubocop](https://rubocop.org/) from 1.36.0 to **1.37.0**
  - [semgrep](https://semgrep.dev/) from 0.117.0 to **0.118.0**
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.16.0 to **7.16.1**
  - [syft](https://github.com/anchore/syft) from 0.58.0 to **0.59.0**
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.3.2 to **1.3.3**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.39.1 to **0.39.2**
  - [terrascan](https://www.accurics.com/products/terrascan/) from 1.15.2 to **1.16.0**

## [v6.12.0] - 2022-10-16

- Add Makefile linter in go flavor
- Fix invalid Docker container names in .pre-commit-hooks.yaml ([#1932](https://github.com/oxsecurity/megalinter/issues/1932))
- Correct removeContainer casing in runner ([#1917](https://github.com/oxsecurity/megalinter/issues/1917))
- Fix use of TERRAFORM_KICS_ARGUMENTS ([#1947](https://github.com/oxsecurity/megalinter/issues/1947))
- Use -p argument for pyright custom config file path ([#1946](https://github.com/oxsecurity/megalinter/issues/1946))
- Fix incorrect link to pytype for pyright ([#1967](https://github.com/oxsecurity/megalinter/issues/1967))
- Deduplicate SHOW_ELAPSED_TIME properties to address v8r error ([#1962](https://github.com/oxsecurity/megalinter/issues/1962))

- Linter versions upgrades
  - [actionlint](https://rhysd.github.io/actionlint/) from 1.6.16 to **1.6.21**
  - [ansible-lint](https://ansible-lint.readthedocs.io/en/latest/) from 6.7.0 to **6.7.0**
  - [bicep_linter](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter) from 0.10.61 to **0.11.1**
  - [black](https://black.readthedocs.io/en/stable/) from 22.8.0 to **22.10.0**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 0.66.0 to **0.67.0**
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2022.09.08 to **2022.10.05**
  - [djlint](https://djlint.com/) from 1.18.0 to **1.19.1**
  - [eslint](https://eslint.org) from 8.24.0 to **8.25.0**
  - [gitleaks](https://github.com/zricethezav/gitleaks) from 8.13.0 to **8.14.1**
  - [golangci-lint](https://golangci-lint.run/) from 1.49.0 to **1.50.0**
  - [kics](https://www.kics.io) from 1.6.1 to **1.6.2**
  - [mypy](https://mypy.readthedocs.io/en/stable/) from 0.981 to **0.982**
  - [npm-groovy-lint](https://nvuillam.github.io/npm-groovy-lint/) from 10.1.0 to **11.0.0**
  - [phpstan](https://phpstan.org/) from 1.8.6 to **1.8.9**
  - [puppet-lint](http://puppet-lint.com/) from 2.5.2 to **3.0.0**
  - [pylint](https://pylint.pycqa.org) from 2.15.3 to **2.15.4**
  - [scalafix](https://scalacenter.github.io/scalafix/) from 0.10.3 to **0.10.4**
  - [semgrep](https://semgrep.dev/) from 0.115.0 to **0.117.0**
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.14.2 to **7.16.0**
  - [stylelint](https://stylelint.io) from 14.13.0 to **14.14.0**
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.3.1 to **1.3.2**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.39.0 to **0.39.1**

## [v6.11.1] - 2022-10-03

- Remove `no-space-check` from MegaLinter default `.pylintrc` file ([#1923](https://github.com/oxsecurity/megalinter/issues/1923))

## [v6.11.0] - 2022-10-02

- Linters
  - Add [bicep](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/linter) linter ([#1898](https://github.com/oxsecurity/megalinter/pull/1898))
  - Add quotes to arm-ttk linter command ([#1879](https://github.com/oxsecurity/megalinter/issues/1879))
  - Add Makefile linter in [java flavor](https://oxsecurity.github.io/megalinter/latest/flavors/java/)

- Core
  - Improve support for devcontainers by using Python base image
    - Fixed Python version in devcontainer from 3.9 -> 3.10
    - Fix build command on linux (thanks a lot to [Edouard Choinière](https://github.com/echoix) for the investigation and solution !)
  - Azure Comments reporter - Change status when all tests pass ([#1915](https://github.com/oxsecurity/megalinter/issues/1915))

- Doc
  - Document the `-f` argument to mega-linter-runner ([#1895](https://github.com/oxsecurity/megalinter/issues/1895))
  - Fix a typo in documentation of bash-exec linter ([#1892](https://github.com/oxsecurity/megalinter/pull/1892))

- Linter versions upgrades
  - [ansible-lint](https://ansible-lint.readthedocs.io/en/latest/) from 6.6.0 to **6.7.0**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 0.65.0 to **0.66.0**
  - [checkov](https://www.checkov.io/) from 2.1.213 to **2.1.244**
  - [checkstyle](https://checkstyle.sourceforge.io) from 10.3.3 to **10.3.4**
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.63 to **0.1.64**
  - [coffeelint](http://www.coffeelint.org) from 5.2.9 to **5.2.10**
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 6.10.0 to **6.12.0**
  - [djlint](https://djlint.com/) from 1.16.0 to **1.18.0**
  - [eslint](https://eslint.org) from 8.23.1 to **8.24.0**
  - [gitleaks](https://github.com/zricethezav/gitleaks) from 8.12.0 to **8.13.0**
  - [jsonlint](https://github.com/prantlf/jsonlint) from 11.6.0 to **11.7.0**
  - [kics](https://www.kics.io) from 1.6.0 to **1.6.1**
  - [markdown-link-check](https://github.com/tcort/markdown-link-check) from 3.10.2 to **3.10.3**
  - [mypy](https://mypy.readthedocs.io/en/stable/) from 0.971 to **0.981**
  - [phpstan](https://phpstan.org/) from 1.8.5 to **1.8.6**
  - [protolint](https://github.com/yoheimuta/protolint) from 0.40.0 to **0.41.0**
  - [scalafix](https://scalacenter.github.io/scalafix/) from 0.10.2 to **0.10.3**
  - [semgrep](https://semgrep.dev/) from 0.113.0 to **0.115.0**
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.14.0 to **7.14.2**
  - [sqlfluff](https://www.sqlfluff.com/) from 1.3.1 to **1.3.2**
  - [stylelint](https://stylelint.io) from 14.12.0 to **14.13.0**
  - [syft](https://github.com/anchore/syft) from 0.56.0 to **0.58.0**
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.2.9 to **1.3.1**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.38.12 to **0.39.0**
  - [tflint](https://github.com/terraform-linters/tflint) from 0.40.0 to **0.41.0**

## [v6.10.0] - 2022-09-19

- Add [git-lfs](https://git-lfs.github.com/) in Docker image to handle large files in git repositories

- MegaLinter Docker images size improvements
  - Remove NPM cache
  - Remove Cargo cache
  - Remove rustup when clippy isn't embedded in the image
  - Remove npm packages useless files

- Linter versions upgrades
  - [ansible-lint](https://ansible-lint.readthedocs.io/en/latest/) from 6.5.2 to **6.6.0**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 0.64.1 to **0.65.0**
  - [checkov](https://www.checkov.io/) from 2.1.201 to **2.1.213**
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 6.8.1 to **6.10.0**
  - [djlint](https://djlint.com/) from 1.12.3 to **1.16.0**
  - [eslint](https://eslint.org) from 8.23.0 to **8.23.1**
  - [kics](https://www.kics.io) from 1.5.15 to **1.6.0**
  - [pylint](https://www.pylint.org) from 2.15.2 to **2.15.3**
  - [scalafix](https://scalacenter.github.io/scalafix/) from 0.10.1 to **0.10.2**
  - [semgrep](https://semgrep.dev/) from 0.112.1 to **0.113.0**
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 2.13.8 to **2.13.9**
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 2.13.8 to **2.13.9**
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 2.13.8 to **2.13.9**
  - [stylelint](https://stylelint.io) from 14.11.0 to **14.12.0**
  - [syft](https://github.com/anchore/syft) from 0.55.0 to **0.56.0**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.38.10 to **0.38.12**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.38.9 to **0.38.10**
  - [yamllint](https://yamllint.readthedocs.io/) from 1.27.1 to **1.28.0**

## [v6.9.1] - 2022-09-11

- Linters
  - Add python type checker [pyright](https://github.com/microsoft/pyright), by Microsoft
  - New linters with available SARIF output for [SARIF Reporter](https://oxsecurity.github.io/megalinter/latest/reporters/SarifReporter/)
    - [ansible-lint](https://oxsecurity.github.io/megalinter/latest/descriptors/ansible_ansible_lint/)
    - [shellcheck](https://github.com/koalaman/shellcheck) thanks to [shellcheck-sarif](https://crates.io/crates/shellcheck-sarif)
  - Use `list_of_files` Cli lint mode for [checkstyle](https://oxsecurity.github.io/megalinter/latest/descriptors/java_checkstyle/), to have unique SARIF output and improve performances
  - Use `list_of_files` Cli lint mode for [golangci-lint](https://oxsecurity.github.io/megalinter/latest/descriptors/go_golangci_lint/) and [revive](https://oxsecurity.github.io/megalinter/latest/descriptors/go_revive/), to improve performances
  - Reactivate [snakefmt](https://oxsecurity.github.io/megalinter/latest/descriptors/snakemake_snakefmt/)

- Core
  - Improve build performances and docker images sizes (reduce from 117 to 36 layers)
    - Use BUILDKIT
    - Join RUN instructions
    - Optimize core Dockerfile items
    - Clean npm, python and cargo caches
  - Create a venv for each python-based linter to avoid issues with dependencies
  - Fix broken link to documentation when using v6

- Linter versions upgrades
  - [ansible-lint](https://ansible-lint.readthedocs.io/en/latest/) from 6.0.2 to **6.5.2**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 0.63.2 to **0.64.1**
  - [checkov](https://www.checkov.io/) from 2.1.183 to **2.1.201**
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2022.08.03 to **2022.09.08**
  - [djlint](https://djlint.com/) from 1.12.1 to **1.12.3**
  - [gitleaks](https://github.com/zricethezav/gitleaks) from 8.11.2 to **8.12.0**
  - [golangci-lint](https://golangci-lint.run/) from 1.48.0 to **1.49.0**
  - [ktlint](https://ktlint.github.io) from 0.47.0 to **0.47.1**
  - [phpstan](https://phpstan.org/) from 1.8.4 to **1.8.5**
  - [protolint](https://github.com/yoheimuta/protolint) from 0.39.0 to **0.40.0**
  - [pylint](https://www.pylint.org) from 2.15.0 to **2.15.2**
  - [semgrep](https://semgrep.dev/) from 0.103.0 to **0.112.1**
  - [sqlfluff](https://www.sqlfluff.com/) from 1.3.0 to **1.3.1**
  - [standard](https://standardjs.com/) from 15.0.1 to **17.0.0**
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.2.8 to **1.2.9**
  - [tflint](https://github.com/terraform-linters/tflint) from 0.39.3 to **0.40.0**

_Note: MegaLinter 6.9.0 release has been cancelled: it was fine but the docker image sizes were not optimized enough._

## [v6.8.0] - 2022-09-04

- Run MegaLinter pre-commit hooks serially (#1826).
- Replace deprecated StandardJS VS Code extension with the newer official version
- When SARIF_REPORTER is active, use [sarif-fmt](https://crates.io/crates/sarif-fmt) to convert SARIF into text for console and text reporters ([#1822](https://github.com/oxsecurity/megalinter/issues/1822)).
- Count checkstyle errors ([#1820](https://github.com/oxsecurity/megalinter/pull/1820))

- Linter versions upgrades
  - [black](https://black.readthedocs.io/en/stable/) from 22.6.0 to **22.8.0**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 0.63.0 to **0.63.2**
  - [checkov](https://www.checkov.io/) from 2.1.160 to **2.1.183**
  - [checkstyle](https://checkstyle.sourceforge.io) from 10.3.2 to **10.3.3**
  - [djlint](https://djlint.com/) from 1.12.0 to **1.12.1**
  - [kics](https://www.kics.io) from 1.5.14 to **1.5.15**
  - [phpstan](https://phpstan.org/) from 1.8.2 to **1.8.4**
  - [rubocop](https://rubocop.org/) from 1.35.1 to **1.36.0**
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.13.0 to **7.14.0**
  - [syft](https://github.com/anchore/syft) from 0.54.0 to **0.55.0**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.38.8 to **0.38.9**

## [v6.7.1] - 2022-08-28

- Fix Azure Comments reporter: Use BuildId to build artifacts url
- Fix actionlint install command

## [v6.7.0] - 2022-08-28

- Linters
  - Add [PMD](https://pmd.github.io/latest/) java linter

- [Azure Pipelines](https://azure.microsoft.com/en-us/services/devops/pipelines/) integration enhancements
  - Update [installation instructions](https://oxsecurity.github.io/megalinter/latest/installation/#azure-pipelines)
  - Console reporter: manage collapsible groups for easier display & navigation in job logs (requires CI=true and TF_BUILD=true sent as env variables)
  - Azure comments reporter (see [documentation](https://oxsecurity.github.io/megalinter/latest/reporters/AzureCommentReporter/))

- Performances improvements
  - When running linters in parallel, run in the same process only the linters from same descriptor and that can update the same sources (to avoid concurrency). Other linters can be run independently.
  - Define `linter_speed` of linter descriptors (default 3). Can be from 1 (super slow) to 5 (super fast). This is used to optimize the processing order of linters.

- Fixes
  - Fix: Properly match `files_sub_directory` as a prefix instead of partial string matching ([#1765](https://github.com/oxsecurity/megalinter/pull/1765))
  - Match regex without `workspace` and `sub_directory`
  - Remove config variables that aren't applicable to linters analyzing all files or all other linters files

- Linter versions upgrades
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 0.62.0 to **0.63.0**
  - [checkov](https://www.checkov.io/) from 2.1.139 to **2.1.160**
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 6.8.0 to **6.8.1**
  - [djlint](https://djlint.com/) from 1.11.0 to **1.12.0**
  - [eslint](https://eslint.org) from 8.22.0 to **8.23.0**
  - [gitleaks](https://github.com/zricethezav/gitleaks) from 8.11.0 to **8.11.2**
  - [golangci-lint](https://golangci-lint.run/) from 1.48.0 to **1.49.0**
  - [luacheck](https://luacheck.readthedocs.io) from 0.26.1 to **1.0.0**
  - [pylint](https://www.pylint.org) from 2.14.5 to **2.15.0**
  - [rubocop](https://rubocop.org/) from 1.35.0 to **1.35.1**
  - [secretlint](https://github.com/secretlint/secretlint) from 5.2.3 to **5.2.4**
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.12.1 to **7.13.0**
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.2.7 to **1.2.8**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.38.7 to **0.38.8**
  - [tflint](https://github.com/terraform-linters/tflint) from 0.35.0 to **0.39.3**

## [v6.6.0] - 2022-08-21

- Fix flavors suggestions to ignore linters not relevant for such flavor ([#1746](https://github.com/oxsecurity/megalinter/issues/1746))
- Update pre-commit hooks from v5 to v6 ([#1755](https://github.com/oxsecurity/megalinter/issues/1755)).
- Fix version in URL in logs produced by reporters
- Add Makefile linter within python flavor ([#1760](https://github.com/oxsecurity/megalinter/issues/1760))
- Set DEFAULT_WORKSPACE as git safe directory per default [#1766](https://github.com/oxsecurity/megalinter/issues/1766)
- Improve documentation for TAP_REPORTER

- Linter versions upgrades
  - [actionlint](https://rhysd.github.io/actionlint/) from 1.6.15 to **1.6.16**
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 0.61.5 to **0.62.0**
  - [checkov](https://www.checkov.io/) from 2.1.127 to **2.1.139**
  - [cpplint](https://github.com/cpplint/cpplint) from 1.6.0 to **1.6.1**
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 6.6.1 to **6.8.0**
  - [djlint](https://djlint.com/) from 1.9.5 to **1.11.0**
  - [eslint-plugin-jsonc](https://ota-meshi.github.io/eslint-plugin-jsonc/) from 2.3.1 to **2.4.0**
  - [gitleaks](https://github.com/zricethezav/gitleaks) from 8.10.3 to **8.11.0**
  - [kics](https://www.kics.io) from 1.5.13 to **1.5.14**
  - [ktlint](https://ktlint.github.io) from 0.46.1 to **0.47.0**
  - [markdownlint](https://github.com/DavidAnson/markdownlint) from 0.32.1 to **0.32.2**
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 2.13.7 to **2.13.8**
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 2.13.7 to **2.13.8**
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 2.13.7 to **2.13.8**
  - [sqlfluff](https://www.sqlfluff.com/) from 1.2.1 to **1.3.0**
  - [stylelint](https://stylelint.io) from 14.10.0 to **14.11.0**
  - [syft](https://github.com/anchore/syft) from 0.53.4 to **0.54.0**

## [v6.5.0] - 2022-08-15

- npm-groovy-lint: Use Cli lint mode `list_of_files` for much better performances
- Disable proselint by default if .proselintrc file isn't found

- Linter versions upgrades
  - [checkov](https://www.checkov.io/) from 2.1.121 to **2.1.127**
  - [eslint](https://eslint.org) from 8.21.0 to **8.22.0**
  - [gitleaks](https://github.com/zricethezav/gitleaks) from 8.10.2 to **8.10.3**
  - [npm-groovy-lint](https://nvuillam.github.io/npm-groovy-lint/) from 9.5.0 to **10.1.0**
  - [rstcheck](https://github.com/myint/rstcheck) from 6.0.0 to **6.1.0**

## [v6.4.0] - 2022-08-12

- Add REPOSITORY_CHECKOV in all flavors

- New config variables
  - **MEGALINTER_FILES_TO_LINT**: Comma-separated list of files to analyze. Using this variable will bypass other file listing methods ([#808](https://github.com/oxsecurity/megalinter/issues/808))
  - **SKIP_CLI_LINT_MODES**: Comma-separated list of cli_lint_modes. To use if you want to skip linters with some CLI lint modes (ex: `file,project`). Available values: `file`,`cli_lint_mode`,`project`.

- mega-linter-runner:
  - Allow `MEGALINTER_FILES_TO_LINT` to be sent as positional arguments
  - New argument `--filesonly` that sends `SKIP_CLI_LINT_MODES=project`
  - Example: `mega-linter-runner --flavor python --release beta --filesonly megalinter/config.py megalinter/flavor_factory.py megalinter/MegaLinter.py`

- Fixes
  - Fix SARIF when a run is missing a results list ([#1725](https://github.com/oxsecurity/megalinter/issues/1725))
  - Fix missing quotes for Powershell script analyzer ([#1728](https://github.com/oxsecurity/megalinter/issues/1728))

- Linter versions upgrades
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 0.61.4 to **0.61.5**
  - [checkov](https://www.checkov.io/) from 2.1.100 to **2.1.121**
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.62 to **0.1.63**
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 6.5.0 to **6.6.1**
  - [gitleaks](https://github.com/zricethezav/gitleaks) from 8.10.1 to **8.10.1**
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.2.5 to **7.2.6**
  - [protolint](https://github.com/yoheimuta/protolint) from 0.38.3 to **0.39.0**
  - [rubocop](https://rubocop.org/) from 1.33.0 to **1.35.0**
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.12.0 to **7.12.1**
  - [stylelint](https://stylelint.io) from 14.9.1 to **14.10.0**
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.2.6 to **1.2.7**
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.38.6 to **0.38.7**

## [v6.3.0] - 2022-08-07

- Linters

  - Add REPOSITORY_CHECKOV to benefit from all checks and not only terraform ones. TERRAFORM_CHECKOV will be deprecated in a next major version
  - Add [djlint](https://www.djlint.com/) (HTML_DJLINT) to lint HTML files (html, django, jinja, nunjucks, handlebars, golang, angular)
  - Upgrade jsonlint to use maintained package @prantlf/jsonlint]([<https://www.npmjs.com/package/@prantlf/jsonlint>) + use cli_lint_mode `list_of_files` to improve performances

- Core
  - Support for automatic removal of Docker container when linting is finished
  - Fix SARIF when endColumn is 0 ([#1702](https://github.com/oxsecurity/megalinter/issues/1702))
  - Use dynamic REPORT_FOLDER value for output files for SALESFORCE and COPYPASTE descriptors
  - Fix collapsible sections in Gitlab console logs
  - Manage ignore files (like `.secretlintignore` or `.eslintignore`)
    - Define ignore argument for client in descriptors
    - Define ignore file name in descriptors (overridable with _IGNORE_FILE_NAME at runtime)
    - Update documentation generation to take in account this new configuration

- Linter versions upgrades
  - [checkov](https://www.checkov.io/) from 2.1.83 to **2.1.98**
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2022.04.25 to **2022.08.03**
  - [eslint](https://eslint.org) from 8.20.0 to **8.21.0**
  - [flake8](https://flake8.pycqa.org) from 5.0.1 to **5.0.2**
  - [golangci-lint](https://golangci-lint.run/) from 1.47.2 to **1.48.0**
  - [jsonlint](https://github.com/prantlf/jsonlint) from 1.6.3 to **11.6.0**
  - [kics](https://www.kics.io) from 1.5.12 to **1.5.13**
  - [rubocop](https://rubocop.org/) from 1.32.0 to **1.33.0**
  - [syft](https://github.com/anchore/syft) from 0.52.0 to **0.53.4**

## [v6.2.1] - 2022-08-01

- Fix blocking bug in MegaLinter v6.2.0 core ([#1684](https://github.com/oxsecurity/megalinter/issues/1684) and [#1685](https://github.com/oxsecurity/megalinter/issues/1685))

- Linter versions upgrades
  - [checkstyle](https://checkstyle.sourceforge.io) from 10.3.1 to **10.3.2** on 2022-08-01
  - [flake8](https://flake8.pycqa.org) from 5.0.0 to **5.0.1** on 2022-08-01
  - [checkov](https://www.checkov.io/) from 2.1.82 to **2.1.83** on 2022-08-01

## [v6.2.0] - 2022-07-31

- Core
  - Fix mega-linter-runner --install template [(#1662)](https://github.com/oxsecurity/megalinter/issues/1662)
  - Use `REPORT_OUTPUT_FOLDER: none` to not generate report files
  - Add info in doc about CLI_LINT_MODE and about how to ignore files when cli_lint_mode is `project`
  - Fix bug that disables generation of `megalinter.log` file in most cases
  - Fixes about JSON Schema [(#1621)](https://github.com/oxsecurity/megalinter/issues/1621)
  - Remove redundant line separator after generated table [(#1650)](https://github.com/oxsecurity/megalinter/pull/1650)
  - Avoid flavor suggestion message when only REPOSITORY linters aren't found

- Linters
  - Add [checkmake](https://github.com/mrtazz/checkmake) to lint Makefile
  - Disable SemGrep by default if `REPOSITORY_SEMGREP_RULESETS` isn't defined.
  - Avoid cspell to lint all files. Lint only other linter files [(#1648)](https://github.com/oxsecurity/megalinter/issues/1648)
  - Fix revive installation command
  - New default config for gitleaks with `useDefault=true`

- Linter versions upgrades
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 0.61.3 to **0.61.4** on 2022-07-30
  - [checkov](https://www.checkov.io/) from 2.1.60 to **2.1.61** on 2022-07-19
  - [checkov](https://www.checkov.io/) from 2.1.61 to **2.1.63** on 2022-07-20
  - [checkov](https://www.checkov.io/) from 2.1.63 to **2.1.65** on 2022-07-21
  - [checkov](https://www.checkov.io/) from 2.1.65 to **2.1.67** on 2022-07-21
  - [checkov](https://www.checkov.io/) from 2.1.67 to **2.1.68** on 2022-07-23
  - [checkov](https://www.checkov.io/) from 2.1.68 to **2.1.69** on 2022-07-24
  - [checkov](https://www.checkov.io/) from 2.1.69 to **2.1.70** on 2022-07-24
  - [checkov](https://www.checkov.io/) from 2.1.70 to **2.1.74** on 2022-07-25
  - [checkov](https://www.checkov.io/) from 2.1.74 to **2.1.82** on 2022-07-30
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 6.3.0 to **6.4.0** on 2022-07-19
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 6.4.0 to **6.4.1** on 2022-07-24
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 6.4.1 to **6.5.0** on 2022-07-30
  - [flake8](https://flake8.pycqa.org) from 4.0.1 to **5.0.0** on 2022-07-31
  - [gitleaks](https://github.com/zricethezav/gitleaks) from 8.8.12 to **8.9.0** on 2022-07-30
  - [golangci-lint](https://golangci-lint.run/) from 1.47.0 to **1.47.1** on 2022-07-19
  - [golangci-lint](https://golangci-lint.run/) from 1.47.1 to **1.47.2** on 2022-07-21
  - [jscpd](https://github.com/kucherenko/jscpd/tree/master/packages/jscpd) from 3.4.5 to **3.3.26** on 2022-07-19
  - [markdown-table-formatter](https://www.npmjs.com/package/markdown-table-formatter) from 1.3.0 to **1.4.0** on 2022-07-25
  - [markdownlint](https://github.com/DavidAnson/markdownlint) from 0.32.0 to **0.32.1** on 2022-07-25
  - [mypy](https://mypy.readthedocs.io/en/stable/) from 0.961 to **0.971** on 2022-07-19
  - [phpstan](https://phpstan.org/) from 1.8.1 to **1.8.2** on 2022-07-20
  - [rubocop](https://rubocop.org/) from 1.31.2 to **1.32.0** on 2022-07-21
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 2.13.5 to **2.13.6** on 2022-07-21
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 2.13.6 to **2.13.7** on 2022-07-30
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 2.13.5 to **2.13.6** on 2022-07-21
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 2.13.6 to **2.13.7** on 2022-07-30
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 2.13.5 to **2.13.6** on 2022-07-21
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 2.13.6 to **2.13.7** on 2022-07-30
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.8.5 to **7.9.0** on 2022-07-19
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.9.0 to **7.12.0** on 2022-07-30
  - [syft](https://github.com/anchore/syft) from 0.51.0 to **0.52.0** on 2022-07-22
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.2.5 to **1.2.6** on 2022-07-30
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.38.5 to **0.38.6** on 2022-07-24

## [v6.1.0] - 2022-07-19

- Improve console logs by using collapsible sections in GitHub Actions and Gitlab CI (disable by defining `CONSOLE_REPORTER_SECTIONS: false`)
- Define `CLEAR_REPORT_FOLDER=true` to empty report folder at the beginning of each run ([#1502](https://github.com/oxsecurity/megalinter/issues/1502))
- Improve SARIF output
  - Replace CI paths in logs
  - Add missing required properties so SARIF is [valid](https://sarifweb.azurewebsites.net/Validation)
  - Add MegaLinter information in SARIF linter runs
  - Allow to select linters to activate SARIF for, using SARIF_REPORTER_LINTERS
  - Fix issue when a linter is used in multiple SARIF lint results

- Linter versions upgrades
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 0.61.2 to **0.61.3** on 2022-07-19
  - [checkov](https://www.checkov.io/) from 2.1.57 to **2.1.59** on 2022-07-18
  - [checkov](https://www.checkov.io/) from 2.1.59 to **2.1.60** on 2022-07-19
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 6.2.3 to **6.3.0** on 2022-07-18
  - [eslint](https://eslint.org) from 8.19.0 to **8.20.0** on 2022-07-17
  - [golangci-lint](https://golangci-lint.run/) from 1.46.2 to **1.47.0** on 2022-07-19
  - [jscpd](https://github.com/kucherenko/jscpd/tree/master/packages/jscpd) from 3.3.26 to **3.4.5** on 2022-07-19
  - [markdownlint](https://github.com/DavidAnson/markdownlint) from 0.31.1 to **0.32.0** on 2022-07-17
  - [pylint](https://www.pylint.org) from 2.14.4 to **2.14.5** on 2022-07-18

## [v6.0.5] - 2022-07-16

- Fix mega-linter-runner --upgrade so it also updates report folder to megalinter-reports in GitHub Actions Workflows [#1609](https://github.com/oxsecurity/megalinter/issues/1609)
- Fix documentation and templates to use `megalinter-reports` folder everywhere
- Workaround for python-markdown issue <https://github.com/radude/mdx_truly_sane_lists/issues/9>

- Linter versions upgrades
  - [checkov](https://www.checkov.io/) from 2.1.54 to **2.1.56** on 2022-07-15
  - [checkov](https://www.checkov.io/) from 2.1.56 to **2.1.57** on 2022-07-16
  - [gitleaks](https://github.com/zricethezav/gitleaks) from 8.8.7 to **8.8.12** on 2022-07-16
  - [kics](https://www.kics.io) from 1.5.11 to **1.5.12** on 2022-07-16
  - [protolint](https://github.com/yoheimuta/protolint) from 0.38.2 to **0.38.3** on 2022-07-15
  - [sqlfluff](https://www.sqlfluff.com/) from 1.2.0 to **1.2.1** on 2022-07-16
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.2.4 to **1.2.5** on 2022-07-15
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.38.4 to **0.38.5** on 2022-07-15

## [v6.0.4] - 2022-07-14

- Fix count of errors when using SARIF reporter
- DevSkim: Ignore megalinter-reports by default [(#1603)](https://github.com/oxsecurity/megalinter/issues/1603)
- Load JSON when list of objects is defined in an ENV var [(#1605)](https://github.com/oxsecurity/megalinter/issues/1605)
- AutoFix pre_commands using `npm install` [(1258)](https://github.com/oxsecurity/megalinter/issues/1258)

- Linter versions upgrades
  - [checkov](https://www.checkov.io/) from 2.1.43 to **2.1.54** on 2022-07-14
  - [git_diff](https://git-scm.com) from 2.34.2 to **2.34.4** on 2022-07-14
  - [phpstan](https://phpstan.org/) from 1.8.0 to **1.8.1** on 2022-07-14
  - [sqlfluff](https://www.sqlfluff.com/) from 1.1.0 to **1.2.0** on 2022-07-14
  - [syft](https://github.com/anchore/syft) from 0.50.0 to **0.51.0** on 2022-07-14

## [v6.0.3] - 2022-07-11

- mega-linter-runner: Update query args when opening OX Security
- Fix mega-linter-runner doesn't default to v6 for flavors [(1596)](https://github.com/oxsecurity/megalinter/issues/1596)

## [v6.0.0] - 2022-07-10

- Breaking changes: you must run `npx mega-linter-runner --upgrade` to use MegaLinter v6

- Core architecture
  - New reporter **SARIF_REPORTER** that aggregates all SARIF output files into a single one
    - Correct SARIF files for known format errors
  - New config variable **DISABLE_LINTERS_ERRORS** to define a list of linters that will be considered as non blocking
  - Upgrade base docker image to python:3.10.4-alpine3.15
  - Rename default report folder from `report` to `megalinter-reports`
  - Display GitHub stars in linters summary table in documentation

- Linters:
  - Add [DevSkim](https://github.com/microsoft/DevSkim) security linter by Microsoft
  - Add [dustilock](https://github.com/Checkmarx/dustilock) to check for dependency confusion attacks with node and python packages
  - Add [gitleaks](https://github.com/zricethezav/gitleaks) to lint git repository
  - Add [goodcheck](https://github.com/sider/goodcheck) as regex-based linter
  - Add [PMD](https://pmd.github.io/) to lint java files (disabled for now)
  - Add [semgrep](https://github.com/returntocorp/semgrep) as regex-based linter with many community rules
  - Add [syft](https://github.com/anchore/syft) to generate SBOM (Software Bill Of Materials)
  - Add [trivy](https://github.com/aquasecurity/trivy) security linter
  - Remove **dockerfilelint**, as it'sn't maintained anymore and hadolint contains all its rules
  - Remove **rstfmt** as it'sn't maintained anymore
  - SARIF management for:
    - bandit
    - checkov
    - checkstyle
    - cfn-lint
    - devskim
    - eslint
    - gitleaks
    - hadolint
    - ktlint
    - npm-groovy-lint
    - psalm
    - semgrep
    - secretlint
    - revive
    - terrascan
    - tflint
    - trivy

- Descriptors:
  - New flavor **Security**
  - New descriptor **repository**: contains DevSkim, dustilock, gitleaks, secretlint, semgrep, syft, trivy
  - Remove CREDENTIALS and GIT descriptors

- mega-linter-runner
  - `--upgrade` option can now upgrade repos MegaLinter config to v6
  - Create/update local `.gitignore` file when installing / updating MegaLinter using mega-linter-runner
  - Propose to test ox.security service
  - Switch from npm to yarn

- Dev architecture
  - Manage offline run of `bash build.sh` for those who want to code in planes :)
  - Automate update of CHANGELOG.md after release (beta)
  - Accelerate internal CI testing performances

- Linter versions upgrades
  - [actionlint](https://rhysd.github.io/actionlint/) from 1.6.13 to **1.6.15** on 2022-07-10
  - [black](https://black.readthedocs.io/en/stable/) from 22.3.0 to **22.6.0** on 2022-07-10
  - [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) from 0.61.1 to **0.61.2** on 2022-07-10
  - [checkov](https://www.checkov.io/) from 3.9 to **2.1.43** on 2022-07-10
  - [checkstyle](https://checkstyle.sourceforge.io) from 10.3 to **10.3.1** on 2022-07-10
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.61 to **0.1.62** on 2022-07-10
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 6.1.2 to **6.2.3** on 2022-07-10
  - [eslint-plugin-jsonc](https://ota-meshi.github.io/eslint-plugin-jsonc/) from 2.3.0 to **2.3.1** on 2022-07-10
  - [eslint](https://eslint.org) from 8.18.0 to **8.19.0** on 2022-07-10
  - [git_diff](https://git-scm.com) from 2.30.3 to **2.34.2** on 2022-07-10
  - [phpstan](https://phpstan.org/) from 1.7.15 to **1.8.0** on 2022-07-10
  - [pylint](https://www.pylint.org) from 2.14.3 to **2.14.4** on 2022-07-10
  - [rubocop](https://rubocop.org/) from 1.30.1 to **1.31.2** on 2022-07-10
  - [secretlint](https://github.com/secretlint/secretlint) from 4.1.0 to **5.2.3** on 2022-07-10
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.8.3 to **7.8.5** on 2022-07-10
  - [spectral](https://meta.stoplight.io/docs/spectral/README.md) from 5.6.0 to **5.9.2** on 2022-07-10
  - [sqlfluff](https://www.sqlfluff.com/) from 1.0.0 to **1.1.0** on 2022-07-10
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.2.3 to **1.2.4** on 2022-07-10
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.38.1 to **0.38.4** on 2022-07-10
  - [terrascan](https://www.accurics.com/products/terrascan/) from 1.14.0 to **1.15.2** on 2022-07-10
  - [v8r](https://github.com/chris48s/v8r) from 0.6.1 to **0.13.0** on 2022-07-10
  - [yamllint](https://yamllint.readthedocs.io/) from 1.26.3 to **1.27.1** on 2022-07-10

## [v5.17.0] - 2022-07-10

- Message to propose users to upgrade to v6

## [v5.16.1] - 2022-06-26

- Quick fix release management

## [v5.16.0] - 2022-06-26

- Support for named Docker container.

- Linter versions upgrades
  - [checkov](https://www.checkov.io/) from 2.0.1230 to **2.1.0** on 2022-06-23
  - [checkov](https://www.checkov.io/) from 2.1.0 to **2.1.5** on 2022-06-24
  - [checkov](https://www.checkov.io/) from 2.1.5 to **2.1.7** on 2022-06-25
  - [checkov](https://www.checkov.io/) from 2.1.7 to **3.9** on 2022-06-26
  - [kics](https://www.kics.io) from 1.5.10 to **1.5.11** on 2022-06-23
  - [protolint](https://github.com/yoheimuta/protolint) from 0.38.1 to **0.38.2** on 2022-06-26
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 2.13.4 to **2.13.5** on 2022-06-23
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 2.13.4 to **2.13.5** on 2022-06-23
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 2.13.4 to **2.13.5** on 2022-06-23
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.38.0 to **0.38.1** on 2022-06-23

## [v5.15.0] - 2022-06-23

- [OX Security](https://www.ox.security/?ref=megalinter) branding and [pre-announcement](https://github.com/megalinter/megalinter/issues/1549)
- Linter versions upgrades
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.61.0 to **0.61.1** on 2022-06-22
  - [checkov](https://www.checkov.io/) from 2.0.1209 to **2.0.1210** on 2022-06-14
  - [checkov](https://www.checkov.io/) from 2.0.1210 to **2.0.1212** on 2022-06-15
  - [checkov](https://www.checkov.io/) from 2.0.1212 to **2.0.1217** on 2022-06-15
  - [checkov](https://www.checkov.io/) from 2.0.1217 to **2.0.1218** on 2022-06-17
  - [checkov](https://www.checkov.io/) from 2.0.1218 to **2.0.1219** on 2022-06-19
  - [checkov](https://www.checkov.io/) from 2.0.1219 to **2.0.1226** on 2022-06-22
  - [checkov](https://www.checkov.io/) from 2.0.1226 to **2.0.1230** on 2022-06-22
  - [eslint](https://eslint.org) from 8.17.0 to **8.18.0** on 2022-06-19
  - [ktlint](https://ktlint.github.io) from 0.45.2 to **0.46.0** on 2022-06-19
  - [ktlint](https://ktlint.github.io) from 0.46.0 to **0.46.1** on 2022-06-22
  - [phpcs](https://github.com/squizlabs/PHP_CodeSniffer) from 3.6.2 to **3.7.0** on 2022-06-14
  - [phpcs](https://github.com/squizlabs/PHP_CodeSniffer) from 3.7.0 to **3.7.1** on 2022-06-19
  - [phpstan](https://phpstan.org/) from 1.7.12 to **1.7.13** on 2022-06-14
  - [phpstan](https://phpstan.org/) from 1.7.13 to **1.7.14** on 2022-06-15
  - [phpstan](https://phpstan.org/) from 1.7.14 to **1.7.15** on 2022-06-22
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.2.4 to **7.2.5** on 2022-06-22
  - [prettier](https://prettier.io/) from 2.6.2 to **2.7.0** on 2022-06-15
  - [prettier](https://prettier.io/) from 2.7.0 to **2.7.1** on 2022-06-17
  - [pylint](https://www.pylint.org) from 2.14.1 to **2.14.2** on 2022-06-15
  - [pylint](https://www.pylint.org) from 2.14.2 to **2.14.3** on 2022-06-19
  - [snakefmt](https://github.com/snakemake/snakefmt) from 0.6.0 to **0.6.1** on 2022-06-14
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.8.2 to **7.8.3** on 2022-06-22
  - [sql-lint](https://github.com/joereynolds/sql-lint) from 0.0.19 to **0.0.20** on 2022-06-19
  - [sql-lint](https://github.com/joereynolds/sql-lint) from 0.0.20 to **1.0.0** on 2022-06-22
  - [sqlfluff](https://www.sqlfluff.com/) from 0.13.2 to **1.0.0** on 2022-06-19
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.2.2 to **1.2.3** on 2022-06-17
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.37.3 to **0.37.4** on 2022-06-15
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.37.4 to **0.38.0** on 2022-06-19

## [v5.14.0] - 2022-06-12

- Local plugins support & documentation
- Update R lintr documentation

- Linter versions upgrades
  - [actionlint](https://rhysd.github.io/actionlint/) from 1.6.12 to **1.6.13** on 2022-05-20
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.60.0 to **0.60.1** on 2022-05-20
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.60.1 to **0.61.0** on 2022-06-01
  - [checkov](https://www.checkov.io/) from 2.0.1141 to **2.0.1143** on 2022-05-17
  - [checkov](https://www.checkov.io/) from 2.0.1143 to **2.0.1147** on 2022-05-20
  - [checkov](https://www.checkov.io/) from 2.0.1147 to **2.0.1150** on 2022-05-22
  - [checkov](https://www.checkov.io/) from 2.0.1150 to **2.0.1158** on 2022-05-24
  - [checkov](https://www.checkov.io/) from 2.0.1158 to **2.0.1159** on 2022-05-24
  - [checkov](https://www.checkov.io/) from 2.0.1159 to **2.0.1161** on 2022-05-25
  - [checkov](https://www.checkov.io/) from 2.0.1161 to **2.0.1162** on 2022-05-27
  - [checkov](https://www.checkov.io/) from 2.0.1162 to **2.0.1174** on 2022-05-30
  - [checkov](https://www.checkov.io/) from 2.0.1174 to **2.0.1175** on 2022-05-31
  - [checkov](https://www.checkov.io/) from 2.0.1175 to **2.0.1177** on 2022-05-31
  - [checkov](https://www.checkov.io/) from 2.0.1177 to **2.0.1182** on 2022-05-31
  - [checkov](https://www.checkov.io/) from 2.0.1182 to **2.0.1185** on 2022-06-02
  - [checkov](https://www.checkov.io/) from 2.0.1185 to **2.0.1188** on 2022-06-03
  - [checkov](https://www.checkov.io/) from 2.0.1188 to **2.0.1206** on 2022-06-08
  - [checkov](https://www.checkov.io/) from 2.0.1206 to **2.0.1207** on 2022-06-09
  - [checkov](https://www.checkov.io/) from 2.0.1207 to **2.0.1209** on 2022-06-10
  - [checkstyle](https://checkstyle.sourceforge.io) from 10.2 to **10.3** on 2022-05-30
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.60 to **0.1.61** on 2022-05-20
  - [coffeelint](http://www.coffeelint.org) from 5.2.8 to **5.2.9** on 2022-05-17
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.20.0 to **5.21.0** on 2022-05-20
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.21.0 to **5.21.1** on 2022-05-21
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.21.1 to **6.0.0** on 2022-05-22
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 6.0.0 to **6.1.0** on 2022-05-31
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 6.1.0 to **6.1.1** on 2022-06-03
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 6.1.1 to **6.1.2** on 2022-06-09
  - [eslint-plugin-jsonc](https://ota-meshi.github.io/eslint-plugin-jsonc/) from 2.2.1 to **2.3.0** on 2022-05-28
  - [eslint](https://eslint.org) from 8.15.0 to **8.16.0** on 2022-05-21
  - [eslint](https://eslint.org) from 8.16.0 to **8.17.0** on 2022-06-08
  - [golangci-lint](https://golangci-lint.run/) from 1.46.1 to **1.46.2** on 2022-05-20
  - [graphql-schema-linter](https://github.com/cjoudrey/graphql-schema-linter) from 3.0.0 to **3.0.1** on 2022-05-22
  - [kics](https://www.kics.io) from 1.5.8 to **1.5.9** on 2022-05-27
  - [kics](https://www.kics.io) from 1.5.9 to **1.5.10** on 2022-06-09
  - [mypy](https://mypy.readthedocs.io/en/stable/) from 0.950 to **0.960** on 2022-05-27
  - [mypy](https://mypy.readthedocs.io/en/stable/) from 0.960 to **0.961** on 2022-06-08
  - [phpstan](https://phpstan.org/) from 1.6.8 to **1.6.9** on 2022-05-22
  - [phpstan](https://phpstan.org/) from 1.6.9 to **1.7.0** on 2022-05-24
  - [phpstan](https://phpstan.org/) from 1.7.0 to **1.7.1** on 2022-05-24
  - [phpstan](https://phpstan.org/) from 1.7.1 to **1.7.2** on 2022-05-27
  - [phpstan](https://phpstan.org/) from 1.7.11 to **1.7.12** on 2022-06-09
  - [phpstan](https://phpstan.org/) from 1.7.2 to **1.7.3** on 2022-05-30
  - [phpstan](https://phpstan.org/) from 1.7.3 to **1.7.6** on 2022-05-31
  - [phpstan](https://phpstan.org/) from 1.7.6 to **1.7.7** on 2022-05-31
  - [phpstan](https://phpstan.org/) from 1.7.7 to **1.7.8** on 2022-06-02
  - [phpstan](https://phpstan.org/) from 1.7.8 to **1.7.9** on 2022-06-03
  - [phpstan](https://phpstan.org/) from 1.7.9 to **1.7.11** on 2022-06-08
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.2.3 to **7.2.4** on 2022-05-20
  - [pylint](https://www.pylint.org) from 2.13.9 to **2.14.0** on 2022-06-02
  - [pylint](https://www.pylint.org) from 2.14.0 to **2.14.1** on 2022-06-08
  - [rstcheck](https://github.com/myint/rstcheck) from 5.0.0 to **6.0.0** on 2022-06-08
  - [rubocop](https://rubocop.org/) from 1.29.1 to **1.30.0** on 2022-05-27
  - [rubocop](https://rubocop.org/) from 1.30.0 to **1.30.1** on 2022-06-08
  - [scalafix](https://scalacenter.github.io/scalafix/) from 0.10.0 to **0.10.1** on 2022-06-10
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 2.13.2 to **2.13.4** on 2022-05-27
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 2.13.2 to **2.13.4** on 2022-05-27
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 2.13.2 to **2.13.4** on 2022-05-27
  - [shfmt](https://github.com/mvdan/sh) from 3.5.0 to **3.6.0** on 2022-05-24
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.6.2 to **7.7.0** on 2022-05-17
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.7.0 to **7.8.0** on 2022-05-24
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.8.0 to **7.8.1** on 2022-05-31
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.8.1 to **7.8.2** on 2022-06-08
  - [sqlfluff](https://www.sqlfluff.com/) from 0.13.1 to **0.13.2** on 2022-05-21
  - [stylelint](https://stylelint.io) from 14.8.2 to **14.8.3** on 2022-05-22
  - [stylelint](https://stylelint.io) from 14.8.3 to **14.8.4** on 2022-05-25
  - [stylelint](https://stylelint.io) from 14.8.4 to **14.8.5** on 2022-05-27
  - [stylelint](https://stylelint.io) from 14.8.5 to **14.9.0** on 2022-06-09
  - [stylelint](https://stylelint.io) from 14.9.0 to **14.9.1** on 2022-06-11
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.1.9 to **1.2.0** on 2022-05-20
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.2.0 to **1.2.1** on 2022-05-24
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.2.1 to **1.2.2** on 2022-06-03
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.37.1 to **0.37.2** on 2022-06-09
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.37.2 to **0.37.3** on 2022-06-12

## [v5.13.0] - 2022-05-15

- Add gherkin-lint in dotnet flavor ([#1435](https://github.com/megalinter/megalinter/issues/1435))
- Define pre-commit hooks ([#569](https://github.com/megalinter/megalinter/issues/569)).
- Pin ansible-lint to 6.0.2 to fix pip dependency conflict between jsonschema versions ([#1470](https://github.com/megalinter/megalinter/issues/1470)).
- Use docker image for editorconfig-checker
- Update sqlfluff descriptor properties to enable error count([#1460](https://github.com/megalinter/megalinter/issues/1460))

- Linter versions upgrades
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.59.0 to **0.59.1** on 2022-05-03
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.59.1 to **0.60.0** on 2022-05-14
  - [checkov](https://www.checkov.io/) from 2.0.1076 to **2.0.1079** on 2022-04-24
  - [checkov](https://www.checkov.io/) from 2.0.1079 to **2.0.1084** on 2022-04-26
  - [checkov](https://www.checkov.io/) from 2.0.1084 to **2.0.1088** on 2022-04-28
  - [checkov](https://www.checkov.io/) from 2.0.1088 to **2.0.1098** on 2022-04-29
  - [checkov](https://www.checkov.io/) from 2.0.1098 to **2.0.1100** on 2022-04-30
  - [checkov](https://www.checkov.io/) from 2.0.1100 to **2.0.1102** on 2022-05-02
  - [checkov](https://www.checkov.io/) from 2.0.1102 to **2.0.1108** on 2022-05-03
  - [checkov](https://www.checkov.io/) from 2.0.1108 to **2.0.1110** on 2022-05-03
  - [checkov](https://www.checkov.io/) from 2.0.1110 to **2.0.1113** on 2022-05-05
  - [checkov](https://www.checkov.io/) from 2.0.1113 to **2.0.1118** on 2022-05-06
  - [checkov](https://www.checkov.io/) from 2.0.1118 to **2.0.1119** on 2022-05-07
  - [checkov](https://www.checkov.io/) from 2.0.1119 to **2.0.1120** on 2022-05-08
  - [checkov](https://www.checkov.io/) from 2.0.1120 to **2.0.1121** on 2022-05-08
  - [checkov](https://www.checkov.io/) from 2.0.1121 to **2.0.1140** on 2022-05-14
  - [checkov](https://www.checkov.io/) from 2.0.1140 to **2.0.1141** on 2022-05-15
  - [checkstyle](https://checkstyle.sourceforge.io) from 10.1 to **10.2** on 2022-04-24
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2022.04.08 to **2022.04.25** on 2022-04-30
  - [coffeelint](http://www.coffeelint.org) from 5.2.7 to **5.2.8** on 2022-04-26
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.19.7 to **5.20.0** on 2022-05-03
  - [editorconfig-checker](https://editorconfig-checker.github.io/) from 2.3.5 to **2.4.0** on 2022-05-15
  - [eslint](https://eslint.org) from 8.14.0 to **8.15.0** on 2022-05-07
  - [golangci-lint](https://golangci-lint.run/) from 1.45.2 to **1.46.1** on 2022-05-14
  - [graphql-schema-linter](https://github.com/cjoudrey/graphql-schema-linter) from 2.0.1 to **2.0.2** on 2022-05-06
  - [graphql-schema-linter](https://github.com/cjoudrey/graphql-schema-linter) from 2.0.2 to **3.0.0** on 2022-05-07
  - [kics](https://www.kics.io) from 1.5.6 to **1.5.7** on 2022-05-03
  - [kics](https://www.kics.io) from 1.5.7 to **1.5.8** on 2022-05-14
  - [luacheck](https://luacheck.readthedocs.io) from 0.26.0 to **0.26.1** on 2022-04-24
  - [markdown-link-check](https://github.com/tcort/markdown-link-check) from 3.10.0 to **3.10.2** on 2022-05-05
  - [mypy](https://mypy.readthedocs.io/en/stable/) from 0.942 to **0.950** on 2022-04-28
  - [phpstan](https://phpstan.org/) from 1.5.7 to **1.6.0** on 2022-04-26
  - [phpstan](https://phpstan.org/) from 1.6.0 to **1.6.2** on 2022-04-28
  - [phpstan](https://phpstan.org/) from 1.6.2 to **1.6.3** on 2022-04-29
  - [phpstan](https://phpstan.org/) from 1.6.3 to **1.6.4** on 2022-05-03
  - [phpstan](https://phpstan.org/) from 1.6.4 to **1.6.7** on 2022-05-05
  - [phpstan](https://phpstan.org/) from 1.6.7 to **1.6.8** on 2022-05-14
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.2.2 to **7.2.3** on 2022-04-28
  - [protolint](https://github.com/yoheimuta/protolint) from 0.37.1 to **0.38.1** on 2022-05-03
  - [psalm](https://psalm.dev) from Psalm.4.x-dev@ to **Psalm.5.x-dev@** on 2022-05-14
  - [pylint](https://www.pylint.org) from 2.13.7 to **2.13.8** on 2022-05-03
  - [pylint](https://www.pylint.org) from 2.13.8 to **2.13.9** on 2022-05-14
  - [rubocop](https://rubocop.org/) from 1.28.1 to **1.28.2** on 2022-04-26
  - [rubocop](https://rubocop.org/) from 1.28.2 to **1.29.0** on 2022-05-07
  - [rubocop](https://rubocop.org/) from 1.29.0 to **1.29.1** on 2022-05-14
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 2.13.1 to **2.13.2** on 2022-05-05
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 2.13.1 to **2.13.2** on 2022-05-05
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 2.13.1 to **2.13.2** on 2022-05-05
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.4.0 to **7.5.0** on 2022-04-28
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.5.0 to **7.6.0** on 2022-05-03
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.6.0 to **7.6.1** on 2022-05-05
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.6.1 to **7.6.2** on 2022-05-07
  - [sqlfluff](https://www.sqlfluff.com/) from 0.13.0 to **0.13.1** on 2022-05-07
  - [stylelint](https://stylelint.io) from 14.7.1 to **14.8.0** on 2022-04-28
  - [stylelint](https://stylelint.io) from 14.8.0 to **14.8.1** on 2022-04-30
  - [stylelint](https://stylelint.io) from 14.8.1 to **14.8.2** on 2022-05-04
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.36.10 to **0.37.1** on 2022-05-14
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.36.7 to **0.36.8** on 2022-04-28
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.36.8 to **0.36.9** on 2022-04-30
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.36.9 to **0.36.10** on 2022-05-06
  - [xmllint](https://gitlab.gnome.org/GNOME/libxml2/-/wikis/home) from 20913 to **20914** on 2022-05-14

## [v5.12.0] - 2022-04-23

- Core
  - Fix [git upgrade issue](https://github.blog/2022-04-12-git-security-vulnerability-announced/)
  - New option **FAIL_IF_UPDATED_SOURCES** ([#1389](https://github.com/megalinter/megalinter/issues/1389))

- Linter versions upgrades
  - [actionlint](https://rhysd.github.io/actionlint/) from 1.6.11 to **1.6.12** on 2022-04-18
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.58.4 to **0.59.0** on 2022-04-18
  - [checkov](https://www.checkov.io/) from 2.0.1047 to **2.0.1050** on 2022-04-11
  - [checkov](https://www.checkov.io/) from 2.0.1050 to **2.0.1067** on 2022-04-18
  - [checkov](https://www.checkov.io/) from 2.0.1067 to **2.0.1068** on 2022-04-18
  - [checkov](https://www.checkov.io/) from 2.0.1068 to **2.0.1076** on 2022-04-22
  - [coffeelint](http://www.coffeelint.org) from 5.2.5 to **5.2.6** on 2022-04-11
  - [coffeelint](http://www.coffeelint.org) from 5.2.6 to **5.2.7** on 2022-04-22
  - [eslint](https://eslint.org) from 8.13.0 to **8.14.0** on 2022-04-23
  - [git_diff](https://git-scm.com) from 2.30.2 to **2.30.3** on 2022-04-18
  - [htmlhint](https://htmlhint.com/) from 1.1.3 to **1.1.4** on 2022-04-11
  - [kics](https://www.kics.io) from 1.5.5 to **1.5.6** on 2022-04-18
  - [npm-groovy-lint](https://nvuillam.github.io/npm-groovy-lint/) from 9.4.1 to **9.5.0** on 2022-04-18
  - [phpstan](https://phpstan.org/) from 1.5.4 to **1.5.6** on 2022-04-18
  - [phpstan](https://phpstan.org/) from 1.5.6 to **1.5.7** on 2022-04-22
  - [pylint](https://www.pylint.org) from 2.13.5 to **2.13.7** on 2022-04-22
  - [rstcheck](https://github.com/myint/rstcheck) from 3.3.1 to **5.0.0** on 2022-04-18
  - [rubocop](https://rubocop.org/) from 1.27.0 to **1.28.1** on 2022-04-22
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.3.8 to **7.4.0** on 2022-04-22
  - [sqlfluff](https://www.sqlfluff.com/) from 0.12.0 to **0.13.0** on 2022-04-22
  - [stylelint](https://stylelint.io) from 14.6.1 to **14.7.1** on 2022-04-18
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.1.8 to **1.1.9** on 2022-04-22
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.36.6 to **0.36.7** on 2022-04-18
  - [tflint](https://github.com/terraform-linters/tflint) from 0.34.1 to **0.35.0** on 2022-04-18

## [v5.11.0] - 2022-04-11

- Linters
  - Disable rstfmt as it's neither stable or maintained
  - markdown-links-check: allow 203 as valid return code

- Fixes
  - Github Comment Reporter: switch to using a hidden HTML comment to mark the comment, with the current workflow and jobid. This is more robust than the old method. ([[#1355](https://github.com/megalinter/megalinter/issues/1355))
  - Allow to provide CI_ACTION_RUN_URL to build hlink for GitHub Comments reporter messages ([[#1341](https://github.com/megalinter/megalinter/issues/1341))
  - Display plugin URL in MegaLinter output logs ([[#1340](https://github.com/megalinter/megalinter/issues/1340))
  - Fix public glibc public key download
  - Fix `no override and no default toolchain set` when lint rust with clippy via github-action ([#975](https://github.com/megalinter/megalinter/issues/975))
  - Fix cspell FileNotFound error by creating subdirectories under `report` as required ([#1397](https://github.com/megalinter/megalinter/issues/1397]))

- Doc
  - Add instructions to upload artifacts when using MegaLinter with Jenkins

- Linter versions upgrades
  - [actionlint](https://rhysd.github.io/actionlint/) from 1.6.10 to **1.6.11** on 2022-04-06
  - [ansible-lint](https://ansible-lint.readthedocs.io/en/latest/) from 6.0.1 to **6.0.2** on 2022-03-24
  - [bash-exec](https://www.gnu.org/software/bash/) from 5.1.0 to **5.1.16** on 2022-03-22
  - [black](https://black.readthedocs.io/en/stable/) from 22.1.0 to **22.3.0** on 2022-03-30
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.58.3 to **0.58.4** on 2022-03-22
  - [checkov](https://www.checkov.io/) from 2.0.1008 to **2.0.1016** on 2022-03-31
  - [checkov](https://www.checkov.io/) from 2.0.1016 to **2.0.1021** on 2022-03-31
  - [checkov](https://www.checkov.io/) from 2.0.1021 to **2.0.1024** on 2022-04-01
  - [checkov](https://www.checkov.io/) from 2.0.1024 to **2.0.1030** on 2022-04-04
  - [checkov](https://www.checkov.io/) from 2.0.1030 to **2.0.1037** on 2022-04-06
  - [checkov](https://www.checkov.io/) from 2.0.1037 to **2.0.1045** on 2022-04-09
  - [checkov](https://www.checkov.io/) from 2.0.1045 to **2.0.1046** on 2022-04-10
  - [checkov](https://www.checkov.io/) from 2.0.1046 to **2.0.1047** on 2022-04-11
  - [checkov](https://www.checkov.io/) from 2.0.975 to **2.0.977** on 2022-03-21
  - [checkov](https://www.checkov.io/) from 2.0.977 to **2.0.980** on 2022-03-22
  - [checkov](https://www.checkov.io/) from 2.0.980 to **2.0.983** on 2022-03-23
  - [checkov](https://www.checkov.io/) from 2.0.983 to **2.0.995** on 2022-03-26
  - [checkov](https://www.checkov.io/) from 2.0.995 to **2.0.999** on 2022-03-27
  - [checkov](https://www.checkov.io/) from 2.0.999 to **2.0.1008** on 2022-03-30
  - [checkstyle](https://checkstyle.sourceforge.io) from 10.0 to **10.1** on 2022-03-27
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.59 to **0.1.60** on 2022-04-09
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2022.02.09 to **2022.04.08** on 2022-04-10
  - [coffeelint](http://www.coffeelint.org) from 5.2.4 to **5.2.5** on 2022-03-22
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.19.2 to **5.19.3** on 2022-03-26
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.19.3 to **5.19.4** on 2022-04-01
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.19.4 to **5.19.5** on 2022-04-02
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.19.5 to **5.19.6** on 2022-04-09
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.19.6 to **5.19.7** on 2022-04-10
  - [eslint](https://eslint.org) from 8.11.0 to **8.12.0** on 2022-03-26
  - [eslint](https://eslint.org) from 8.12.0 to **8.13.0** on 2022-04-09
  - [golangci-lint](https://golangci-lint.run/) from 1.45.0 to **1.45.2** on 2022-03-26
  - [hadolint](https://github.com/hadolint/hadolint) from 2.9.1 to **2.9.3** on 2022-03-31
  - [hadolint](https://github.com/hadolint/hadolint) from 2.9.3 to **2.10.0** on 2022-04-10
  - [htmlhint](https://htmlhint.com/) from 1.1.2 to **1.1.3** on 2022-03-30
  - [kics](https://www.kics.io) from 1.5.4 to **1.5.5** on 2022-03-31
  - [ktlint](https://ktlint.github.io) from 0.45.0 to **0.45.1** on 2022-03-22
  - [ktlint](https://ktlint.github.io) from 0.45.1 to **0.45.2** on 2022-04-07
  - [luacheck](https://luacheck.readthedocs.io) from 0.25.0 to **0.26.0** on 2022-03-26
  - [mypy](https://mypy.readthedocs.io/en/stable/) from 0.941 to **0.942** on 2022-03-26
  - [phpstan](https://phpstan.org/) from 1.4.10 to **1.5.0** on 2022-03-26
  - [phpstan](https://phpstan.org/) from 1.5.0 to **1.5.2** on 2022-03-30
  - [phpstan](https://phpstan.org/) from 1.5.2 to **1.5.3** on 2022-03-31
  - [phpstan](https://phpstan.org/) from 1.5.3 to **1.5.4** on 2022-04-04
  - [prettier](https://prettier.io/) from 2.6.0 to **2.6.1** on 2022-03-26
  - [prettier](https://prettier.io/) from 2.6.1 to **2.6.2** on 2022-04-04
  - [pylint](https://www.pylint.org) from 2.12.2 to **2.13.1** on 2022-03-26
  - [pylint](https://www.pylint.org) from 2.13.1 to **2.13.2** on 2022-03-27
  - [pylint](https://www.pylint.org) from 2.13.2 to **2.13.3** on 2022-03-30
  - [pylint](https://www.pylint.org) from 2.13.3 to **2.13.4** on 2022-03-31
  - [pylint](https://www.pylint.org) from 2.13.4 to **2.13.5** on 2022-04-07
  - [rubocop](https://rubocop.org/) from 1.26.0 to **1.26.1** on 2022-03-23
  - [rubocop](https://rubocop.org/) from 1.26.1 to **1.27.0** on 2022-04-09
  - [scalafix](https://scalacenter.github.io/scalafix/) from 0.9.34 to **0.10.0** on 2022-04-04
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 2.13.0 to **2.13.1** on 2022-03-24
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 2.13.0 to **2.13.1** on 2022-03-24
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 2.13.0 to **2.13.1** on 2022-03-24
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.2.1 to **7.3.0** on 2022-03-22
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.3.0 to **7.3.1** on 2022-03-24
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.3.1 to **7.3.2** on 2022-03-26
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.3.2 to **7.3.3** on 2022-03-30
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.3.3 to **7.3.4** on 2022-03-31
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.3.4 to **7.3.5** on 2022-03-31
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.3.5 to **7.3.6** on 2022-04-04
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.3.6 to **7.3.7** on 2022-04-06
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.3.7 to **7.3.8** on 2022-04-07
  - [sqlfluff](https://www.sqlfluff.com/) from 0.11.1 to **0.11.2** on 2022-03-26
  - [sqlfluff](https://www.sqlfluff.com/) from 0.11.2 to **0.12.0** on 2022-04-09
  - [stylelint](https://stylelint.io) from 14.6.0 to **14.6.1** on 2022-03-26
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.1.7 to **1.1.8** on 2022-04-09
  - [terrascan](https://www.accurics.com/products/terrascan/) from 1.13.2 to **1.14.0** on 2022-04-01

## [v5.10.0] - 2022-03-20

- Linter versions upgrades
  - [ansible-lint](https://ansible-lint.readthedocs.io/en/latest/) from 5.4.0 to **6.0.0** on 2022-03-16
  - [ansible-lint](https://ansible-lint.readthedocs.io/en/latest/) from 6.0.0 to **6.0.1** on 2022-03-19
  - [checkov](https://www.checkov.io/) from 2.0.939 to **2.0.940** on 2022-03-13
  - [checkov](https://www.checkov.io/) from 2.0.940 to **2.0.943** on 2022-03-14
  - [checkov](https://www.checkov.io/) from 2.0.943 to **2.0.949** on 2022-03-15
  - [checkov](https://www.checkov.io/) from 2.0.949 to **2.0.962** on 2022-03-16
  - [checkov](https://www.checkov.io/) from 2.0.962 to **2.0.969** on 2022-03-17
  - [checkov](https://www.checkov.io/) from 2.0.969 to **2.0.970** on 2022-03-17
  - [checkov](https://www.checkov.io/) from 2.0.970 to **2.0.975** on 2022-03-19
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.19.0 to **5.19.1** on 2022-03-13
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.19.1 to **5.19.2** on 2022-03-14
  - [golangci-lint](https://golangci-lint.run/) from 1.44.2 to **1.45.0** on 2022-03-19
  - [hadolint](https://github.com/hadolint/hadolint) from 2.7.0 to **2.9.1** on 2022-03-19
  - [kics](https://www.kics.io) from 1.5.3 to **1.5.4** on 2022-03-17
  - [ktlint](https://ktlint.github.io) from 0.44.0 to **0.45.0** on 2022-03-19
  - [markdown-link-check](https://github.com/tcort/markdown-link-check) from 3.9.3 to **3.10.0** on 2022-03-20
  - [mypy](https://mypy.readthedocs.io/en/stable/) from 0.940 to **0.941** on 2022-03-15
  - [phpstan](https://phpstan.org/) from 1.4.9 to **1.4.10** on 2022-03-14
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.2.1 to **7.2.2** on 2022-03-17
  - [prettier](https://prettier.io/) from 2.5.1 to **2.6.0** on 2022-03-17
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.2.0 to **7.2.1** on 2022-03-14
  - [sqlfluff](https://www.sqlfluff.com/) from 0.11.0 to **0.11.1** on 2022-03-17
  - [stylelint](https://stylelint.io) from 14.5.3 to **14.6.0** on 2022-03-17
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.36.3 to **0.36.5** on 2022-03-17
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.36.5 to **0.36.6** on 2022-03-19

## [v5.9.0] - 2022-03-13

- Linters
  - New linter [**kubeconform**](https://github.com/yannh/kubeconform) to validate Kubernetes manifests with updated schemas

- Core
  - Switch from JDK 8 to JDK 11
  - Use latest version of npm

- Flavors
  - Add shell linters to ci_light flavor ([#1298](https://github.com/megalinter/megalinter/issues/1298))

- Fixes
  - Generate JSON Schema HTML Documentation when building documentation ([#1287](https://github.com/megalinter/megalinter/issues/1287))
  - rubocop: remove `--force-exclusion` from auto-added parameters ([#302](https://github.com/megalinter/megalinter/issues/302))
  - terrascan: call `terrascan init` as a pre-command

- Linter versions upgrades
  - [actionlint](https://rhysd.github.io/actionlint/) from 1.6.8 to **1.6.9** on 2022-02-25
  - [actionlint](https://rhysd.github.io/actionlint/) from 1.6.9 to **1.6.10** on 2022-03-12
  - [bandit](https://bandit.readthedocs.io/en/latest/) from 1.7.2 to **1.7.3** on 2022-02-28
  - [bandit](https://bandit.readthedocs.io/en/latest/) from 1.7.3 to **1.7.4** on 2022-03-06
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.58.0 to **0.58.1** on 2022-02-21
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.58.1 to **0.58.2** on 2022-02-27
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.58.2 to **0.58.3** on 2022-03-09
  - [checkov](https://www.checkov.io/) from 2.0.873 to **2.0.885** on 2022-02-21
  - [checkov](https://www.checkov.io/) from 2.0.885 to **2.0.901** on 2022-02-25
  - [checkov](https://www.checkov.io/) from 2.0.901 to **2.0.902** on 2022-02-25
  - [checkov](https://www.checkov.io/) from 2.0.902 to **2.0.903** on 2022-02-27
  - [checkov](https://www.checkov.io/) from 2.0.903 to **2.0.906** on 2022-02-28
  - [checkov](https://www.checkov.io/) from 2.0.906 to **2.0.914** on 2022-03-03
  - [checkov](https://www.checkov.io/) from 2.0.914 to **2.0.917** on 2022-03-04
  - [checkov](https://www.checkov.io/) from 2.0.917 to **2.0.918** on 2022-03-06
  - [checkov](https://www.checkov.io/) from 2.0.918 to **2.0.923** on 2022-03-08
  - [checkov](https://www.checkov.io/) from 2.0.923 to **2.0.924** on 2022-03-08
  - [checkov](https://www.checkov.io/) from 2.0.924 to **2.0.927** on 2022-03-09
  - [checkov](https://www.checkov.io/) from 2.0.927 to **2.0.931** on 2022-03-10
  - [checkov](https://www.checkov.io/) from 2.0.931 to **2.0.935** on 2022-03-11
  - [checkov](https://www.checkov.io/) from 2.0.935 to **2.0.938** on 2022-03-12
  - [checkov](https://www.checkov.io/) from 2.0.938 to **2.0.939** on 2022-03-13
  - [checkstyle](https://checkstyle.sourceforge.io) from 9.3 to **10.0** on 2022-03-03
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.58 to **0.1.59** on 2022-02-25
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2022.01.15 to **2022.02.09** on 2022-02-21
  - [cpplint](https://github.com/cpplint/cpplint) from 1.5.5 to **1.6.0** on 2022-02-20
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.18.5 to **5.19.0** on 2022-03-13
  - [eslint](https://eslint.org) from 8.10.0 to **8.11.0** on 2022-03-12
  - [eslint](https://eslint.org) from 8.9.0 to **8.10.0** on 2022-02-27
  - [kics](https://www.kics.io) from 1.5.2 to **1.5.3** on 2022-03-03
  - [mypy](https://mypy.readthedocs.io/en/stable/) from 0.931 to **0.940** on 2022-03-12
  - [phpstan](https://phpstan.org/) from 1.4.6 to **1.4.7** on 2022-03-03
  - [phpstan](https://phpstan.org/) from 1.4.7 to **1.4.8** on 2022-03-06
  - [phpstan](https://phpstan.org/) from 1.4.8 to **1.4.9** on 2022-03-11
  - [protolint](https://github.com/yoheimuta/protolint) from 0.37.0 to **0.37.1** on 2022-02-27
  - [rst-lint](https://github.com/twolfson/restructuredtext-lint) from 1.3.2 to **1.4.0** on 2022-02-25
  - [rubocop](https://rubocop.org/) from 1.25.1 to **1.26.0** on 2022-03-10
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 2.12.0 to **2.13.0** on 2022-02-25
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 2.12.0 to **2.13.0** on 2022-02-25
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 2.12.0 to **2.13.0** on 2022-02-25
  - [snakefmt](https://github.com/snakemake/snakefmt) from 0.4.4 to **0.6.0** on 2022-03-04
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.15.5 to **7.0.0** on 2022-02-25
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.0.0 to **7.0.1** on 2022-02-27
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.0.1 to **7.0.3** on 2022-03-03
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.0.3 to **7.0.4** on 2022-03-04
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.0.4 to **7.1.0** on 2022-03-06
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.1.0 to **7.1.1** on 2022-03-08
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 7.1.1 to **7.2.0** on 2022-03-13
  - [sqlfluff](https://www.sqlfluff.com/) from 0.10.1 to **0.11.0** on 2022-03-08
  - [stylelint](https://stylelint.io) from 14.5.1 to **14.5.3** on 2022-02-25
  - [swiftlint](https://github.com/realm/SwiftLint) from 0.46.2 to **0.46.3** on 2022-02-25
  - [swiftlint](https://github.com/realm/SwiftLint) from 0.46.3 to **0.46.4** on 2022-03-08
  - [swiftlint](https://github.com/realm/SwiftLint) from 0.46.4 to **0.46.5** on 2022-03-09
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.1.6 to **1.1.7** on 2022-03-04
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.36.1 to **0.36.2** on 2022-02-25
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.36.2 to **0.36.3** on 2022-03-04
  - [terrascan](https://www.accurics.com/products/terrascan/) from 1.13.1 to **1.13.2** on 2022-02-25
  - [tsqllint](https://github.com/tsqllint/tsqllint) from 1.14.3.0 to **1.14.5.0** on 2022-02-21
  - [xmllint](https://gitlab.gnome.org/GNOME/libxml2/-/wikis/home) from 20912 to **20913** on 2022-03-12

## [v5.8.0] - 2022-02-18

- Linters
  - Improve ansible-lint performances by linting all project in one call, and count number of errors
  - Use project cli_lint_mode to improve performances
    - terrascan

- Fixes
  - Manage to use local certificate with Gitlab comments reporter using GITLAB_SSL_CERTIFICATE_PATH ([#1239](https://github.com/megalinter/megalinter/issues/1239))
  - Fix GITLAB_ACCESS_TOKEN_MEGALINTER suggestion when trying to push comments to gitlab merge request
  - Gitlab Comments Reporter: allow to use certificates with variable GITLAB_CUSTOM_CERTIFICATE (or GITLAB_CERTIFICATE_PATH only if [PRE_COMMANDS](https://megalinter.github.io/configuration/#pre-commands) are used) ([#1239](https://github.com/megalinter/megalinter/issues/1239))

- Core
  - Allow to check prop existence in active_only_if_file_found and apply to eslint descriptors ([#1205](https://github.com/megalinter/megalinter/issues/1205))

- Doc
  - Update images with screen records gifs
  - Add publish artifact task in azure pipelines doc

- Linter versions upgrades
  - [ansible-lint](https://ansible-lint.readthedocs.io/en/latest/) from 5.3.2 to **5.4.0** on 2022-02-13
  - [checkov](https://www.checkov.io/) from 2.0.782 to **2.0.783** on 2022-02-03
  - [checkov](https://www.checkov.io/) from 2.0.783 to **2.0.786** on 2022-02-03
  - [checkov](https://www.checkov.io/) from 2.0.786 to **2.0.791** on 2022-02-05
  - [checkov](https://www.checkov.io/) from 2.0.791 to **2.0.793** on 2022-02-06
  - [checkov](https://www.checkov.io/) from 2.0.793 to **2.0.795** on 2022-02-06
  - [checkov](https://www.checkov.io/) from 2.0.795 to **2.0.812** on 2022-02-09
  - [checkov](https://www.checkov.io/) from 2.0.812 to **2.0.813** on 2022-02-09
  - [checkov](https://www.checkov.io/) from 2.0.813 to **2.0.817** on 2022-02-10
  - [checkov](https://www.checkov.io/) from 2.0.817 to **2.0.830** on 2022-02-13
  - [checkov](https://www.checkov.io/) from 2.0.830 to **2.0.833** on 2022-02-14
  - [checkov](https://www.checkov.io/) from 2.0.833 to **2.0.853** on 2022-02-16
  - [checkov](https://www.checkov.io/) from 2.0.853 to **2.0.866** on 2022-02-18
  - [checkov](https://www.checkov.io/) from 2.0.866 to **2.0.873** on 2022-02-18
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.18.0 to **5.18.3** on 2022-02-05
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.18.3 to **5.18.4** on 2022-02-09
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.18.4 to **5.18.5** on 2022-02-16
  - [eslint-plugin-jsonc](https://ota-meshi.github.io/eslint-plugin-jsonc/) from 2.1.0 to **2.2.1** on 2022-02-18
  - [eslint](https://eslint.org) from 8.8.0 to **8.9.0** on 2022-02-13
  - [golangci-lint](https://golangci-lint.run/) from 1.44.0 to **1.44.2** on 2022-02-18
  - [kics](https://www.kics.io) from 1.5.1 to **1.5.2** on 2022-02-18
  - [ktlint](https://ktlint.github.io) from 0.43.2 to **0.44.0** on 2022-02-16
  - [markdownlint](https://github.com/DavidAnson/markdownlint) from 0.30.0 to **0.31.0** on 2022-02-06
  - [markdownlint](https://github.com/DavidAnson/markdownlint) from 0.31.0 to **0.31.1** on 2022-02-09
  - [phpstan](https://phpstan.org/) from 1.4.5 to **1.4.6** on 2022-02-06
  - [protolint](https://github.com/yoheimuta/protolint) from 0.36.0 to **0.37.0** on 2022-02-13
  - [rubocop](https://rubocop.org/) from 1.25.0 to **1.25.1** on 2022-02-03
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.15.1 to **6.15.2** on 2022-02-06
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.15.2 to **6.15.3** on 2022-02-09
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.15.3 to **6.15.4** on 2022-02-09
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.15.4 to **6.15.5** on 2022-02-10
  - [sqlfluff](https://www.sqlfluff.com/) from 0.10.0 to **0.10.1** on 2022-02-18
  - [sqlfluff](https://www.sqlfluff.com/) from 0.9.4 to **0.10.0** on 2022-02-13
  - [stylelint](https://stylelint.io) from 14.3.0 to **14.4.0** on 2022-02-09
  - [stylelint](https://stylelint.io) from 14.4.0 to **14.5.0** on 2022-02-13
  - [stylelint](https://stylelint.io) from 14.5.0 to **14.5.1** on 2022-02-18
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.1.4 to **1.1.5** on 2022-02-03
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.1.5 to **1.1.6** on 2022-02-18
  - [terrascan](https://www.accurics.com/products/terrascan/) from 1.13.0 to **1.13.1** on 2022-02-13

## [v5.7.1] - 2022-02-02

- Linter updates:
  - temporary disable snakefmt to allow latest versions of black and sqlfluff
  - cspell: Update .cspell default config with `"version: "2.0", "noConfigSearch": true`
  - Use list_of_files mode to improve performances
    - markdown-link-check
    - standard
    - stylelint

- Fixes
  - Remove extraheader in git repo when using Azure Pipelines ([#1125](https://github.com/megalinter/megalinter/issues/1125))
  - Fix gitlab token error message ([#1228](https://github.com/megalinter/megalinter/issues/1228))

- Linter versions upgrades
  - [black](https://black.readthedocs.io/en/stable/) from 21.12 to **22.1.0** on 2022-02-02
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.57.0 to **0.58.0** on 2022-02-01
  - [checkov](https://www.checkov.io/) from 2.0.775 to **2.0.777** on 2022-01-31
  - [checkov](https://www.checkov.io/) from 2.0.777 to **2.0.778** on 2022-02-01
  - [checkov](https://www.checkov.io/) from 2.0.778 to **2.0.780** on 2022-02-02
  - [checkov](https://www.checkov.io/) from 2.0.780 to **2.0.782** on 2022-02-02
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.17.0 to **5.18.0** on 2022-01-31
  - [kics](https://www.kics.io) from 1.5.0 to **1.5.1** on 2022-02-02
  - [markdown-table-formatter](https://www.npmjs.com/package/markdown-table-formatter) from 1.2.0 to **1.3.0** on 2022-01-31
  - [phpstan](https://phpstan.org/) from 1.4.3 to **1.4.4** on 2022-02-01
  - [phpstan](https://phpstan.org/) from 1.4.4 to **1.4.5** on 2022-02-02
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.13.1 to **6.15.1** on 2022-02-02
  - [sqlfluff](https://www.sqlfluff.com/) from 0.9.3 to **0.9.4** on 2022-02-02
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.36.0 to **0.36.1** on 2022-02-01

## [v5.7.0] - 2022-01-30

- Core:
  - New reporter [**GITLAB_COMMENT_REPORTER**](https://megalinter.github.io/reporters/GitlabCommentReporter/) allowing to post MegaLinter results as comments on Gitlab merge requests
  - CI: Update test method to check that the number of errors is correctly calculated (+ fix linter test cases)

- Linter updates:
  - Add configuration file option for SQLFluff ([#1200](https://github.com/megalinter/megalinter/pull/1200))
  - secretlint: Use .gitignore as .secretlintignore if --secretlintignore isn't defined and .secretlintignore not found ([#1207](https://github.com/megalinter/megalinter/issues/1207))
  - Update bash-exec documentation
  - Display correct number of errors in logs
    - actionlint
    - chktex
    - cpplint
    - htmlhint
    - perlcritic
    - sfdx-scanner
    - shellcheck
    - shfmt
  - Use list_of_files mode to improve performances
    - htmlhint
    - shellcheck
    - shfmt

- Fixes:
  - Fix v5 doc deployment when there is a new release ([#1190](https://github.com/megalinter/megalinter/issues/1190))
  - Fix issue when using `VALIDATE_ALL_CODEBASE: false` on Azure Pipelines by defining auth header in CI env variable GIT_AUTHORIZATION_BEARER ([#1125](https://github.com/megalinter/megalinter/issues/1125))
  - Fix tflint initialization so it uses configuration file when defined ([#1134](https://github.com/megalinter/megalinter/issues/1134))

- Linter versions upgrades
  - [bandit](https://bandit.readthedocs.io/en/latest/) from 1.7.1 to **1.7.2** on 2022-01-26
  - [checkov](https://www.checkov.io/) from 2.0.744 to **2.0.745** on 2022-01-23
  - [checkov](https://www.checkov.io/) from 2.0.745 to **2.0.746** on 2022-01-24
  - [checkov](https://www.checkov.io/) from 2.0.746 to **2.0.749** on 2022-01-24
  - [checkov](https://www.checkov.io/) from 2.0.749 to **2.0.754** on 2022-01-24
  - [checkov](https://www.checkov.io/) from 2.0.754 to **2.0.763** on 2022-01-26
  - [checkov](https://www.checkov.io/) from 2.0.763 to **2.0.769** on 2022-01-28
  - [checkov](https://www.checkov.io/) from 2.0.769 to **2.0.772** on 2022-01-29
  - [checkov](https://www.checkov.io/) from 2.0.772 to **2.0.775** on 2022-01-30
  - [checkstyle](https://checkstyle.sourceforge.io) from 9.2.1 to **9.3** on 2022-01-30
  - [coffeelint](http://www.coffeelint.org) from 5.2.3 to **5.2.4** on 2022-01-28
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.16.0 to **5.17.0** on 2022-01-28
  - [dotenv-linter](https://dotenv-linter.github.io/) from 3.1.1 to **3.2.0** on 2022-01-24
  - [eslint-plugin-jsonc](https://ota-meshi.github.io/eslint-plugin-jsonc/) from 2.0.0 to **2.1.0** on 2022-01-28
  - [eslint](https://eslint.org) from 8.7.0 to **8.8.0** on 2022-01-29
  - [golangci-lint](https://golangci-lint.run/) from 1.43.0 to **1.44.0** on 2022-01-26
  - [htmlhint](https://htmlhint.com/) from 1.1.0 to **1.1.1** on 2022-01-23
  - [htmlhint](https://htmlhint.com/) from 1.1.1 to **1.1.2** on 2022-01-28
  - [markdown-link-check](https://github.com/tcort/markdown-link-check) from 3.9.2 to **3.9.3** on 2022-01-29
  - [phpstan](https://phpstan.org/) from 1.4.2 to **1.4.3** on 2022-01-29
  - [rubocop](https://rubocop.org/) from 0.82.0 to **1.25.0** on 2022-01-29
  - [shfmt](https://github.com/mvdan/sh) from 3.2.1 to **3.5.0** on 2022-01-30
  - [shfmt](https://github.com/mvdan/sh) from 3.3.1 to **3.2.1** on 2022-01-30
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.13.1 to **6.14.0** on 2022-01-28
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.14.0 to **6.15.0** on 2022-01-29
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.15.0 to **6.13.1** on 2022-01-30
  - [sqlfluff](https://www.sqlfluff.com/) from 0.9.1 to **0.9.3** on 2022-01-28
  - [stylelint](https://stylelint.io) from 14.2.0 to **14.3.0** on 2022-01-23
  - [swiftlint](https://github.com/realm/SwiftLint) from 0.46.0 to **0.46.2** on 2022-01-28
  - [tsqllint](https://github.com/tsqllint/tsqllint) from 1.14.0.0 to **1.14.3.0** on 2022-01-23

## [v5.6.0] - 2022-01-22

- Add linters licenses to online documentation
- Fix issue when config vars are both from ENV and from config file ([#1154](https://github.com/megalinter/megalinter/issues/1154))
- Fix issue of --files argument format when calling npm-groovy-lint ([#1176](https://github.com/megalinter/megalinter/issues/1176))
- Fix wrong status in reports when DISABLE_ERRORS is used
- Increase memory size for node.js-based linters ([#1149](https://github.com/megalinter/megalinter/pull/1149))
- Make python linters play nice with each other ([#1182](https://github.com/megalinter/megalinter/pull/1182))

- Linter versions upgrades
  - [coffeelint](http://www.coffeelint.org) from 5.2.2 to **5.2.3** on 2022-01-09
  - [phpstan](https://phpstan.org/) from 1.3.0 to **1.3.3** on 2022-01-09
  - [mypy](https://mypy.readthedocs.io/en/stable/) from 0.930 to **0.931** on 2022-01-09
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.14.0 to **5.15.1** on 2022-01-09
  - [checkov](https://www.checkov.io/) from 2.0.702 to **2.0.708** on 2022-01-09
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.1.2 to **1.1.3** on 2022-01-09
  - [terrascan](https://www.accurics.com/products/terrascan/) from 1.12.0 to **1.13.0** on 2022-01-09
  - [npm-groovy-lint](https://nvuillam.github.io/npm-groovy-lint/) from 9.3.0 to **9.3.2** on 2022-01-09
  - [sqlfluff](https://www.sqlfluff.com/) from 0.9.0 to **0.9.1** on 2022-01-09
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.56.3 to **0.56.4** on 2022-01-11
  - [npm-groovy-lint](https://nvuillam.github.io/npm-groovy-lint/) from 9.3.2 to **9.4.0** on 2022-01-11
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.12.3 to **6.13.0** on 2022-01-11
  - [checkov](https://www.checkov.io/) from 2.0.708 to **2.0.709** on 2022-01-11
  - [scalafix](https://scalacenter.github.io/scalafix/) from 0.9.33 to **0.9.34** on 2022-01-12
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.13.0 to **6.13.1** on 2022-01-12
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.15.1 to **5.15.2** on 2022-01-12
  - [checkov](https://www.checkov.io/) from 2.0.709 to **2.0.710** on 2022-01-12
  - [npm-groovy-lint](https://nvuillam.github.io/npm-groovy-lint/) from 9.4.0 to **9.4.1** on 2022-01-13
  - [checkov](https://www.checkov.io/) from 2.0.710 to **2.0.712** on 2022-01-13
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.35.16 to **0.35.18** on 2022-01-13
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2021.12.19 to **2022.01.13** on 2022-01-14
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.57 to **0.1.58** on 2022-01-14
  - [checkov](https://www.checkov.io/) from 2.0.712 to **2.0.717** on 2022-01-14
  - [phpstan](https://phpstan.org/) from 1.3.3 to **1.4.0** on 2022-01-15
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.35.18 to **0.35.19** on 2022-01-15
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.35.19 to **0.35.20** on 2022-01-15
  - [checkov](https://www.checkov.io/) from 2.0.717 to **2.0.718** on 2022-01-16
  - [eslint](https://eslint.org) from 8.6.0 to **8.7.0** on 2022-01-17
  - [checkov](https://www.checkov.io/) from 2.0.718 to **2.0.720** on 2022-01-17
  - [phpstan](https://phpstan.org/) from 1.4.0 to **1.4.1** on 2022-01-18
  - [checkov](https://www.checkov.io/) from 2.0.720 to **2.0.727** on 2022-01-18
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2022.01.13 to **2022.01.15** on 2022-01-22
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.56.4 to **0.57.0** on 2022-01-22
  - [markdown-link-check](https://github.com/tcort/markdown-link-check) from 3.9.0 to **3.9.2** on 2022-01-22
  - [phpstan](https://phpstan.org/) from 1.4.1 to **1.4.2** on 2022-01-22
  - [protolint](https://github.com/yoheimuta/protolint) from 0.35.2 to **0.36.0** on 2022-01-22
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.15.2 to **5.16.0** on 2022-01-22
  - [swiftlint](https://github.com/realm/SwiftLint) from 0.45.1 to **0.46.0** on 2022-01-22
  - [checkov](https://www.checkov.io/) from 2.0.727 to **2.0.744** on 2022-01-22
  - [kics](https://www.kics.io) from 1.4.9 to **1.5.0** on 2022-01-22
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.1.3 to **1.1.4** on 2022-01-22
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.35.20 to **0.36.0** on 2022-01-22

## [v5.5.0] - 2022-01-03

- Linter versions upgrades
  - [checkov](https://www.checkov.io/) from 2.0.680 to **2.0.681** on 2021-12-21
  - [stylelint](https://stylelint.io) from 14.1.0 to **14.2.0** on 2021-12-23
  - [mypy](https://mypy.readthedocs.io/en/stable/) from 0.920 to **0.930** on 2021-12-23
  - [checkov](https://www.checkov.io/) from 2.0.681 to **2.0.687** on 2021-12-23
  - [npm-groovy-lint](https://nvuillam.github.io/npm-groovy-lint/) from 9.1.0 to **9.2.0** on 2021-12-23
  - [checkov](https://www.checkov.io/) from 2.0.687 to **2.0.690** on 2021-12-23
  - [tflint](https://github.com/terraform-linters/tflint) from 0.34.0 to **0.34.1** on 2021-12-26
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2021.06.18 to **2021.12.19** on 2021-12-29
  - [npm-groovy-lint](https://nvuillam.github.io/npm-groovy-lint/) from 9.2.0 to **9.3.0** on 2021-12-29
  - [checkstyle](https://checkstyle.sourceforge.io) from 9.2 to **9.2.1** on 2021-12-29
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.13.4 to **5.14.0** on 2021-12-29
  - [checkov](https://www.checkov.io/) from 2.0.690 to **2.0.695** on 2021-12-29
  - [phpstan](https://phpstan.org/) from 1.2.0 to **1.3.0** on 2021-12-29
  - [checkov](https://www.checkov.io/) from 2.0.695 to **2.0.701** on 2021-12-31
  - [htmlhint](https://htmlhint.com/) from 1.0.0 to **1.1.0** on 2022-01-01
  - [eslint](https://eslint.org) from 8.5.0 to **8.6.0** on 2022-01-01
  - [checkov](https://www.checkov.io/) from 2.0.701 to **2.0.702** on 2022-01-03

## [v5.4.0] - 2021-12-21

- Linter versions upgrades
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.12.1 to **6.12.2** on 2021-12-09
  - [checkov](https://www.checkov.io/) from 2.0.636 to **2.0.639** on 2021-12-09
  - [checkov](https://www.checkov.io/) from 2.0.639 to **2.0.641** on 2021-12-09
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.0.11 to **1.1.0** on 2021-12-09
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.12.2 to **6.12.3** on 2021-12-11
  - [checkov](https://www.checkov.io/) from 2.0.641 to **2.0.648** on 2021-12-11
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.13.2 to **5.13.3** on 2021-12-11
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.35.13 to **0.35.14** on 2021-12-11
  - [checkov](https://www.checkov.io/) from 2.0.648 to **2.0.649** on 2021-12-12
  - [phpcs](https://github.com/squizlabs/PHP_CodeSniffer) from 3.6.1 to **3.6.2** on 2021-12-14
  - [sqlfluff](https://www.sqlfluff.com/) from 0.8.2 to **0.9.0** on 2021-12-14
  - [checkov](https://www.checkov.io/) from 2.0.649 to **2.0.659** on 2021-12-14
  - [tflint](https://github.com/terraform-linters/tflint) from 0.33.2 to **0.34.0** on 2021-12-14
  - [npm-groovy-lint](https://nvuillam.github.io/npm-groovy-lint/) from 9.0.0 to **9.1.0** on 2021-12-15
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.2.0 to **7.2.1** on 2021-12-15
  - [checkov](https://www.checkov.io/) from 2.0.659 to **2.0.660** on 2021-12-15
  - [mypy](https://mypy.readthedocs.io/en/stable/) from 0.910 to **0.920** on 2021-12-16
  - [checkov](https://www.checkov.io/) from 2.0.660 to **2.0.662** on 2021-12-16
  - [checkov](https://www.checkov.io/) from 2.0.662 to **2.0.668** on 2021-12-17
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.1.0 to **1.1.1** on 2021-12-17
  - [eslint](https://eslint.org) from 8.4.1 to **8.5.0** on 2021-12-18
  - [checkov](https://www.checkov.io/) from 2.0.668 to **2.0.672** on 2021-12-18
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.13.3 to **5.13.4** on 2021-12-18
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.1.1 to **1.1.2** on 2021-12-18
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.35.14 to **0.35.16** on 2021-12-18
  - [coffeelint](http://www.coffeelint.org) from 5.2.1 to **5.2.2** on 2021-12-21
  - [checkov](https://www.checkov.io/) from 2.0.672 to **2.0.680** on 2021-12-21
  - [kics](https://www.kics.io) from 1.4.8 to **1.4.9** on 2021-12-21

## [v5.3.0] - 2021-12-08

- Fix jscpd typo about `.venv` (#986)
- markdownlint: rename default config file from .markdown-lint.json to .markdownlint.json
- Deprecate `DEFAULT_BRANCH` setting (#948)
- Correct some broken links in `README` from `Mega-Linter` to `MegaLinter` (#1030)
- Docker run -- clean-up containers when exits (#1033)
- Add missing Bandit config file and rules path options (#679)
- Fix getting linter version of npm plugin. (#845)
- Improve runtime performances when using a flavor and defining `FLAVORS_SUGGESTION: false`
- Don't check for updated files when `APPLY_FIXES` isn't active
- Fix CLI_LINT_MODE default value in doc (#1086)

- Linters
  - New linter `phplint` to speed-up linting of php files (#1031)
    - Fix `phplint` constraint to accept all future bugfix v3.0.x versions (PHP 7.4 support) (#1043)
  - `cpplint`: Use `cli_lint_mode: project` to improve performances

- Linter versions upgrades
  - [remark-lint](https://remark.js.org/) from 14.0.1 to **14.0.2** on 2021-11-19
  - [php](https://www.php.net) from 7.4.25 to **7.4.26** on 2021-11-19
  - [checkov](https://www.checkov.io/) from 2.0.587 to **2.0.588** on 2021-11-19
  - [markdownlint](https://github.com/DavidAnson/markdownlint) from 0.29.0 to **0.30.0** on 2021-11-21
  - [checkov](https://www.checkov.io/) from 2.0.588 to **2.0.591** on 2021-11-21
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.35.10 to **0.35.12** on 2021-11-21
  - [eslint](https://eslint.org) from 8.2.0 to **8.3.0** on 2021-11-21
  - [checkov](https://www.checkov.io/) from 2.0.591 to **2.0.595** on 2021-11-21
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.56.1 to **0.56.2** on 2021-11-22
  - [sqlfluff](https://www.sqlfluff.com/) from 0.8.1 to **0.8.2** on 2021-11-22
  - [checkov](https://www.checkov.io/) from 2.0.595 to **2.0.597** on 2021-11-22
  - [htmlhint](https://htmlhint.com/) from 0.16.1 to **0.16.2** on 2021-11-24
  - [checkov](https://www.checkov.io/) from 2.0.597 to **2.0.600** on 2021-11-24
  - [htmlhint](https://htmlhint.com/) from 0.16.2 to **0.16.3** on 2021-11-25
  - [markdown-link-check](https://github.com/tcort/markdown-link-check) from 0.0.0 to **3.9.0** on 2021-11-25
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.13.0 to **5.13.1** on 2021-11-25
  - [checkov](https://www.checkov.io/) from 2.0.600 to **2.0.603** on 2021-11-25
  - [kics](https://www.kics.io) from 1.4.7 to **1.4.8** on 2021-11-25
  - [prettier](https://prettier.io/) from 2.4.1 to **2.5.0** on 2021-11-26
  - [pylint](https://www.pylint.org) from 2.11.1 to **2.12.1** on 2021-11-26
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.10.0 to **6.11.0** on 2021-11-26
  - [checkov](https://www.checkov.io/) from 2.0.603 to **2.0.605** on 2021-11-26
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.35.12 to **0.35.13** on 2021-11-26
  - [htmlhint](https://htmlhint.com/) from 0.16.3 to **1.0.0** on 2021-11-27
  - [scalafix](https://scalacenter.github.io/scalafix/) from 0.9.32 to **0.9.33** on 2021-11-27
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.11.0 to **6.11.1** on 2021-11-27
  - [checkstyle](https://checkstyle.sourceforge.io) from 9.1 to **9.2** on 2021-11-29
  - [checkov](https://www.checkov.io/) from 2.0.605 to **2.0.606** on 2021-11-29
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.11.1 to **6.12.1** on 2021-11-30
  - [swiftlint](https://github.com/realm/SwiftLint) from 0.45.0 to **0.45.1** on 2021-11-30
  - [checkov](https://www.checkov.io/) from 2.0.606 to **2.0.609** on 2021-11-30
  - [v8r](https://github.com/chris48s/v8r) from 0.6.1 to **0.7.0** on 2021-11-30
  - [v8r](https://github.com/chris48s/v8r) from 0.7.0 to **0.6.1** on 2021-12-01
  - [checkov](https://www.checkov.io/) from 2.0.614 to **2.0.616** on 2021-12-01
  - [checkov](https://www.checkov.io/) from 2.0.616 to **2.0.618** on 2021-12-01
  - [coffeelint](http://www.coffeelint.org) from 5.2.0 to **5.2.1** on 2021-12-02
  - [checkov](https://www.checkov.io/) from 2.0.618 to **2.0.621** on 2021-12-02
  - [ktlint](https://ktlint.github.io) from 0.40.0 to **0.43.2** on 2021-12-02
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.56 to **0.1.57** on 2021-12-03
  - [checkov](https://www.checkov.io/) from 2.0.621 to **2.0.625** on 2021-12-03
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.56.2 to **0.56.3** on 2021-12-04
  - [pylint](https://www.pylint.org) from 2.12.1 to **2.12.2** on 2021-12-04
  - [checkov](https://www.checkov.io/) from 2.0.625 to **2.0.626** on 2021-12-04
  - [eslint](https://eslint.org) from 8.3.0 to **8.4.0** on 2021-12-04
  - [prettier](https://prettier.io/) from 2.5.0 to **2.5.1** on 2021-12-05
  - [black](https://black.readthedocs.io/en/stable/) from 21.11 to **21.12** on 2021-12-06
  - [checkov](https://www.checkov.io/) from 2.0.626 to **2.0.628** on 2021-12-06
  - [checkov](https://www.checkov.io/) from 2.0.628 to **2.0.632** on 2021-12-07
  - [eslint](https://eslint.org) from 8.4.0 to **8.4.1** on 2021-12-07
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.13.1 to **5.13.2** on 2021-12-07
  - [checkov](https://www.checkov.io/) from 2.0.632 to **2.0.634** on 2021-12-07
  - [tflint](https://github.com/terraform-linters/tflint) from 0.33.1 to **0.33.2** on 2021-12-07
  - [checkov](https://www.checkov.io/) from 2.0.634 to **2.0.636** on 2021-12-08

## [v5.2.0] - 2021-11-18

- Fix release doc CI
- Add <utteranc.es> comments in online documentation
- Add link to MegaLinter documentation in console logs

- Linter versions upgrades
  - [actionlint](https://rhysd.github.io/actionlint/) from 1.6.7 to **1.6.8** on 2021-11-15
  - [checkov](https://www.checkov.io/) from 2.0.572 to **2.0.573** on 2021-11-15
  - [checkov](https://www.checkov.io/) from 2.0.573 to **2.0.574** on 2021-11-15
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.56.0 to **0.56.1** on 2021-11-17
  - [checkov](https://www.checkov.io/) from 2.0.574 to **2.0.580** on 2021-11-17
  - [black](https://black.readthedocs.io/en/stable/) from 21.10 to **21.11** on 2021-11-17
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.12.6 to **5.13.0** on 2021-11-17
  - [checkov](https://www.checkov.io/) from 2.0.580 to **2.0.582** on 2021-11-17
  - [checkov](https://www.checkov.io/) from 2.0.582 to **2.0.583** on 2021-11-18
  - [phpstan](https://phpstan.org/) from 1.1.2 to **1.2.0** on 2021-11-18
  - [checkov](https://www.checkov.io/) from 2.0.583 to **2.0.587** on 2021-11-18

## [v5.1.0] - 2021-11-15

- Fix config issue with IGNORE_GITIGNORED_FILES (#932)
- Bypass random CI issue with sql_tsqllint_test test version and test help
- New configuration **PRINT_ALL_FILES** (default: `true`). If set to `false`, console log only displays updated and error files, not all of them
- Update **black** configuration, that now uses a `pyproject.toml` file (#949)
- Allows `list_of_files` cli_lint_mode on Psalm linter to improve performance compare to `file` mode
- mega-linter-runner: Upgrade yeoman environment to allow spaces in path
- Documentation versioning with mike
- Accordingly, to official [PHPStan documentation](https://phpstan.org/user-guide/rule-levels), the TEMPLATES/phpstan.neon.dist config file set default level to zero.
- Downgrade dotnet from 6.0 to 5.0, to be compliant with tsqllint
- Allow GithubStatusReporter to work for other CI platforms
- Add license badge in linters documentation (All linters)
- Upgrade checkov install instructions to use alpine-oriented ones
- Fix wrong errors count displayed with PHPStan and Psalm linters (#985)
- Fix typo error in `.jscpd.json` config file (#986)
- Deprecate `DEFAULT_BRANCH`, and change its default from `master` to `HEAD` (#915)

- Core architecture
  - New configuration **PRINT_ALL_FILES** (default: `true`). If set to `false`, console log only displays updated and error files, not all of them
  - Documentation versioning with mike
  - Allow GithubStatusReporter to work for other CI platforms
  - Add license info in **List of linters** documentation page

- Linters
  - Update **black** configuration, that now uses a `pyproject.toml` file (#949)
  - Allows `list_of_files` cli_lint_mode on Psalm linter to improve performance compare to `file` mode
  - Upgrade checkov install instructions to use alpine-oriented ones
  - Accordingly, to official [PHPStan documentation](https://phpstan.org/user-guide/rule-levels), the TEMPLATES/phpstan.neon.dist config file set default level to zero.
  - Downgrade dotnet from 6.0 to 5.0, to be compliant with tsqllint

- Bug fixes
  - Fix config issue with IGNORE_GITIGNORED_FILES (#932)
  - Bypass random CI issue with sql_tsqllint_test test version and test help
  - mega-linter-runner: Upgrade yeoman environment to allow spaces in path

- Linter versions upgrades
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.12.5 to **5.12.6** on 2021-11-04
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.55.0 to **0.56.0** on 2021-11-06
  - [coffeelint](http://www.coffeelint.org) from 5.1.0 to **5.1.1** on 2021-11-06
  - [jscpd](https://github.com/kucherenko/jscpd/tree/master/packages/jscpd) from 3.3.26 to **3.4.1** on 2021-11-06
  - [hadolint](https://github.com/hadolint/hadolint) from 2.7.0 to **2.8.0** on 2021-11-06
  - [eslint-plugin-jsonc](https://ota-meshi.github.io/eslint-plugin-jsonc/) from 1.7.0 to **2.0.0** on 2021-11-06
  - [phpstan](https://phpstan.org/) from 1.0.2 to **1.1.0** on 2021-11-06
  - [jscpd](https://github.com/kucherenko/jscpd/tree/master/packages/jscpd) from 3.4.1 to **3.4.2** on 2021-11-07
  - [shellcheck](https://github.com/koalaman/shellcheck) from 0.7.2 to **0.8.0** on 2021-11-07
  - [coffeelint](http://www.coffeelint.org) from 5.1.1 to **5.2.0** on 2021-11-07
  - [jscpd](https://github.com/kucherenko/jscpd/tree/master/packages/jscpd) from 3.4.2 to **3.3.26** on 2021-11-07
  - [hadolint](https://github.com/hadolint/hadolint) from 2.8.0 to **2.7.0** on 2021-11-07
  - [sqlfluff](https://www.sqlfluff.com/) from 0.7.1 to **0.8.0** on 2021-11-07
  - [sqlfluff](https://www.sqlfluff.com/) from 0.8.0 to **0.8.1** on 2021-11-08
  - [swiftlint](https://github.com/realm/SwiftLint) from 0.43.1 to **0.44.0** on 2021-11-08
  - [actionlint](https://rhysd.github.io/actionlint/) from 1.6.6 to **1.6.7** on 2021-11-08
  - [eslint](https://eslint.org) from 7.32.0 to **8.2.0** on 2021-11-08
  - [swiftlint](https://github.com/realm/SwiftLint) from 0.44.0 to **0.45.0** on 2021-11-08
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.1.5 to **7.2.0** on 2021-11-08
  - [protolint](https://github.com/yoheimuta/protolint) from 0.35.1 to **0.35.2** on 2021-11-09
  - [isort](https://pycqa.github.io/isort/) from 5.10.0 to **5.10.1** on 2021-11-09
  - [phpstan](https://phpstan.org/) from 1.1.1 to **1.1.2** on 2021-11-09
  - [kics](https://www.kics.io) from 1.4.6 to **1.4.7** on 2021-11-11
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.0.10 to **1.0.11** on 2021-11-11
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.35.6 to **0.35.8** on 2021-11-11
  - [htmlhint](https://htmlhint.com/) from 0.16.0 to **0.16.1** on 2021-11-12
  - [checkov](https://www.checkov.io/) from 2.0.524 to **2.0.566** on 2021-11-12
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.35.8 to **0.35.9** on 2021-11-12
  - [bandit](https://bandit.readthedocs.io/en/latest/) from 1.7.0 to **1.7.1** on 2021-11-13
  - [scalafix](https://scalacenter.github.io/scalafix/) from 0.9.31 to **0.9.32** on 2021-11-13
  - [checkov](https://www.checkov.io/) from 2.0.566 to **2.0.569** on 2021-11-13
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.35.9 to **0.35.10** on 2021-11-13
  - [checkov](https://www.checkov.io/) from 2.0.569 to **2.0.571** on 2021-11-14
  - [stylelint](https://stylelint.io) from 14.0.1 to **14.1.0** on 2021-11-14
  - [checkov](https://www.checkov.io/) from 2.0.571 to **2.0.572** on 2021-11-14

## [v5.0.7] - 2021-11-04

- Fix that upgrader removed all jobs after cancel_duplicates but the last (#925)

- Linter versions upgrades
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.54.4 to **0.55.0** on 2021-11-03
  - [phpstan](https://phpstan.org/) from 1.0.0 to **1.0.1** on 2021-11-03
  - [golangci-lint](https://golangci-lint.run/) from 1.42.1 to **1.43.0** on 2021-11-04
  - [phpstan](https://phpstan.org/) from 1.0.1 to **1.0.2** on 2021-11-04
  - [isort](https://pycqa.github.io/isort/) from 5.9.3 to **5.10.0** on 2021-11-04

## [v5.0.6] - 2021-11-03

- Use GH actions concurrency to cancel runs (#921)

## [v5.0.5] - 2021-11-02

- Fix `mega-linter-runner --install` template for Github Action Workflow
- Replace expression "abusive copy-paste" by "excessive copy-paste"

- Linter versions upgrades
  - [coffeelint](http://www.coffeelint.org) from 5.0.5 to **5.1.0** on 2021-11-02
  - [phpstan](https://phpstan.org/) from 0.12.99 to **1.0.0** on 2021-11-02
  - [black](https://black.readthedocs.io/en/stable/) from 21.9 to **21.10** on 2021-11-02
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.12.4 to **5.12.5** on 2021-11-02
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.35.5 to **0.35.6** on 2021-11-02

## [v5.0.2] - 2021-10-31

- Quick build to fix stargazers badge regression (see issue #873) (#909)
- Improve Azure Pipeline template documentation (#908)
- Take in account  legacy docker images for total docker pull count (#910)
- Upgrade stale github action

- Linter versions upgrades
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.12.3 to **5.12.4** on 2021-10-31
  - [checkstyle](https://checkstyle.sourceforge.io) from 9.0.1 to **9.1** on 2021-10-31
  - [tflint](https://github.com/terraform-linters/tflint) from 0.33.0 to **0.33.1** on 2021-10-31

## [v5.0.1] - 2021-10-30

- Fix mega-linter-runner bug related to v5
- Fix online documentation

## [v5.0.0] - 2021-10-30

- Migration from github individual repo **nvuillam/mega-linter** to github organization repo **megalinter/megalinter**
- Migration from docker hub space **nvuillam** to space **megalinter**
  - Docker images are now **megalinter/megalinter** or **megalinter/megalinter-FLAVOR**
- Documentation is now hosted at <https://megalinter.github.io/>
- Tool to upgrade user repos configuration files using `npx mega-linter-runner --upgrade` (will upgrade references to nvuillam/mega-linter into megalinter/megalinter)
- Version management: Now mega-linter docker images, github action and mega-linter-runner versions are aligned
  - **latest** for latest official release
  - **beta** for current content of main branch
  - **alpha** for current content of alpha branch
  - docker image, github action and mega-linter-runner can still be called with exact version number
- Being more inclusive: rename `master` branch into `main`
- **IGNORE_GITIGNORED_FILES** parameter default to `true`

## [4.47.0] - 2021-10-30

- Upgrades
  - Base docker image python:3.9.6-alpine3.13 to python:3.9.7-alpine3.13
  - Automerge internal job pascalgn/automerge-action-0.14.2 to pascalgn/automerge-action-0.14.3
- Config reporter: Parse `.vscode/extensions.json` as json5 (with comments)
- Add eslint-plugin-jsx-a11y dependency
- Rename default PHPStan config file, from `phpstan.neon` to `phpstan.neon.dist` accordingly to [PHPStan resolution priority](https://phpstan.org/config-reference#config-file)
- Allows `list_of_files` cli_lint_mode on PHPSTAN linter to improve performance compare to `file` mode
- `phpstan` is now installed with `phive` rather than `composer` (reduces disk usage)
- Allows `list_of_files` cli_lint_mode on PHPCS linter to improve performance compare to `file` mode
- Allows `list_of_files` cli_lint_mode on EditorConfig-Checker linter to improve performance compare to `file` mode
- Fix internal CSS because of StyleLint new rule `selector-class-pattern`
- Fix ansible-lint version collection
- Message to recommend to upgrade to MegaLinter v5

- Linter versions upgrades
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.54.1 to **0.54.2** on 2021-09-23
  - [eslint-plugin-jsonc](https://ota-meshi.github.io/eslint-plugin-jsonc/) from 1.6.0 to **1.7.0** on 2021-09-23
  - [checkov](https://www.checkov.io/) from 2.0.430 to **2.0.436** on 2021-09-23
  - [coffeelint](http://www.coffeelint.org) from 5.0.3 to **5.0.4** on 2021-09-24
  - [checkov](https://www.checkov.io/) from 2.0.436 to **2.0.438** on 2021-09-24
  - [php](https://www.php.net) from 7.4.21 to **7.4.24** on 2021-09-24
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.32.3 to **0.32.4** on 2021-09-24
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.8.0 to **6.8.1** on 2021-09-25
  - [checkov](https://www.checkov.io/) from 2.0.438 to **2.0.441** on 2021-09-25
  - [secretlint](https://github.com/secretlint/secretlint) from 4.0.0 to **4.1.0** on 2021-09-25
  - [checkov](https://www.checkov.io/) from 2.0.441 to **2.0.442** on 2021-09-26
  - [checkov](https://www.checkov.io/) from 2.0.442 to **2.0.443** on 2021-09-27
  - [protolint](https://github.com/yoheimuta/protolint) from 0.32.0 to **0.35.1** on 2021-09-26
  - [protolint](https://github.com/yoheimuta/protolint) from 0.32.0 to **0.35.1** on 2021-09-27
  - [checkov](https://www.checkov.io/) from 2.0.443 to **2.0.446** on 2021-09-27
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.10.1 to **5.11.0** on 2021-09-29
  - [checkov](https://www.checkov.io/) from 2.0.446 to **2.0.448** on 2021-09-29
  - [npm-groovy-lint](https://nvuillam.github.io/npm-groovy-lint/) from 8.2.0 to **9.0.0** on 2021-09-30
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 2.11.0 to **2.12.0** on 2021-09-30
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 2.11.0 to **2.12.0** on 2021-09-30
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 2.11.0 to **2.12.0** on 2021-09-30
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.8.1 to **6.9.0** on 2021-09-30
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.11.0 to **5.11.1** on 2021-09-30
  - [checkov](https://www.checkov.io/) from 2.0.448 to **2.0.454** on 2021-09-30
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.9.0 to **6.9.1** on 2021-09-30
  - [checkov](https://www.checkov.io/) from 2.0.454 to **2.0.461** on 2021-09-30
  - [checkstyle](https://checkstyle.sourceforge.io) from 9.0 to **9.0.1** on 2021-10-03
  - [luacheck](https://luacheck.readthedocs.io) from 0.23.0 to **0.25.0** on 2021-10-03
  - [checkov](https://www.checkov.io/) from 2.0.461 to **2.0.467** on 2021-10-03
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.0.7 to **1.0.8** on 2021-10-03
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.32.4 to **0.34.0** on 2021-10-03
  - [sqlfluff](https://www.sqlfluff.com/) from 0.6.6 to **0.6.7** on 2021-10-05
  - [checkov](https://www.checkov.io/) from 2.0.467 to **2.0.469** on 2021-10-05
  - [markdownlint](https://github.com/DavidAnson/markdownlint) from 0.28.1 to **0.29.0** on 2021-10-06
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.11.1 to **5.12.0** on 2021-10-06
  - [sqlfluff](https://www.sqlfluff.com/) from 0.6.7 to **0.6.8** on 2021-10-06
  - [checkov](https://www.checkov.io/) from 2.0.469 to **2.0.475** on 2021-10-06
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.12.0 to **5.12.1** on 2021-10-06
  - [checkov](https://www.checkov.io/) from 2.0.475 to **2.0.476** on 2021-10-06
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.12.1 to **5.12.2** on 2021-10-07
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.34.0 to **0.34.1** on 2021-10-07
  - [checkov](https://www.checkov.io/) from 2.0.476 to **2.0.477** on 2021-10-07
  - [terrascan](https://www.accurics.com/products/terrascan/) from 1.10.0 to **1.11.0** on 2021-10-07
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.12.2 to **5.12.3** on 2021-10-09
  - [checkov](https://www.checkov.io/) from 2.0.477 to **2.0.479** on 2021-10-09
  - [sqlfluff](https://www.sqlfluff.com/) from 0.6.8 to **0.6.9** on 2021-10-10
  - [checkov](https://www.checkov.io/) from 2.0.479 to **2.0.481** on 2021-10-10
  - [checkov](https://www.checkov.io/) from 2.0.481 to **2.0.482** on 2021-10-10
  - [phpcs](https://github.com/squizlabs/PHP_CodeSniffer) from 3.6.0 to **3.6.1** on 2021-10-12
  - [flake8](https://flake8.pycqa.org) from 3.9.2 to **4.0.1** on 2021-10-12
  - [checkov](https://www.checkov.io/) from 2.0.482 to **2.0.484** on 2021-10-12
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.34.1 to **0.34.3** on 2021-10-12
  - [checkov](https://www.checkov.io/) from 2.0.484 to **2.0.485** on 2021-10-13
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.1.4 to **7.1.5** on 2021-10-16
  - [sqlfluff](https://www.sqlfluff.com/) from 0.6.9 to **0.7.0** on 2021-10-16
  - [checkov](https://www.checkov.io/) from 2.0.485 to **2.0.491** on 2021-10-16
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.0.8 to **1.0.9** on 2021-10-16
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.34.3 to **0.35.3** on 2021-10-16
  - [tflint](https://github.com/terraform-linters/tflint) from 0.32.1 to **0.33.0** on 2021-10-16
  - [checkov](https://www.checkov.io/) from 2.0.491 to **2.0.492** on 2021-10-17
  - [actionlint](https://rhysd.github.io/actionlint/) from 1.6.5 to **1.6.6** on 2021-10-17
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.54.2 to **0.54.3** on 2021-10-21
  - [coffeelint](http://www.coffeelint.org) from 5.0.4 to **5.0.5** on 2021-10-21
  - [snakefmt](https://github.com/snakemake/snakefmt) from 0.4.3 to **0.4.4** on 2021-10-21
  - [tekton-lint](https://github.com/IBM/tekton-lint) from 0.5.2 to **0.6.0** on 2021-10-21
  - [checkov](https://www.checkov.io/) from 2.0.492 to **2.0.497** on 2021-10-21
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.35.3 to **0.35.4** on 2021-10-21
  - [stylelint](https://stylelint.io) from 13.13.1 to **14.0.0** on 2021-10-24
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.55 to **0.1.56** on 2021-10-24
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.9.1 to **6.10.0** on 2021-10-24
  - [sqlfluff](https://www.sqlfluff.com/) from 0.7.0 to **0.7.1** on 2021-10-24
  - [checkov](https://www.checkov.io/) from 2.0.497 to **2.0.509** on 2021-10-24
  - [terrascan](https://www.accurics.com/products/terrascan/) from 1.11.0 to **1.12.0** on 2021-10-24
  - [checkov](https://www.checkov.io/) from 2.0.509 to **2.0.510** on 2021-10-25
  - [checkov](https://www.checkov.io/) from 2.0.510 to **2.0.516** on 2021-10-26
  - [stylelint](https://stylelint.io) from 14.0.0 to **14.0.1** on 2021-10-26
  - [checkov](https://www.checkov.io/) from 2.0.516 to **2.0.524** on 2021-10-26
  - [php](https://www.php.net) from 7.4.24 to **7.4.25** on 2021-10-27
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.54.3 to **0.54.4** on 2021-10-28
  - [htmlhint](https://htmlhint.com/) from 0.15.2 to **0.16.0** on 2021-10-29
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.0.9 to **1.0.10** on 2021-10-29
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.35.4 to **0.35.5** on 2021-10-29

## [4.46.0] - 2021-09-21

- Add openssh apk for git repos using ssh
- Change default yamllint config file name from `.yaml-lint.yml` to `.yamllint.yml`
- Allow to disable console reporter using `CONSOLE_REPORTER: false`
- Override `cli_lint_mode` of linters using configuration : _LINTER_\_CLI_LINT_MODE
- Performances
  - Use list_of_files linting mode for yamllint , black and prettier
- Fixes
  - Add CONFIG_REPORTER in json schema
  - Fix Broken CI due to mega-linter test plugin

- Linter versions upgrades
  - [checkov](https://www.checkov.io/) from 2.0.396 to **2.0.399** on 2021-09-06
  - [golangci-lint](https://golangci-lint.run/) from 1.42.0 to **1.42.1** on 2021-09-07
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.7.0 to **6.8.0** on 2021-09-07
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.53.1 to **0.54.1** on 2021-09-12
  - [prettier](https://prettier.io/) from 2.3.2 to **2.4.0** on 2021-09-12
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.54 to **0.1.55** on 2021-09-12
  - [sqlfluff](https://www.sqlfluff.com/) from 0.6.4 to **0.6.5** on 2021-09-12
  - [checkov](https://www.checkov.io/) from 2.0.399 to **2.0.407** on 2021-09-12
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.31.8 to **0.31.10** on 2021-09-12
  - [tflint](https://github.com/terraform-linters/tflint) from 0.31.0 to **0.32.1** on 2021-09-12
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.9.0 to **5.9.1** on 2021-09-12
  - [phpstan](https://phpstan.org/) from 0.12.98 to **0.12.99** on 2021-09-15
  - [puppet-lint](http://puppet-lint.com/) from 2.5.0 to **2.5.2** on 2021-09-15
  - [black](https://black.readthedocs.io/en/stable/) from 21.8 to **21.9** on 2021-09-15
  - [checkov](https://www.checkov.io/) from 2.0.407 to **2.0.414** on 2021-09-15
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.31.10 to **0.31.11** on 2021-09-15
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.31.11 to **0.32.1** on 2021-09-15
  - [secretlint](https://github.com/secretlint/secretlint) from 3.3.0 to **4.0.0** on 2021-09-18
  - [htmlhint](https://htmlhint.com/) from 0.15.1 to **0.15.2** on 2021-09-18
  - [prettier](https://prettier.io/) from 2.4.0 to **2.4.1** on 2021-09-18
  - [pylint](https://www.pylint.org) from 2.10.2 to **2.11.1** on 2021-09-18
  - [scalafix](https://scalacenter.github.io/scalafix/) from 0.9.30 to **0.9.31** on 2021-09-18
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.9.1 to **5.10.1** on 2021-09-18
  - [checkov](https://www.checkov.io/) from 2.0.414 to **2.0.421** on 2021-09-18
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.0.6 to **1.0.7** on 2021-09-18
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.32.1 to **0.32.2** on 2021-09-18
  - [checkov](https://www.checkov.io/) from 2.0.421 to **2.0.425** on 2021-09-19
  - [checkov](https://www.checkov.io/) from 2.0.425 to **2.0.426** on 2021-09-19
  - [checkov](https://www.checkov.io/) from 2.0.426 to **2.0.427** on 2021-09-20
  - [coffeelint](http://www.coffeelint.org) from 5.0.2 to **5.0.3** on 2021-09-21
  - [rstfmt](https://github.com/dzhu/rstfmt) from 0.0.9 to **0.0.10** on 2021-09-21
  - [sqlfluff](https://www.sqlfluff.com/) from 0.6.5 to **0.6.6** on 2021-09-21
  - [checkov](https://www.checkov.io/) from 2.0.427 to **2.0.428** on 2021-09-21
  - [checkov](https://www.checkov.io/) from 2.0.428 to **2.0.430** on 2021-09-21
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.32.2 to **0.32.3** on 2021-09-21

## [4.45.0] - 2021-09-04

- New CONFIG_REPORTER to generate "ready to copy" folder containing default linter configurations and IDE extensions recommendations
- New JSON_REPORTER to generate an output json file in report folder
- Manage pre_commands and post_commands at linter level
  - Default commands defined at linter descriptor level
  - Overridable by user in linterName_PRE_COMMANDS and linterName_POST_COMMANDS in `.mega-linter.yml`
- Fix tflint config so no custom PRE_COMMAND is necessary
- Use dotnet installer to setup tsqllint. tsqllint is now part of the main MegaLinter flavor, but removed from JAVASCRIPT flavor
- Ignore linter_FILTER_REGEX_INCLUDE/linter_FILTER_REGEX_EXCLUDE for linters running on the whole project directory
- mega-linter-runner updates
  - New CLI argument `--json`, to get the full report as JSON in stdout last line
  - Fix mega-linter-runner --install when local folder path contain spaces
  - Upgrade mega-linter-runner dependencies (npm audit fix)
  - Better comments for generated .mega-linter.yml config file

- Linter versions upgrades
  - [markdown-table-formatter](https://www.npmjs.com/package/markdown-table-formatter) from 1.1.0 to **1.2.0** on 2021-08-20
  - [phpstan](https://phpstan.org/) from 0.12.94 to **0.12.95** on 2021-08-20
  - [pylint](https://www.pylint.org) from 2.9.6 to **2.10.1** on 2021-08-21
  - [sqlfluff](https://www.sqlfluff.com/) from 0.6.3 to **0.6.4** on 2021-08-21
  - [phpstan](https://phpstan.org/) from 0.12.95 to **0.12.96** on 2021-08-21
  - [pylint](https://www.pylint.org) from 2.10.1 to **2.10.2** on 2021-08-22
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.7.2 to **5.8.0** on 2021-08-22
  - [yamllint](https://yamllint.readthedocs.io/) from 1.26.2 to **1.26.3** on 2021-08-22
  - [eslint-plugin-jsonc](https://ota-meshi.github.io/eslint-plugin-jsonc/) from 1.5.0 to **1.6.0** on 2021-08-23
  - [checkov](https://www.checkov.io/) from 2.0.363 to **2.0.367** on 2021-08-23
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.8.0 to **5.8.1** on 2021-08-24
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.31.5 to **0.31.6** on 2021-08-24
  - [hadolint](https://github.com/hadolint/hadolint) from 2.6.0 to **2.7.0** on 2021-08-28
  - [dotenv-linter](https://dotenv-linter.github.io/) from 3.1.0 to **3.1.1** on 2021-08-28
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.8.1 to **5.8.2** on 2021-08-28
  - [checkov](https://www.checkov.io/) from 2.0.367 to **2.0.376** on 2021-08-28
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.31.6 to **0.31.7** on 2021-08-28
  - [terrascan](https://www.accurics.com/products/terrascan/) from 1.9.0 to **1.10.0** on 2021-08-28
  - [checkov](https://www.checkov.io/) from 2.0.376 to **2.0.377** on 2021-08-29
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.53.0 to **0.53.1** on 2021-08-31
  - [tsqllint](https://github.com/tsqllint/tsqllint) from 1.13.5.0 to **1.14.0.0** on 2021-08-31
  - [checkov](https://www.checkov.io/) from 2.0.377 to **2.0.380** on 2021-08-31
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.31.7 to **0.31.8** on 2021-08-31
  - [checkstyle](https://checkstyle.sourceforge.io) from 8.45.1 to **9.0** on 2021-09-01
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.8.2 to **5.9.0** on 2021-09-01
  - [checkov](https://www.checkov.io/) from 2.0.380 to **2.0.387** on 2021-09-01
  - [phpstan](https://phpstan.org/) from 0.12.96 to **0.12.97** on 2021-09-02
  - [checkov](https://www.checkov.io/) from 2.0.387 to **2.0.392** on 2021-09-02
  - [checkov](https://www.checkov.io/) from 2.0.392 to **2.0.393** on 2021-09-02
  - [phpstan](https://phpstan.org/) from 0.12.97 to **0.12.98** on 2021-09-03
  - [checkov](https://www.checkov.io/) from 2.0.393 to **2.0.395** on 2021-09-03
  - [checkov](https://www.checkov.io/) from 2.0.395 to **2.0.396** on 2021-09-04
  - [black](https://black.readthedocs.io/en/stable/) from 20.8 to **21.8** on 2021-09-04
  - [snakefmt](https://github.com/snakemake/snakefmt) from 0.4.2 to **0.4.3** on 2021-09-04
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.0.5 to **1.0.6** on 2021-09-04

## [4.44.0] - 2021-08-19

- Upgrade tflint descriptor to use ghcr.io/terraform-linters/tflint docker image and initialize tflint
- Add page for flavors stats in online documentation
- Unable to list git ignored files when IGNORED_GITIGNORED_FILES: true ([#PR605](https://github.com/megalinter/megalinter/pull/605), by [David Bernard](https://github.com/davidB) with the contribution of [Tim Pansino](https://github.com/TimPansino))

- Linter versions upgrades
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.1.3 to **7.1.4** on 2021-08-13
  - [checkov](https://www.checkov.io/) from 2.0.347 to **2.0.348** on 2021-08-13
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.6.6 to **5.6.7** on 2021-08-14
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.31.3 to **0.31.4** on 2021-08-14
  - [tflint](https://github.com/terraform-linters/tflint) from 0.29.1 to **0.31.0** on 2021-08-14
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.6.7 to **5.7.1** on 2021-08-15
  - [eslint-plugin-jsonc](https://ota-meshi.github.io/eslint-plugin-jsonc/) from 1.4.0 to **1.5.0** on 2021-08-15
  - [checkov](https://www.checkov.io/) from 2.0.348 to **2.0.350** on 2021-08-15
  - [coffeelint](http://www.coffeelint.org) from 5.0.1 to **5.0.2** on 2021-08-17
  - [scalafix](https://scalacenter.github.io/scalafix/) from 0.9.29 to **0.9.30** on 2021-08-17
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.7.1 to **5.7.2** on 2021-08-17
  - [sqlfluff](https://www.sqlfluff.com/) from 0.6.2 to **0.6.3** on 2021-08-17
  - [checkov](https://www.checkov.io/) from 2.0.350 to **2.0.352** on 2021-08-17
  - [golangci-lint](https://golangci-lint.run/) from 1.41.1 to **1.42.0** on 2021-08-18
  - [checkov](https://www.checkov.io/) from 2.0.352 to **2.0.361** on 2021-08-18
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 2.10.1005 to **2.11.0** on 2021-08-19
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 2.10.1005 to **2.11.0** on 2021-08-19
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 2.10.1005 to **2.11.0** on 2021-08-19
  - [checkov](https://www.checkov.io/) from 2.0.361 to **2.0.363** on 2021-08-19
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.0.4 to **1.0.5** on 2021-08-19
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.31.4 to **0.31.5** on 2021-08-19

## [4.43.0] - 2021-08-12

- Add [secretlint](https://github.com/secretlint/secretlint) to check for credentials , secrets and passwords stored in linted repository

- Linter versions upgrades
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.6.1 to **6.7.0** on 2021-08-12
  - [checkov](https://www.checkov.io/) from 2.0.344 to **2.0.346** on 2021-08-12
  - [checkov](https://www.checkov.io/) from 2.0.346 to **2.0.347** on 2021-08-12

## [4.42.0] - 2021-08-12

- Add [tsqllint](https://github.com/tsqllint/tsqllint) to lint [TSQL files](https://www.tsql.info/)
- Store docker pulls statistics history
- add `IGNORE_GENERATED_FILES` in json schema
- allow commonjs config file for eslint - [#629](https://github.com/megalinter/megalinter/pull/629), by [vitalitytv](https://github.com/vitaliytv)

- Linter versions upgrades
  - [checkov](https://www.checkov.io/) from 2.0.295 to **2.0.297** on 2021-07-25
  - [puppet-lint](http://puppet-lint.com/) from 2.4.2 to **2.5.0** on 2021-07-26
  - [checkov](https://www.checkov.io/) from 2.0.297 to **2.0.303** on 2021-07-26
  - [checkov](https://www.checkov.io/) from 2.0.303 to **2.0.307** on 2021-07-28
  - [v8r](https://github.com/chris48s/v8r) from 0.5.0 to **0.6.0** on 2021-07-29
  - [pylint](https://www.pylint.org) from 2.9.5 to **2.9.6** on 2021-07-29
  - [checkov](https://www.checkov.io/) from 2.0.307 to **2.0.313** on 2021-07-29
  - [isort](https://pycqa.github.io/isort/) from 5.9.2 to **5.9.3** on 2021-07-30
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.53 to **0.1.54** on 2021-07-30
  - [snakefmt](https://github.com/snakemake/snakefmt) from 0.4.1 to **0.4.2** on 2021-07-30
  - [checkov](https://www.checkov.io/) from 2.0.313 to **2.0.317** on 2021-07-30
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.31.1 to **0.31.2** on 2021-07-30
  - [eslint](https://eslint.org) from 7.31.0 to **7.32.0** on 2021-07-31
  - [phpstan](https://phpstan.org/) from 0.12.93 to **0.12.94** on 2021-07-31
  - [checkov](https://www.checkov.io/) from 2.0.317 to **2.0.318** on 2021-07-31
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.31.2 to **0.31.3** on 2021-07-31
  - [checkstyle](https://checkstyle.sourceforge.io) from 8.44 to **8.45** on 2021-08-01
  - [shfmt](https://github.com/mvdan/sh) from 3.3.0 to **3.3.1** on 2021-08-02
  - [checkov](https://www.checkov.io/) from 2.0.318 to **2.0.323** on 2021-08-02
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.52.0 to **0.53.0** on 2021-08-03
  - [checkov](https://www.checkov.io/) from 2.0.323 to **2.0.327** on 2021-08-03
  - [remark-lint](https://remark.js.org/) from 13.0.0 to **14.0.1** on 2021-08-04
  - [checkov](https://www.checkov.io/) from 2.0.327 to **2.0.330** on 2021-08-04
  - [yamllint](https://yamllint.readthedocs.io/) from 1.26.1 to **1.26.2** on 2021-08-04
  - [checkov](https://www.checkov.io/) from 2.0.330 to **2.0.334** on 2021-08-05
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.0.3 to **1.0.4** on 2021-08-05
  - [checkov](https://www.checkov.io/) from 2.0.334 to **2.0.336** on 2021-08-05
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 2.10.0 to **2.10.1005** on 2021-08-06
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 2.10.0 to **2.10.1005** on 2021-08-06
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 2.10.0 to **2.10.1005** on 2021-08-06
  - [v8r](https://github.com/chris48s/v8r) from 0.6.0 to **0.6.1** on 2021-08-07
  - [checkov](https://www.checkov.io/) from 2.0.336 to **2.0.337** on 2021-08-07
  - [terrascan](https://www.accurics.com/products/terrascan/) from 1.8.1 to **1.9.0** on 2021-08-07
  - [checkov](https://www.checkov.io/) from 2.0.337 to **2.0.338** on 2021-08-08
  - [checkstyle](https://checkstyle.sourceforge.io) from 8.45 to **8.45.1** on 2021-08-09
  - [checkov](https://www.checkov.io/) from 2.0.338 to **2.0.340** on 2021-08-09
  - [checkov](https://www.checkov.io/) from 2.0.340 to **2.0.342** on 2021-08-10
  - [checkov](https://www.checkov.io/) from 2.0.342 to **2.0.344** on 2021-08-10

## [4.41.0] - 2021-07-25

- New config variable **IGNORE_GITIGNORED_FILES** (default: `false`). If set to `true`, MegaLinter will skips files ignored by git using `.gitignore` files
- New config variable **IGNORE_GENERATED_FILES** (default: `false`). If set to `true`, MegaLinter will skips files containing `@generated` marker and not containing `@not-generated` marker

- Linter versions upgrades
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 2.9.2 to **2.9.1** on 2021-07-14
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 2.9.2 to **2.9.1** on 2021-07-14
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 2.9.2 to **2.9.1** on 2021-07-14
  - [checkov](https://www.checkov.io/) from 2.0.267 to **2.0.269** on 2021-07-14
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.5.3 to **6.6.0** on 2021-07-17
  - [sqlfluff](https://www.sqlfluff.com/) from 0.6.0 to **0.6.1** on 2021-07-17
  - [checkov](https://www.checkov.io/) from 2.0.269 to **1.0.860** on 2021-07-17
  - [checkov](https://www.checkov.io/) from 1.0.860 to **2.0.276** on 2021-07-17
  - [eslint](https://eslint.org) from 7.30.0 to **7.31.0** on 2021-07-17
  - [checkov](https://www.checkov.io/) from 2.0.276 to **2.0.278** on 2021-07-18
  - [checkov](https://www.checkov.io/) from 2.0.278 to **2.0.279** on 2021-07-18
  - [checkov](https://www.checkov.io/) from 2.0.279 to **2.0.280** on 2021-07-18
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.6.0 to **6.6.1** on 2021-07-20
  - [checkov](https://www.checkov.io/) from 2.0.280 to **2.0.283** on 2021-07-20
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.0.1 to **1.0.2** on 2021-07-20
  - [phpstan](https://phpstan.org/) from 0.12.92 to **0.12.93** on 2021-07-21
  - [pylint](https://www.pylint.org) from 2.9.3 to **2.9.4** on 2021-07-21
  - [checkov](https://www.checkov.io/) from 2.0.283 to **2.0.287** on 2021-07-21
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.31.0 to **0.31.1** on 2021-07-21
  - [markdownlint](https://github.com/DavidAnson/markdownlint) from 0.27.1 to **0.28.1** on 2021-07-25
  - [pylint](https://www.pylint.org) from 2.9.4 to **2.9.5** on 2021-07-25
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 2.9.1 to **2.10.0** on 2021-07-25
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 2.9.1 to **2.10.0** on 2021-07-25
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 2.9.1 to **2.10.0** on 2021-07-25
  - [sqlfluff](https://www.sqlfluff.com/) from 0.6.1 to **0.6.2** on 2021-07-25
  - [checkov](https://www.checkov.io/) from 2.0.287 to **2.0.295** on 2021-07-25
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.0.2 to **1.0.3** on 2021-07-25
  - [terrascan](https://www.accurics.com/products/terrascan/) from 1.8.0 to **1.8.1** on 2021-07-25
  - [xmllint](https://gitlab.gnome.org/GNOME/libxml2/-/wikis/home) from 20910 to **20912** on 2021-07-25

## [4.40.0] - 2021-07-14

- Add [mypy](https://github.com/python/mypy) python linter
- mega-linter-runner: Add possibility to send the docker image to use, including from another registry than docker hub, with argument `--image`

- Linter versions upgrades
  - [phpstan](https://phpstan.org/) from 0.12.91 to **0.12.92** on 2021-07-10
  - [checkov](https://www.checkov.io/) from 2.0.259 to **2.0.261** on 2021-07-11
  - [checkov](https://www.checkov.io/) from 2.0.261 to **2.0.262** on 2021-07-11
  - [checkov](https://www.checkov.io/) from 2.0.262 to **2.0.263** on 2021-07-12
  - [checkov](https://www.checkov.io/) from 2.0.263 to **2.0.266** on 2021-07-13
  - [checkov](https://www.checkov.io/) from 2.0.266 to **2.0.267** on 2021-07-13

## [4.39.0] - 2021-07-14 [DELETED RELEASE BECAUSE NOT WORKING, USE 4.38.0 UNTIL 4.40.0 RELEASE]

- Add [mypy](https://github.com/python/mypy) python linter
- mega-linter-runner: Add possibility to send the docker image to use, including from another registry than docker hub, with argument `--image`

- Linter versions upgrades
  - [phpstan](https://phpstan.org/) from 0.12.91 to **0.12.92** on 2021-07-10
  - [checkov](https://www.checkov.io/) from 2.0.259 to **2.0.261** on 2021-07-11
  - [checkov](https://www.checkov.io/) from 2.0.261 to **2.0.262** on 2021-07-11
  - [checkov](https://www.checkov.io/) from 2.0.262 to **2.0.263** on 2021-07-12
  - [checkov](https://www.checkov.io/) from 2.0.263 to **2.0.266** on 2021-07-13
  - [checkov](https://www.checkov.io/) from 2.0.266 to **2.0.267** on 2021-07-13

## [4.38.0] - 2021-07-10

- New python linter: [bandit](https://github.com/PyCQA/bandit), added by [Tom Pansino](https://github.com/tpansino)
- Manage Github action versioning: Match MegaLinter docker image version

- Linter versions upgrades
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.5.2 to **6.5.3** on 2021-07-07
  - [checkov](https://www.checkov.io/) from 2.0.251 to **2.0.253** on 2021-07-07
  - [php](https://www.php.net) from 7.4.19 to **7.4.21** on 2021-07-07
  - [sql-lint](https://github.com/joereynolds/sql-lint) from 0.0.18 to **0.0.19** on 2021-07-08
  - [checkov](https://www.checkov.io/) from 2.0.253 to **2.0.257** on 2021-07-08
  - [isort](https://pycqa.github.io/isort/) from 5.9.1 to **5.9.2** on 2021-07-10
  - [checkov](https://www.checkov.io/) from 2.0.257 to **2.0.259** on 2021-07-10

## [4.37.0] - 2021-07-05

- Downgrade npm to npm@latest-6 to avoid idealTree error when using npm install
- Use pip to install ansible & ansible-lint as alpine apk package ansible disappeared
- Add `--doc` argument to build.sh to generate doc only when requested (manually, or from CI job Auto-Update-Linters)
- Add rust in default installations as it's required for latest pip cryptography package

- Linter versions upgrades
  - [rstfmt](https://github.com/dzhu/rstfmt) from 0.0.0 to **0.0.9** on 2021-06-24
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 2.9.1 to **2.9.2** on 2021-06-24
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 2.9.1 to **2.9.2** on 2021-06-24
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 2.9.1 to **2.9.2** on 2021-06-24
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.4.1 to **6.5.0** on 2021-06-24
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from Terraform.v1.0.0 to **1.0.0** on 2021-06-24
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.30.7 to **0.31.0** on 2021-06-24
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.5.0 to **6.5.1** on 2021-06-24
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from 1.0.0 to **1.0.1** on 2021-06-24
  - [prettier](https://prettier.io/) from 2.3.1 to **2.3.2** on 2021-06-27
  - [checkstyle](https://checkstyle.sourceforge.io) from 8.43 to **8.44** on 2021-06-28
  - [checkov](https://www.checkov.io/) from 2.0.226 to **2.0.228** on 2021-06-28
  - [checkov](https://www.checkov.io/) from 2.0.228 to **2.0.229** on 2021-06-28
  - [checkov](https://www.checkov.io/) from 2.0.229 to **2.0.230** on 2021-06-28
  - [checkov](https://www.checkov.io/) from 2.0.230 to **2.0.232** on 2021-06-28
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.51.0 to **0.52.0** on 2021-07-05
  - [hadolint](https://github.com/hadolint/hadolint) from 2.5.0 to **2.6.0** on 2021-07-05
  - [eslint](https://eslint.org) from 7.29.0 to **7.30.0** on 2021-07-05
  - [eslint-plugin-jsonc](https://ota-meshi.github.io/eslint-plugin-jsonc/) from 1.3.1 to **1.4.0** on 2021-07-05
  - [phpstan](https://phpstan.org/) from 0.12.90 to **0.12.91** on 2021-07-05
  - [pylint](https://www.pylint.org) from 2.8.3 to **2.9.3** on 2021-07-05
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.5.1 to **6.5.2** on 2021-07-05
  - [checkov](https://www.checkov.io/) from 2.0.232 to **2.0.250** on 2021-07-05
  - [terrascan](https://www.accurics.com/products/terrascan/) from 1.7.0 to **1.8.0** on 2021-07-05
  - [checkov](https://www.checkov.io/) from 2.0.250 to **2.0.251** on 2021-07-05

## [4.36.0] - 2021-06-22

- Fix Phive (php package manager) installation
- Fix dependency error with importlib_metadata before build

- Linter versions upgrades
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2021.04.23 to **2021.06.18** on 2021-06-22
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.50.0 to **0.51.0** on 2021-06-22
  - [hadolint](https://github.com/hadolint/hadolint) from 2.4.1 to **2.5.0** on 2021-06-22
  - [dotenv-linter](https://dotenv-linter.github.io/) from 3.0.0 to **3.1.0** on 2021-06-22
  - [golangci-lint](https://golangci-lint.run/) from 1.40.1 to **1.41.1** on 2021-06-22
  - [npm-groovy-lint](https://nvuillam.github.io/npm-groovy-lint/) from 8.1.0 to **8.2.0** on 2021-06-22
  - [htmlhint](https://htmlhint.com/) from 0.14.2 to **0.15.1** on 2021-06-22
  - [eslint](https://eslint.org) from 7.28.0 to **7.29.0** on 2021-06-22
  - [eslint-plugin-jsonc](https://ota-meshi.github.io/eslint-plugin-jsonc/) from 1.2.1 to **1.3.1** on 2021-06-22
  - [phpstan](https://phpstan.org/) from 0.12.88 to **0.12.90** on 2021-06-22
  - [isort](https://pycqa.github.io/isort/) from 5.8.0 to **5.9.1** on 2021-06-22
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.1.52 to **0.1.53** on 2021-06-22
  - [snakefmt](https://github.com/snakemake/snakefmt) from 0.4.0 to **0.4.1** on 2021-06-22
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.6.0 to **5.6.6** on 2021-06-22
  - [sqlfluff](https://www.sqlfluff.com/) from 0.5.6 to **0.6.0** on 2021-06-22
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from Terraform.v0.15.5 to **Terraform.v1.0.0** on 2021-06-22
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.29.8 to **0.30.7** on 2021-06-22
  - [terrascan](https://www.accurics.com/products/terrascan/) from 1.6.0 to **1.7.0** on 2021-06-22
  - [tflint](https://github.com/terraform-linters/tflint) from 0.29.0 to **0.29.1** on 2021-06-22

## [4.35.0] - 2021-06-12

- Fix [#304](https://github.com/megalinter/megalinter/issues/304): Display error message when docker isn't found when running mega-linter-runner
- Calculate sum of docker pulls for main page counter badge
- Check _RULES_PATH for active_only_if_file_found check ([#418](https://github.com/megalinter/megalinter/pull/418), by [Omeed Musavi](https://github.com/omusavi))
- Upgrade clj-kondo 2021.04.23-alpine
- Upgrade to python:3.9.5-alpine
- Partial fix [#481](https://github.com/megalinter/megalinter/issues/481): Allow applying fixes on push events ([PR487](https://github.com/megalinter/megalinter/pull/487) by [Vít Kučera](https://github.com/vkucera))
- Fix build.sh on windows
- Add trivy security check of all built MegaLinter docker images

- Linter versions upgrades
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.29.2 to **0.29.3** on 2021-05-16
  - [shfmt](https://github.com/mvdan/sh) from 3.2.4 to **3.3.0** on 2021-05-18
  - [phpstan](https://phpstan.org/) from 0.12.87 to **0.12.88** on 2021-05-18
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.49.1 to **0.49.2** on 2021-05-19
  - [cpplint](https://github.com/cpplint/cpplint) from 1.5.4 to **1.5.5** on 2021-05-21
  - [scalafix](https://scalacenter.github.io/scalafix/) from 0.9.27 to **0.9.28** on 2021-05-21
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.3.0 to **6.4.0** on 2021-05-21
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from Terraform.v0.15.3 to **Terraform.v0.15.4** on 2021-05-21
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.29.3 to **0.29.4** on 2021-05-21
  - [sfdx-scanner-apex](https://forcedotcom.github.io/sfdx-scanner/) from 2.8.0 to **2.9.1** on 2021-05-22
  - [sfdx-scanner-aura](https://forcedotcom.github.io/sfdx-scanner/) from 2.8.0 to **2.9.1** on 2021-05-22
  - [sfdx-scanner-lwc](https://forcedotcom.github.io/sfdx-scanner/) from 2.8.0 to **2.9.1** on 2021-05-22
  - [jscpd](https://github.com/kucherenko/jscpd/tree/master/packages/jscpd) from 3.3.25 to **3.3.26** on 2021-05-24
  - [eslint](https://eslint.org) from 7.26.0 to **7.27.0** on 2021-05-24
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2021.02.13 to **2021.04.23** on 2021-05-24
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.29.4 to **0.29.5** on 2021-05-24
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.4.0 to **6.4.1** on 2021-05-28
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.29.5 to **0.29.6** on 2021-05-28
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.29.6 to **0.29.7** on 2021-05-29
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 4.1.3 to **5.5.2** on 2021-05-30
  - [checkstyle](https://checkstyle.sourceforge.io) from 8.42 to **8.43** on 2021-05-30
  - [scalafix](https://scalacenter.github.io/scalafix/) from 0.9.28 to **0.9.29** on 2021-05-30
  - [pylint](https://www.pylint.org) from 2.8.2 to **2.8.3** on 2021-06-01
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.49.2 to **0.50.0** on 2021-06-04
  - [terraform-fmt](https://www.terraform.io/docs/cli/commands/fmt.html) from Terraform.v0.15.4 to **Terraform.v0.15.5** on 2021-06-04
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.29.7 to **0.29.8** on 2021-06-04
  - [eslint](https://eslint.org) from 7.27.0 to **7.28.0** on 2021-06-05
  - [prettier](https://prettier.io/) from 2.3.0 to **2.3.1** on 2021-06-07
  - [protolint](https://github.com/yoheimuta/protolint) from 0.31.0 to **0.32.0** on 2021-06-07
  - [cspell](https://github.com/streetsidesoftware/cspell/tree/master/packages/cspell) from 5.5.2 to **5.6.0** on 2021-06-07
  - [sql-lint](https://github.com/joereynolds/sql-lint) from 0.0.17 to **0.0.18** on 2021-06-07
  - [tflint](https://github.com/terraform-linters/tflint) from 0.28.1 to **0.29.0** on 2021-06-07

## [4.34.0] - 2021-04-30

- Fix bug in MegaLinter plugins installation (related to [#PR403](https://github.com/megalinter/megalinter/pull/403))

- Linter versions upgrades
  - [sqlfluff](https://www.sqlfluff.com/) from 0.5.3 to **0.5.5** on 2021-05-14
  - [hadolint](https://github.com/hadolint/hadolint) from 2.4.0 to **2.4.1** on 2021-05-15
  - [golangci-lint](https://golangci-lint.run/) from 1.40.0 to **1.40.1** on 2021-05-15
  - [sqlfluff](https://www.sqlfluff.com/) from 0.5.5 to **0.5.6** on 2021-05-15

## [4.33.0] - 2021-04-30

- Split Salesforce sfdx-scanner into pmd, eslint aura and eslint lwc

- Linter versions upgrades
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.1.1 to **6.1.2** on 2021-04-20
  - [stylelint](https://stylelint.io) from 13.12.0 to **13.13.0** on 2021-04-25
  - [hadolint](https://github.com/hadolint/hadolint) from 2.2.0 to **2.3.0** on 2021-04-25
  - [eslint](https://eslint.org) from 7.24.0 to **7.25.0** on 2021-04-25
  - [pylint](https://www.pylint.org) from 2.7.4 to **2.8.0** on 2021-04-25
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.1.2 to **6.2.1** on 2021-04-25
  - [terrascan](https://www.accurics.com/products/terrascan/) from 1.4.0 to **1.5.0** on 2021-04-25
  - [checkstyle](https://checkstyle.sourceforge.io) from 8.41.1 to **8.42** on 2021-04-25
  - [pylint](https://www.pylint.org) from 2.8.0 to **2.8.1** on 2021-04-25
  - [tflint](https://github.com/terraform-linters/tflint) from 0.27.0 to **0.28.0** on 2021-04-25
  - [pylint](https://www.pylint.org) from 2.8.1 to **2.8.2** on 2021-04-27
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.48.3 to **0.49.0** on 2021-04-28
  - [phpstan](https://phpstan.org/) from 0.12.84 to **0.12.85** on 2021-04-28
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.28.21 to **0.29.0** on 2021-04-28
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.2.1 to **6.3.0** on 2021-04-30
  - [terrascan](https://www.accurics.com/products/terrascan/) from 1.5.0 to **1.5.1** on 2021-04-30

## [4.32.0] - 2021-04-20

- Fix #376 : Link-title to license
- Add support from prettier as JSON formatter ([#421](https://github.com/megalinter/megalinter/pull/421), by [Omeed Musavi](https://github.com/omusavi)

- Linter versions upgrades
  - [phpstan](https://phpstan.org/) from 0.12.82 to **0.12.83** on 2021-04-03
  - [markdown-table-formatter](https://www.npmjs.com/package/markdown-table-formatter) from 1.0.4 to **1.1.0** on 2021-04-05
  - [tflint](https://github.com/terraform-linters/tflint) from 0.25.0 to **0.26.0** on 2021-04-05
  - [sqlfluff](https://www.sqlfluff.com/) from 0.4.1 to **0.5.0** on 2021-04-06
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.48.1 to **0.48.2** on 2021-04-07
  - [yamllint](https://yamllint.readthedocs.io/) from 1.26.0 to **1.26.1** on 2021-04-07
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.1.0 to **6.1.1** on 2021-04-08
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.28.16 to **0.28.19** on 2021-04-09
  - [phpcs](https://github.com/squizlabs/PHP_CodeSniffer) from 3.5.8 to **3.6.0** on 2021-04-09
  - [eslint](https://eslint.org) from 7.23.0 to **7.24.0** on 2021-04-10
  - [sqlfluff](https://www.sqlfluff.com/) from 0.5.0 to **0.5.1** on 2021-04-10
  - [protolint](https://github.com/yoheimuta/protolint) from 0.30.1 to **0.31.0** on 2021-04-11
  - [sqlfluff](https://www.sqlfluff.com/) from 0.5.1 to **0.5.2** on 2021-04-11
  - [sfdx-scanner](https://forcedotcom.github.io/sfdx-scanner/) from 2.7.0 to **2.8.0** on 2021-04-14
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.28.19 to **0.28.21** on 2021-04-15
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.48.2 to **0.48.3** on 2021-04-17
  - [flake8](https://flake8.pycqa.org) from 3.9.0 to **3.9.1** on 2021-04-17
  - [tflint](https://github.com/terraform-linters/tflint) from 0.26.0 to **0.27.0** on 2021-04-19
  - [hadolint](https://github.com/hadolint/hadolint) from 2.1.0 to **2.2.0** on 2021-04-19
  - [phpstan](https://phpstan.org/) from 0.12.83 to **0.12.84** on 2021-04-19
  - [shellcheck](https://github.com/koalaman/shellcheck) from 0.7.1 to **0.7.2** on 2021-04-19

## [4.31.0] - 2021-04-03

- Keep license pre-formatted in docs
- Use Python virtual-environment in dev-dependencies shell example
- Fix #367 : Display editorconfig-checker version
- Fix #379 : New configuration FAIL_IF_MISSING_LINTER_IN_FLAVOR

- Linter versions upgrades
  - [flake8](https://flake8.pycqa.org) from 3.8.4 to **3.9.0** on 2021-03-15
  - [ktlint](https://ktlint.github.io) from 0.40.0 to **0.41.0** on 2021-03-21
  - [phpstan](https://phpstan.org/) from 0.12.81 to **0.12.82** on 2021-03-21
  - [isort](https://pycqa.github.io/isort/) from 5.7.0 to **5.8.0** on 2021-03-21
  - [sfdx-scanner](https://forcedotcom.github.io/sfdx-scanner/) from 2.6.0 to **2.7.0** on 2021-03-21
  - [sql-lint](https://github.com/joereynolds/sql-lint) from 0.0.15 to **0.0.16** on 2021-03-21
  - [swiftlint](https://github.com/realm/SwiftLint) from 0.43.0 to **0.43.1** on 2021-03-21
  - [editorconfig-checker](https://editorconfig-checker.github.io/) from 0.0.0 to **2.3.4** on 2021-03-22
  - [ktlint](https://ktlint.github.io) from 0.41.0 to **0.40.0** on 2021-03-22
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.47.2 to **0.48.1** on 2021-03-30
  - [coffeelint](http://www.coffeelint.org) from 4.1.3 to **4.1.4** on 2021-03-30
  - [hadolint](https://github.com/hadolint/hadolint) from 1.23.0 to **2.0.0** on 2021-03-30
  - [golangci-lint](https://golangci-lint.run/) from 1.38.0 to **1.39.0** on 2021-03-30
  - [checkstyle](https://checkstyle.sourceforge.io) from 8.41 to **8.41.1** on 2021-03-30
  - [eslint](https://eslint.org) from 7.22.0 to **7.23.0** on 2021-03-30
  - [kubeval](https://www.kubeval.com/) from 0.15.0 to **0.16.1** on 2021-03-30
  - [perlcritic](https://metacpan.org/pod/Perl::Critic) from 1.138 to **1.140** on 2021-03-30
  - [pylint](https://www.pylint.org) from 2.7.2 to **2.7.4** on 2021-03-30
  - [clippy](https://github.com/rust-lang/rust-clippy) from 0.0.212 to **0.1.51** on 2021-03-30
  - [scalafix](https://scalacenter.github.io/scalafix/) from 0.9.26 to **0.9.27** on 2021-03-30
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.28.9 to **0.28.16** on 2021-03-30
  - [kubeval](https://www.kubeval.com/) from 0.16.0 to **0.16.1** on 2021-03-30
  - [pylint](https://www.pylint.org) from 2.7.3 to **2.7.4** on 2021-03-30
  - [editorconfig-checker](https://editorconfig-checker.github.io/) from 2.3.4 to **2.3.5** on 2021-03-31
  - [hadolint](https://github.com/hadolint/hadolint) from 2.0.0 to **2.1.0** on 2021-04-02
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.0.5 to **6.1.0** on 2021-04-02

## [4.30.0] - 2021-03-14

- Fix #361 - Not respecting `*_DISABLE_ERRORS: false`
- New variable **FORMATTERS_DISABLE_ERRORS** to force all formatters to be blocking if errors are found
- Add *.svg in .jscpd (copy-paste detector) default ignore paths

- Linter versions upgrades
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.47.1 to **0.47.2** on 2021-03-13
  - [eslint](https://eslint.org) from 7.21.0 to **7.22.0** on 2021-03-13
  - [eslint-plugin-jsonc](https://ota-meshi.github.io/eslint-plugin-jsonc/) from 1.1.0 to **1.2.1** on 2021-03-14

## [4.29.0] - 2021-03-12

- Fix regex to list Salesforce errors
- Fix Updated Files Reporter when MegaLinter isn't running on GitHub Action
- Fix #359 - invalid literal with _DISABLE_ERRORS_IF_LESS_THAN

- Linter versions upgrades
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2021.01.20 to **2021.02.13** on 2021-03-01
  - [jscpd](https://github.com/kucherenko/jscpd/tree/master/packages/jscpd) from 3.3.24 to **3.3.25** on 2021-03-06
  - [hadolint](https://github.com/hadolint/hadolint) from 1.22.1 to **1.23.0** on 2021-03-06
  - [golangci-lint](https://golangci-lint.run/) from 1.37.1 to **1.38.0** on 2021-03-06
  - [markdownlint](https://github.com/DavidAnson/markdownlint) from 0.26.0 to **0.27.1** on 2021-03-06
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.0.0 to **6.0.2** on 2021-03-06
  - [sqlfluff](https://www.sqlfluff.com/) from 0.4.0 to **0.4.1** on 2021-03-06
  - [swiftlint](https://github.com/realm/SwiftLint) from 0.42.0 to **0.43.0** on 2021-03-06
  - [terrascan](https://www.accurics.com/products/terrascan/) from 1.3.3 to **1.4.0** on 2021-03-06
  - [stylelint](https://stylelint.io) from 13.11.0 to **13.12.0** on 2021-03-06
  - [tflint](https://github.com/terraform-linters/tflint) from 0.24.1 to **0.25.0** on 2021-03-06
  - [shfmt](https://github.com/mvdan/sh) from 3.2.2 to **3.2.4** on 2021-03-10
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.46.0 to **0.47.0** on 2021-03-10
  - [git_diff](https://git-scm.com) from 2.30.1 to **2.30.2** on 2021-03-10
  - [phpstan](https://phpstan.org/) from 0.12.80 to **0.12.81** on 2021-03-10
  - [protolint](https://github.com/yoheimuta/protolint) from 0.29.0 to **0.30.1** on 2021-03-10
  - [snakefmt](https://github.com/snakemake/snakefmt) from 0.3.1 to **0.4.0** on 2021-03-10
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.0.2 to **6.0.3** on 2021-03-10
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.47.0 to **0.47.1** on 2021-03-12
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.1.2 to **7.1.3** on 2021-03-12
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 6.0.3 to **6.0.5** on 2021-03-12
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.28.6 to **0.28.9** on 2021-03-12

## [4.28.0] - 2021-03-01

- Feature: **<LINTER_NAME>_DISABLE_ERRORS_IF_LESS_THAN** : set linter status to warning if maximum allowed errors isn't reached
- Add colors in logs

- Linter versions upgrades
  - [pylint](https://www.pylint.org) from 2.6.0 to **2.6.2** on 2021-02-16
  - [golangci-lint](https://golangci-lint.run/) from 1.36.0 to **1.37.0** on 2021-02-19
  - [phpstan](https://phpstan.org/) from 0.12.76 to **0.12.77** on 2021-02-19
  - [sfdx-scanner](https://forcedotcom.github.io/sfdx-scanner/) from 2.5.1 to **2.6.0** on 2021-02-19
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.28.2 to **0.28.6** on 2021-02-19
  - [terrascan](https://www.accurics.com/products/terrascan/) from 1.3.2 to **1.3.3** on 2021-02-19
  - [stylelint](https://stylelint.io) from 13.10.0 to **13.11.0** on 2021-02-21
  - [golangci-lint](https://golangci-lint.run/) from 1.37.0 to **1.37.1** on 2021-02-21
  - [phpstan](https://phpstan.org/) from 0.12.77 to **0.12.78** on 2021-02-21
  - [pylint](https://www.pylint.org) from 2.6.2 to **2.7.0** on 2021-02-22
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.45.0 to **0.46.0** on 2021-02-24
  - [pylint](https://www.pylint.org) from 2.7.0 to **2.7.1** on 2021-02-24
  - [eslint-plugin-jsonc](https://ota-meshi.github.io/eslint-plugin-jsonc/) from 0.9.0 to **1.0.0** on 2021-02-25
  - [phpstan](https://phpstan.org/) from 0.12.78 to **0.12.79** on 2021-02-25
  - [protolint](https://github.com/yoheimuta/protolint) from 0.28.2 to **0.29.0** on 2021-02-25
  - [jscpd](https://github.com/kucherenko/jscpd/tree/master/packages/jscpd) from 3.3.23 to **3.3.24** on 2021-02-28
  - [eslint](https://eslint.org) from 7.20.0 to **7.21.0** on 2021-02-28
  - [scalafix](https://scalacenter.github.io/scalafix/) from 0.9.25 to **0.9.26** on 2021-02-28
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 5.32.2 to **6.0.0** on 2021-02-28
  - [checkstyle](https://checkstyle.sourceforge.io) from 8.40 to **8.41** on 2021-03-01
  - [eslint-plugin-jsonc](https://ota-meshi.github.io/eslint-plugin-jsonc/) from 1.0.0 to **1.1.0** on 2021-03-01
  - [phpstan](https://phpstan.org/) from 0.12.79 to **0.12.80** on 2021-03-01
  - [pylint](https://www.pylint.org) from 2.7.1 to **2.7.2** on 2021-03-01
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2021.01.20 to **2021.02.13** on 2021-03-01

## [4.27.0] - 2021-02-16

- Linters
  - Format YAML with prettier

- Core
  - Lint docker image using [Dockle](https://github.com/goodwithtech/dockle)

- Fixes
  - Fix ansible-lint test cases for new version
  - Update --help expected return code for shfmt ash formatter and revive go linter
  - Add --write to update files fixed by eslint
  - Pimp MegaLinter sources by adding newLines when missing (manually and from build.py) + fix logger initialization error + call python3 by default ([PR329](https://github.com/megalinter/megalinter/pull/329) by [Tom Klingenberg](https://github.com/ktomk))
  - Increase max line length to 500 in yaml-lint default configuration

- Linter versions upgrades
  - [ansible-lint](https://ansible-lint.readthedocs.io/en/latest/) from 4.2.0 to **5.0.0** on 2021-02-09
  - [bash-exec](https://www.gnu.org/software/bash/) from 5.0.17 to **5.1.0** on 2021-02-09
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.44.6 to **0.44.7** on 2021-02-09
  - [hadolint](https://github.com/hadolint/hadolint) from 1.21.0 to **1.22.1** on 2021-02-09
  - [git_diff](https://git-scm.com) from 2.26.2 to **2.30.1** on 2021-02-09
  - [php](https://www.php.net) from 7.3.26 to **7.4.15** on 2021-02-09
  - [phpstan](https://phpstan.org/) from 0.12.71 to **0.12.74** on 2021-02-09
  - [protolint](https://github.com/yoheimuta/protolint) from 0.28.0 to **0.28.2** on 2021-02-09
  - [lintr](https://github.com/jimhester/lintr) from 2.0.1.9000 to **0.0.0** on 2021-02-09
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 5.32.0 to **5.32.1** on 2021-02-09
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.27.1 to **0.28.2** on 2021-02-09
  - [ansible-lint](https://ansible-lint.readthedocs.io/en/latest/) from 5.0.0 to **0.0.0** on 2021-02-09
  - [dotnet-format](https://github.com/dotnet/format) from 4.1.131201 to **5.0.211103** on 2021-02-12
  - [stylelint](https://stylelint.io) from 13.9.0 to **13.10.0** on 2021-02-12
  - [phpstan](https://phpstan.org/) from 0.12.74 to **0.12.75** on 2021-02-12
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.0.4 to **7.1.2** on 2021-02-12
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 5.32.1 to **5.32.2** on 2021-02-12
  - [coffeelint](http://www.coffeelint.org) from 4.1.2 to **4.1.3** on 2021-02-14
  - [eslint](https://eslint.org) from 7.19.0 to **7.20.0** on 2021-02-14
  - [phpstan](https://phpstan.org/) from 0.12.75 to **0.12.76** on 2021-02-14
  - [black](https://black.readthedocs.io/en/stable/) from 19.10 to **20.8** on 2021-02-15
  - [snakefmt](https://github.com/snakemake/snakefmt) from 0.2.6 to **0.3.0** on 2021-02-15
  - [sqlfluff](https://www.sqlfluff.com/) from 0.3.6 to **0.4.0** on 2021-02-15
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.44.7 to **0.45.0** on 2021-02-16
  - [snakefmt](https://github.com/snakemake/snakefmt) from 0.3.0 to **0.3.1** on 2021-02-16

## [4.26.2] - 2021-01-29

- Linter versions upgrades
  - [shfmt](https://github.com/mvdan/sh) from 3.2.1 to **3.2.2** on 2021-01-30
  - [yamllint](https://yamllint.readthedocs.io/) from 1.25.0 to **1.26.0** on 2021-01-30
  - [hadolint](https://github.com/hadolint/hadolint) from 1.20.0 to **1.21.0** on 2021-02-02
  - [checkstyle](https://checkstyle.sourceforge.io) from 8.39 to **8.40** on 2021-02-02
  - [eslint](https://eslint.org) from 7.18.0 to **7.19.0** on 2021-02-02
  - [phpstan](https://phpstan.org/) from 0.12.70 to **0.12.71** on 2021-02-02
  - [tflint](https://github.com/terraform-linters/tflint) from 0.23.1 to **0.24.1** on 2021-02-02
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.44.5 to **0.44.6** on 2021-02-03
  - [terrascan](https://www.accurics.com/products/terrascan/) from 1.3.1 to **1.3.2** on 2021-02-04

## [4.26.1] - 2021-01-29

- Fixes
  - Prevent `unexpected token` error using mega-linter-runner on old versions of node
  - [#293](https://github.com/megalinter/megalinter/issues/293) Fix CI for PR from forked repositories
  - [#295](https://github.com/megalinter/megalinter/issues/295) Fix crash when .cspell.json isn't parseable (wrong JSON format)
  - [#311](https://github.com/megalinter/megalinter/issues/295) Add java in salesforce flavor descriptor because it's used by Apex PMD

- Linter versions upgrades
  - [phpstan](https://phpstan.org/) from 0.12.68 to **0.12.69** on 2021-01-24
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.44.4 to **0.44.5** on 2021-01-25
  - [golangci-lint](https://golangci-lint.run/) from 1.35.2 to **1.36.0** on 2021-01-27
  - [protolint](https://github.com/yoheimuta/protolint) from 0.27.0 to **0.28.0** on 2021-01-27
  - [hadolint](https://github.com/hadolint/hadolint) from 1.19.0 to **1.20.0** on 2021-01-28
  - [phpstan](https://phpstan.org/) from 0.12.69 to **0.12.70** on 2021-01-28
  - [clj-kondo](https://github.com/borkdude/clj-kondo) from 2020.09.09 to **2021.01.20** on 2021-01-28

## [4.26.0] - 2021-01-24

- Core architecture
  - Manage remote `mega-linter.yml` configuration files
  - New property **EXTENDS**, allowing to inherit from remote `mega-linter.yml` configuration files
  - Add docker-in-docker management (reuse running docker instance)
  - Allow to skip auto apply fixes with commit or PR if latest commit text contains `skip fix`
  - Provide new issue link to create a new flavor to improve performances

- Linters
  - Add [revive](https://github.com/mgechev/revive) GO linter
  - Add [SwiftLint](https://github.com/realm/SwiftLint) for Swift language
  - New MegaLinter flavor **swift**
  - Get correct version for eslint-plugin-jsonc

- Linter versions upgrades
  - [snakefmt](https://github.com/snakemake/snakefmt) from 0.2.5 to **0.2.6** on 2021-01-22
  - [terrascan](https://www.accurics.com/products/terrascan/) from 1.3.0 to **1.3.1** on 2021-01-22
  - [eslint-plugin-jsonc](https://ota-meshi.github.io/eslint-plugin-jsonc/) from 6.14.10 to **0.9.0** on 2021-01-24

## [4.25.0] - 2021-01-22

- Linters
  - Add SQL linter [sqlfluff](https://github.com/sqlfluff/sqlfluff)

- Fixes
  - [#269](https://github.com/megalinter/megalinter/issues/269) eslint: .eslintrc.yml is considered as found whereas it's not located in workspace root

- Linter versions upgrades
  - [stylelint](https://stylelint.io) from 13.8.0 to **13.9.0** on 2021-01-19
  - [markdown-table-formatter](https://www.npmjs.com/package/markdown-table-formatter) from 1.0.1 to **1.0.4** on 2021-01-19
  - [terrascan](https://www.accurics.com/products/terrascan/) from 1.2.0 to **1.3.0** on 2021-01-19
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.44.3 to **0.44.4** on 2021-01-19
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.1.1 to **7.0.4** on 2021-01-19
  - [sfdx-scanner](https://forcedotcom.github.io/sfdx-scanner/) from 2.4.0 to **2.5.1** on 2021-01-21
  - [terragrunt](https://terragrunt.gruntwork.io) from 0.26.7 to **0.27.1** on 2021-01-22

## [4.24.1] - 2021-01-19

- mega-linter-runner --install
  - Create .jscpd.json file if copy-paste detection is activated
  - Display ending message

- Fixes
  - [#266](https://github.com/megalinter/megalinter/issues/266): shfmt error in python flavor, and reactivate BASH_SHFMT and DOCKERFILE_HADOLINT for own sources linting)

- Linter versions upgrades
  - [powershell](https://github.com/PowerShell/PSScriptAnalyzer) from 7.1.0 to **7.1.1** on 2021-01-15
  - [eslint](https://eslint.org) from 7.17.0 to **7.18.0** on 2021-01-16
  - [eslint-plugin-jsonc](https://ota-meshi.github.io/eslint-plugin-jsonc/) from 7.17.0 to **7.18.0** on 2021-01-16
  - [scalafix](https://scalacenter.github.io/scalafix/) from 0.9.24 to **0.9.25** on 2021-01-16
  - [snakemake](https://snakemake.readthedocs.io/en/stable/) from 5.31.1 to **5.32.0** on 2021-01-16
  - [protolint](https://github.com/yoheimuta/protolint) from 0.26.1 to **0.27.0** on 2021-01-18
  - [phpstan](https://phpstan.org/) from 0.12.67 to **0.12.68** on 2021-01-19

## [4.24.0] - 2021-01-14

- Linters
  - Add [markdown-table-formatter](https://github.com/nvuillam/markdown-table-formatter)
  - Fix python error when CSpell found no errors

- Linter versions upgrades
  - [v8r](https://github.com/chris48s/v8r) from 0.4.0 to **0.5.0** on 2021-01-14
  - [phpstan](https://phpstan.org/) from 0.12.66 to **0.12.67** on 2021-01-14
  - [psalm](https://psalm.dev) from 4.3.1 to **Psalm.4.x-dev@** on 2021-01-14

## [4.23.3] - 2021-01-14

- Fix `.cspell.json` file updater

- Linter versions upgrades
  - [v8r](https://github.com/chris48s/v8r) from 0.4.0 to **0.5.0** on 2021-01-14

## [4.23.2] - 2021-01-14

- mega-linter-runner --install:
  - Fix `.mega-linter.yml` DISABLE property when nothing in it
  - Add default `.cspell.json` if spelling mistakes detector is activated

## [4.23.1] - 2021-01-12

- Core
  - Refactor part of Linter & reporters to manage correctly logs when linter cli_lint_mode is `project` or `list_of_files`
    - Generate ConsoleLinter and Text reports based from Linter.files_lint_results instead of at each loop
    - When TAP Reporter active, switch linters with cli_lint_mode == "list_of_files" to "files"
    - Fix linter output when cli_lint_mode == "list_of_files"
  - Decrease number of Dockerfile steps

## [4.23.0] - 2021-01-12

- Core
  - If the linter is a formatter, errors aren't considered as blocking errors by default

- Linters
  - Add **prettier** to format Javascript and Typescript. **standard** remains default
  - Add **remark-lint** to check and fix Markdown files. **markdownlint** remains default

- Linter versions upgrades
  - [golangci-lint](https://golangci-lint.run/) from 1.35.1 to **1.35.2** on 2021-01-11
    - [golangci-lint](https://golangci-lint.run/) from 1.35.0 to **1.35.1** on 2021-01-11
    - [golangci-lint](https://golangci-lint.run/) from 1.34.1 to **1.35.0** on 2021-01-08
  - [cfn-lint](https://github.com/martysweet/cfn-lint) from 0.44.2 to **0.44.3** on 2021-01-09
  - [tflint](https://github.com/terraform-linters/tflint) from 0.23.0 to **0.23.1** on 2021-01-10
  - [dotenv-linter](https://dotenv-linter.github.io/) from 2.2.1 to **3.0.0** on 2021-01-11
    - Update MegaLinter to call dotenv-linter v3 with `fix` and not `--fix` anymore
  - [phpstan](https://phpstan.org/) from 0.12.65 to **0.12.66** on 2021-01-11

## [4.22.1] - 2021-01-07

- Core
  - Improve `warning` status in logs
  - Remove timestamp at each log line

- Enhance integration with GitLab CI
  - Update configuration generator
  - Update core to clean logs when in GitLab CI context

## [4.22.0] - 2021-01-06

- Core
  - Allow user to configure custom scripts in `.mega-linter.yml` to run before and after linting, with variables `PRE_RUN` and `POST_RUN`
  - Fix wrong linter status bug
  - Enhance configuration variables performances
  - Rename XXX_FILE_NAME into XXX_CONFIG_FILE

- Linters
  - Add JSONC (json with comments) linting with eslint-plugin-jsonc

## [4.21.0] - 2021-01-03

- Linters
  - Add misspell spell checker
  - Allow to define cli_lint_errors_regex in descriptors to extract number of errors from linter output stdout
  - Call linters CLIs with list of files instead of once by file, to improve performances
    - eslint
    - markdownlint
    - pylint
    - flake8
    - isort

- Core
  - Implement architecture for MegaLinter plugins
  - Count number of errors in linter logs with regexes (`cli_lint_errors_count` and `cli_lint_errors_regex` in descriptor files)
  - Cleanup unused legacy from Super-Linter

- Reports
  - Better icons for Console, GitHub Comment and Text reporters: ✅ ❌

- Documentation
  - Add Install button for VSCode IDE extensions when available
  - Add Install button for JetBrains IDEs extensions when available
  - Add a new page **All linters** listing all linters and references to MegaLinter in their documentation
  - Add json-schema documentation generation and references

- CI
  - Use `quick build` and `TEST_KEYWORDS` in commit messages, to improve contributor experience

- Fixes
  - Upgrade .tflint default config to work with new tflint version

## [4.20.0] - 2020-12-28

- Flavors
  - Add **ci_light** flavor for only CI config files (Dockerfile,Jenkinsfile,JSON,YAML,XML)
  - Add **salesforce** flavor for Salesforce projects (DX or Metadata)
  - If all required linters aren't in the current flavor, just skip them with a warning message

- Core
  - Add Json Schema for descriptors (allows validation and auto-completion from IDEs)
  - Add Json Schema for .mega-linter.yml configuration files

## [4.19.0] - 2020-12-27

- Installation
  - Add a yeoman generator in mega-linter-runner to initialize configuration in a repository: `npx mega-linter-runner --install`

- Linters
  - New linter v8r to validate json and yaml files with schemastore.org

## [4.18.0] - 2020-12-23

- Core
  - Don't suggest flavors when MegaLinter validates only the diff files (`VALIDATE_ALL_CODE_BASE: false`)
  - Fix ConsoleReporter active linters table content
  - Check if linter is able to fix before flagging it as a fixing linter during runtime

- Flavors
  - New flavor: **documentation**

- Reporters
  - Support GitHub Enterprise for GitHub Comment Reporter
  - Support GitHub Enterprise for GitHub Status Reporter

- Doc
  - Add docker pulls badge in flavors documentation
  - Generate list of references to MegaLinter

## [4.17.0] - 2020-12-18

- Core
  - Allow to use remote linters configuration files with LINTER_RULES_PATH
  - Add `.jekyll-cache` in the list of ignored folders by default
  - Arrange display of Flavor suggestions (text and order) in reporter logs
- Build
  - Dynamically generate (build.py) the list of flavors in github actions workflows
- Doc
  - Reorganize online documentation menus
- Linters
  - Add new linter git_diff to check for git conflicts markers
  - Fix rakudo installation
  - Fix phpstan installation

## [4.16.0] - 2020-12-14

- Flavored MegaLinters
  - Generate lightweight docker images to improve MegaLinter performances on some language based projects
  - During MegaLinter run, suggest user to use a flavor and write it in reporters
  - Update descriptor YML files to define flavours
  - Update build.py to create one Dockerfile by MegaLinter flavour & flavors documentation
  - New GHA workflows to build all flavoured MegaLinters when pushing in master

- Fixes
  - Output reporter problems as warnings
  - Don't make MegaLinter fail in case GitHubStatusReporter fails

- Doc
  - Rename "index" pages into more meaningful labels

## [4.15.0] - 2020-12-13

- Add Vue.js linting (eslint-plugin-vue added in dependencies)

- Configuration parameters changes:
  - Change config setting logic: `EXCLUDED_DIRECTORIES` is now replacing original directory list instead of extending it
  - Add config setting: `ADDITIONAL_EXCLUDED_DIRECTORIES` extends `EXCLUDED_DIRECTORIES` directory list
  - Add config setting: `&lt;LINTER_KEY&gt;_FILE_EXTENSIONS` to override corresponding value from linter descriptor file
  - Add config setting: `&lt;LINTER_KEY&gt;_FILE_NAMES_REGEX` to override corresponding value from linter descriptor file

- Descriptor yaml schema changes:
  - Rename `files_names_not_ends_with` to `file_names_not_ends_with`
  - Rename `files_names` to `files_names_regex` and change behavior to expect regular expressions in the list.
    they're applied using full match (the whole text should match the regular expression)

- Fix error message from Email Reporter when SMTP password isn't set
- Fix automerge action yml (skip if secrets.PAT isn't set)
- Improve caching of compiled regular expressions
- Override mkdocs theme to make analytics work

- CI
  - Auto update linters and documentation: Create update PR only if linter versions has been updated
  - Build and deploy docker images only when it's relevant (not in case of just documentation update for example)

## [4.14.2] - 2020-12-07

- Quick fix Github Comment Reporter
- Reorder linters for reports

## [4.14.1] - 2020-12-07

- Fixes
  - Fix python error when File.io doesn't respond, + harmonize reporter logs

## [4.14.0] - 2020-12-07

- Linters
  - Add Salesforce linter: sfdx-scanner

- Core architecture
  - Allow to call extra commands to build help content

## [4.13.0] - 2020-12-05

- Major updates in online documentation generation
  - Reorganize TOC
  - Generate individual pages from README sections and update their internal links targets
  - Open external links in a new browser tab

- New configuration parameters
  - Allow disabling printing alpaca image to console using PRINT_ALPACA config parameter
  - Support list of additional excluded directory basenames via EXCLUDED_DIRECTORIES configuration parameter

- New reporters:
  - Email reporter, to send mega-linter reports by mail if smtp server is configured
  - File.io reporter, to access reports with a file.io hyperlink

- Fixes
  - Fix markdown comments generator when build on Windows
  - Fix terrascan unit test case
  - Run some actions/steps only when PR is from same repository
  - Add comments in markdown generated by build.py
  - Fix boolean variables not taken in account in .mega-linter.yml config file

- Performance
  - Change way to install linters in Dockerfile (replace FROM … COPY) by package or sh installation, to reduce the docker build steps from 93 to 87
    - shellcheck
    - editorconfig-checker
    - dotenv-linter
    - golangci-lint
    - kubeval

## [4.12.0] - 2020-11-29

- Performances
  - Update default workflow to get ride of has_updates action (replace by output `has_updated_files` from mega-linter github action)
  - Avoid duplicate runs in mega-linter.yml template and internal workflows, using [skip-duplicate-actions](https://github.com/fkirc/skip-duplicate-actions)
  - Give a proper name to each internal workflow
  - Fix issue about mkdirs failing

## [4.11.0] - 2020-11-29

- Manage parallel processing of linters to improve performances

## [4.10.1] - 2020-11-28

- Fallback to default behaviours instead of crashes when git not available

- mega-linter-runner
  - Allow to send env parameters to mega-linter-runner cli
  - Add examples in documentation
  - Publish mega-linter-runner beta version when pushing in master branch

## [4.10.0] - 2020-11-23

- Add link to linters rules index in documentation
- Remove ANSI color codes from log files
- Add performances by linter in console log
- New option **SHOW_ELAPSED_TIME** , allowing the number of seconds elapsed by linter in reports

- NPM package **MegaLinter runner**
  - runs MegaLinter locally, using .mega-linter.yml configuration (requires docker installed on your computer)
  - test cases added in CI

## [4.9.0] - 2020-11-23

- Core
  - Allow configuration to be defined in a `.mega-linter.yml` file

- Linters
  - Add Gherkin (Cucumber language) & gherkin-lint
  - Add RST linter : [rst-lint](https://github.com/twolfson/restructuredtext-lint)
  - Add RST linter : [rstcheck](https://github.com/myint/rstcheck)
  - Add RST formatter : [rstfmt](https://github.com/dzhu/rstfmt)
  - Activate formatting for BASH_SHFMT
  - Activate formatting for SNAKEMAKE_SNAKEFMT
  - JsCpd: remove copy-paste HTML folder when no abuse copy-paste has been found

- Logs
  - Store log files as artifacts during test cases
  - Add examples of success and failed linter logs in documentation
  - Remove `/tmp/lint` and `/github/workspace` from log files

- Documentation
  - Add list of supported IDE in each linter documentation
  - Generate GitHub card on linter doc when available
  - Store link preview info during build

## [4.8.0] - 2020-11-17

- New reporter: [Updated sources](https://megalinter.github.io/reporters/UpdatedSourcesReporter/)

## [4.7.1] - 2020-11-16

- Activate auto-fix for Groovy

## [4.7.0] - 2020-11-16

- Update markdown-link-check default config
- Add tip in documentation about .cspell.json generated by MegaLinter
- Remove /tmp/lint from logs
- Improve summary table for linters in project mode (all project linted in one call, not one file by one file)
- Add Reporters in documentation, with screenshots
- New MegaLinter variables to activate/deactivate/configure reporters

## [4.6.0] - 2020-11-13

- Automatic build of documentation with mkdocs-material
- Automatic deployment to [https://megalinter.github.io/](https://megalinter.github.io/)
- Add [markdown-link-check](https://github.com/tcort/markdown-link-check)

## [4.5.0] - 2020-11-11

- Add Visual Basic .NET language & dotnet-format
- Refactor removal of arguments for formatters (from custom class to Linter generic class)
- Perl: lint files with no extension containing Perl shebang
- Add automerge for PR issues from linter versions updates
- Fix ignored root files issue

## [4.4.0] - 2020-11-05

- Add Python [iSort](https://pycqa.github.io/isort/)
- Quick fix "PR Comment" reporter (orange light emoji)
- Refresh fork

## [4.3.2] - 2020-11-04

- Add spell checker **cspell**
- Add Github Action Workflow to automatically:
  - update linters dependencies
  - rebuild MegaLinter documentation
  - create a PR with updates

- Apply fixes performed by linters:
  - User configuration (APPLY_FIXES vars)
  - Descriptors configuration: cli_lint_fix_arg_name set on linter in YML when it can format and/or auto-fix issues
  - Provide fixed files info in reports
  - Test cases for all fixable file types: sample_project_fixes
  - Generate README linters table with column "Fix"
  - Provide fix capability in linters docs
  - Update Workflows YMLs to create PR or commit to apply fixes

- Core Archi:
  - All linters now have a name different than descriptor_id
  - replace calls from os.path.exists to os.path.isfile and os.path.isdir

- Other:
  - fix Phive install
  - Upgrade linter versions & help

## [4.0.0] - 2020-10-01

- Initial version
