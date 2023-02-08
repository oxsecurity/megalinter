# Contributing

:wave: Hi there!
We're thrilled that you'd like to contribute to this project. Your help is essential for keeping it great.

## Submitting a pull request

[Pull Requests][pulls] are used for adding new playbooks, roles, and documents to the repository, or editing the existing ones.

### Pre-requisites

- You need [**Python 3**](https://www.python.org/downloads/) (version 3.7 minimum) and [**Node.js** (14+)](https://nodejs.org/en/download/) to be installed on your computer.
  - If you have issues running Python on Windows, you can uninstall it then reinstall it using [this video tutorial](https://www.youtube.com/watch?v=uDbDIhR76H4), then copy python.exe and name it python3.exe

- Run the following commands at the root of the repository to install required dev dependencies
```shell
python3 -m venv .venv
. .venv/bin/activate
echo ".venv/" >> .git/info/exclude
python3 -m pip install -U pip
python3 -m pip install -r requirements.dev.txt
```

_If it does not work, just run the following script_

```shell
pip install -r requirements.dev.txt
pip install mkdocs-material
npm install markdown-table-formatter -g
```

Second level dev dependencies are installed by running `./build.sh` which is also a test if the installation worked

```shell
./build.sh
2021-03-30 19:40:03,790 [INFO] Validating ansible.megalinter-descriptor.yml
2021-03-30 19:40:03,879 [INFO] Validating arm.megalinter-descriptor.yml
...
Formatting markdown tables...
Need to install the following packages:
  markdown-table-formatter
Ok to proceed? (y)
...
INFO    -  Documentation built in 9.76 seconds
(done.)
```

_(if you have a permission denied issue on Windows, please check [this solution](https://stackoverflow.com/a/57168165/7113625))_

### With write access

1. Clone the repository (only if you have write access)
2. Create a new branch: `git checkout -b my-branch-name`
3. Make your change
4. Update **CHANGELOG.md** (the root one, not the one in /docs)
5. Run `bash build.sh` to regenerate dockerfile from updated sources (run `bash build.sh --doc` if you want to also regenerate documentation)
6. Push and [submit a pull request][pr]
7. Pat yourself on the back and wait for your pull request to be reviewed and merged.

### Without write access

1. [Fork][fork] and clone the repository
2. Create a new branch: `git checkout -b my-branch-name`
3. Make your change
4. Update **CHANGELOG.md** (the root one, not the one in /docs)
5. Run `bash build.sh` to regenerate dockerfile from updated sources (run `bash build.sh --doc` if you want to also regenerate documentation)
6. Push to your fork and [submit a pull request][pr]
7. Pat your self on the back and wait for your pull request to be reviewed and merged.

Here are a few things you can do that will increase the likelihood of your pull request being accepted:

- Keep your change as focused as possible. If there are multiple changes you would like to make that are not dependent upon each other, consider submitting them as separate pull requests.
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

In order to be able to run locally a server that serves all the documentation and make the testing as real as possible you will have to run at least 2 commands.

Command to execute (only one time):

```bash
pip install --upgrade "markdown==3.3.7" mike mkdocs-material mdx_truly_sane_lists jsonschema json-schema-for-humans giturlparse webpreview github-dependents-info
```

Command to run every time you want to bring up the server:

```bash
mkdocs serve
```

By default it listens on `http://127.0.0.1:8000/`.

Every time a change is made to a `.md` file it will automatically update if the server is up.

Once you think everything is correct run `bash build.sh --doc` and it will generate all the rest!

### Add a new linter

Each linter must:

- Be defined in a descriptor file. Few properties are required ([see json schema documentation](https://megalinter.github.io/json-schemas/descriptor.html)), but please think to input doc URLs and `ide` section for documentation
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
* It is not installed on the machine locally and you do not want to install it.
* The OS does not allow the installation of the linter because it is not cross-platform.
* The behavior between running it on the local machine (host) and the container is different.

For those cases, it is important to have the possibility to run the tests inside the container. To do so:
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
3. Change the value of **TEST_KEYWORDS_TO_USE** which is the one that is responsible for finding the tests of the particular linter

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

[pulls]: https://github.com/oxsecurity/megalinter/pulls
[pr]: https://github.com/oxsecurity/megalinter/compare
[fork]: https://github.com/oxsecurity/megalinter/fork
