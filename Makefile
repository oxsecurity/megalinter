.PHONY: all SHELL

python_launcher := python$(shell cat .config/python_version.config | cut -d '=' -f 2)

-include $(addsuffix /*.mak, $(shell find .config/make -type d))

## —— Tests ———————————————————————————————————————————————————————————————————————
.PHONY: tests
tests: ## Tests all
	$(MAKE) gitpod-tests

.PHONY: tests-fast
tests-fast: ## Tests quickly for TDD mode

## —— Virtualenv ————————————————————————————————————————————————————————————————————————————————
.PHONY: bootstrap
bootstrap: ## Bootstrap environment
	$(MAKE) python-bootstrap

.PHONY: bootstrap-dev
bootstrap-dev: ## Bootstrap environment for development
	$(MAKE) bootstrap
	$(MAKE) python-bootstrap-dev

.PHONY: reinitialization
reinitialization: ## Return to an initial state of Bootstrap
	$(MAKE) clean
	$(MAKE) bootstrap

.PHONY: reinitialization-dev
reinitialization-dev: ## Return to an initial state of Bootstrap for development
	$(MAKE) reinitialization
	$(MAKE) bootstrap-dev

.PHONY: clean
clean: ## Cleaning environment
	$(MAKE) python-venv-purge