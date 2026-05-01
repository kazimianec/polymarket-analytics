#!/bin/sh
set -e
: "${BACKEND_URL:?BACKEND_URL is required}"
envsubst '${BACKEND_URL}' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf
exec nginx -g 'daemon off;'
