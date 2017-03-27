class PRNMedicationSummary(object):
    """Contains summary data on a PRN medication"""

    def __init__(self, prn_medication_id, description, max_daily, min_interval, medication):
        self.prn_medication_id = prn_medication_id
        self.description = description
        self.max_daily = max_daily
        self.min_interval = min_interval
        self.medication = medication


class PRNMedicationLocal(object):
    """Contains both summary data and dispensing status of PRN medications"""
    def __init__(self, prn_medication_id, description, max_daily, min_interval, medication):
        self.prn_medication_id = prn_medication_id
        self.description = description
        self.max_daily = max_daily
        self.min_interval = min_interval
        self.medication = medication

    def get_description(self):
        description = "[i]%s[/i]" % self.description
        max_daily = "    - Max [b]%d[/b] daily" % self.max_daily if self.max_daily > 0 else "    - No daily limit"
        min_interval = "    - At least [b]%d hours[/b] in between" % self.min_interval if self.min_interval > 0 else "    - No mimimum in-between time"
        return "%s\n\n%s\n%s" % (description, max_daily, min_interval)