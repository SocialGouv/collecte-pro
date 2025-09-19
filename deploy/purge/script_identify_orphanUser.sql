CREATE OR REPLACE FUNCTION identify_orphanUser(interval_purge_rep_orph INTERVAL)
RETURNS TABLE (
    user_id INTEGER,
    username VARCHAR,
    profile_type VARCHAR,
    date_inscription DATE,
    date_derniere_connexion  DATE,
    status VARCHAR,
    id_control_associe VARCHAR,
    date_extraction DATE
) AS $$
BEGIN
    TRUNCATE TABLE purge_eligible_rep_orph_trv;

    INSERT INTO purge_eligible_rep_orph_trv (
        user_id,
        username,
        profile_type,
        date_joined,
        last_login,
        status,
        id_control_associe,
        date_extraction
    )
    SELECT 
        au.id AS user_id,
        au.username,
        upu.profile_type,
        au.date_joined,
        au.last_login,
        CASE 
            WHEN COUNT(ua.control_id) = 0 THEN 'orphelin'
            WHEN COUNT(DISTINCT ua.control_id) > 0
                 AND COUNT(DISTINCT CASE WHEN ua.control_id NOT IN 
                     (SELECT control_id FROM purge_eligible_control_trv) THEN ua.control_id END) = 0
            THEN 'orphelin_eligible'
        END AS status,
        CASE 
            WHEN COUNT(ua.control_id) = 0 THEN NULL
            ELSE string_agg(DISTINCT ua.control_id::text, ', ')
        END AS id_control_associe,
        NOW() AS date_extraction
    FROM auth_user au
    JOIN user_profiles_userprofile upu 
        ON upu.user_id = au.id
    LEFT JOIN user_profiles_access ua 
        ON ua.userprofile_id = upu.user_id
    WHERE upu.profile_type = 'audited'
    AND au.date_joined < NOW() - interval_purge_rep_orph
    GROUP BY au.id, au.username, upu.profile_type, au.date_joined, au.last_login
    HAVING 
        COUNT(ua.control_id) = 0
        OR (
            COUNT(DISTINCT ua.control_id) > 0
            AND COUNT(DISTINCT CASE WHEN ua.control_id NOT IN 
                (SELECT control_id FROM purge_eligible_control_trv) THEN ua.control_id END) = 0
        )
    ORDER BY au.date_joined DESC;

END;
$$ LANGUAGE plpgsql;
