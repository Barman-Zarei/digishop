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
    def __init__(self, item, on_change_quantity, on_remove, **kwargs):
        super().__init__(orientation="horizontal", padding=dp(10), spacing=dp(8), **kwargs)
        self.item = item
        self.size_hint_y = None
        self.height = dp(70)

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(8)])
        self.bind(size=self.update_bg, pos=self.update_bg)

        info_box = BoxLayout(orientation="vertical", size_hint=(0.5, 1))
        info_box.add_widget(Label(text=item["name"], color=(0.1, 0.1, 0.1, 1), font_size="13sp", bold=True))
        info_box.add_widget(Label(
            text=f"{float(item['price']):,.0f} Toman", color=(0.3, 0.5, 0.9, 1), font_size="12sp"
        ))
        self.add_widget(info_box)

        qty_box = BoxLayout(size_hint=(0.3, 1), spacing=dp(4))
        minus_btn = Button(text="-", background_color=(0.7, 0.3, 0.3, 1), background_normal="", color=(1, 1, 1, 1))
        minus_btn.bind(on_press=lambda instance: on_change_quantity(item, -1))
        qty_box.add_widget(minus_btn)
        qty_box.add_widget(Label(text=str(item["quantity"]), color=(0.1, 0.1, 0.1, 1), font_size="14sp"))
        plus_btn = Button(text="+", background_color=(0.3, 0.6, 0.3, 1), background_normal="", color=(1, 1, 1, 1))
        plus_btn.bind(on_press=lambda instance: on_change_quantity(item, 1))
        qty_box.add_widget(plus_btn)
        self.add_widget(qty_box)

        remove_btn = Button(
            text="Remove", size_hint=(0.2, 1), background_color=(0.8, 0.2, 0.2, 1),
            background_normal="", color=(1, 1, 1, 1), font_size="11sp"
        )
        remove_btn.bind(on_press=lambda instance: on_remove(item))
        self.add_widget(remove_btn)

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
        self.items_layout = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None, padding=[0, dp(5), 0, dp(5)])
        self.items_layout.bind(minimum_height=self.items_layout.setter("height"))
        scroll.add_widget(self.items_layout)
        outer.add_widget(scroll)

        self.total_label = Label(text="Total: 0 Toman", font_size="16sp", bold=True, color=(0.1, 0.1, 0.1, 1), size_hint=(1, None), height=dp(30))
        outer.add_widget(self.total_label)

        self.checkout_button = Button(
            text="Checkout", size_hint=(1, None), height=dp(50),
            background_color=(0.2, 0.6, 0.3, 1), background_normal="", color=(1, 1, 1, 1), font_size="15sp"
        )
        self.checkout_button.bind(on_press=self.go_to_checkout)
        outer.add_widget(self.checkout_button)

        self.add_widget(outer)

    def update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def on_pre_enter(self, *args):
        self.load_cart()

    def load_cart(self):
        if not client.is_logged_in():
            self.message_label.text = "Please login first"
            return
        self.message_label.text = ""
        CartItem.get_cart(self.on_cart_loaded)

    def on_cart_loaded(self, items, error):
        if error:
            self.message_label.color = (0.8, 0.2, 0.2, 1)
            self.message_label.text = error
            self.items_layout.clear_widgets()
            self.total_label.text = "Total: 0 Toman"
            return

        self.message_label.text = "" if items else "Your cart is empty"
        self.items_layout.clear_widgets()
        total = 0
        for item in items:
            self.items_layout.add_widget(CartRow(
                item=item, on_change_quantity=self.change_quantity, on_remove=self.remove_item
            ))
            total += float(item["price"]) * item["quantity"]
        self.total_label.text = f"Total: {total:,.0f} Toman"
        self.checkout_button.disabled = not items

    def _disable_rows(self, disabled):
        for row in self.items_layout.children:
            row.disabled = disabled

    def change_quantity(self, item, delta):
        new_quantity = item["quantity"] + delta
        if new_quantity < 1:
            self.remove_item(item)
            return

        self._disable_rows(True)

        def on_result(data, status_code):
            self._disable_rows(False)
            if status_code != 200:
                self.message_label.color = (0.8, 0.2, 0.2, 1)
                error_data = data if isinstance(data, dict) else {}
                self.message_label.text = str(error_data.get("error", "Could not update quantity"))
            self.load_cart()

        CartItem.update_quantity(item["id"], new_quantity, on_result)

    def remove_item(self, item):
        self._disable_rows(True)

        def on_result(success):
            if not success:
                self._disable_rows(False)
                self.message_label.color = (0.8, 0.2, 0.2, 1)
                self.message_label.text = "Error removing item"
                return
            self.load_cart()

        CartItem.remove(item["id"], on_result)

    def go_to_checkout(self, instance):
        self.manager.current = "checkout"

    def go_back(self, instance):
        self.manager.current = "product_list"
