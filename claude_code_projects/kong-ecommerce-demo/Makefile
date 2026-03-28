.PHONY: up down restart logs ps build clean status oidc-on oidc-off

## Start all services (builds custom Kong image with oidc plugin)
up:
	docker compose up -d --build

## Start without rebuilding
start:
	docker compose up -d

## Stop all services
down:
	docker compose down

## Rebuild and restart
restart:
	docker compose down && docker compose up -d --build

## Show live logs
logs:
	docker compose logs -f

## Show logs for a specific service: make log s=kong
log:
	docker compose logs -f $(s)

## Show running containers
ps:
	docker compose ps

## Show Kong routes, services, plugins
status:
	./scripts/setup-kong.sh status

## Enable OIDC on orders + users (requires Kong built with kong-oidc)
oidc-on:
	./scripts/setup-kong.sh oidc-all

## Remove OIDC plugins
oidc-off:
	./scripts/setup-kong.sh oidc-off

## Destroy everything including volumes (full reset)
clean:
	docker compose down -v --remove-orphans
