SELECT
  IFNULL((PM.MaxDaily = 0 OR PM.MaxDaily < PH.NDispensed) AND
    (DATE_ADD(PH.LastDispensed, INTERVAL PM.Mininterval HOUR)) < NOW(), 1) AS CanDispense,
  CASE
    WHEN (PM.MaxDaily != 0 AND PM.MaxDaily > PH.NDispensed) THEN TIMESTAMP(DATE_ADD(CURRENT_DATE(), INTERVAL 1 DAY), TIME(0))
    WHEN IFNULL((PM.MaxDaily = 0 OR PM.MaxDaily < PH.NDispensed) AND
      (DATE_ADD(PH.LastDispensed, INTERVAL PM.Mininterval HOUR)) < NOW(), 1) THEN NOW()
    ELSE DATE_ADD(PH.LastDispensed, INTERVAL PM.Mininterval HOUR)
  END AS CanDispenseAt
FROM PRNMedications PM
  LEFT JOIN (SELECT PRNMedicationID, MAX(DispensedTime) AS LastDispensed, COUNT(*) AS NDispensed FROM PRNHistory
    WHERE DATE(DispensedTime) = CURRENT_DATE()
    GROUP BY PRNMedicationID) PH ON PH.PRNMedicationID = PM.ID