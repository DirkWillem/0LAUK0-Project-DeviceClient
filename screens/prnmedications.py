from kivy.uix.screenmanager import Screen

import time
import thread

import localapi.prnmedications


class PRNMedications(Screen):
    """Screen containing the PRN medications"""

    medications = []

    def __init__(self, sm, **kwargs):
        super(Screen, self).__init__(**kwargs)
        self.sm = sm
        self.stop = False

    def on_enter(self):
        self.start_prn_workers()

    def open_home(self):
        self.stop = True
        self.sm.transition.direction = 'right'
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
        self.ids.list_view.adapter.data = self.medications

    def start_prn_workers(self):
        """Starts the background processes that check for updates in PRN medication"""

        def update_current_medications_worker():
            while True:
                # Check whether the thread needs to be stopped
                if self.stop:
                    return

                # Update data
                self.medications = localapi.prnmedications.get_prn_medications()
                self.ids.list_view.adapter.data = self.medications
                time.sleep(0.2)

        def update_medications_from_remote_worker():
            while True:
                # Check whether the thread needs to be stopped
                if self.stop:
                    return

                # Update data
                localapi.prnmedications.update_prn_medications_from_remote()
                time.sleep(2.5)

        thread.start_new_thread(update_current_medications_worker, ())
        thread.start_new_thread(update_medications_from_remote_worker, ())

