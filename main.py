import utils.persian_patch  # noqa: F401  (must stay first)

from kivy.lang import Builder

from ui.app import DigiShopApp

Builder.load_file("ui/persian_style.kv")

if __name__ == "__main__":
    DigiShopApp().run()
