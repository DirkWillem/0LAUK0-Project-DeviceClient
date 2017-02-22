from api import client
from config import AppConfig

import models.dose
import models.medication


def get_doses():
    config = AppConfig()
    doses = client.get_json("/users/%d/doses" % config.dispenser.patient_id)

    return [models.dose.DoseSummary(
        dose["id"],
        dose["title"],
        dose["description"],
        dose["dispenseBefore"],
        dose["dispenseAfter"]) for dose in doses]


def get_dose(dose_id):
    config = AppConfig()
    dose = client.get_json("/users/%d/doses/%d" % (config.dispenser.patient_id, dose_id))

    medications = []

    for dm in dose["medications"]:
        med = models.medication.MedicationSummary(dm["medication"]["id"],
                                                  dm["medication"]["title"],
                                                  dm["medication"]["description"])
        medications.append(models.dose.DoseDetails.DoseMedication(-1, dm["amount"], med))

    return models.dose.DoseDetails(
        dose["id"],
        dose["title"],
        dose["description"],
        dose["dispenseBefore"],
        dose["dispenseAfter"],
        medications)
