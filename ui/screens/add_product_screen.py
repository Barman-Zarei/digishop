from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle

from models.product import Product


class AddProductScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(0.96, 0.97, 1, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_bg, pos=self.update_bg)

        outer = BoxLayout(orientation="vertical", padding=30, spacing=12)

        header = BoxLayout(size_hint=(1, 0.1))
        back_button = Button(
            text="< Back",
            size_hint=(0.3, 1),
            background_color=(0, 0, 0, 0),
            background_normal="",
            color=(0.3, 0.4, 0.7, 1)
        )
        back_button.bind(on_press=self.go_back)
        title = Label(
            text="Add Product",
            font_size="22sp",
            bold=True,
            color=(0.2, 0.3, 0.6, 1)
        )
        header.add_widget(back_button)
        header.add_widget(title)
        outer.add_widget(header)

        self.name_input = TextInput(
            hint_text="Product Name",
            multiline=False,
            size_hint=(1, 0.1),
            padding=[15, 15, 15, 15]
        )
        self.description_input = TextInput(
            hint_text="Description",
            multiline=False,
            size_hint=(1, 0.1),
            padding=[15, 15, 15, 15]
        )
        self.price_input = TextInput(
            hint_text="Price",
            multiline=False,
            input_filter="float",
            size_hint=(1, 0.1),
            padding=[15, 15, 15, 15]
        )
        self.stock_input = TextInput(
            hint_text="Stock Quantity",
            multiline=False,
            input_filter="int",
            size_hint=(1, 0.1),
            padding=[15, 15, 15, 15]
        )
        self.image_path_input = TextInput(
            hint_text="Image Path (optional)",
            multiline=False,
            size_hint=(1, 0.1),
            padding=[15, 15, 15, 15]
        )

        outer.add_widget(self.name_input)
        outer.add_widget(self.description_input)
        outer.add_widget(self.price_input)
        outer.add_widget(self.stock_input)
        outer.add_widget(self.image_path_input)

        self.message_label = Label(
            text="",
            color=(0.8, 0.2, 0.2, 1),
            size_hint=(1, 0.08)
        )
        outer.add_widget(self.message_label)

        submit_button = Button(
            text="Add Product",
            size_hint=(1, 0.15),
            background_color=(0.3, 0.7, 0.4, 1),
            background_normal="",
            color=(1, 1, 1, 1),
            font_size="17sp"
        )
        submit_button.bind(on_press=self.on_submit)
        outer.add_widget(submit_button)

        self.add_widget(outer)

    def update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def validate_inputs(self):
        if not self.name_input.text.strip():
            return "Product name cannot be empty"
        if not self.price_input.text.strip():
            return "Price cannot be empty"
        if not self.stock_input.text.strip():
            return "Stock quantity cannot be empty"
        return None

    def on_submit(self, instance):
        app = App.get_running_app()
        seller = app.current_seller

        if seller is None:
            self.message_label.text = "You must be a seller first"
            return

        error = self.validate_inputs()
        if error:
            self.message_label.text = error
            return

        try:
            Product.create(
                seller_id=seller["id"],
                name=self.name_input.text.strip(),
                price=float(self.price_input.text),
                stock_quantity=int(self.stock_input.text),
                description=self.description_input.text.strip() or None,
                image_path=self.image_path_input.text.strip() or None
            )
            self.message_label.color = (0.2, 0.6, 0.3, 1)
            self.message_label.text = "Product added successfully"
            self.clear_form()

        except Exception as e:
            self.message_label.color = (0.8, 0.2, 0.2, 1)
            self.message_label.text = f"Error: {e}"

    def clear_form(self):
        self.name_input.text = ""
        self.description_input.text = ""
        self.price_input.text = ""
        self.stock_input.text = ""
        self.image_path_input.text = ""

    def go_back(self, instance):
        self.manager.current = "product_list"
