#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
#  Kong E-Commerce Demo – Admin API helper
#  Use this to inspect or configure Kong dynamically via
#  the Admin API (useful when switching to DB mode).
# ─────────────────────────────────────────────────────────────

set -euo pipefail

KONG_ADMIN="${KONG_ADMIN:-http://localhost:8001}"

wait_for_kong() {
  echo "Waiting for Kong Admin API..."
  until curl -sf "$KONG_ADMIN/status" > /dev/null; do
    sleep 2
  done
  echo "Kong is ready."
}

show_routes() {
  echo ""
  echo "=== Kong Services ==="
  curl -s "$KONG_ADMIN/services" | python3 -m json.tool
  echo ""
  echo "=== Kong Routes ==="
  curl -s "$KONG_ADMIN/routes" | python3 -m json.tool
  echo ""
  echo "=== Kong Plugins ==="
  curl -s "$KONG_ADMIN/plugins" | python3 -m json.tool
}

enable_oidc_orders() {
  echo "Enabling OIDC plugin on orders-service..."
  curl -s -X POST "$KONG_ADMIN/services/orders-service/plugins" \
    --data "name=oidc" \
    --data "config.client_id=kong" \
    --data "config.client_secret=kong-secret" \
    --data "config.discovery=http://keycloak:8080/realms/ecommerce/.well-known/openid-configuration" \
    --data "config.introspection_endpoint=http://keycloak:8080/realms/ecommerce/protocol/openid-connect/token/introspect" \
    --data "config.bearer_only=yes" \
    --data "config.realm=ecommerce" | python3 -m json.tool
  echo ""
  echo "✓ OIDC enabled on orders-service"
}

enable_oidc_users() {
  echo "Enabling OIDC plugin on users-service..."
  curl -s -X POST "$KONG_ADMIN/services/users-service/plugins" \
    --data "name=oidc" \
    --data "config.client_id=kong" \
    --data "config.client_secret=kong-secret" \
    --data "config.discovery=http://keycloak:8080/realms/ecommerce/.well-known/openid-configuration" \
    --data "config.bearer_only=yes" \
    --data "config.realm=ecommerce" | python3 -m json.tool
  echo ""
  echo "✓ OIDC enabled on users-service"
}

disable_oidc() {
  echo "Removing all OIDC plugins..."
  for plugin_id in $(curl -s "$KONG_ADMIN/plugins?name=oidc" | python3 -c "import sys,json; [print(p['id']) for p in json.load(sys.stdin)['data']]"); do
    curl -s -X DELETE "$KONG_ADMIN/plugins/$plugin_id"
    echo "Removed plugin: $plugin_id"
  done
}

rate_limit_orders() {
  echo "Adding rate limiting (10 req/min) to orders-service..."
  curl -s -X POST "$KONG_ADMIN/services/orders-service/plugins" \
    --data "name=rate-limiting" \
    --data "config.minute=10" \
    --data "config.policy=local" | python3 -m json.tool
}

print_usage() {
  echo "Usage: $0 <command>"
  echo ""
  echo "Commands:"
  echo "  status          - Show all routes, services, plugins"
  echo "  oidc-orders     - Enable OIDC on orders-service"
  echo "  oidc-users      - Enable OIDC on users-service"
  echo "  oidc-all        - Enable OIDC on orders + users"
  echo "  oidc-off        - Remove all OIDC plugins"
  echo "  rate-orders     - Add rate limiting to orders-service"
  echo "  wait            - Wait until Kong is ready"
}

case "${1:-help}" in
  status)       wait_for_kong; show_routes ;;
  oidc-orders)  wait_for_kong; enable_oidc_orders ;;
  oidc-users)   wait_for_kong; enable_oidc_users ;;
  oidc-all)     wait_for_kong; enable_oidc_orders; enable_oidc_users ;;
  oidc-off)     wait_for_kong; disable_oidc ;;
  rate-orders)  wait_for_kong; rate_limit_orders ;;
  wait)         wait_for_kong ;;
  *)            print_usage ;;
esac
