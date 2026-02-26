CREATE OR REPLACE FUNCTION get_liste_utilisateurs()
RETURNS TABLE (
                "type_profil"  VARCHAR,
                "nom" VARCHAR,
                "prenom"  VARCHAR,
                "mail"  VARCHAR,
                "date_creation" VARCHAR,
                "actif"  VARCHAR,
                "date_derniere_connexion" VARCHAR
)
AS $$
BEGIN
    RETURN QUERY 
    SELECT
        uu.profile_type ::varchar AS type_profil,
        au.last_name    ::varchar AS nom,
        au.first_name   ::varchar AS prenom,
        au.username     ::varchar AS mail,
        to_char(au.date_joined, 'DD/MM/YYYY') ::varchar AS date_creation,
        CASE 
            WHEN au.is_active = true THEN 'Oui'
            ELSE 'Non'
        END ::varchar AS actif,
        to_char(au.last_login, 'DD/MM/YYYY MM:SS') ::varchar AS date_derniere_connexion
    FROM auth_user au
    JOIN user_profiles_userprofile uu
    ON uu.user_id = au.id
    ORDER BY au.date_joined DESC;



END;
$$ LANGUAGE plpgsql;