CREATE OR REPLACE FUNCTION get_top_20(val text)
RETURNS TABLE (
    username varchar,
    nb bigint
) AS $$
BEGIN
    IF val = 'espaces_de_depot_par_utilisateur' THEN
        RETURN QUERY
        SELECT DISTINCT au.username, count(upa.control_id) as nb
        FROM user_profiles_access upa
        INNER JOIN auth_user au ON au.id = upa.userprofile_id
        INNER JOIN control_control cc ON cc.id = upa.control_id
        GROUP BY au.username
        ORDER BY nb DESC
        LIMIT 20;
    ELSIF val = 'questionnaires_par_utilisateur' THEN
        RETURN QUERY
        SELECT DISTINCT au.username, count(cq.id) as nb
        FROM user_profiles_access upa
        INNER JOIN auth_user au ON au.id = upa.userprofile_id
        INNER JOIN control_questionnaire cq ON cq.control_id = upa.control_id
        GROUP BY au.username
        ORDER BY nb DESC
        LIMIT 20;
    ELSIF val = 'questions_par_utilisateur' THEN
        RETURN QUERY
        SELECT DISTINCT au.username, count(cqu.id) as nb
        FROM user_profiles_access upa
        INNER JOIN auth_user au ON au.id = upa.userprofile_id
        INNER JOIN control_questionnaire cq ON cq.control_id = upa.control_id
        INNER JOIN control_theme ct ON ct.questionnaire_id = cq.id
        INNER JOIN control_question cqu ON cqu.theme_id = ct.id
        GROUP BY au.username
        ORDER BY nb DESC
        LIMIT 20;
    ELSIF val = 'themes_par_utilisateur' THEN
        RETURN QUERY
        SELECT DISTINCT au.username, count(ct.id) as nb
        FROM user_profiles_access upa
        INNER JOIN auth_user au ON au.id = upa.userprofile_id
        INNER JOIN control_questionnaire cq ON cq.control_id = upa.control_id
        INNER JOIN control_theme ct ON ct.questionnaire_id = cq.id
        GROUP BY au.username
        ORDER BY nb DESC
        LIMIT 20;
    
    END IF;
END;
$$ LANGUAGE plpgsql;