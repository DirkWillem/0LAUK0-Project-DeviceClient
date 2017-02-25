import kivy
from kivy.app import App
from kivy.config import Config
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen

from screens.home import HomeScreen

from config import AppConfig

kivy.require('1.9.1')

# Set display settings from config
cfg = AppConfig()

Config.set('graphics', 'width', cfg.display.width)
Config.set('graphics', 'height', cfg.display.height)

# Initialize screen manager
sm = ScreenManager()
sm.add_widget(HomeScreen())

# Load UI file
Builder.load_file("./main.kv")


class Application(App):
    def build(self):
        return sm

if __name__ == '__main__':
    Application().run()
