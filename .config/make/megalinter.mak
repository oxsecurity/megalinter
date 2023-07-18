## —— Megalinter —————————————————————————————————————————————————————————————————————————————————————
.PHONY: megalinter-build
megalinter-build: ## Run script build.sh
	source .venv/bin/activate
	bash build.sh

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
