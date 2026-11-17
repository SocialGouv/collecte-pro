import os
import sys

import django

SQL_FILES = [
    "stats/script_get_top_20.sql",
    "stats/script_get_espace_depot_modele.sql",
    "stats/script_get_espace_depot_elig_supp.sql",
    "stats/script_get_repondants_orphelins.sql",
    "stats/script_get_liste_utilisateurs.sql",
    "stats/script_get_statistiques.sql",
    "purge/script_identify_purgeable_controls.sql",
    "purge/script_identify_orphanUser.sql",
    "purge/script_logical_delete_controls.sql",
    "purge/script_physical_delete_controls.sql",
    "purge/init_last_response_file_action.sql",
    "purge/trigger_set_created_date_triggers.sql",
    "purge/trigger_update_last_response_file_action.sql",
]


def main():
    deploy_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(deploy_dir))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ecc.settings")
    django.setup()
    from django.db import connection

    with connection.cursor() as cursor:
        for name in SQL_FILES:
            print(f"-- {name}")
            with open(os.path.join(deploy_dir, name), encoding="utf-8") as sql_file:
                cursor.execute(sql_file.read())


if __name__ == "__main__":
    main()
