CREATE OR REPLACE FUNCTION physical_delete_controls(interval_purge_rep_orph INTERVAL)
RETURNS VOID AS $$
DECLARE
    record_control RECORD;
BEGIN
    FOR record_control IN 
        SELECT phc.control_id 
        FROM purge_histo_control phc
        INNER JOIN control_control cc ON phc.control_id = cc.id
        WHERE phc.is_supp_physique = FALSE 
        AND cc.is_model = FALSE
    LOOP

        DELETE FROM control_responsefile
        WHERE question_id IN (
            SELECT cqu.id 
            FROM control_question cqu
            INNER JOIN control_theme ct ON cqu.theme_id = ct.id
            INNER JOIN control_questionnaire cq ON ct.questionnaire_id = cq.id
            INNER JOIN control_control cc ON cq.control_id = cc.id
            WHERE cc.id = record_control.control_id
            AND cc.is_deleted = TRUE
            AND cc.is_model = FALSE
        );


        DELETE FROM control_questionfile
        WHERE question_id IN (
            SELECT cqu.id 
            FROM control_question cqu
            INNER JOIN control_theme ct ON cqu.theme_id = ct.id
            INNER JOIN control_questionnaire cq ON ct.questionnaire_id = cq.id
            INNER JOIN control_control cc ON cq.control_id = cc.id
            WHERE cc.id = record_control.control_id
            AND cc.is_deleted = TRUE
            AND cc.is_model = FALSE
        );


        DELETE FROM control_question
        WHERE theme_id IN (
            SELECT ct.id 
            FROM control_theme ct
            INNER JOIN control_questionnaire cq ON ct.questionnaire_id = cq.id
            INNER JOIN control_control cc ON cq.control_id = cc.id
            WHERE cc.id = record_control.control_id
            AND cc.is_deleted = TRUE
            AND cc.is_model = FALSE
        );


        DELETE FROM control_theme
        WHERE questionnaire_id IN (
            SELECT cq.id 
            FROM control_questionnaire cq
            INNER JOIN control_control cc ON cq.control_id = cc.id
            WHERE cc.id = record_control.control_id
            AND cc.is_deleted = TRUE
            AND cc.is_model = FALSE
        );


        DELETE FROM control_questionnairefile
        WHERE questionnaire_id IN (
            SELECT cq.id 
            FROM control_questionnaire cq
            INNER JOIN control_control cc ON cq.control_id = cc.id
            WHERE cc.id = record_control.control_id
            AND cc.is_deleted = TRUE
            AND cc.is_model = FALSE
        );


        DELETE FROM control_questionnaire
        WHERE control_id = record_control.control_id
        AND control_id IN (
            SELECT id 
            FROM control_control 
            WHERE is_deleted = TRUE
            AND is_model = FALSE
        );


        DELETE FROM user_profiles_access
        WHERE control_id = record_control.control_id
        AND control_id IN (
            SELECT id 
            FROM control_control 
            WHERE is_deleted = TRUE
            AND is_model = FALSE
        );


        DELETE FROM control_control
        WHERE id = record_control.control_id
        AND is_deleted = TRUE
        AND is_model = FALSE;

        UPDATE purge_histo_control
        SET is_supp_physique = TRUE, date_supp_physique = NOW(), date_traitement = NOW()
        WHERE control_id = record_control.control_id;
		
    END LOOP;

    -- Récupération des répondants orphelins
    INSERT INTO purge_histo_rep_orphelins (
        user_id,
        username,
        profile_type,
        date_joined,
        is_physically_deleted,
        physical_deletion_date
    )
    SELECT 
        au.id AS user_id,
        au.username,
        upu.profile_type,
        au.date_joined,            
        FALSE,
        NULL
    FROM auth_user au
    INNER JOIN user_profiles_userprofile upu 
        ON upu.user_id = au.id
    LEFT JOIN user_profiles_access ua 
        ON ua.userprofile_id = upu.user_id
    WHERE upu.profile_type = 'audited'
    AND ua.id IS NULL
    AND au.date_joined < NOW() - interval_purge_rep_orph
    ORDER BY au.date_joined DESC;

    --Purge des répondants orphelins
    DELETE FROM user_profiles_userprofile
    WHERE user_id IN (SELECT user_id FROM purge_histo_rep_orphelins);

    DELETE FROM user_profiles_useripaddress
    WHERE username IN (SELECT username FROM purge_histo_rep_orphelins);

    DELETE FROM auth_user_groups
    WHERE user_id IN (SELECT user_id FROM purge_histo_rep_orphelins);

    DELETE FROM auth_user_user_permissions
    WHERE user_id IN (SELECT user_id FROM purge_histo_rep_orphelins);

    DELETE FROM auth_user
    WHERE id IN (SELECT user_id FROM purge_histo_rep_orphelins);


    UPDATE purge_histo_rep_orphelins
    SET 
        is_physically_deleted = TRUE,
        physical_deletion_date = NOW()
    WHERE is_physically_deleted = FALSE;

     
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Erreur lors de la suppression physique : %', SQLERRM;
END;
$$ LANGUAGE plpgsql;
