from kivy.uix.screenmanager import Screen
from kivy.uix.settings import Settings
from kivy.core.window import Window
import config


class SettingsScreen(Screen):
    def __init__(self, sm, **kwargs):
        """Initialize the screen"""
        super(Screen, self).__init__(**kwargs)

        self.sm = sm

    def on_enter(self):
        cfg = config.AppConfig().config_parser

        s = Settings()
        s.add_json_panel('API', cfg, 'assets/settings/api.json')
        s.add_json_panel('Database', cfg, 'assets/settings/database.json')
        s.add_json_panel('Dispenser', cfg, 'assets/settings/dispenser.json')
        s.on_close = lambda: self.close()

        self.add_widget(s, 0)

    def close(self):
        self.sm.transition.direction = 'down'
        self.sm.current = self.sm.prev
