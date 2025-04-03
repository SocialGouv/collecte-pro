CREATE OR REPLACE FUNCTION get_espace_depot_elig_supp()
RETURNS TABLE (
    "id_espace_depot" INTEGER, 
    "espace_depot" VARCHAR,
    "procedure" VARCHAR,
    "organisme_interroge" VARCHAR,
    "date_traitement" DATE  
) 
AS $$
BEGIN
    RETURN QUERY 
    SELECT 
        ce.control_id AS "id_espace_depot",
        cc.reference_code AS "espace_depot",
        cc.title AS "procedure",
        cc.depositing_organization AS "organisme_interroge",
        ce.date_traitement::DATE AS "date_traitement"  
    FROM purge_eligible_control_trv ce
    INNER JOIN control_control cc ON cc.id = ce.control_id
    ORDER BY id_espace_depot;
END;
$$ LANGUAGE plpgsql;