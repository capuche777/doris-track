.PHONY: help build up run down test migrate makemigrations shell check lint \
	backup-export backup-import

COMPOSE := docker compose
SVC := web
BACKUP_DIR := backups
# Models excluded from backups: auto-generated tables that conflict on restore.
BACKUP_EXCLUDE := --exclude contenttypes --exclude auth.permission \
	--exclude admin.logentry --exclude sessions.session

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-16s %s\n", $$1, $$2}'

build: ## Build the image
	$(COMPOSE) build

up run: ## Start the dev stack
	$(COMPOSE) up

down: ## Stop the dev stack
	$(COMPOSE) down

test: ## Run the test suite inside the container
	$(COMPOSE) exec -T $(SVC) python -m pytest

migrate: ## Apply database migrations
	$(COMPOSE) exec -T $(SVC) python manage.py migrate

makemigrations: ## Generate new migrations
	$(COMPOSE) exec -T $(SVC) python manage.py makemigrations

check: ## Run Django system checks
	$(COMPOSE) exec -T $(SVC) python manage.py check

lint: ## Report PEP8 issues (non-blocking)
	$(COMPOSE) exec -T $(SVC) python -m flake8 . || true

shell: ## Open a Django shell in the container
	$(COMPOSE) exec $(SVC) python manage.py shell

backup-export: ## Export data to a JSON fixture (override path with FILE=path)
	@mkdir -p $(BACKUP_DIR)
	$(eval FILE ?= $(BACKUP_DIR)/doristrack-$(shell date +%Y%m%d-%H%M%S).json)
	@$(COMPOSE) exec -T $(SVC) python manage.py dumpdata \
		--natural-foreign --natural-primary $(BACKUP_EXCLUDE) --indent 2 \
		> "$(FILE)" && echo "Backup written to $(FILE)" \
		|| { rm -f "$(FILE)"; echo "Export failed"; exit 1; }

backup-import: ## Restore data from a fixture: make backup-import FILE=path
	@test -n "$(FILE)" || { echo "Usage: make backup-import FILE=<path>"; exit 1; }
	@test -f "$(FILE)" || { echo "File not found: $(FILE)"; exit 1; }
	$(COMPOSE) exec -T $(SVC) python manage.py loaddata --format=json - < "$(FILE)"
