from kivy.uix.screenmanager import Screen

import localapi.dosehistory


class HistoryScreen(Screen):
    """Screen containing the history for the current day"""

    history = []
    data_converter = lambda self, idx, entry: {'entry': entry, 'height': 40}

    def __init__(self, sm, **kwargs):
        super(Screen, self).__init__(**kwargs)
        self.sm = sm

    def on_enter(self):
        self.history = localapi.dosehistory.get_current_date_dose_status()
        self.ids.list_view.adapter.data = self.history

    def open_home(self):
        self.sm.transition.direction = 'right'
        self.sm.prev = 'History'
        self.sm.current = 'Home'
