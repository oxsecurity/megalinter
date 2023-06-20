.PHONY: all test SHELL

python_launcher := python$(shell cut -d '.' -f 1,2 .python-version)

-include $(addsuffix /*.mak, $(shell find .config/make -type d))

## —— Tests ———————————————————————————————————————————————————————————————————————
.PHONY: tests
tests: ## Tests all
	$(MAKE) gitpod-tests
	$(MAKE) megalinter-tests

.PHONY: tests-fast
tests-fast: ## Tests quickly for TDD mode
	$(MAKE) megalinter-tests

## —— Virtualenv ————————————————————————————————————————————————————————————————————————————————
.PHONY: bootstrap
bootstrap: ## Bootstrap environment for development
	$(MAKE) python-bootstrap
	$(MAKE) python-bootstrap-dev
	$(MAKE) nodejs-bootstrap

.PHONY: reinitialization
reinitialization: ## Return to an initial state of Bootstrap
	$(MAKE) clean
	$(MAKE) bootstrap

.PHONY: clean
clean: ## Cleaning environment
	$(MAKE) python-venv-purge
	$(MAKE) nodejs-clean
	$(MAKE) megalinter-clean
