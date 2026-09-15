from kivy.metrics import dp

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle

from models.cart import CartItem
from models.order import Order
from api import client


class CheckoutScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cart_items = []

        with self.canvas.before:
            Color(0.96, 0.97, 1, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_bg, pos=self.update_bg)

        outer = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))

        header = BoxLayout(size_hint=(1, None), height=dp(44))
        back_button = Button(text="< Back", size_hint=(0.3, 1), background_color=(0, 0, 0, 0), background_normal="", color=(0.3, 0.4, 0.7, 1), font_size="14sp")
        back_button.bind(on_press=self.go_back)
        header.add_widget(back_button)
        header.add_widget(Label(text="Checkout", font_size="18sp", bold=True, color=(0.2, 0.3, 0.6, 1)))
        outer.add_widget(header)

        scroll = ScrollView(size_hint=(1, 1))
        self.summary_layout = BoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None, padding=[0, dp(5), 0, dp(5)])
        self.summary_layout.bind(minimum_height=self.summary_layout.setter("height"))
        scroll.add_widget(self.summary_layout)
        outer.add_widget(scroll)

        self.total_label = Label(text="Total: $0", font_size="17sp", bold=True, color=(0.1, 0.1, 0.1, 1), size_hint=(1, None), height=dp(34))
        outer.add_widget(self.total_label)

        self.message_label = Label(text="", color=(0.8, 0.2, 0.2, 1), size_hint=(1, None), height=dp(24), font_size="13sp")
        outer.add_widget(self.message_label)

        self.place_order_button = Button(
            text="Place Order", size_hint=(1, None), height=dp(52),
            background_color=(0.3, 0.7, 0.4, 1), background_normal="", color=(1, 1, 1, 1), font_size="16sp"
        )
        self.place_order_button.bind(on_press=self.place_order)
        outer.add_widget(self.place_order_button)

        self.add_widget(outer)

    def update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def on_pre_enter(self, *args):
        self.load_summary()

    def load_summary(self):
        self.summary_layout.clear_widgets()
        self.message_label.text = ""

        if not client.is_logged_in():
            self.message_label.text = "Please login first"
            return

        self.message_label.text = "Loading..."
        CartItem.get_cart(self.on_summary_loaded)

    def on_summary_loaded(self, cart_items):
        self.message_label.text = ""
        self.cart_items = cart_items
        self.summary_layout.clear_widgets()

        total = 0
        for item in cart_items:
            row_text = f"{item['name']}  x{item['quantity']}  -  ${float(item['price']) * item['quantity']:.2f}"
            self.summary_layout.add_widget(Label(text=row_text, color=(0.2, 0.2, 0.2, 1), size_hint_y=None, height=dp(30), font_size="13sp"))
            total += float(item["price"]) * item["quantity"]

        self.total_label.text = f"Total: ${total:.2f}"

    def place_order(self, instance):
        if not client.is_logged_in():
            self.message_label.text = "Please login first"
            return

        if not self.cart_items:
            self.message_label.text = "Your cart is empty"
            return

        self.place_order_button.disabled = True
        self.message_label.color = (0.3, 0.3, 0.3, 1)
        self.message_label.text = "Placing order..."

        Order.create(self.on_order_placed)

    def on_order_placed(self, data, status_code):
        self.place_order_button.disabled = False

        if status_code != 201:
            self.message_label.color = (0.8, 0.2, 0.2, 1)
            self.message_label.text = str(data.get("error", "Error placing order"))
            return

        order_ids = [order["id"] for order in data]
        self.show_confirmation_popup(order_ids)

    def show_confirmation_popup(self, order_ids):
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(15))
        content.add_widget(Label(
            text=f"Order placed successfully!\nOrder ID(s): {', '.join(str(i) for i in order_ids)}",
            color=(0.1, 0.1, 0.1, 1)
        ))

        close_button = Button(text="OK", size_hint=(1, 0.4), background_color=(0.3, 0.5, 0.9, 1), background_normal="", color=(1, 1, 1, 1))
        content.add_widget(close_button)

        popup = Popup(title="Success", content=content, size_hint=(0.8, 0.4), auto_dismiss=False)
        close_button.bind(on_press=lambda instance: self.on_popup_close(popup))
        popup.open()

    def on_popup_close(self, popup):
        popup.dismiss()
        self.manager.current = "product_list"

    def go_back(self, instance):
        self.manager.current = "cart"
