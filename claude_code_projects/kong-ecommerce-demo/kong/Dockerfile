# Custom Kong image with kong-oidc plugin installed.
# This is used for the OIDC demo phase.
# For basic routing only, use `image: kong:3.7` in docker-compose.yml.

FROM kong:3.7

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends git unzip && \
    rm -rf /var/lib/apt/lists/*

# Install kong-oidc community plugin
RUN luarocks install kong-oidc

USER kong
