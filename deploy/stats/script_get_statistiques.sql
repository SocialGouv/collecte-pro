CREATE OR REPLACE FUNCTION get_statistiques(_verb TEXT)
RETURNS TABLE (nb BIGINT, mois TEXT)
LANGUAGE plpgsql AS $func$
BEGIN
    IF _verb = 'nb users' THEN
        RETURN QUERY
        SELECT
            COALESCE(COUNT(au.date_joined), 0) AS nb,
            TO_CHAR(mois.mois, 'YYYY-MM') AS mois
        FROM (
            SELECT
                generate_series(
                    DATE_TRUNC('month', NOW() - INTERVAL '11 months'),
                    DATE_TRUNC('month', NOW()),
                    '1 month'::interval
                ) AS mois
        ) mois
        LEFT JOIN auth_user au ON EXTRACT(YEAR FROM mois.mois) = EXTRACT(YEAR FROM au.date_joined) 
        AND EXTRACT(MONTH FROM mois.mois) = EXTRACT(MONTH FROM au.date_joined)
        GROUP BY mois.mois
        ORDER BY mois.mois;
    ELSE
        RETURN QUERY
        SELECT
            COALESCE(COUNT(aa.timestamp), 0) AS nb,
            TO_CHAR(mois.mois, 'YYYY-MM') AS mois
        FROM (
            SELECT
                generate_series(
                    DATE_TRUNC('month', NOW() - INTERVAL '11 months'),
                    DATE_TRUNC('month', NOW()),
                    '1 month'::interval
                ) AS mois
        ) mois
        LEFT JOIN actstream_action aa ON EXTRACT(YEAR FROM mois.mois) = EXTRACT(YEAR FROM aa.timestamp) 
        AND EXTRACT(MONTH FROM mois.mois) = EXTRACT(MONTH FROM aa.timestamp)
        AND aa.verb = _verb
        GROUP BY mois.mois
        ORDER BY mois.mois;
    END IF;
END
$func$;