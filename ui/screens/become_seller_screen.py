from kivy.metrics import dp

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle

from models.user import User


class BecomeSellerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(0.96, 0.97, 1, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_bg, pos=self.update_bg)

        outer = BoxLayout(orientation="vertical", padding=dp(25), spacing=dp(10))

        header = BoxLayout(size_hint=(1, None), height=dp(44))
        back_button = Button(text="< Back", size_hint=(0.3, 1), background_color=(0, 0, 0, 0), background_normal="", color=(0.3, 0.4, 0.7, 1), font_size="14sp")
        back_button.bind(on_press=self.go_back)
        header.add_widget(back_button)
        header.add_widget(Label(text="Become a Seller", font_size="18sp", bold=True, color=(0.2, 0.3, 0.6, 1)))
        outer.add_widget(header)

        scroll = ScrollView(size_hint=(1, 1))
        form = BoxLayout(orientation="vertical", spacing=dp(12), size_hint_y=None)
        form.bind(minimum_height=form.setter("height"))

        input_style = {"multiline": False, "size_hint_y": None, "height": dp(52), "padding": [dp(15)] * 4, "font_size": "15sp"}

        self.store_name_input = TextInput(hint_text="Store Name", **input_style)
        self.phone_input = TextInput(hint_text="Phone", input_filter="int", **input_style)
        self.national_id_input = TextInput(hint_text="National ID (10 digits)", input_filter="int", **input_style)
        self.legal_name_input = TextInput(hint_text="Full Legal Name (as on your ID card)", **input_style)
        self.bank_account_input = TextInput(hint_text="Bank Account / IBAN Number", **input_style)

        note = Label(
            text="Your identity details are only shown to a buyer if you report an\n"
                 "order as delivered and they do not confirm receipt within 3 days.",
            font_size="11sp", color=(0.5, 0.5, 0.5, 1), size_hint_y=None, height=dp(50)
        )

        for widget in (self.store_name_input, self.phone_input, self.national_id_input,
                       self.legal_name_input, self.bank_account_input, note):
            form.add_widget(widget)

        scroll.add_widget(form)
        outer.add_widget(scroll)

        self.message_label = Label(text="", color=(0.8, 0.2, 0.2, 1), size_hint=(1, None), height=dp(24), font_size="13sp")
        outer.add_widget(self.message_label)

        self.submit_button = Button(
            text="Become a Seller", size_hint=(1, None), height=dp(52),
            background_color=(0.3, 0.7, 0.4, 1), background_normal="", color=(1, 1, 1, 1), font_size="16sp"
        )
        self.submit_button.bind(on_press=self.on_submit)
        outer.add_widget(self.submit_button)

        self.add_widget(outer)

    def update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def validate(self):
        if not self.store_name_input.text.strip():
            return "Please enter a store name"
        if len(self.phone_input.text.strip()) < 8:
            return "Please enter a valid phone number"
        if len(self.national_id_input.text.strip()) != 10:
            return "National ID must be exactly 10 digits"
        if len(self.legal_name_input.text.strip()) < 3:
            return "Please enter your full legal name"
        if len(self.bank_account_input.text.strip()) < 10:
            return "Please enter a valid bank account number"
        return None

    def on_submit(self, instance):
        error = self.validate()
        if error:
            self.message_label.text = error
            return

        self.submit_button.disabled = True
        self.message_label.color = (0.3, 0.3, 0.3, 1)
        self.message_label.text = "Submitting..."

        User.become_seller(
            store_name=self.store_name_input.text.strip(),
            phone=self.phone_input.text.strip(),
            national_id=self.national_id_input.text.strip(),
            legal_full_name=self.legal_name_input.text.strip(),
            bank_account_number=self.bank_account_input.text.strip(),
            callback=self.on_result
        )

    def on_result(self, data, status_code):
        self.submit_button.disabled = False
        if status_code != 201:
            self.message_label.color = (0.8, 0.2, 0.2, 1)
            error_data = data if isinstance(data, dict) else {}
            self.message_label.text = str(error_data.get("error", data))
            return
        self.message_label.color = (0.2, 0.6, 0.3, 1)
        self.message_label.text = "You are now a seller!"
        self.manager.current = "add_product"

    def go_back(self, instance):
        self.manager.current = "product_list"
