from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
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

        outer = BoxLayout(orientation="vertical", padding=30, spacing=15)

        header = BoxLayout(size_hint=(1, 0.1))
        back_button = Button(text="< Back", size_hint=(0.3, 1), background_color=(0, 0, 0, 0), background_normal="", color=(0.3, 0.4, 0.7, 1))
        back_button.bind(on_press=self.go_back)
        header.add_widget(back_button)
        header.add_widget(Label(text="Become a Seller", font_size="22sp", bold=True, color=(0.2, 0.3, 0.6, 1)))
        outer.add_widget(header)

        self.store_name_input = TextInput(hint_text="Store Name", multiline=False, size_hint=(1, 0.12), padding=[15, 15, 15, 15])
        self.phone_input = TextInput(hint_text="Phone", multiline=False, size_hint=(1, 0.12), padding=[15, 15, 15, 15])

        outer.add_widget(self.store_name_input)
        outer.add_widget(self.phone_input)

        self.message_label = Label(text="", color=(0.8, 0.2, 0.2, 1), size_hint=(1, 0.1))
        outer.add_widget(self.message_label)

        self.submit_button = Button(
            text="Become a Seller", size_hint=(1, 0.15),
            background_color=(0.3, 0.7, 0.4, 1), background_normal="", color=(1, 1, 1, 1), font_size="17sp"
        )
        self.submit_button.bind(on_press=self.on_submit)
        outer.add_widget(self.submit_button)

        self.add_widget(outer)

    def update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def on_submit(self, instance):
        store_name = self.store_name_input.text.strip()
        if not store_name:
            self.message_label.text = "Store name cannot be empty"
            return

        self.submit_button.disabled = True
        self.message_label.color = (0.3, 0.3, 0.3, 1)
        self.message_label.text = "Submitting..."

        User.become_seller(store_name, self.phone_input.text.strip(), self.on_result)

    def on_result(self, data, status_code):
        self.submit_button.disabled = False

        if status_code != 201:
            self.message_label.color = (0.8, 0.2, 0.2, 1)
            self.message_label.text = str(data.get("error", data))
            return

        self.message_label.color = (0.2, 0.6, 0.3, 1)
        self.message_label.text = "You are now a seller!"
        self.manager.current = "add_product"

    def go_back(self, instance):
        self.manager.current = "product_list"
