# Contributing

:wave: Hi there!
We're thrilled that you'd like to contribute to this project. Your help is essential for keeping it great.

## How to Contribute

### 1. Create an issue

Report problems or suggest improvements by [creating an issue](https://github.com/oxsecurity/megalinter/issues).

### 2. Fork the project

[Fork the repository](https://github.com/oxsecurity/megalinter) to your GitHub account.

### 3. Make changes

Clone your fork locally and make the necessary changes:

```bash
git clone git@github.com:YOURNAMESPACE/megalinter.git
```

### 4. Test your changes

#### 4.1 Gitpod

Use Gitpod for a cloud-based development environment:

1. Sign up for Gitpod: <https://gitpod.io>
2. Fork the `megalinter` repository
3. Open your fork in Gitpod: `https://gitpod.io/#https://github.com/username/megalinter`
4. Create a new branch: `git checkout -b my-feature-branch`
5. Make your changes and commit: `git add .` and `git commit -m "chore: description of changes"`
6. Test all : `make tests` or `make tests-fast` for TDD mode
7. Test with megalinter: `make megalinter-tests`
8. Push your changes: `git push origin my-feature-branch`
9. Create a pull request on GitHub
10. Wait for a review

Keep your Gitpod workspace synced with the main repository.

#### 4.2 Desktop

Install [make](https://www.gnu.org/software/make/), [Python3.11](https://www.python.org/), [venv](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/), [docker](https://docs.docker.com/engine/install/ubuntu/) and [nodejs](https://github.com/nodesource/distributions/tree/master).

Run `make` for Makefile help. Initialize virtualenv and install dependencies with `make reinitialization` or `make bootstrap`. Test your changes with `make tests` or `make tests-fast`.

You can lint with `make megalinter` (Incoming)

### 5. Submit a pull request

[Create a pull request](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request-from-a-fork) and [refer to the issue number](https://help.github.com/en/github/writing-on-github/autolinked-references-and-urls) using #123, where 123 is the issue number.

### 6. Wait

Your pull request will be reviewed, and you'll receive feedback. Thanks for contributing!

Consider sponsoring the maintainer via [GitHub](https://github.com/sponsors/nvuillam).

### With write access

1. Clone the repository (only if you have write access)
2. Create a new branch: `git checkout -b my-branch-name`
3. Make your change
4. Update **CHANGELOG.md** (the root one, not the one in /docs)
5. Run `bash build.sh` to regenerate dockerfile from updated sources (run `bash build.sh --doc` if you want to also regenerate documentation)
6. Push and [submit a pull request][pr]
7. Pat yourself on the back and wait for your pull request to be reviewed and merged.

Maintainers with write access can also comment on pull requests with a command to run the build script on the PR, for example:
```text
/build
```

Available commands can be listed with the help command by posting the following comment:
```text
/help
```
Which returns:
> Command | Description
> --- | ---
> /build | Updates the Dockerfile, documentation, and other files from the yml descriptors
> /build [ref=…]| Same as /build, but executes workflow in any branch using the ref named argument. The reference can be a branch, tag, or a commit SHA. This can be useful to test workflows in PR branches before merging.
> /help | Returns this help message

### Without write access

1. [Fork][fork] and clone the repository
2. Create a new branch: `git checkout -b my-branch-name`
3. Make your change
4. Update **CHANGELOG.md** (the root one, not the one in /docs)
5. Run `bash build.sh` to regenerate dockerfile from updated sources (run `bash build.sh --doc` if you want to also regenerate documentation)
6. Push to your fork and [submit a pull request][pr]
7. Pat your self on the back and wait for your pull request to be reviewed and merged.

Here are a few things you can do that will increase the likelihood of your pull request being accepted:

- Keep your change as focused as possible. If there are multiple changes you would like to make that aren't dependent upon each other, consider submitting them as separate pull requests.
- Write [good commit messages](http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html).
- Update [CHANGELOG.md](https://github.com/oxsecurity/megalinter/blob/main/CHANGELOG.md) to briefly describe your changes

Draft pull requests are also welcome to get feedback early on, or if there is something blocking you.

- Create a branch with a name that identifies the user and nature of the changes (similar to `user/branch-purpose`)
- Open a pull request

### Update Dockerfile base image

1. `/Dockerfile` file has to be updated
2. Run `bash build.sh`, and it will automatically propagate to all the other Dockerfiles

### Improve documentation

Apart from the descriptors, it will usually involve modifying files such as [.automation/build.py](https://github.com/oxsecurity/megalinter/blob/main/.automation/build.py)

In order to be able to run locally a server that serves all the documentation and make the testing as real as possible you should setup a virtual environment.

Commands to execute (only one time):

```bash
mkdir venv
python -m venv venv/
source venv/bin/activate
pip install --upgrade -r .config/python/dev/requirements.txt
```

Commands to run every time you want to enter the environment and run the server:

```bash
source venv/bin/activate
mkdocs serve
```

By default it listens on `http://127.0.0.1:8000/`.

Every time a change is made to a `.md` file it will automatically update if the server is up.

Once you think everything is correct run `bash build.sh --doc` and it will generate all the rest!

### Add a new linter

Each linter must:

- Be defined in a descriptor file. Few properties are required ([see json schema documentation](https://megalinter.io/json-schemas/descriptor.html)), but please think to input doc URLs and `ide` section for documentation
- Have two test files in `.automation/test`: one for success and one for failure

Then run `bash build.sh` and it will generate all the rest!

- Documentation (markdown)
- Dockerfile (main and flavors)
- Test classes
- Configuration JSON schema
- Online documentation menus

![Screenshot](https://github.com/oxsecurity/megalinter/blob/main/docs/assets/images/ContributingAddLinter_1.jpg?raw=true>)

### Execute the tests locally (Visual Studio Code)

1. Install [Test Explorer UI](https://marketplace.visualstudio.com/items?itemName=hbenl.vscode-test-explorer) extension
2. Install [Python Test Explorer for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=LittleFoxTeam.vscode-python-test-adapter) extension
3. Execute or debug tests via the side menu

### Execute linter tests inside the container

If you are creating a linter or making changes to a linter, you may want to run the tests to check that none of them fail.

When running them, you may encounter several problems:

* it's not installed on the machine locally and you don't want to install it.
* The OS doesn't allow the installation of the linter because it's not cross-platform.
* The behavior between running it on the local machine (host) and the container is different.

For those cases, it's important to have the possibility to run the tests inside the container. To do so:

1. Run `bash build.sh` to update the Dockerfile files of each linter.
2. Execute the following commands in a ***.sh** script. Example:

```bash
docker buildx build -f linters/spell_misspell/Dockerfile . --tag spell_misspell
TEST_KEYWORDS_TO_USE="spell_misspell"
docker run -e TEST_CASE_RUN=true -e OUTPUT_DETAIL=detailed -e TEST_KEYWORDS="${TEST_KEYWORDS_TO_USE}" -e MEGALINTER_VOLUME_ROOT="." -v "/var/run/docker.sock:/var/run/docker.sock:rw" -v $(pwd):/tmp/lint spell_misspell
```

In the above example, it builds the **misspell** linter image and then runs its tests. To do the same for another linter you would have to:

1. Change the path to the Dockerfile to the appropriate Dockerfile
2. Change the **tag** in the 2 places (docker buildx build and docker run)
3. Change the value of **TEST_KEYWORDS_TO_USE** which is the one that's responsible for finding the tests of the particular linter

### CI/CT/CD

The **MegaLinter** has _CI/CT/CD_ configured utilizing **GitHub** Actions.

- When a branch is created and code is pushed, a **GitHub** Action is triggered for building the new **Docker** container with the new codebase
  - To test your updates during your development, you may have to create a draft Pull Request to trigger CI on the main repo
  - During development, if all you updated is python code, you can write `quick build` in the commit message body to benefit from a quicker build (about 15 minutes): only python files are copied over oxsecurity/megalinter:test-YOURUSERNAME-YOURBRANCH or oxsecurity/megalinter:latest if a previous full run has not been performed yet
  - You can [filter the performed tests](https://docs.pytest.org/en/stable/usage.html#specifying-tests-selecting-tests) by writing `TEST_KEYWORDS=my keywords` in the commit message body. Example: `TEST_KEYWORDS=kubernetes_kubeval_test`
  - The last commit before the validation of a Pull Request must be a full build with all tests (about 45 minutes)
- The **Docker** container is then ran against the _test cases_ to validate all code sanity
  - `.automation/test` contains all test cases for each language that should be validated
- These **GitHub** Actions utilize the Checks API and Protected Branches to help follow the SDLC
- When the Pull Request is merged to main, the **MegaLinter** **Docker** container is then updated and deployed with the new codebase
  - **Note:** The branch's **Docker** container is also removed from **DockerHub** to cleanup after itself

## Releasing

If you are the current maintainer of this action:

1. If a major version number change: Update `README.md` and the wiki to reflect new version number in the example workflow file sections
2. Draft [Releases](https://help.github.com/en/github/administering-a-repository/managing-releases-in-a-repository) are created automatically. They just need to be checked over for accuracy before making it official.
3. Ensure you check the box for [publishing to the marketplace](https://help.github.com/en/actions/creating-actions/publishing-actions-in-github-marketplace#publishing-an-action)
4. A GitHub Action will Publish the Docker image to GitHub Package Registry once a Release is created
5. A GitHub Action will Publish the Docker image to Docker Hub once a Release is created
6. Look for approval from [CODEOWNERS](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/about-code-owners)

## Resources

- [How to Contribute to Open Source](https://opensource.guide/how-to-contribute/)
- [Using Pull Requests](https://help.github.com/articles/about-pull-requests/)
- [GitHub Help](https://help.github.com)

[pr]: https://github.com/oxsecurity/megalinter/compare
[fork]: https://github.com/oxsecurity/megalinter/fork
