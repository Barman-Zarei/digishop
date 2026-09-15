from kivy.metrics import dp

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle

from models.user import User


class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(0.96, 0.97, 1, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_bg, pos=self.update_bg)

        outer = BoxLayout(orientation="vertical", padding=dp(30), spacing=dp(10))

        title = Label(text="Create Account", font_size="26sp", color=(0.2, 0.3, 0.6, 1), size_hint=(1, 0.15))
        outer.add_widget(title)

        scroll = ScrollView(size_hint=(1, 0.75))
        form = BoxLayout(orientation="vertical", spacing=dp(12), size_hint_y=None, padding=[0, dp(10), 0, dp(10)])
        form.bind(minimum_height=form.setter("height"))

        input_style = {
            "multiline": False,
            "size_hint_y": None,
            "height": dp(56),
            "padding": [dp(15), dp(15), dp(15), dp(15)],
            "font_size": "16sp",
        }

        self.username_input = TextInput(hint_text="Username", **input_style)
        self.password_input = TextInput(hint_text="Password", password=True, **input_style)
        self.email_input = TextInput(hint_text="Email", **input_style)
        self.fullname_input = TextInput(hint_text="Full Name", **input_style)
        self.address_input = TextInput(hint_text="Address", **input_style)
        self.phone_input = TextInput(hint_text="Phone", **input_style)

        for widget in (self.username_input, self.password_input, self.email_input,
                       self.fullname_input, self.address_input, self.phone_input):
            form.add_widget(widget)

        scroll.add_widget(form)
        outer.add_widget(scroll)

        self.message_label = Label(text="", color=(0.8, 0.2, 0.2, 1), size_hint=(1, 0.1))
        outer.add_widget(self.message_label)

        self.register_button = Button(
            text="Register", size_hint=(1, 0.15),
            background_color=(0.3, 0.7, 0.4, 1), background_normal="", color=(1, 1, 1, 1), font_size="18sp"
        )
        self.register_button.bind(on_press=self.on_register)
        outer.add_widget(self.register_button)

        login_link = Button(
            text="Have an account? Login", size_hint=(1, 0.1),
            background_color=(0, 0, 0, 0), background_normal="", color=(0.3, 0.4, 0.7, 1)
        )
        login_link.bind(on_press=self.go_to_login)
        outer.add_widget(login_link)

        self.add_widget(outer)

    def update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def validate_inputs(self):
        if not self.username_input.text.strip():
            return "Username cannot be empty"
        if not self.password_input.text.strip():
            return "Password cannot be empty"
        if not self.fullname_input.text.strip():
            return "Full name cannot be empty"
        return None

    def on_register(self, instance):
        error = self.validate_inputs()
        if error:
            self.message_label.color = (0.8, 0.2, 0.2, 1)
            self.message_label.text = error
            return

        self.register_button.disabled = True
        self.message_label.color = (0.3, 0.3, 0.3, 1)
        self.message_label.text = "Registering..."

        User.register(
            username=self.username_input.text.strip(),
            password=self.password_input.text,
            full_name=self.fullname_input.text.strip(),
            email=self.email_input.text.strip(),
            phone=self.phone_input.text.strip(),
            address=self.address_input.text.strip(),
            callback=self.on_register_result
        )

    def on_register_result(self, data, status_code):
        self.register_button.disabled = False

        if status_code != 201:
            self.message_label.color = (0.8, 0.2, 0.2, 1)
            self.message_label.text = str(data)
            return

        self.message_label.color = (0.2, 0.6, 0.3, 1)
        self.message_label.text = "Registration successful!"
        self.manager.current = "product_list"

    def go_to_login(self, instance):
        self.manager.current = "login"
