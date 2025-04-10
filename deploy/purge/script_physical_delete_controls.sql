CREATE OR REPLACE FUNCTION physical_delete_controls()
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
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        --RAISE EXCEPTION 'Erreur lors de la suppression physique : %', SQLERRM;
END;
$$ LANGUAGE plpgsql;
