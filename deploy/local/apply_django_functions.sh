#!/usr/bin/env bash
#
# Applies the SQL functions/procedures that are directly called from the
# Django application (via cursor.callproc / cursor.execute in
# stats/views.py and reporting/tasks.py) into the Postgres container
# defined in docker-compose.yml.
#
# Usage:
#   ./deploy/local/apply_django_functions.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Fixed to match docker-compose.yml (services.postgres / POSTGRES_DB / POSTGRES_USER).
readonly DB_SERVICE="postgres"
readonly DB_NAME="ecc"
readonly DB_USER="ecc"

# Files used directly by the Django code (stats/views.py, reporting/tasks.py),
# in a safe dependency order.
FILES=(
  "${DEPLOY_DIR}/stats/script_get_top_20.sql"
  "${DEPLOY_DIR}/stats/script_get_espace_depot_modele.sql"
  "${DEPLOY_DIR}/stats/script_get_espace_depot_elig_supp.sql"
  "${DEPLOY_DIR}/stats/script_get_repondants_orphelins.sql"
  "${DEPLOY_DIR}/stats/script_get_liste_utilisateurs.sql"
  "${DEPLOY_DIR}/stats/script_get_statistiques.sql"
  "${DEPLOY_DIR}/purge/script_identify_purgeable_controls.sql"
  "${DEPLOY_DIR}/purge/script_identify_orphanUser.sql"
  "${DEPLOY_DIR}/purge/script_logical_delete_controls.sql"
  "${DEPLOY_DIR}/purge/script_physical_delete_controls.sql"
)

echo "==> Waiting for '${DB_SERVICE}' to accept connections..."
until docker compose exec -T "${DB_SERVICE}" pg_isready -U "${DB_USER}" -d "${DB_NAME}" >/dev/null 2>&1; do
  sleep 1
done

for file in "${FILES[@]}"; do
  if [[ ! -f "${file}" ]]; then
    echo "!! Missing file: ${file}" >&2
    exit 1
  fi
  echo "==> Applying $(basename "${file}")"
  docker compose exec -T "${DB_SERVICE}" psql -v ON_ERROR_STOP=1 -U "${DB_USER}" -d "${DB_NAME}" < "${file}"
done

echo "==> Done. All Django-invoked SQL functions have been (re)created."
