DOCKER_COMPOSE ?= docker compose        # o "docker-compose" si usás la versión legacy

build:            ## Construir la imagen
	$(DOCKER_COMPOSE) build

up:               ## Levantar contenedor en segundo plano
	$(DOCKER_COMPOSE) up -d

logs:             ## Ver logs en vivo
	$(DOCKER_COMPOSE) logs -f

down:             ## Apagar y borrar contenedores
	$(DOCKER_COMPOSE) down

shell:            ## Shell dentro del contenedor
	$(DOCKER_COMPOSE) exec audiomate bash

test-gpu:
	${DOCKER_COMPOSE} exec audiomate python test_gpu.py
