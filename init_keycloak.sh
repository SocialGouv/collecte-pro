#!/usr/bin/env bash
#
# init_keycloak.sh
#
# Populates the "collecte-pro" Keycloak realm with test users:
#   - "realm_admin" granted a set of realm-management client roles, so it can
#     manage users/clients through the Keycloak Admin REST API without being
#     a full realm/master admin.
#   - "admin_fonctionnel" granted the "inspector", "admin" and "igas" client
#     roles on "client_1".
# It also regenerates the "client_1" client secret and updates it in .env.
#
# Requirements: curl, jq
# Usage: ./init_keycloak.sh
#
# Configuration values are fixed below (edit the script to change them).

set -euo pipefail

KEYCLOAK_URL="http://localhost:8080"
KEYCLOAK_REALM="collecte-pro"
ADMIN_USERNAME="admin"
ADMIN_PASSWORD="admin"
REALM_ADMIN_USERNAME="realm_admin"
REALM_ADMIN_PASSWORD="1234"
FUNC_ADMIN_USERNAME="admin_fonctionnel"
FUNC_ADMIN_PASSWORD="1234"
FUNC_ADMIN_FIRST_NAME="admin"
FUNC_ADMIN_LAST_NAME="fonctionnel"
FUNC_ADMIN_EMAIL="admin_fonctionnel@user.com"
REALM_MANAGEMENT_CLIENT="realm-management"
ROLES=(view-users view-clients manage-users query-clients query-users)
APP_CLIENT_ID="client_1"
FUNC_ADMIN_ROLES=(inspector admin igas)
ENV_FILE="$(dirname "$0")/.env"
ENV_SAMPLE_FILE="$(dirname "$0")/.env.sample"

for bin in curl jq; do
  if ! command -v "$bin" >/dev/null 2>&1; then
    echo "Error: '$bin' is required but not installed." >&2
    exit 1
  fi
done

echo "Waiting for Keycloak to be ready at ${KEYCLOAK_URL}..."
until curl --silent --fail --output /dev/null "${KEYCLOAK_URL}/realms/master"; do
  sleep 2
done

echo "Authenticating against the master realm as '${ADMIN_USERNAME}'..."
ADMIN_TOKEN=$(curl --silent --fail \
  -X POST "${KEYCLOAK_URL}/realms/master/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password" \
  -d "client_id=admin-cli" \
  -d "username=${ADMIN_USERNAME}" \
  -d "password=${ADMIN_PASSWORD}" |
  jq -r '.access_token')

if [[ -z "${ADMIN_TOKEN}" || "${ADMIN_TOKEN}" == "null" ]]; then
  echo "Error: failed to obtain an admin access token." >&2
  exit 1
fi

api() {
  curl --silent --fail -H "Authorization: Bearer ${ADMIN_TOKEN}" "$@"
}

echo "Looking up existing user '${REALM_ADMIN_USERNAME}' in realm '${KEYCLOAK_REALM}'..."
USER_ID=$(api "${KEYCLOAK_URL}/admin/realms/${KEYCLOAK_REALM}/users?username=${REALM_ADMIN_USERNAME}&exact=true" |
  jq -r '.[0].id // empty')

if [[ -z "${USER_ID}" ]]; then
  echo "Creating user '${REALM_ADMIN_USERNAME}'..."
  api -X POST "${KEYCLOAK_URL}/admin/realms/${KEYCLOAK_REALM}/users" \
    -H "Content-Type: application/json" \
    -d "{
      \"username\": \"${REALM_ADMIN_USERNAME}\",
      \"enabled\": true,
      \"emailVerified\": true,
      \"credentials\": [{
        \"type\": \"password\",
        \"value\": \"${REALM_ADMIN_PASSWORD}\",
        \"temporary\": false
      }]
    }"

  USER_ID=$(api "${KEYCLOAK_URL}/admin/realms/${KEYCLOAK_REALM}/users?username=${REALM_ADMIN_USERNAME}&exact=true" |
    jq -r '.[0].id // empty')
else
  echo "User '${REALM_ADMIN_USERNAME}' already exists (id=${USER_ID}), resetting password..."
  api -X PUT "${KEYCLOAK_URL}/admin/realms/${KEYCLOAK_REALM}/users/${USER_ID}/reset-password" \
    -H "Content-Type: application/json" \
    -d "{\"type\": \"password\", \"value\": \"${REALM_ADMIN_PASSWORD}\", \"temporary\": false}"
fi

if [[ -z "${USER_ID}" ]]; then
  echo "Error: could not determine user id for '${REALM_ADMIN_USERNAME}'." >&2
  exit 1
fi

echo "Looking up '${REALM_MANAGEMENT_CLIENT}' client in realm '${KEYCLOAK_REALM}'..."
CLIENT_UUID=$(api "${KEYCLOAK_URL}/admin/realms/${KEYCLOAK_REALM}/clients?clientId=${REALM_MANAGEMENT_CLIENT}" |
  jq -r '.[0].id // empty')

if [[ -z "${CLIENT_UUID}" ]]; then
  echo "Error: client '${REALM_MANAGEMENT_CLIENT}' not found in realm '${KEYCLOAK_REALM}'." >&2
  exit 1
fi

echo "Fetching '${REALM_MANAGEMENT_CLIENT}' roles: ${ROLES[*]}..."
ROLES_JSON="[]"
for role in "${ROLES[@]}"; do
  role_repr=$(api "${KEYCLOAK_URL}/admin/realms/${KEYCLOAK_REALM}/clients/${CLIENT_UUID}/roles/${role}")
  if [[ -z "${role_repr}" ]]; then
    echo "Error: role '${role}' not found on client '${REALM_MANAGEMENT_CLIENT}'." >&2
    exit 1
  fi
  ROLES_JSON=$(jq -c --argjson roles "${ROLES_JSON}" --argjson role "${role_repr}" -n '$roles + [$role]')
done

echo "Assigning roles to '${REALM_ADMIN_USERNAME}'..."
api -X POST "${KEYCLOAK_URL}/admin/realms/${KEYCLOAK_REALM}/users/${USER_ID}/role-mappings/clients/${CLIENT_UUID}" \
  -H "Content-Type: application/json" \
  -d "${ROLES_JSON}"

echo "Done. '${REALM_ADMIN_USERNAME}' now has roles [${ROLES[*]}] on client '${REALM_MANAGEMENT_CLIENT}' in realm '${KEYCLOAK_REALM}'."

echo "Looking up existing user '${FUNC_ADMIN_USERNAME}' in realm '${KEYCLOAK_REALM}'..."
FUNC_USER_ID=$(api "${KEYCLOAK_URL}/admin/realms/${KEYCLOAK_REALM}/users?username=${FUNC_ADMIN_USERNAME}&exact=true" |
  jq -r '.[0].id // empty')

if [[ -z "${FUNC_USER_ID}" ]]; then
  echo "Creating user '${FUNC_ADMIN_USERNAME}'..."
  api -X POST "${KEYCLOAK_URL}/admin/realms/${KEYCLOAK_REALM}/users" \
    -H "Content-Type: application/json" \
    -d "{
      \"username\": \"${FUNC_ADMIN_USERNAME}\",
      \"firstName\": \"${FUNC_ADMIN_FIRST_NAME}\",
      \"lastName\": \"${FUNC_ADMIN_LAST_NAME}\",
      \"email\": \"${FUNC_ADMIN_EMAIL}\",
      \"enabled\": true,
      \"emailVerified\": true,
      \"credentials\": [{
        \"type\": \"password\",
        \"value\": \"${FUNC_ADMIN_PASSWORD}\",
        \"temporary\": false
      }]
    }"

  FUNC_USER_ID=$(api "${KEYCLOAK_URL}/admin/realms/${KEYCLOAK_REALM}/users?username=${FUNC_ADMIN_USERNAME}&exact=true" |
    jq -r '.[0].id // empty')
else
  echo "User '${FUNC_ADMIN_USERNAME}' already exists (id=${FUNC_USER_ID}), updating profile and resetting password..."
  api -X PUT "${KEYCLOAK_URL}/admin/realms/${KEYCLOAK_REALM}/users/${FUNC_USER_ID}" \
    -H "Content-Type: application/json" \
    -d "{
      \"firstName\": \"${FUNC_ADMIN_FIRST_NAME}\",
      \"lastName\": \"${FUNC_ADMIN_LAST_NAME}\",
      \"email\": \"${FUNC_ADMIN_EMAIL}\",
      \"emailVerified\": true
    }"
  api -X PUT "${KEYCLOAK_URL}/admin/realms/${KEYCLOAK_REALM}/users/${FUNC_USER_ID}/reset-password" \
    -H "Content-Type: application/json" \
    -d "{\"type\": \"password\", \"value\": \"${FUNC_ADMIN_PASSWORD}\", \"temporary\": false}"
fi

if [[ -z "${FUNC_USER_ID}" ]]; then
  echo "Error: could not determine user id for '${FUNC_ADMIN_USERNAME}'." >&2
  exit 1
fi

echo "Looking up client '${APP_CLIENT_ID}' in realm '${KEYCLOAK_REALM}'..."
APP_CLIENT_UUID=$(api "${KEYCLOAK_URL}/admin/realms/${KEYCLOAK_REALM}/clients?clientId=${APP_CLIENT_ID}" |
  jq -r '.[0].id // empty')

if [[ -z "${APP_CLIENT_UUID}" ]]; then
  echo "Error: client '${APP_CLIENT_ID}' not found in realm '${KEYCLOAK_REALM}'." >&2
  exit 1
fi

echo "Fetching '${APP_CLIENT_ID}' roles: ${FUNC_ADMIN_ROLES[*]}..."
FUNC_ROLES_JSON="[]"
for role in "${FUNC_ADMIN_ROLES[@]}"; do
  role_repr=$(api "${KEYCLOAK_URL}/admin/realms/${KEYCLOAK_REALM}/clients/${APP_CLIENT_UUID}/roles/${role}")
  if [[ -z "${role_repr}" ]]; then
    echo "Error: role '${role}' not found on client '${APP_CLIENT_ID}'." >&2
    exit 1
  fi
  FUNC_ROLES_JSON=$(jq -c --argjson roles "${FUNC_ROLES_JSON}" --argjson role "${role_repr}" -n '$roles + [$role]')
done

echo "Assigning roles to '${FUNC_ADMIN_USERNAME}'..."
api -X POST "${KEYCLOAK_URL}/admin/realms/${KEYCLOAK_REALM}/users/${FUNC_USER_ID}/role-mappings/clients/${APP_CLIENT_UUID}" \
  -H "Content-Type: application/json" \
  -d "${FUNC_ROLES_JSON}"

echo "Done. '${FUNC_ADMIN_USERNAME}' now has roles [${FUNC_ADMIN_ROLES[*]}] on client '${APP_CLIENT_ID}' in realm '${KEYCLOAK_REALM}'."

echo "Regenerating client secret for '${APP_CLIENT_ID}'..."
NEW_CLIENT_SECRET=$(api -X POST "${KEYCLOAK_URL}/admin/realms/${KEYCLOAK_REALM}/clients/${APP_CLIENT_UUID}/client-secret" |
  jq -r '.value // empty')

if [[ -z "${NEW_CLIENT_SECRET}" ]]; then
  echo "Error: failed to regenerate the client secret for '${APP_CLIENT_ID}'." >&2
  exit 1
fi

if [[ ! -f "${ENV_FILE}" ]]; then
  if [[ -f "${ENV_SAMPLE_FILE}" ]]; then
    echo "'${ENV_FILE}' not found, copying '${ENV_SAMPLE_FILE}'..."
    cp "${ENV_SAMPLE_FILE}" "${ENV_FILE}"
  fi
fi

if [[ -f "${ENV_FILE}" ]]; then
  echo "Updating OIDC_RP_CLIENT_SECRET in '${ENV_FILE}'..."
  if grep -q '^export OIDC_RP_CLIENT_SECRET=' "${ENV_FILE}"; then
    sed -i.bak "s|^export OIDC_RP_CLIENT_SECRET=.*|export OIDC_RP_CLIENT_SECRET='${NEW_CLIENT_SECRET}'|" "${ENV_FILE}"
    rm -f "${ENV_FILE}.bak"
  else
    echo "export OIDC_RP_CLIENT_SECRET='${NEW_CLIENT_SECRET}'" >>"${ENV_FILE}"
  fi
  echo "Done. '${APP_CLIENT_ID}' secret regenerated and written to '${ENV_FILE}'."
else
  echo "Warning: '${ENV_FILE}' not found, new secret for '${APP_CLIENT_ID}' was not persisted: ${NEW_CLIENT_SECRET}" >&2
fi
