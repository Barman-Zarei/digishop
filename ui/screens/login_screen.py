import json
import os

from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle

from models.user import User
from models.customer import Customer
from models.seller import Seller

SESSION_FILE = "session.json"


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(0.96, 0.97, 1, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_bg, pos=self.update_bg)

        layout = BoxLayout(orientation="vertical", padding=40, spacing=15)

        title = Label(
            text="Welcome to DigiShop",
            font_size="28sp",
            color=(0.2, 0.3, 0.6, 1),
            size_hint=(1, 0.3)
        )

        self.username_input = TextInput(
            hint_text="Username",
            multiline=False,
            size_hint=(1, 0.12),
            padding=[15, 15, 15, 15]
        )
        self.password_input = TextInput(
            hint_text="Password",
            multiline=False,
            password=True,
            size_hint=(1, 0.12),
            padding=[15, 15, 15, 15]
        )

        self.message_label = Label(
            text="",
            color=(0.8, 0.2, 0.2, 1),
            size_hint=(1, 0.1)
        )

        login_button = Button(
            text="Login",
            size_hint=(1, 0.15),
            background_color=(0.3, 0.5, 0.9, 1),
            background_normal="",
            color=(1, 1, 1, 1),
            font_size="18sp"
        )
        login_button.bind(on_press=self.on_login)

        register_link = Button(
            text="No account? Register",
            size_hint=(1, 0.1),
            background_color=(0, 0, 0, 0),
            background_normal="",
            color=(0.3, 0.4, 0.7, 1)
        )
        register_link.bind(on_press=self.go_to_register)

        layout.add_widget(title)
        layout.add_widget(self.username_input)
        layout.add_widget(self.password_input)
        layout.add_widget(login_button)
        layout.add_widget(self.message_label)
        layout.add_widget(register_link)

        self.add_widget(layout)

    def update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def on_login(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text

        if not username or not password:
            self.message_label.text = "Please enter username and password"
            return

        try:
            user = User.authenticate(username, password)

            if user is None:
                self.message_label.text = "Invalid username or password"
                return

            self.load_user_session(user)

            self.message_label.color = (0.2, 0.6, 0.3, 1)
            self.message_label.text = "Login successful"
            self.manager.current = "product_list"

        except Exception as e:
            self.message_label.color = (0.8, 0.2, 0.2, 1)
            self.message_label.text = f"Login error: {e}"

    def load_user_session(self, user):
        app = App.get_running_app()
        app.current_user = user
        app.current_customer = Customer.get_by_user_id(user["id"])
        app.current_seller = Seller.get_by_user_id(user["id"])

        with open(SESSION_FILE, "w") as f:
            json.dump({"user_id": user["id"]}, f)

    def go_to_register(self, instance):
        self.manager.current = "register"


def try_auto_login(app):
    if not os.path.exists(SESSION_FILE):
        return False

    try:
        with open(SESSION_FILE, "r") as f:
            data = json.load(f)

        user = User.get_by_id(data["user_id"])
        if user is None:
            return False

        app.current_user = user
        app.current_customer = Customer.get_by_user_id(user["id"])
        app.current_seller = Seller.get_by_user_id(user["id"])
        return True

    except Exception:
        return False


def clear_session(app):
    app.current_user = None
    app.current_customer = None
    app.current_seller = None

    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
