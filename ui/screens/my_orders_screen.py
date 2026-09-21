from kivy.metrics import dp

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, RoundedRectangle

from models.order import Order


class MyOrderRow(BoxLayout):
    def __init__(self, order, on_confirm, **kwargs):
        super().__init__(orientation="vertical", padding=dp(10), spacing=dp(6), **kwargs)
        self.order = order

        extra_height = 0
        if order.get("fraud_report_available"):
            extra_height = dp(90)
        elif order.get("can_confirm_delivery") and order.get("status") == "delivered":
            extra_height = dp(46)

        self.size_hint_y = None
        self.height = dp(140) + extra_height

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(10)])
        self.bind(size=self.update_bg, pos=self.update_bg)

        top_row = BoxLayout(size_hint=(1, None), height=dp(30))
        top_row.add_widget(Label(
            text=f"Order #{order['id']} - {order['store_name']}",
            color=(0.1, 0.1, 0.1, 1), font_size="14sp", bold=True
        ))
        top_row.add_widget(Label(text=f"${order['total_amount']}", color=(0.3, 0.5, 0.9, 1), font_size="14sp"))
        self.add_widget(top_row)

        items_text = ", ".join(f"{item['name']} x{item['quantity']}" for item in order["items"])
        self.add_widget(Label(text=items_text, color=(0.4, 0.4, 0.4, 1), font_size="11sp", size_hint=(1, None), height=dp(30)))

        status_colors = {
            "pending": (0.7, 0.6, 0.2, 1), "confirmed": (0.3, 0.5, 0.9, 1),
            "shipped": (0.4, 0.4, 0.8, 1), "delivered": (0.2, 0.6, 0.3, 1),
            "cancelled": (0.8, 0.2, 0.2, 1),
        }
        self.add_widget(Label(
            text=f"Status: {order['status']}",
            color=status_colors.get(order["status"], (0.3, 0.3, 0.3, 1)),
            font_size="12sp", bold=True, size_hint=(1, None), height=dp(24)
        ))

        if order.get("customer_confirmed_at"):
            self.add_widget(Label(text="Delivery confirmed by you", color=(0.2, 0.6, 0.3, 1), font_size="11sp", size_hint=(1, None), height=dp(22)))
        elif order.get("status") == "delivered":
            confirm_btn = Button(
                text="Confirm I received this order", size_hint=(1, None), height=dp(40),
                background_color=(0.2, 0.6, 0.3, 1), background_normal="", color=(1, 1, 1, 1), font_size="13sp"
            )
            confirm_btn.bind(on_press=lambda instance: on_confirm(order))
            self.add_widget(confirm_btn)

        if order.get("fraud_report_available"):
            fraud_box = BoxLayout(orientation="vertical", spacing=dp(2), size_hint=(1, None), height=dp(80))
            fraud_box.add_widget(Label(
                text="No confirmation received within 3 days of delivery.\nSeller identity for fraud reporting:",
                font_size="10sp", color=(0.8, 0.2, 0.2, 1), size_hint=(1, None), height=dp(34)
            ))
            fraud_box.add_widget(Label(
                text=f"Legal name: {order.get('seller_legal_name', '')}",
                font_size="11sp", color=(0.2, 0.2, 0.2, 1), size_hint=(1, None), height=dp(22)
            ))
            fraud_box.add_widget(Label(
                text=f"National ID: {order.get('seller_national_id', '')}",
                font_size="11sp", color=(0.2, 0.2, 0.2, 1), size_hint=(1, None), height=dp(22)
            ))
            self.add_widget(fraud_box)

    def update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos


class MyOrdersScreen(Screen):
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
        header.add_widget(Label(text="My Orders", font_size="16sp", bold=True, color=(0.2, 0.3, 0.6, 1)))
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
        self.message_label.color = (0.2, 0.6, 0.3, 1)
        self.message_label.text = "Loading..."
        Order.get_all(self.on_orders_loaded)

    def on_orders_loaded(self, orders, error):
        if error:
            self.message_label.color = (0.8, 0.2, 0.2, 1)
            self.message_label.text = error
            self.orders_layout.clear_widgets()
            return
        self.message_label.color = (0.2, 0.6, 0.3, 1)
        self.message_label.text = "" if orders else "You haven't placed any orders yet"
        self.orders_layout.clear_widgets()
        for order in orders:
            self.orders_layout.add_widget(MyOrderRow(order=order, on_confirm=self.confirm_delivery))

    def confirm_delivery(self, order):
        self.message_label.color = (0.3, 0.3, 0.3, 1)
        self.message_label.text = "Confirming..."
        Order.confirm_delivery(order["id"], lambda data, status_code: self.on_confirm_result(data, status_code))

    def on_confirm_result(self, data, status_code):
        if status_code != 200:
            self.message_label.color = (0.8, 0.2, 0.2, 1)
            error_data = data if isinstance(data, dict) else {}
            self.message_label.text = str(error_data.get("error", "Error confirming delivery"))
            return
        self.message_label.color = (0.2, 0.6, 0.3, 1)
        self.message_label.text = "Delivery confirmed"
        self.load_orders()

    def go_back(self, instance):
        self.manager.current = "product_list"
