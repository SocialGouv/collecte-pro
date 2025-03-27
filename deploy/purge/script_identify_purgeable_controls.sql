CREATE OR REPLACE FUNCTION identify_purgeable_controls(purge_interval INTERVAL)
RETURNS TABLE (
    mail_inspecteur VARCHAR,
    espaces_depot VARCHAR,
    ids_espaces_depot INTEGER[]
) 
LANGUAGE plpgsql
AS $$
BEGIN

    TRUNCATE TABLE purge_eligible_control_trv;

    --si end_date est null ? 

    INSERT INTO purge_eligible_control_trv (control_id)
    SELECT DISTINCT cc.id
    FROM control_control cc
    INNER JOIN control_questionnaire cq ON cq.control_id = cc.id
    WHERE cc.is_model = FALSE
      AND cq.end_date < NOW() - purge_interval; 

    RETURN QUERY 
    SELECT
        au.username AS mail_inspecteur,
        STRING_AGG(cc.reference_code, '; ')::VARCHAR AS espaces_depot,  
        ARRAY_AGG(ce.control_id) AS ids_espaces_depot
    FROM purge_eligible_control_trv ce
    INNER JOIN control_control cc ON cc.id = ce.control_id
    INNER JOIN user_profiles_access upa ON upa.control_id = cc.id
    INNER JOIN auth_user au ON au.id = upa.userprofile_id
    INNER JOIN user_profiles_userprofile uu ON uu.user_id = au.id
    WHERE uu.profile_type = 'inspector'
    GROUP BY au.username 
    ORDER BY MIN(ce.control_id);

END;
$$;
