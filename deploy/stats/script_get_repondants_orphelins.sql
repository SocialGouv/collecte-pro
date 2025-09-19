CREATE OR REPLACE FUNCTION get_repondants_orphelins()
RETURNS TABLE (
    "user_id"           INTEGER,
    "username"          VARCHAR,
    "profile_type"      VARCHAR,
    "date_inscription"  DATE,
    "date_derniere_connexion"  DATE,
    "status"            VARCHAR,
    "id_control_associe" VARCHAR,
    "date_extraction"   DATE
)
AS $$
BEGIN
    RETURN QUERY 
    SELECT 
        per.user_id AS "user_id",
        per.username AS "username",
        per.profile_type AS "profile_type",
        per.date_joined ::DATE AS "date_inscription",
        per.last_login ::DATE AS "date_derniere_connexion",
        per.status AS "status",
        per.id_control_associe AS "id_control_associe",
        per.date_extraction::DATE AS "date_extraction"
    FROM purge_eligible_rep_orph_trv per
    ORDER BY per.date_joined DESC;

END;
$$ LANGUAGE plpgsql;