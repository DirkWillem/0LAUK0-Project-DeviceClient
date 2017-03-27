from config import AppConfig

import api
import models.prnmedication
import models.medication


def get_prn_medications():
    """Returns all PRN medications from the service"""

    config = AppConfig()
    client = api.RestClient()
    medications = client.get_json("/users/%d/prnmedications" % config.dispenser.patient_id)

    return [models.prnmedication.PRNMedicationSummary(
        medication["id"],
        medication["description"],
        medication["maxDaily"],
        medication["minInterval"],
        models.medication.MedicationSummary(
            medication["medication"]["id"],
            medication["medication"]["title"],
            medication["medication"]["description"])
    ) for medication in medications]
