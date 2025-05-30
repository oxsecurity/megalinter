## —— Megalinter —————————————————————————————————————————————————————————————————————————————————————
.PHONY: megalinter-build
megalinter-build: ## Run script build.sh
	@if [ -f .venv/bin/activate ]; then \
		. .venv/bin/activate; \
	elif [ -f .venv/Scripts/activate ]; then \
		. .venv/Scripts/activate; \
	else \
		echo "No venv activation script found! Try command 'make bootstrap'" >&2; \
		exit 1; \
	fi; \
	bash build.sh

.PHONY: megalinter-build
megalinter-build-with-doc: ## Run script build.sh and generate documentation
	@if [ -f .venv/bin/activate ]; then \
		. .venv/bin/activate; \
	elif [ -f .venv/Scripts/activate ]; then \
		. .venv/Scripts/activate; \
	else \
		echo "No venv activation script found! Try command 'make bootstrap'" >&2; \
		exit 1; \
	fi; \
	bash build.sh --doc

.PHONY: megalinter-run
megalinter-run: ## Run megalinter locally
	npx mega-linter-runner --flavor python --release beta

.PHONY: megalinter-tests
megalinter-tests: ## Run all megalinter tests
	$(MAKE) megalinter-run
	$(MAKE) megalinter-build

.PHONY: megalinter-clean
megalinter-clean: ## Clean megalinter locally
	sudo rm -rf megalinter-reports
	sudo rm -rf site
	sudo rm -f *megalinter_file_names_cspell.txt

.PHONY: megalinter-release
megalinter-release: ## Generate a release commit and tag. make megalinter-release RELEASE_VERSION=v1.2.3
	@if [ -f .venv/bin/activate ]; then \
		. .venv/bin/activate; \
	elif [ -f .venv/Scripts/activate ]; then \
		. .venv/Scripts/activate; \
	else \
		echo "No venv activation script found! Try command 'make bootstrap'" >&2; \
		exit 1; \
	fi; \
	if [ -z "$(RELEASE_VERSION)" ]; then \
		echo "Please set RELEASE_VERSION variable to the desired version number" >&2; \
		exit 1; \
	fi; \
	if ! echo "$(RELEASE_VERSION)" | grep -Eq '^v[0-9]+\.[0-9]+\.[0-9]+$$'; then \
		echo "RELEASE_VERSION must follow the format vX.X.X (e.g., v1.2.3)" >&2; \
		exit 1; \
	fi; \
	bash build.sh --doc --version $(RELEASE_VERSION)
	bash build.sh --release $(RELEASE_VERSION)
