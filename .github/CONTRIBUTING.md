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
python3 -m venv venv
. venv/bin/activate
echo "venv/" >> .git/info/exclude
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
- Update [CHANGELOG.md](https://github.com/megalinter/megalinter/blob/main/CHANGELOG.md) to briefly describe your changes

Draft pull requests are also welcome to get feedback early on, or if there is something blocking you.

- Create a branch with a name that identifies the user and nature of the changes (similar to `user/branch-purpose`)
- Open a pull request

### Add a new linter

Each linter must:

- Be defined in a descriptor file. Few properties are required ([see json schema documentation](https://megalinter.github.io/json-schemas/descriptor.html)), but please think to input doc URLs and `ide` section for documentation
- Have two test files in `.automation/test`: one for success and one for failure

Then run `bash build.py` and it will generate all the rest !

- Documentation (markdown)
- Dockerfile (main and flavors)
- Test classes
- Configuration JSON schema
- Online documentation menus

![Screenshot](https://github.com/megalinter/megalinter/blob/main/docs/assets/images/ContributingAddLinter_1.jpg?raw=true>)


### CI/CT/CD

The **Mega-Linter** has _CI/CT/CD_ configured utilizing **GitHub** Actions.

- When a branch is created and code is pushed, a **GitHub** Action is triggered for building the new **Docker** container with the new codebase
  - To test your updates during your development, you may have to create a draft Pull Request to trigger CI on the main repo
  - During development, if all you updated is python code, you can write `quick build` in the commit message body to benefit from a quicker build (about 15 minutes): only python files are copied over megalinter/megalinter:test-YOURUSERNAME-YOURBRANCH or megalinter/megalinter:latest if a previous full run has not been performed yet
  - You can [filter the performed tests](https://docs.pytest.org/en/stable/usage.html#specifying-tests-selecting-tests) by writing `TEST_KEYWORDS=my keywords` in the commit message body. Example: `TEST_KEYWORDS=kubernetes_kubeval_test`
  - The last commit before the validation of a Pull Request must be a full build with all tests (about 45 minutes)
- The **Docker** container is then ran against the _test cases_ to validate all code sanity
  - `.automation/test` contains all test cases for each language that should be validated
- These **GitHub** Actions utilize the Checks API and Protected Branches to help follow the SDLC
- When the Pull Request is merged to main, the **Mega-Linter** **Docker** container is then updated and deployed with the new codebase
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

[pulls]: https://github.com/megalinter/megalinter/pulls
[pr]: https://github.com/megalinter/megalinter/compare
[fork]: https://github.com/megalinter/megalinter/fork
