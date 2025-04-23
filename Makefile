DB_URL=postgresql://admin:adminSecret@localhost:5432/videoproc?sslmode=disable

network:
	docker network create videoproc-network

postgres:
	docker run -d --rm \
  --name postgres \
  -p 5432:5432 \
  --network videoproc-network \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=adminSecret \
  -e POSTGRES_DB=videoproc \
  -v postgres-data:/var/lib/postgresql/data \
  postgres

pgadmin4:
	docker run -d --rm \
  --name pgadmin4 \
  -p 8000:80 \
  --network videoproc-network \
  -e PGADMIN_DEFAULT_EMAIL=admin@example.com \
  -e PGADMIN_DEFAULT_PASSWORD=adminSecret \
  -v pgadmin-data:/var/lib/pgadmin \
  dpage/pgadmin4

redis:
	docker run -d --rm --name redis -p 6379:6379 -d redis:7-alpine

jaeger-up:
	docker run -d --name jaeger \
		-e COLLECTOR_ZIPKIN_HOST_PORT=:9411 \
		-e COLLECTOR_OTLP_ENABLED=true \
		-p 16686:16686 \
		-p 9411:9411 \
		jaegertracing/all-in-one:1.51

jaeger-down:
	docker stop jaeger || true
	docker rm jaeger || true

otel-up:
	docker run -d --name otel-collector \
		--link jaeger \
		-p 4317:4317 \
		-p 13133:13133 \
		-v $$PWD/docker/otel/otel-collector-config.yaml:/etc/otel-collector-config.yaml \
		otel/opentelemetry-collector-contrib:latest \
		--config=/etc/otel-collector-config.yaml

otel-down:
	docker stop otel-collector || true
	docker rm otel-collector || true

tracing-up: jaeger-up otel-up

tracing-down: otel-down jaeger-down

DOCKER_RUNNING := $(shell docker ps -q -f name=postgres)

create-db:
	@echo "DOCKER_RUNNING is [$(DOCKER_RUNNING)]"
ifeq ($(DOCKER_RUNNING),)
	@echo "Using local psql to create DB with owner 'videoproc'"
	psql -h localhost -U admin -d postgres -c "CREATE DATABASE videoproc OWNER videoproc;"
else
	@echo "Using docker to create DB with owner 'videoproc'"
	docker exec -it postgres createdb --username=admin --owner=videoproc videoproc
endif

dropdb:
	docker exec -it postgres dropdb videoproc

stopdb:
	docker stop postgres pgadmin4

db_docs:
	dbdocs build docs/db.dbml

db_schema:
	dbml2sql --postgres -o docs/schema.sql doc/db.dbml

migrations:
	python manage.py makemigrations --settings=config.settings

migrate:
	python manage.py migrate

create-superuser:
	python manage.py createsuperuser

startLocalEnv:
	@$(MAKE) postgres
	@sleep 2
	@$(MAKE) pgadmin4
	@sleep 2
	@$(MAKE) redis
	@sleep 2
	@$(MAKE) tracing-up

server:
	OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317 \
    OTEL_SERVICE_NAME=video-processing \
    OTEL_TRACES_SAMPLER=always_on \
	TMPDIR=/media/tmp \
	python manage.py runserver 5000

celery:
	OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317 \
	OTEL_SERVICE_NAME=celery-worker \
	DJANGO_SETTINGS_MODULE=config.settings \
	CELERY_BROKER_URL=redis://localhost:6379/0 \
	CELERY_RESULT_BACKEND=redis://localhost:6379/0 \
	POSTGRES_DB=videoproc \
	POSTGRES_USER=admin \
	POSTGRES_PASSWORD=adminSecret \
	POSTGRES_HOST=localhost \
	TMPDIR=./media/tmp \
	opentelemetry-instrument celery -A config.celery worker --loglevel=debug -Q encoding

celery_beat:
	OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317 \
	OTEL_SERVICE_NAME=celery-worker \
	DJANGO_SETTINGS_MODULE=config.settings \
	CELERY_BROKER_URL=redis://localhost:6379/0 \
	CELERY_RESULT_BACKEND=redis://localhost:6379/0 \
	TMPDIR=./media/tmp \
	opentelemetry-instrument celery -A config.celery beat --loglevel=debug --schedule=./media/tmp/celerybeat-schedule

# ci_tests:
# 	@set -e; \
# 	COMPOSE_BAKE=true docker compose -f docker-compose.ci.yaml build --no-cache backend migrations unitests component_tests && \
# 	docker compose -f docker-compose.ci.yaml up -d postgres migrations && \
# 	docker compose -f docker-compose.ci.yaml run --rm unitests && \
# 	docker compose -f docker-compose.ci.yaml run --rm component_tests; \
# 	EXIT_CODE=$$?; \
# 	docker compose -f docker-compose.ci.yaml down; \
# 	exit $$EXIT_CODE

# dev_comp_tests:
# 	@set -e; \
# 	COMPOSE_BAKE=true docker compose -f docker-compose.dev.yml build && \
# 	docker compose -f docker-compose.dev.yml up -d postgres migrations pgadmin4 && \
# 	# docker compose -f docker-compose.dev.yml run --rm unitests && \
# 	# docker compose -f docker-compose.dev.yml run --rm component_tests; \
# 	EXIT_CODE=$$?; \
# 	docker compose -f docker-compose.dev.yml down; \
# 	exit $$EXIT_CODE

project-up:
	docker compose -f docker-compose.dev.yml up

project-down:
	docker compose -f docker-compose.dev.yml down

project-build:
	mkdir -p media/tmp media/videos media/processed
	COMPOSE_BAKE=true docker compose -f docker-compose.dev.yml build --no-cache

videoproc:
	docker compose -f docker-compose.dev.yml build video-proc --no-cache
	
# unittests:
# 	coverage run manage.py test --settings=config.settings_test
# 	coverage report

# unittests-html:
# 	coverage html
# 	xdg-open htmlcov/index.html

# documentation:
# 	python manage.py spectacular --file docs/openapi-schema.yml
# 	npx @redocly/cli build-docs docs/openapi-schema.yml -o docs/openapi.html

.PHONY: documentation celery celery_beat jaeger-up jaeger-down otel-up otel-down tracing-up tracing-down startLocalEnv network postgres createdb dropdb db_docs db_schema migrate migrations frontend redis stopdb server shell ci_comp_tests project unittests unittests-html
