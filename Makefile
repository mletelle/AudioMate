# Makefile
DOCKER_COMPOSE ?= docker compose  

build: 
	$(DOCKER_COMPOSE) build

up:
	$(DOCKER_COMPOSE) up -d

logs: 
	$(DOCKER_COMPOSE) logs -f

down:
	$(DOCKER_COMPOSE) down

shell:
	$(DOCKER_COMPOSE) exec audiomate sh

test-gpu:
	${DOCKER_COMPOSE} exec audiomate python -m pytest tests/test_gpu.py

test:
	${DOCKER_COMPOSE} exec audiomate python -m pytest tests/