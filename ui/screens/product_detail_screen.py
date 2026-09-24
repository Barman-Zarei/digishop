from kivy.metrics import dp

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

        outer = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(12))

        back_button = Button(text="< Back", size_hint=(1, None), height=dp(40), background_color=(0, 0, 0, 0), background_normal="", color=(0.3, 0.4, 0.7, 1), font_size="14sp")
        back_button.bind(on_press=self.go_back)
        outer.add_widget(back_button)

        self.image = AsyncImage(size_hint=(1, 0.4), fit_mode="contain")
        outer.add_widget(self.image)

        self.name_label = Label(text="", font_size="20sp", bold=True, color=(0.1, 0.1, 0.1, 1), size_hint=(1, None), height=dp(36))
        outer.add_widget(self.name_label)

        self.price_label = Label(text="", font_size="17sp", color=(0.3, 0.5, 0.9, 1), size_hint=(1, None), height=dp(30))
        outer.add_widget(self.price_label)

        self.description_label = Label(text="", font_size="13sp", color=(0.3, 0.3, 0.3, 1), size_hint=(1, 0.15))
        outer.add_widget(self.description_label)

        self.stock_label = Label(text="", font_size="12sp", color=(0.5, 0.5, 0.5, 1), size_hint=(1, None), height=dp(24))
        outer.add_widget(self.stock_label)

        quantity_row = BoxLayout(size_hint=(1, None), height=dp(48), spacing=dp(10))
        self.minus_button = Button(text="-", background_color=(0.85, 0.85, 0.85, 1), background_normal="", color=(0.1, 0.1, 0.1, 1), font_size="18sp")
        self.minus_button.bind(on_press=self.decrease_quantity)
        self.quantity_label = Label(text="1", color=(0.1, 0.1, 0.1, 1), font_size="16sp")
        self.plus_button = Button(text="+", background_color=(0.85, 0.85, 0.85, 1), background_normal="", color=(0.1, 0.1, 0.1, 1), font_size="18sp")
        self.plus_button.bind(on_press=self.increase_quantity)
        quantity_row.add_widget(self.minus_button)
        quantity_row.add_widget(self.quantity_label)
        quantity_row.add_widget(self.plus_button)
        outer.add_widget(quantity_row)

        self.message_label = Label(text="", color=(0.2, 0.6, 0.3, 1), size_hint=(1, None), height=dp(24), font_size="13sp")
        outer.add_widget(self.message_label)

        self.add_button = Button(
            text="Add to Cart", size_hint=(1, None), height=dp(52),
            background_color=(0.3, 0.7, 0.4, 1), background_normal="", color=(1, 1, 1, 1), font_size="16sp"
        )
        self.add_button.bind(on_press=self.add_to_cart)
        outer.add_widget(self.add_button)

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
        self.price_label.text = f"Toman {product['price']}"
        self.description_label.text = product.get("description") or "No description available"

        in_stock = product["stock_quantity"] > 0
        self.stock_label.text = f"In stock: {product['stock_quantity']}" if in_stock else "Out of stock"
        self.stock_label.color = (0.5, 0.5, 0.5, 1) if in_stock else (0.8, 0.2, 0.2, 1)

        self.add_button.disabled = not in_stock
        self.add_button.text = "Add to Cart" if in_stock else "Out of stock"
        self.minus_button.disabled = not in_stock
        self.plus_button.disabled = not in_stock

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

        if not self.product or self.product["stock_quantity"] <= 0:
            self.message_label.color = (0.8, 0.2, 0.2, 1)
            self.message_label.text = "This product is out of stock"
            return

        self.add_button.disabled = True
        self.message_label.color = (0.3, 0.3, 0.3, 1)
        self.message_label.text = "Adding..."

        CartItem.add(self.product["id"], self.quantity, self.on_add_result)

    def on_add_result(self, data, status_code):
        self.add_button.disabled = self.product is not None and self.product["stock_quantity"] <= 0
        if status_code != 201:
            self.message_label.color = (0.8, 0.2, 0.2, 1)
            error_data = data if isinstance(data, dict) else {}
            self.message_label.text = str(error_data.get("error", data))
            return
        self.message_label.color = (0.2, 0.6, 0.3, 1)
        self.message_label.text = "Added to cart"

    def go_back(self, instance):
        self.manager.current = "product_list"
