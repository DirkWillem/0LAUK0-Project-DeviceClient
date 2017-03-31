from kivy.logger import Logger

from localapi import get_mysql_cnx

import localapi.medications
from localapi.doses import format_date, format_time
import models.prnmedication
import models.medication
import api.prnmedications


def get_prn_medications():
    """Returns all PRN medications that are saved locally"""

    query = """
SELECT
  PM.ID, PM.Description, PM.MaxDaily, PM.MinInterval, M.ID, M.Title, M.Description,
  IFNULL((PM.MaxDaily = 0 OR PM.MaxDaily > IFNULL(PHC.NDispensed, 0)) AND
    (DATE_ADD(PHT.LastDispensed, INTERVAL PM.Mininterval HOUR)) < NOW(), 1) AS CanDispense,
  CASE
    WHEN IFNULL((PM.MaxDaily != 0 AND PM.MaxDaily <= IFNULL(PHC.NDispensed, 0)), 1) THEN
      GREATEST(TIMESTAMP(DATE_ADD(CURRENT_DATE(), INTERVAL 1 DAY), TIME(0)),
          IFNULL(DATE_ADD(PHT.LastDispensed, INTERVAL PM.Mininterval HOUR), NOW()))
    WHEN IFNULL((PM.MaxDaily = 0 OR PM.MaxDaily < PHC.NDispensed) AND
      (DATE_ADD(PHT.LastDispensed, INTERVAL PM.Mininterval HOUR)) < NOW(), 1) THEN NOW()
    ELSE DATE_ADD(PHT.LastDispensed, INTERVAL PM.Mininterval HOUR)
  END AS CanDispenseAt,
  PHC.NDispensed AS NDispensed,
  PHT.LastDispensed AS LastDispensed
FROM PRNMedications PM
  LEFT JOIN (SELECT PRNMedicationID, COUNT(*) AS NDispensed FROM PRNHistory
    WHERE DATE(DispensedTime) = CURRENT_DATE()
    GROUP BY PRNMedicationID) PHC ON PHC.PRNMedicationID = PM.ID
  LEFT JOIN (SELECT PRNMedicationID, MAX(DispensedTime) AS LastDispensed FROM PRNHistory
    GROUP BY PRNMedicationID) PHT ON PHT.PRNMedicationID = PM.ID
  LEFT JOIN Medications M ON M.ID = PM.MedicationID"""

    # Connect to MySQL
    cnx = get_mysql_cnx()
    cursor = cnx.cursor()

    # Execute query
    result = []
    cursor.execute(query)
    for (
            prn_medication_id, description, max_daily, min_interval, medication_id, title,
            medication_description, can_dispense, can_dispense_at, n_dispensed, last_dispensed) in cursor:
        medication = models.medication.MedicationSummary(medication_id, title, medication_description)
        result.append(models.prnmedication.PRNMedicationLocal(prn_medication_id, description, max_daily, min_interval,
                                                              medication, can_dispense, can_dispense_at, n_dispensed,
                                                              last_dispensed))

    # Close connection and return
    cursor.close()
    cnx.close()
    return result


def get_prn_medication(prn_medication_id):
    """Returns a locally saved PRN medication by its ID"""

    query = """
SELECT
  PM.ID, PM.Description, PM.MaxDaily, PM.MinInterval, M.ID, M.Title, M.Description,
  IFNULL((PM.MaxDaily = 0 OR PM.MaxDaily > IFNULL(PHC.NDispensed, 0)) AND
    (DATE_ADD(PHT.LastDispensed, INTERVAL PM.Mininterval HOUR)) < NOW(), 1) AS CanDispense,
  CASE
    WHEN IFNULL((PM.MaxDaily != 0 AND PM.MaxDaily <= IFNULL(PHC.NDispensed, 0)), 1) THEN
      GREATEST(TIMESTAMP(DATE_ADD(CURRENT_DATE(), INTERVAL 1 DAY), TIME(0)),
          IFNULL(DATE_ADD(PHT.LastDispensed, INTERVAL PM.Mininterval HOUR), NOW()))
    WHEN IFNULL((PM.MaxDaily = 0 OR PM.MaxDaily < PHC.NDispensed) AND
      (DATE_ADD(PHT.LastDispensed, INTERVAL PM.Mininterval HOUR)) < NOW(), 1) THEN NOW()
    ELSE DATE_ADD(PHT.LastDispensed, INTERVAL PM.Mininterval HOUR)
  END AS CanDispenseAt,
  PHC.NDispensed AS NDispensed,
  PHT.LastDispensed AS LastDispensed
FROM PRNMedications PM
  LEFT JOIN (SELECT PRNMedicationID, COUNT(*) AS NDispensed FROM PRNHistory
    WHERE DATE(DispensedTime) = CURRENT_DATE()
    GROUP BY PRNMedicationID) PHC ON PHC.PRNMedicationID = PM.ID
  LEFT JOIN (SELECT PRNMedicationID, MAX(DispensedTime) AS LastDispensed FROM PRNHistory
    GROUP BY PRNMedicationID) PHT ON PHT.PRNMedicationID = PM.ID
  LEFT JOIN Medications M ON M.ID = PM.MedicationID
WHERE PM.ID = %(id)s"""

    # Connect to MySQL
    cnx = get_mysql_cnx()
    cursor = cnx.cursor()

    # Execute query
    result_tuple = None
    cursor.execute(query, {"id": prn_medication_id})

    for res in cursor:
        result_tuple = res

    cursor.close()
    cnx.close()

    if result_tuple is not None:
        (prn_medication_id, description, max_daily, min_interval, medication_id, title,
         medication_description, can_dispense, can_dispense_at, n_dispensed, last_dispensed) = result_tuple

        medication = models.medication.MedicationSummary(medication_id, title, medication_description)
        return models.prnmedication.PRNMedicationLocal(prn_medication_id, description, max_daily, min_interval,
                                                       medication, can_dispense, can_dispense_at, n_dispensed,
                                                       last_dispensed)
    return None


def notify_prn_dispensed(prn_medication):
    """Inserts a PRNHistory record"""

    Logger.info("PRN medication %d has been dispensed, inserting PRNHistory record" % prn_medication.prn_medication_id)

    insert_query = """
INSERT INTO PRNHistory (PRNMedicationID, DispensedTime) VALUES (%(prn_id)s, TIMESTAMP(CURRENT_DATE(), CURRENT_TIME()))
    """

    select_query = """
SELECT DispensedTime, DispensedTime FROM PRNHistory WHERE ID = %(prn_history_id)s
    """

    # Connect to MySQL
    cnx = get_mysql_cnx()
    cursor = cnx.cursor()

    # Execute query
    cursor.execute(insert_query, {'prn_id': prn_medication.prn_medication_id})

    insert_id = cursor.lastrowid

    result = None
    cursor.execute(select_query, {"prn_history_id": insert_id})

    for (dispensed_day, dispensed_time) in cursor:
        result = models.prnmedication.PRNHistorySummary(insert_id, format_date(dispensed_day), format_time(dispensed_time))

    api.prnmedications.create_prn_history_entry(prn_medication.prn_medication_id, result)

    # Commit
    cnx.commit()
    cursor.close()
    cnx.close()


def update_prn_medications_from_remote():
    """Updates the PRN medications from remote"""
    insert_prn_medication_query = """
INSERT INTO PRNMedications (ID, Description, MaxDaily, MinInterval, MedicationID)
VALUES (%(id)s, %(description)s, %(max_daily)s, %(min_interval)s, %(medication_id)s)
    """

    update_prn_medication_query = """
UPDATE PRNMedications
SET
  Description = %(description)s,
  MaxDaily = %(max_daily)s,
  MinInterval = %(min_interval)s,
  MedicationId = %(medication_id)s
WHERE ID = %(id)s
    """

    delete_prn_medication_query = """
DELETE FROM PRNMedications WHERE ID = %(id)s
    """

    insert_medication_query = """
INSERT INTO Medications (ID, Title, Description)
VALUES (%(id)s, %(title)s, %(description)s)
    """

    # Connect to MySQL
    cnx = get_mysql_cnx()
    cursor = cnx.cursor()

    # Load all local medications
    medications_local = localapi.medications.get_medications()

    # Load all PRN medications from remote
    prn_remote = api.prnmedications.get_prn_medications()

    # Iterate over all local PRN medications
    for pr in prn_remote:
        pl = get_prn_medication(pr.prn_medication_id)

        # Check if the medication needs to be inserted
        if not any([m for m in medications_local if m.medication_id == pr.medication.medication_id]):
            Logger.info("Inserting new Medication record with ID %d" % pr.medication.medication_id)

            cursor.execute(insert_medication_query, {
                "id": pr.medication.medication_id,
                "title": pr.medication.title,
                "description": pr.medication.description
            })

            medications_local.append(pr.medication)

        # If the PRN medication doesn't exist locally, create it
        if pl is None:
            Logger.info("Inserting new PRN medication record with ID %d" % pr.prn_medication_id)

            cursor.execute(insert_prn_medication_query, {
                "id": pr.prn_medication_id,
                "description": pr.description,
                "max_daily": pr.max_daily,
                "min_interval": pr.min_interval,
                "medication_id": pr.medication.medication_id
            })
        else:
            if pl.description != pr.description \
                    or pl.max_daily != pr.max_daily \
                    or pl.min_interval != pr.min_interval \
                    or pl.medication.medication_id != pr.medication.medication_id:
                Logger.info("Updating PRN medication record with ID %d", pr.prn_medication_id)

                cursor.execute(update_prn_medication_query, {
                    "id": pr.prn_medication_id,
                    "description": pr.description,
                    "max_daily": pr.max_daily,
                    "min_interval": pr.min_interval,
                    "medication_id": pr.medication.medication_id
                })

    # Check if any PRN medications need to be removed
    prn_local = get_prn_medications()

    for pl in prn_local:
        if not any([pr for pr in prn_remote if pr.prn_medication_id == pl.prn_medication_id]):
            Logger.info("Deleting PRN medication record with ID %d" % pl.prn_medication_id)

            cursor.execute(delete_prn_medication_query, {
                "id": pl.prn_medication_id
            })

    # Commit and close
    cnx.commit()
    cursor.close()
    cnx.close()
