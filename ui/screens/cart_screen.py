from kivy.metrics import dp

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, RoundedRectangle

from models.cart import CartItem
from api import client


class CartRow(BoxLayout):
    def __init__(self, item, on_remove, on_quantity_change, **kwargs):
        super().__init__(orientation="horizontal", padding=dp(10), spacing=dp(10), **kwargs)
        self.item = item
        self.size_hint_y = None
        self.height = dp(80)

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(10)])
        self.bind(size=self.update_bg, pos=self.update_bg)

        info = BoxLayout(orientation="vertical", size_hint=(0.5, 1))
        info.add_widget(Label(text=item["name"], color=(0.1, 0.1, 0.1, 1), font_size="14sp", bold=True))
        info.add_widget(Label(text=f"${item['price']} x {item['quantity']}", color=(0.4, 0.4, 0.4, 1), font_size="12sp"))

        at_max_stock = item["quantity"] >= item.get("stock_quantity", item["quantity"])

        minus_button = Button(text="-", size_hint=(0.12, 1), background_color=(0.85, 0.85, 0.85, 1), background_normal="", color=(0.1, 0.1, 0.1, 1), font_size="16sp")
        minus_button.bind(on_press=lambda instance: on_quantity_change(item, -1))

        plus_button = Button(
            text="+", size_hint=(0.12, 1),
            background_color=(0.75, 0.75, 0.75, 1) if at_max_stock else (0.85, 0.85, 0.85, 1),
            background_normal="", color=(0.1, 0.1, 0.1, 1), font_size="16sp",
            disabled=at_max_stock
        )
        plus_button.bind(on_press=lambda instance: on_quantity_change(item, 1))

        remove_button = Button(text="Remove", size_hint=(0.26, 1), background_color=(0.9, 0.3, 0.3, 1), background_normal="", color=(1, 1, 1, 1), font_size="12sp")
        remove_button.bind(on_press=lambda instance: on_remove(item))

        self.add_widget(info)
        self.add_widget(minus_button)
        self.add_widget(plus_button)
        self.add_widget(remove_button)

    def update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos


class CartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(0.96, 0.97, 1, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_bg, pos=self.update_bg)

        outer = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))

        header = BoxLayout(size_hint=(1, None), height=dp(44))
        back_button = Button(text="< Back", size_hint=(0.3, 1), background_color=(0, 0, 0, 0), background_normal="", color=(0.3, 0.4, 0.7, 1), font_size="14sp")
        back_button.bind(on_press=self.go_back)
        header.add_widget(back_button)
        header.add_widget(Label(text="My Cart", font_size="18sp", bold=True, color=(0.2, 0.3, 0.6, 1)))
        outer.add_widget(header)

        self.message_label = Label(text="", color=(0.8, 0.2, 0.2, 1), size_hint=(1, None), height=dp(24), font_size="13sp")
        outer.add_widget(self.message_label)

        scroll = ScrollView(size_hint=(1, 1))
        self.items_layout = BoxLayout(orientation="vertical", spacing=dp(10), size_hint_y=None, padding=[0, dp(5), 0, dp(5)])
        self.items_layout.bind(minimum_height=self.items_layout.setter("height"))
        scroll.add_widget(self.items_layout)
        outer.add_widget(scroll)

        self.total_label = Label(text="Total: $0", font_size="17sp", bold=True, color=(0.1, 0.1, 0.1, 1), size_hint=(1, None), height=dp(34))
        outer.add_widget(self.total_label)

        checkout_button = Button(
            text="Checkout", size_hint=(1, None), height=dp(50),
            background_color=(0.3, 0.7, 0.4, 1), background_normal="", color=(1, 1, 1, 1), font_size="16sp"
        )
        checkout_button.bind(on_press=self.go_to_checkout)
        outer.add_widget(checkout_button)

        self.add_widget(outer)

    def update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def on_pre_enter(self, *args):
        self.load_cart()

    def load_cart(self):
        self.items_layout.clear_widgets()

        if not client.is_logged_in():
            self.message_label.color = (0.8, 0.2, 0.2, 1)
            self.message_label.text = "Please login first"
            self.total_label.text = "Total: $0"
            return

        self.message_label.color = (0.2, 0.6, 0.3, 1)
        self.message_label.text = "Loading..."
        CartItem.get_cart(self.on_cart_loaded)

    def on_cart_loaded(self, cart_items, error):
        self.items_layout.clear_widgets()

        if error:
            self.message_label.color = (0.8, 0.2, 0.2, 1)
            self.message_label.text = error
            self.total_label.text = "Total: $0"
            return

        self.message_label.text = ""

        total = 0
        for item in cart_items:
            row = CartRow(item=item, on_remove=self.remove_item, on_quantity_change=self.change_quantity)
            self.items_layout.add_widget(row)
            total += float(item["price"]) * item["quantity"]

        self.total_label.text = f"Total: ${total:.2f}"

    def remove_item(self, item):
        CartItem.remove(item["id"], lambda success: self.load_cart())

    def change_quantity(self, item, delta):
        new_quantity = item["quantity"] + delta
        if new_quantity < 1:
            self.remove_item(item)
            return

        def on_result(data, status_code):
            if status_code != 200:
                self.message_label.color = (0.8, 0.2, 0.2, 1)
                error_data = data if isinstance(data, dict) else {}
                self.message_label.text = str(error_data.get("error", "Could not update quantity"))
            self.load_cart()

        CartItem.update_quantity(item["id"], new_quantity, on_result)

    def go_to_checkout(self, instance):
        self.manager.current = "checkout"

    def go_back(self, instance):
        self.manager.current = "product_list"
