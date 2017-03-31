import datetime


class PRNHistorySummary(object):
    """Contains summary data on a PRN history entry"""

    def __init__(self, prn_history_id, dispensed_day, dispensed_time):
        self.prn_history_id = prn_history_id
        self.dispensed_day = dispensed_day
        self.dispensed_time = dispensed_time


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
    def __init__(self, prn_medication_id, description, max_daily, min_interval, medication, can_dispense, can_dispense_at, n_dispensed, last_dispensed_at):
        self.prn_medication_id = prn_medication_id
        self.description = description
        self.max_daily = max_daily
        self.min_interval = min_interval
        self.medication = medication
        self.can_dispense = can_dispense
        self.can_dispense_at = can_dispense_at
        self.n_dispensed = n_dispensed if last_dispensed_at is not None else 0
        self.last_dispensed_at = last_dispensed_at

    def get_description(self):
        can_dispense_at = "[color=#7caeff]Can dispense again at %s[/color]\n" % self.format_date(self.can_dispense_at) if not self.can_dispense else ""

        description = "[i]%s[/i]" % self.description
        max_daily = "    - Max [b][color=#ffffff]%d[/color][/b] daily (%d today)" % (self.max_daily, self.n_dispensed) \
            if self.max_daily > 0 else "    - No daily limit"
        min_interval = "    - At least [b][color=#ffffff]%d hours[/color][/b] in between (last at %s)" \
                       % (self.min_interval, self.format_date(self.last_dispensed_at))\
            if self.min_interval > 0 else "    - No mimimum in-between time"

        return "%s[color=#d0d0d0]%s\n\n%s\n%s[/color]" % (can_dispense_at, description, max_daily, min_interval)

    def format_date(self, dt):
        if dt is None:
            return "never"
        if dt.day == datetime.datetime.now().day:
            return dt.strftime("%H:%M")
        return dt.strftime("%B %d, %H:%M")
