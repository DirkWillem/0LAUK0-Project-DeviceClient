class DoseMinimal(object):
    """Contains minimal data on a dose"""

    def __init__(self, dose_id, title, description):
        self.id = dose_id
        self.title = title
        self.description = description


class DoseSummary(object):
    """Represents a DoseSummary object from the API"""

    def __init__(self, dose_id, title, description, dispense_before, dispense_after):
        self.dose_id = dose_id
        self.title = title
        self.description = description
        self.dispense_before = dispense_before
        self.dispense_after = dispense_after

    def __str__(self):
        return "<Dose %d: %s>" % (self.dose_id, self.title)


class DoseDetails(DoseSummary):
    """Represents a DoseDetails object from the API"""

    class DoseMedication(object):
        def __init__(self, dmid, amount, medication):
            self.dosemedication_id = dmid
            self.amount = amount
            self.medication = medication

    def __init__(self, dose_id, title, description, dispense_before, dispense_after, medications):
        super(DoseDetails, self).__init__(dose_id, title, description, dispense_before, dispense_after)

        self.medications = medications

    def __str__(self):
        return "<Dose %d: %s>" % (self.dose_id, self.title)
