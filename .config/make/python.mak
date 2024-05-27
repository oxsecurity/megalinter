# Python default launcher
python_launcher ?= python3.11
python_requirements_file ?= .config/python/dev/requirements.txt
python_requirements_dev_file ?= .config/python/dev/requirements.txt

## —— Python —————————————————————————————————————————————————————————————————————————————————————
.PHONY: python-bootstrap
python-bootstrap: ## Bootstrap python
	$(MAKE) python-venv-init
	$(MAKE) python-venv-upgrade
	$(MAKE) python-venv-requirements

.PHONY: python-bootstrap-dev
python-bootstrap-dev: ## Bootstrap python for dev env
	$(MAKE) python-venv-requirements-dev
	$(MAKE) python-venv-linters-install

# ===============================================================================================
# .venv
# ===============================================================================================
.PHONY: python-venv-init
python-venv-init: ## Create venv ".venv/" if not exist
	if [ ! -d .venv ] ; then \
		if ! command -v -- "uv" > /dev/null 2>&1; then \
			echo "In python-venv-init, using uv"; \
			uv venv; \
		else \
			echo "In python-venv-init, using pip"; \
			$(python_launcher) -m venv .venv; \
		fi \
	fi
# $(python_launcher) -m venv .venv

.PHONY: python-venv-upgrade
python-venv-upgrade: ## Upgrade venv with pip, setuptools and wheel
	source .venv/bin/activate
	if ! command -v -- "uv" > /dev/null 2>&1; then \
		echo "In python-venv-upgrade, using uv"; \
		uv pip install setuptools wheel; \
	else \
		echo "In python-venv-upgrade, using pip"; \
		pip install --upgrade pip setuptools wheel; \
	fi
# uv pip install --upgrade pip setuptools wheel
# pip install --upgrade pip setuptools wheel

.PHONY: python-venv-requirements
python-venv-requirements: ## Install or upgrade from $(python_requirements_file)
	source .venv/bin/activate
	if ! command -v -- "uv" > /dev/null 2>&1; then \
		echo "In python-venv-requirements, using uv"; \
		uv pip install --upgrade --requirement $(python_requirements_file); \
	else \
		echo "In python-venv-requirements, using pip"; \
		pip install --upgrade --requirement $(python_requirements_file); \
	fi

# uv pip install --upgrade --requirement $(python_requirements_file)
# pip install --upgrade --requirement $(python_requirements_file)

.PHONY: python-venv-requirements-dev
python-venv-requirements-dev: ## Install or upgrade from $(python_requirements_dev_file)
	source .venv/bin/activate
	if ! command -v -- "uv" > /dev/null 2>&1; then \
		echo "In python-venv-requirements-dev, using uv"; \
		uv pip install --upgrade --requirement $(python_requirements_dev_file); \
	else \
		echo "In python-venv-requirements-dev, using pip"; \
		pip install --upgrade --requirement $(python_requirements_dev_file); \
	fi
# pip install --upgrade --requirement $(python_requirements_dev_file)
# uv pip install --upgrade --requirement $(python_requirements_dev_file)

.PHONY: python-venv-linters-install
python-venv-linters-install: ## Install or upgrade linters
	source .venv/bin/activate
	if ! command -v -- "uv" > /dev/null 2>&1; then \
		echo "python-venv-linters-install, using uv"; \
		uv pip install --upgrade flake8; \
	else \
		echo "python-venv-linters-install, using pip"; \
		pip install --upgrade flake8; \
	fi
# pip install --upgrade flake8

.PHONY: python-venv-purge
python-venv-purge: ## Remove venv ".venv/" folder
	rm -rf .venv

# ===============================================================================================
# Utils
# ===============================================================================================
.PHONY: python-purge-cache
python-purge-cache: ## Purge cache to avoid used cached files
	if [ -d .venv ] ; then
		source .venv/bin/activate
		pip cache purge
		if ! command -v -- "uv" > /dev/null 2>&1; then \
			uv cache clean; \
		fi
	fi

.PHONY: python-version
python-version: ## Displays the python version used for the .venv
	source .venv/bin/activate
	$(python_launcher) --version

.PHONY: python-flake8
python-flake8: ## Run flake8 linter for python
	source .venv/bin/activate
	flake8 --config .config/.flake8

.PHONY: python-pytest
python-pytest: ## Run pytest to test python scripts
	source .venv/bin/activate
	cd scripts/
	$(python_launcher) -m pytest
