import time
import thread
from kivy.uix.screenmanager import Screen

import api


class ConnectingScreen(Screen):
    """Screen that is shown while connecting to MySMDS"""

    def __init__(self, sm, **kwargs):
        """Initialize the screen"""
        super(Screen, self).__init__(**kwargs)
        self.name = 'Connecting'
        self.sm = sm
        self.stop = False

    def on_enter(self):
        self.stop = False
        self.connect()

    def open_settings(self):
        self.stop = True
        self.sm.transition.direction = 'up'
        self.sm.prev = 'Connecting'
        self.sm.current = 'Settings'

    def connect(self):
        def connect_worker():
            while True:
                if self.stop:
                    return
                if api.try_connect():
                    self.sm.transition.direction = 'left'
                    self.sm.current = 'Home'
                    return
                time.sleep(1)

        thread.start_new(connect_worker, ())
