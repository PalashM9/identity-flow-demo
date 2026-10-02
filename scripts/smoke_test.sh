#!/usr/bin/env bash
set -euo pipefail

USER_NAME="${API_USERNAME:-demo_user}"
PASSWORD="${API_PASSWORD:-demo_password_change_me}"

echo "Health:"
curl -s http://localhost:8000/health
echo

echo "Demo people:"
curl -s -u "${USER_NAME}:${PASSWORD}" http://localhost:8000/v1/demo-people
echo