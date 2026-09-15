from kivy.metrics import dp

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, RoundedRectangle

from models.order import Order

STATUS_OPTIONS = ["pending", "confirmed", "shipped", "delivered", "cancelled"]


class SellerOrderRow(BoxLayout):
    def __init__(self, order, on_status_change, on_delete, **kwargs):
        super().__init__(orientation="vertical", padding=dp(10), spacing=dp(6), **kwargs)
        self.order = order
        self.size_hint_y = None
        self.height = dp(160)

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(10)])
        self.bind(size=self.update_bg, pos=self.update_bg)

        top_row = BoxLayout(size_hint=(1, 0.3))
        top_row.add_widget(Label(
            text=f"Order #{order['id']} - {order['customer_name']}",
            color=(0.1, 0.1, 0.1, 1), font_size="14sp", bold=True
        ))
        top_row.add_widget(Label(text=f"${order['total_amount']}", color=(0.3, 0.5, 0.9, 1), font_size="14sp"))
        self.add_widget(top_row)

        items_text = ", ".join(f"{item['name']} x{item['quantity']}" for item in order["items"])
        self.add_widget(Label(text=items_text, color=(0.4, 0.4, 0.4, 1), font_size="11sp", size_hint=(1, 0.25)))

        status_row = BoxLayout(size_hint=(1, 0.45), spacing=dp(6))
        status_row.add_widget(Label(text=f"Status: {order['status']}", color=(0.2, 0.2, 0.2, 1), size_hint=(0.4, 1), font_size="11sp"))

        for option in STATUS_OPTIONS:
            btn = Button(
                text=option[:4].capitalize(),
                background_color=(0.5, 0.5, 0.8, 1) if option != order["status"] else (0.2, 0.6, 0.3, 1),
                background_normal="", color=(1, 1, 1, 1), font_size="10sp"
            )
            btn.bind(on_press=lambda instance, opt=option: on_status_change(order, opt))
            status_row.add_widget(btn)

        delete_button = Button(text="Delete", size_hint=(0.3, 1), background_color=(0.8, 0.3, 0.3, 1), background_normal="", color=(1, 1, 1, 1), font_size="11sp")
        delete_button.bind(on_press=lambda instance: on_delete(order))
        status_row.add_widget(delete_button)

        self.add_widget(status_row)

    def update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos


class SellerOrdersScreen(Screen):
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
        header.add_widget(Label(text="My Store Orders", font_size="16sp", bold=True, color=(0.2, 0.3, 0.6, 1)))
        outer.add_widget(header)

        self.message_label = Label(text="", color=(0.2, 0.6, 0.3, 1), size_hint=(1, None), height=dp(24), font_size="13sp")
        outer.add_widget(self.message_label)

        scroll = ScrollView(size_hint=(1, 1))
        self.orders_layout = BoxLayout(orientation="vertical", spacing=dp(10), size_hint_y=None, padding=[0, dp(5), 0, dp(5)])
        self.orders_layout.bind(minimum_height=self.orders_layout.setter("height"))
        scroll.add_widget(self.orders_layout)
        outer.add_widget(scroll)

        self.add_widget(outer)

    def update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def on_pre_enter(self, *args):
        self.load_orders()

    def load_orders(self):
        self.message_label.text = "Loading..."
        Order.get_seller_orders(self.on_orders_loaded)

    def on_orders_loaded(self, orders):
        self.message_label.text = "" if orders else "No orders yet"
        self.orders_layout.clear_widgets()

        for order in orders:
            row = SellerOrderRow(order=order, on_status_change=self.change_status, on_delete=self.delete_order)
            self.orders_layout.add_widget(row)

    def change_status(self, order, new_status):
        Order.update_status(order["id"], new_status, lambda data, status_code: self.load_orders())

    def delete_order(self, order):
        Order.delete(order["id"], lambda success: self.load_orders())

    def go_back(self, instance):
        self.manager.current = "product_list"
