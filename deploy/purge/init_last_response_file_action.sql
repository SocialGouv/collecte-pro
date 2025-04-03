UPDATE control_questionnaire 
SET last_response_file_action = GREATEST(end_date, sent_date, modified)
WHERE last_response_file_action IS NULL;