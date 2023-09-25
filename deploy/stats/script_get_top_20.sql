CREATE OR REPLACE FUNCTION get_top_20(val integer)
RETURNS TABLE (
    username text,
    nb text
) AS $$
BEGIN
    IF val = 1 THEN
        RETURN QUERY
        SELECT DISTINCT au.username::text, count(upa.control_id)::text as nb
        FROM user_profiles_access upa
        INNER JOIN auth_user au ON au.id = upa.userprofile_id
        INNER JOIN control_control cc ON cc.id = upa.control_id
        GROUP BY au.username
        ORDER BY nb DESC
        LIMIT 20;
    ELSIF val = 2 THEN
        RETURN QUERY
        SELECT DISTINCT au.username::text, count(cq.id)::text as nb
        FROM user_profiles_access upa
        INNER JOIN auth_user au ON au.id = upa.userprofile_id
        INNER JOIN control_questionnaire cq ON cq.control_id = upa.control_id
        GROUP BY au.username
        ORDER BY nb DESC
        LIMIT 20;
    ELSIF val = 3 THEN
        RETURN QUERY
        SELECT DISTINCT au.username::text, count(cqu.id)::text as nb
        FROM user_profiles_access upa
        INNER JOIN auth_user au ON au.id = upa.userprofile_id
        INNER JOIN control_questionnaire cq ON cq.control_id = upa.control_id
        INNER JOIN control_theme ct ON ct.questionnaire_id = cq.id
        INNER JOIN control_question cqu ON cqu.theme_id = ct.id
        GROUP BY au.username
        ORDER BY nb DESC
        LIMIT 20;
    ELSIF val = 4 THEN
        RETURN QUERY
        SELECT DISTINCT au.username::text, count(ct.id)::text as nb
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