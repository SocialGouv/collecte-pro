"""CREATE OR REPLACE FUNCTION physical_delete_controls()
RETURNS VOID AS $$
BEGIN

    DELETE FROM control_control 
    WHERE is_deleted = TRUE 
    AND id IN (SELECT control_id FROM purge_histo_control);

    UPDATE purge_histo_control
    SET is_supp_physique = TRUE, date_supp_physique = NOW()
    WHERE NOT EXISTS (
        SELECT 1 FROM control_control cc WHERE cc.id = purge_histo_control.control_id
    );

END;
$$ LANGUAGE plpgsql;"""
