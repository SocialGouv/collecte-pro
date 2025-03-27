CREATE OR REPLACE FUNCTION update_last_response_file_action()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE control_questionnaire
    SET last_response_file_action = NOW()
    WHERE id IN (
        SELECT cq.id
        FROM control_questionnaire cq
        INNER JOIN control_theme ct ON ct.questionnaire_id = cq.id
        INNER JOIN control_question cqu ON cqu.theme_id = ct.id
        WHERE cqu.id = NEW.question_id
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_last_response_file_action
AFTER INSERT OR UPDATE ON control_responsefile
FOR EACH ROW
EXECUTE FUNCTION update_last_response_file_action();
