from kivy.metrics import dp

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle

from models.user import User


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(0.96, 0.97, 1, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_bg, pos=self.update_bg)

        layout = BoxLayout(orientation="vertical", padding=dp(40), spacing=dp(15))

        title = Label(
            text="Welcome to DigiShop", font_size="28sp",
            color=(0.2, 0.3, 0.6, 1), size_hint=(1, 0.3)
        )

        self.username_input = TextInput(
            hint_text="Username", multiline=False, size_hint=(1, None),
            height=dp(56), padding=[dp(15)] * 4, font_size="16sp"
        )
        self.password_input = TextInput(
            hint_text="Password", multiline=False, password=True, size_hint=(1, None),
            height=dp(56), padding=[dp(15)] * 4, font_size="16sp"
        )
        self.password_input.bind(on_text_validate=self.on_login)


        self.message_label = Label(text="", color=(0.8, 0.2, 0.2, 1), size_hint=(1, 0.1), font_size="14sp")

        self.login_button = Button(
            text="Login", size_hint=(1, None), height=dp(50),
            background_color=(0.3, 0.5, 0.9, 1), background_normal="", color=(1, 1, 1, 1), font_size="18sp"
        )
        self.login_button.bind(on_press=self.on_login)

        register_link = Button(
            text="No account? Register", size_hint=(1, None), height=dp(44),
            background_color=(0, 0, 0, 0), background_normal="", color=(0.3, 0.4, 0.7, 1), font_size="14sp"
        )
        register_link.bind(on_press=self.go_to_register)

        layout.add_widget(title)
        layout.add_widget(self.username_input)
        layout.add_widget(self.password_input)
        layout.add_widget(self.login_button)
        layout.add_widget(self.message_label)
        layout.add_widget(register_link)

        self.add_widget(layout)

    def update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def on_login(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text = ""

        if not username or not password:
            self.message_label.text = "Please enter username and password"
            return

        self.login_button.disabled = True
        self.message_label.color = (0.3, 0.3, 0.3, 1)
        self.message_label.text = "Logging in..."

        User.login(username, password, self.on_login_result)

    def on_login_result(self, data, status_code):
        self.login_button.disabled = False

        if status_code != 200:
            self.message_label.color = (0.8, 0.2, 0.2, 1)
            self.message_label.text = data.get("error", "Login failed")
            return

        self.message_label.color = (0.2, 0.6, 0.3, 1)
        self.message_label.text = "Login successful"
        self.manager.current = "product_list"

    def on_pre_enter(self, *args):
        self.password_input.text = ""

    def go_to_register(self, instance):
        self.manager.current = "register"
