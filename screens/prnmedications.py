from kivy.uix.screenmanager import Screen

import localapi.prnmedications


class PRNMedications(Screen):
    """Screen containing the PRN medications"""

    medications = []

    def __init__(self, sm, **kwargs):
        super(Screen, self).__init__(**kwargs)
        self.sm = sm

    def on_enter(self):
        localapi.prnmedications.update_prn_medications_from_remote()
        self.medications = localapi.prnmedications.get_prn_medications()
        self.ids.list_view.adapter.data = self.medications

    def open_home(self):
        self.sm.transition.direction = 'up'
        self.sm.prev = 'PRNMedications'
        self.sm.current = 'Home'

    def convert_data(self, idx, medication):
        """Data converter for SimpleListAdapter"""

        return {
            'medication': medication,
            'dispense_callback': lambda: self.prn_dispensed(medication)
        }

    def prn_dispensed(self, medication):
        """Callback handler for the dispensing of a PRN medication"""
        localapi.prnmedications.notify_prn_dispensed(medication)
        self.medications = localapi.prnmedications.get_prn_medications()

