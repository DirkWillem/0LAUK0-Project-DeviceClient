import time
import thread

from kivy.uix.screenmanager import Screen
import localapi.doses


class HomeScreen(Screen):
    """Main screen of the application"""

    dispense_enabled = True

    def __init__(self, sm, **kwargs):
        """Initialize the screen"""
        super(Screen, self).__init__(**kwargs)
        self.sm = sm
        self.stop = False
        self.pending_dose = None

    def on_enter(self):
        self.start_dose_workers()

    def open_settings(self):
        self.stop = True
        self.sm.transition.direction = 'up'
        self.sm.prev = 'Home'
        self.sm.current = 'Settings'

    def open_history(self):
        self.stop = True
        self.sm.transition.direction = 'left'
        self.sm.prev = 'Home'
        self.sm.current = 'History'

    def open_prn_medications(self):
        self.stop = True
        self.sm.transition.direction = 'left'
        self.sm.prev = 'Home'
        self.sm.current = 'PRNMedications'

    def start_dose_workers(self):
        """Starts the background process that checks for new doses"""

        def check_current_dose_worker():
            """Checks if there is a new dose to dispense"""
            while True:
                # Check if the thread needs to be stopped
                if self.stop:
                    return

                # Check for pending doses and sleep
                self.check_pending_dose()
                time.sleep(0.2)

        def fetch_doses_from_remote_worker():
            while True:
                if self.stop:
                    return

                localapi.doses.update_doses_from_remote()
                time.sleep(2.5)

        thread.start_new_thread(check_current_dose_worker, ())
        thread.start_new_thread(fetch_doses_from_remote_worker, ())

    def check_pending_dose(self):
        """Checks whether there is a dose that can be pended"""

        # If there is no pending dose, check for a new pending dose
        self.pending_dose = localapi.doses.get_current_dose()

        # Update the message if necessary
        if self.pending_dose is None:
            self.ids.dispense_button.disabled = True
            self.ids.dispense_label.text = "[i]You've taken all your medicines :-)[/i]"
        else:
            self.ids.dispense_button.disabled = False
            self.ids.dispense_label.text = "[size=40][b]%s[/b][/size]\n%s" \
                                           % (self.pending_dose.title, self.pending_dose.description)

    def dispense_clicked(self):
        self.check_pending_dose()

        if self.pending_dose is not None:
            self.ids.dispense_button.disabled = True
            localapi.doses.notify_dose_dispensed(self.pending_dose)
            self.pending_dose = None
            self.check_pending_dose()
