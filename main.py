import kivy
from kivy.app import App
from kivy.config import Config
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen

from screens.home import HomeScreen

kivy.require('1.9.1')

Builder.load_file("./main.kv")
Config.set('graphics', 'width', 480)
Config.set('graphics', 'height', 320)

sm = ScreenManager()
sm.add_widget(HomeScreen())


class Application(App):
    def build(self):
        return sm

if __name__ == '__main__':
    Application().run()
