.PHONY: help build up run down test migrate makemigrations shell check lint

COMPOSE := docker compose
SVC := web

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
