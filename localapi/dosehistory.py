from localapi import get_mysql_cnx

import models.dosehistory


def get_current_date_dose_status():
    """Returns all dose statuses on the current day"""

    query = """
SELECT
  D.Title, D.Description,
  (DH.ID IS NOT NULL) AS Dispensed,
  (DH.ID IS NULL AND (
    (D.DispenseAfter < D.DispenseBefore AND CURRENT_TIME < D.DispenseBefore) OR D.DispenseAfter > D.DispenseBefore)) AS Pending,
  (DH.ID IS NULL AND (
    (D.DispenseAfter < D.DispenseBefore AND CURRENT_TIME BETWEEN D.DispenseBefore AND D.DispenseAfter) OR
    (D.DispenseAfter > D.DispenseBefore AND CURRENT_TIME >= D.DispenseAfter))) AS BeingDispensed,
  TIME(DH.DispensedTime) AS DispensedTime
FROM Doses D
  LEFT JOIN (
    SELECT DHH.ID, DHH.DoseID, DHH.DispensedTime FROM DoseHistory DHH
      LEFT JOIN Doses DD ON DHH.DoseID = DD.ID
    WHERE (DD.DispenseBefore < DD.DispenseAfter AND DATE(DHH.DispensedTime) = CURRENT_DATE())
      OR (DD.DispenseBefore > DD.DispenseAfter AND (
        (TIME(DHH.DispensedTime) > DD.DispenseAfter AND DATE(DHH.DispensedTime) = CURRENT_DATE())
        OR (TIME(DHH.DispensedTime) < DD.DispenseAfter AND DATE(DHH.DispensedTime) = CURRENT_DATE() + INTERVAL 1 DAY)))
  ) DH ON DH.DoseID = D.ID
"""

    # Connect to MySQL
    cnx = get_mysql_cnx()
    cursor = cnx.cursor()

    # Execute query
    result = []
    cursor.execute(query)
    for (title, description, dispensed, pending, being_dispensed, dispensed_time) in cursor:
        result.append(models.dosehistory.DoseStatus(title, description, dispensed, pending, being_dispensed, dispensed_time))

    # Close connection and return
    cursor.close()
    cnx.close()
    return result
