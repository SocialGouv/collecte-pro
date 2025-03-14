CREATE OR REPLACE FUNCTION get_espace_depot_modele()
RETURNS TABLE (
    id_espace_depot VARCHAR, 
    nombre_de_duplication BIGINT,
    date_derniere_duplication TIMESTAMPTZ
) 
AS $$
BEGIN
    RETURN QUERY 
    SELECT
        target_object_id AS id_espace_depot,  
        COUNT(*) AS nombre_de_duplication,
        MAX(timestamp) AS date_derniere_duplication
    FROM 
        actstream_action 
    WHERE
        verb = 'created control'
        AND target_object_id IS NOT NULL
    GROUP BY
        target_object_id
    ORDER BY 
        nombre_de_duplication DESC;
END;
$$ LANGUAGE plpgsql;
