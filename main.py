import kivy
from kivy.app import App
from kivy.config import Config
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager

from screens.home import HomeScreen
from screens.connecting import ConnectingScreen
from screens.settings import SettingsScreen

from config import AppConfig

kivy.require('1.9.1')

# Set display settings from config
cfg = AppConfig()

Config.set('graphics', 'width', cfg.display.width)
Config.set('graphics', 'height', cfg.display.height)

print cfg.display.width

# Load UI file
Builder.load_file("./main.kv")

# Initialize screen manager
sm = ScreenManager()
sm.add_widget(ConnectingScreen(sm, name='Connecting'))
sm.add_widget(HomeScreen(sm, name='Home'))
sm.add_widget(SettingsScreen(sm, name='Settings'))


class Application(App):
    def build(self):
        self.icon = 'assets/smds-logo.png'
        return sm

if __name__ == '__main__':
    Application().run()
