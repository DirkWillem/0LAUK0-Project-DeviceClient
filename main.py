import kivy
from kivy.config import Config
from config import AppConfig

cfg = AppConfig()

kivy.require('1.9.1')

# Set display settings from config
Config.set('graphics', 'width', cfg.display.width)
Config.set('graphics', 'height', cfg.display.height)
Config.set('kivy', 'keyboard_mode', 'dock')


from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager

from screens.home import HomeScreen
from screens.connecting import ConnectingScreen
from screens.settings import SettingsScreen
from screens.history import HistoryScreen



# Load UI file
Builder.load_file("./main.kv")

# Initialize screen manager
sm = ScreenManager()
sm.add_widget(ConnectingScreen(sm, name='Connecting'))
sm.add_widget(HomeScreen(sm, name='Home'))
sm.add_widget(SettingsScreen(sm, name='Settings'))
sm.add_widget(HistoryScreen(sm, name='History'))


class Application(App):
    def build(self):
        self.icon = 'assets/smds-logo.png'
        self.title = 'DeviceClient'
        return sm

if __name__ == '__main__':
    Application().run()
