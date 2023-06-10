## —— Megalinter —————————————————————————————————————————————————————————————————————————————————————
.PHONY: megalinter-test
megalinter-test: ## Run script build.sh
	source .venv/bin/activate
	bash build.sh