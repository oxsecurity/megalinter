## —— Gitpod —————————————————————————————————————————————————————————————————————————————————————
.PHONY: gitpod-build
gitpod-build: ## Run docker build image in local
	docker build --tag postgresql_cluster:local --file .config/gitpod/Dockerfile .

.PHONY: gitpod-lint
gitpod-lint: ## Run hadolint command to lint Dokerfile
	docker run --rm -i hadolint/hadolint < .config/gitpod/Dockerfile

.PHONY: gitpod-tests
gitpod-tests: ## Run tests for gitpod
	$(MAKE) gitpod-build
	$(MAKE) gitpod-lint
