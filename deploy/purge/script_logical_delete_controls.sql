CREATE OR REPLACE FUNCTION logical_delete_controls()
RETURNS VOID AS $$
BEGIN

    UPDATE control_control
    SET is_deleted = TRUE, deleted_at = NOW()
    WHERE id IN (SELECT control_id FROM purge_eligible_control_trv);

    --ED avec is_deleted = TRUE ?? mais date echance moins de 3 ans ?! => on les détecte pas dans notre scipt !
    --add reference_code 
    INSERT INTO purge_histo_control(
        control_id, reference_code, is_supp_logique, date_supp_logique, is_supp_physique, date_supp_physique, code_ano)
    SELECT pce.control_id, cc.reference_code, TRUE, cc.deleted_at, FALSE, NULL, NULL
    FROM purge_eligible_control_trv pce
    INNER JOIN control_control cc ON cc.id = pce.control_id;
END;
$$ LANGUAGE plpgsql;
