from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.graphics import Color, Rectangle

from models.cart import CartItem
from api import client


class ProductDetailScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.product = None
        self.quantity = 1

        with self.canvas.before:
            Color(0.96, 0.97, 1, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_bg, pos=self.update_bg)

        outer = BoxLayout(orientation="vertical", padding=20, spacing=12)

        back_button = Button(text="< Back", size_hint=(1, 0.08), background_color=(0, 0, 0, 0), background_normal="", color=(0.3, 0.4, 0.7, 1))
        back_button.bind(on_press=self.go_back)
        outer.add_widget(back_button)

        self.image = AsyncImage(size_hint=(1, 0.4), allow_stretch=True)
        outer.add_widget(self.image)

        self.name_label = Label(text="", font_size="22sp", bold=True, color=(0.1, 0.1, 0.1, 1), size_hint=(1, 0.1))
        outer.add_widget(self.name_label)

        self.price_label = Label(text="", font_size="18sp", color=(0.3, 0.5, 0.9, 1), size_hint=(1, 0.08))
        outer.add_widget(self.price_label)

        self.description_label = Label(text="", font_size="14sp", color=(0.3, 0.3, 0.3, 1), size_hint=(1, 0.15))
        outer.add_widget(self.description_label)

        self.stock_label = Label(text="", font_size="13sp", color=(0.5, 0.5, 0.5, 1), size_hint=(1, 0.06))
        outer.add_widget(self.stock_label)

        quantity_row = BoxLayout(size_hint=(1, 0.1), spacing=10)
        minus_button = Button(text="-", background_color=(0.85, 0.85, 0.85, 1), background_normal="", color=(0.1, 0.1, 0.1, 1))
        minus_button.bind(on_press=self.decrease_quantity)
        self.quantity_label = Label(text="1", color=(0.1, 0.1, 0.1, 1))
        plus_button = Button(text="+", background_color=(0.85, 0.85, 0.85, 1), background_normal="", color=(0.1, 0.1, 0.1, 1))
        plus_button.bind(on_press=self.increase_quantity)
        quantity_row.add_widget(minus_button)
        quantity_row.add_widget(self.quantity_label)
        quantity_row.add_widget(plus_button)
        outer.add_widget(quantity_row)

        self.message_label = Label(text="", color=(0.2, 0.6, 0.3, 1), size_hint=(1, 0.06))
        outer.add_widget(self.message_label)

        add_button = Button(
            text="Add to Cart", size_hint=(1, 0.12),
            background_color=(0.3, 0.7, 0.4, 1), background_normal="", color=(1, 1, 1, 1), font_size="17sp"
        )
        add_button.bind(on_press=self.add_to_cart)
        outer.add_widget(add_button)

        self.add_widget(outer)

    def update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def set_product(self, product):
        self.product = product
        self.quantity = 1
        self.quantity_label.text = "1"
        self.message_label.text = ""

        self.image.source = product.get("image_path") or "assets/no_image.png"
        self.name_label.text = product["name"]
        self.price_label.text = f"${product['price']}"
        self.description_label.text = product.get("description") or "No description available"
        self.stock_label.text = f"In stock: {product['stock_quantity']}"

    def increase_quantity(self, instance):
        if self.product and self.quantity < self.product["stock_quantity"]:
            self.quantity += 1
            self.quantity_label.text = str(self.quantity)

    def decrease_quantity(self, instance):
        if self.quantity > 1:
            self.quantity -= 1
            self.quantity_label.text = str(self.quantity)

    def add_to_cart(self, instance):
        if not client.is_logged_in():
            self.message_label.color = (0.8, 0.2, 0.2, 1)
            self.message_label.text = "Please login first"
            return

        CartItem.add(self.product["id"], self.quantity, self.on_add_result)

    def on_add_result(self, data, status_code):
        if status_code != 201:
            self.message_label.color = (0.8, 0.2, 0.2, 1)
            self.message_label.text = str(data)
            return
        self.message_label.color = (0.2, 0.6, 0.3, 1)
        self.message_label.text = "Added to cart"

    def go_back(self, instance):
        self.manager.current = "product_list"
