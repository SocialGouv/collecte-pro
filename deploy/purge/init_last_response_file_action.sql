UPDATE control_questionnaire
SET last_response_file_action = COALESCE(end_date, CURRENT_DATE)
WHERE last_response_file_action IS NULL;