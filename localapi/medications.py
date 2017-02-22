from localapi import get_mysql_cnx

import models.medication


def get_medications():
    """Returns all medications in the local database"""

    query = """
SELECT ID, Title, Description FROM Medications
"""

    # Connect to MySQL
    cnx = get_mysql_cnx()
    cursor = cnx.cursor()

    # Execute query
    results = []
    cursor.execute(query)
    for (dose_id, title, description) in cursor:
        results.append(models.medication.MedicationSummary(dose_id, title, description))

    # Close connection and return
    cursor.close()
    cnx.close()
    return results
