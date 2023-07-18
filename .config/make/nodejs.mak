## —— Node.js —————————————————————————————————————————————————————————————————————————————————————
.PHONY: nodejs-clean
nodejs-clean: ## Clean nodejs files
	sudo rm -rf node_modules

.PHONY: nodejs-bootstrap
nodejs-bootstrap: ## Bootstrap nodejs
	npm install
