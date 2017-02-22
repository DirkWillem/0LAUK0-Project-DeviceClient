import datetime
import time
import thread

from kivy.uix.screenmanager import Screen
import localapi.doses

class HomeScreen(Screen):
    """Main screen of the application"""

    dispense_enabled = True

    def __init__(self):
        """Initialize the screen"""
        super(Screen, self).__init__()
        self.name = "Home"
        self.stop = False
        self.start_dose_workers()
        self.pending_dose = None

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
                time.sleep(5)

        thread.start_new_thread(check_current_dose_worker, ())
        thread.start_new_thread(fetch_doses_from_remote_worker, ())

    def check_pending_dose(self):
        """Checks whether there is a dose that can be pended"""

        # If there is no pending dose, check for a new pending dose
        if self.pending_dose is None:
            self.pending_dose = localapi.doses.get_current_dose(datetime.time(8))

        # Update the message if necessary
        if self.pending_dose is None:
            self.ids.dispense_button.disabled = True
            self.ids.dispense_label.text = "[i]You've taken all your medicines :-)[/i]"
        else:
            self.ids.dispense_button.disabled = False
            self.ids.dispense_label.text = "[size=40][b]%s[/b][/size]\n%s" \
                                           % (self.pending_dose.title, self.pending_dose.description)

    def dispense_clicked(self):
        localapi.doses.notify_dose_dispensed(self.pending_dose, datetime.time(9, 33, 21))
        self.pending_dose = None
        self.check_pending_dose()
