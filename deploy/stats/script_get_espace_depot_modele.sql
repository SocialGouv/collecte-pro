CREATE OR REPLACE FUNCTION get_espace_depot_modele()
RETURNS TABLE (
    id_espace_depot VARCHAR, 
    reference_code VARCHAR,
    nombre_de_duplication BIGINT,
    date_derniere_duplication TIMESTAMPTZ,
    top_model_coche VARCHAR  
) 
AS $$
BEGIN
    RETURN QUERY 
    SELECT
        aa.target_object_id AS id_espace_depot,  
        cc.reference_code,
        COUNT(*) AS nombre_de_duplication,
        MAX(aa.timestamp) AS date_derniere_duplication,
        CAST(
            CASE 
                WHEN cc.is_model = TRUE THEN 'Oui' 
                ELSE 'Non' 
            END 
        AS VARCHAR) AS top_model_coche  
    FROM 
        actstream_action aa
    JOIN 
        control_control cc ON cc.id = aa.target_object_id::INTEGER
    WHERE
        aa.verb = 'created control'
        AND aa.target_object_id IS NOT NULL
    GROUP BY
        aa.target_object_id, cc.reference_code, cc.is_model
    ORDER BY 
        nombre_de_duplication DESC;
END;
$$ LANGUAGE plpgsql;
