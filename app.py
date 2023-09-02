from kivymd.app import MDApp
from kivy.lang.builder import Builder
from kivymd.uix.screen import MDScreen

KV="""
<MainScreen>:
    MDBoxLayout:
        Button:
            text:"Hello"

MainScreen:
"""

class MainScreen(MDScreen):
    pass

class ChessApp(MDApp):
    def build(self):
        return Builder.load_string(KV)

if __name__ == "__main__":
    app = ChessApp()
    app.run()