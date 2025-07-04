CREATE OR REPLACE FUNCTION trg_set_created_date()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.created_date IS NULL THEN
        NEW.created_date := NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_created_date_trigger_control_control
BEFORE INSERT ON control_control
FOR EACH ROW
EXECUTE FUNCTION trg_set_created_date();

CREATE TRIGGER set_created_date_trigger_control_questionnaire
BEFORE INSERT ON control_questionnaire
FOR EACH ROW
EXECUTE FUNCTION trg_set_created_date();
