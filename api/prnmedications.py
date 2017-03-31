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


def create_prn_history_entry(prn_id, prn_history):
    """Creates a new PRN history entry in the service"""
    config = AppConfig()
    client = api.RestClient()

    client.post_json_no_response("/users/%d/prnhistory" % config.dispenser.patient_id, {
        "prnMedicationId": prn_id,
        "dispensedDay": prn_history.dispensed_day,
        "dispensedTime": prn_history.dispensed_time
    })
