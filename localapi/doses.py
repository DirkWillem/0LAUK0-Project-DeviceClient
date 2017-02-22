import json

from localapi import get_mysql_cnx
import api.doses
import localapi.medications
import models.dose
import models.medication


def get_doses():
    """Returns all doses that are saved locally"""

    query = """
    SELECT ID, Title, Description FROM Doses
    """

    # Connect to MySQL
    cnx = get_mysql_cnx()
    cursor = cnx.cursor()

    # Execute query
    result = []
    cursor.execute(query)
    for (dose_id, title, description) in cursor:
        result.append(models.dose.DoseMinimal(dose_id, title, description))

    # Close connection and return
    cursor.close()
    cnx.close()
    return result


def get_dose(dose_id):
    """Returns a dose as it is represented in the local database"""
    dose_query = """
SELECT ID, Title, Description, DispenseBefore, DispenseAfter
FROM Doses
WHERE ID = %(dose_id)s
"""

    medication_query = """
SELECT DM.ID, DM.Amount, M.ID, M.Title, M.Description FROM DoseMedications DM
LEFT JOIN Medications M ON DM.MedicationId = M.ID
WHERE DM.DoseID = %(dose_id)s
"""

    # Connect to MySQL
    cnx = get_mysql_cnx()
    cursor = cnx.cursor()

    result_tuple = None
    cursor.execute(dose_query, {"dose_id": dose_id})
    for res in cursor:
        result_tuple = res

    if result_tuple is not None:
        cursor.execute(medication_query, {"dose_id": dose_id})

        dose_medications = []
        for (dmid, amount, mid, title, description) in cursor:
            medication = models.medication.MedicationSummary(mid, title, description)
            dose_medications.append(models.dose.DoseDetails.DoseMedication(dmid, amount, medication))

        (did, title, description, dispense_before, dispense_after) = result_tuple
        return models.dose.DoseDetails(did, title, description, dispense_before, dispense_after, dose_medications)

    return None


def get_current_dose(time):
    """Returns all doses that should be dispensed at the given time"""

    query = """
SELECT D.ID, Title, Description
FROM Doses D
LEFT JOIN (SELECT MAX(DispensedTime) AS MaxDispensedTime, DoseID FROM DoseHistory GROUP BY DoseID) DH ON DH.DoseID = D.ID
WHERE
  ((DispenseAfter < DispenseBefore AND CAST(%(time)s AS TIME) BETWEEN DispenseAfter AND DispenseBefore) OR
    (DispenseAfter > DispenseBefore AND (CAST(%(time)s AS TIME) > DispenseAfter OR CAST(%(time)s AS TIME) < DispenseBefore)))
  AND (ISNULL(DH.MaxDispensedTime) OR DH.MaxDispensedTime < TIMESTAMP(CURRENT_DATE(), %(time)s))
ORDER BY DispenseAfter
LIMIT 1
"""

    # Connect to MySQL
    cnx = get_mysql_cnx()
    cursor = cnx.cursor()

    # Execute query
    result = None
    cursor.execute(query, {'time': time})
    for (dose_id, title, description) in cursor:
        result = models.dose.DoseMinimal(dose_id, title, description)

    # Close connection and return
    cursor.close()
    cnx.close()
    return result


def notify_dose_dispensed(dose, dispensed_time):
    """Notifies the system that a dose has been dispensed and inserts it into the dose history table"""

    query = """
    INSERT INTO DoseHistory (DoseID, DispensedTime) VALUES (%(dose_id)s, CAST(%(dispensed_time)s AS TIME))
        """

    # Connect to MySQL
    cnx = get_mysql_cnx()
    cursor = cnx.cursor()

    # Execute query
    cursor.execute(query, {'dose_id': dose.id, 'dispensed_time': dispensed_time})
    cnx.commit()

    # Close connection
    cursor.close()
    cnx.close()


def update_doses_from_remote():
    """Updates the doses from the remote server"""
    insert_dose_query = """
INSERT INTO Doses (ID, Title, Description, DispenseBefore, DispenseAfter)
VALUES (%(id)s, %(title)s, %(description)s, %(dispense_before)s, %(dispense_after)s)
"""

    update_dose_query = """
UPDATE Doses
SET
  Title = %(title)s,
  Description = %(description)s,
  DispenseBefore = %(dispense_before)s,
  DispenseAfter = %(dispense_after)s
WHERE ID = %(id)s
"""

    delete_dose_query = """
DELETE FROM Doses WHERE ID = %(id)s
"""

    update_dose_medication_query = """
UPDATE DoseMedications
SET
  Amount = %(amount)s
WHERE ID = %(id)s
    """

    insert_dose_medication_query = """
    INSERT INTO DoseMedications (Amount, MedicationID, DoseID)
    VALUES (%(amount)s, %(medication_id)s, %(dose_id)s)
    """
    delete_dose_medication_query = """
    DELETE FROM DoseMedications WHERE ID = %(id)s
    """

    insert_medication_query = """
INSERT INTO Medications (ID, Title, Description)
VALUES (%(id)s, %(title)s, %(description)s)
"""


    # Connect to MySQL
    cnx = get_mysql_cnx()
    cursor = cnx.cursor()

    # Load all medications
    medications = localapi.medications.get_medications()

    # Load all doses
    doses = api.doses.get_doses()

    for d in doses:
        dose_remote = api.doses.get_dose(d.dose_id)
        dose_local = get_dose(d.dose_id)

        # Check if any medications need to be inserted
        for dose_medication in dose_remote.medications:
            if not any([m for m in medications if m.medication_id == dose_medication.medication.medication_id]):
                cursor.execute(insert_medication_query, {
                    "id": dose_medication.medication.medication_id,
                    "title": dose_medication.medication.title,
                    "description": dose_medication.medication.description
                })

                medications.append(dose_medication.medication)

        # If the dose doesn't exist locally, create it
        if dose_local is None:
            cursor.execute(insert_dose_query, {
                "id": dose_remote.dose_id,
                "title": dose_remote.title,
                "description": dose_remote.description,
                "dispense_before": dose_remote.dispense_before,
                "dispense_after": dose_remote.dispense_after
            })

            for dm in dose_remote.medications:
                cursor.execute(insert_dose_medication_query, {
                    "amount": dm.amount,
                    "dose_id": dose_remote.dose_id,
                    "medication_id": dm.medication.medication_id
                })
        # Otherwise, check for any differences
        else:
            if dose_remote.title != dose_local.title \
                    or dose_remote.description != dose_local.description \
                    or dose_remote.dispense_after != dose_local.dispense_after \
                    or dose_remote.dispense_before != dose_local.dispense_before:
                cursor.execute(update_dose_query, {
                    "title": dose_remote.title,
                    "description": dose_remote.description,
                    "dispense_after": dose_remote.dispense_after,
                    "dispense_before": dose_remote.dispense_before,
                    "id": dose_remote.dose_id
                })

            # Check if any dose medications need to be added or updated
            for dose_medication in dose_remote.medications:
                local_medications = [dm for dm in dose_local.medications
                         if dm.medication.medication_id == dose_medication.medication.medication_id]

                if any(local_medications):
                    dm = local_medications[0]
                    if dm.amount != dose_medication.amount:
                        cursor.execute(update_dose_medication_query, {
                            "amount": dose_medication.amount,
                            "id": dm.dosemedication_id
                        })
                else:
                    cursor.execute(insert_dose_medication_query, {
                        "amount": dose_medication.amount,
                        "dose_id": dose_remote.id,
                        "medication_id": dose_medication.medication.medication_id
                    })

            # Check if any dose medications need to be removed
            for dose_medication in dose_local.medications:
                remote_medications = [dm for dm in dose_remote.medications
                                      if dm.medication.medication_id == dose_medication.medication.medication_id]
                if not any(remote_medications):
                    cursor.execute(delete_dose_medication_query, {
                        "id": dose_medication.id
                    })

    # Check if any doses need to be removed
    doses_local = get_doses()

    for dose in doses_local:
        if not any([d for d in doses if d.dose_id == dose.dose_id]):
            cursor.execute(delete_dose_query, {
                "id": d.dose_id
            })

    # Commit and close
    cnx.commit()
    cursor.close()
    cnx.close()
