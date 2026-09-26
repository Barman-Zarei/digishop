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
        super().__init__(orientation="vertical", padding=dp(10), spacing=dp(4), **kwargs)
        self.order = order
        self.size_hint_y = None
        self.height = dp(230)

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(10)])
        self.bind(size=self.update_bg, pos=self.update_bg)

        top_row = BoxLayout(size_hint=(1, None), height=dp(26))
        top_row.add_widget(Label(
            text=f"Order #{order['id']} - {order['customer_name']}",
            color=(0.1, 0.1, 0.1, 1), font_size="13sp", bold=True
        ))
        top_row.add_widget(Label(text=f"{order['total_amount']} Toman", color=(0.3, 0.5, 0.9, 1), font_size="12sp"))
        self.add_widget(top_row)

        items_text = ", ".join(f"{item['name']} x{item['quantity']}" for item in order["items"])
        self.add_widget(Label(text=items_text, color=(0.4, 0.4, 0.4, 1), font_size="10sp", size_hint=(1, None), height=dp(24)))

        self.add_widget(Label(
            text=f"Ship to: {order.get('shipping_address', '-')}",
            color=(0.3, 0.3, 0.3, 1), font_size="10sp", size_hint=(1, None), height=dp(24)
        ))
        self.add_widget(Label(
            text=f"Phone: {order.get('shipping_phone', '-')}",
            color=(0.3, 0.3, 0.3, 1), font_size="10sp", size_hint=(1, None), height=dp(22)
        ))

        status_row = BoxLayout(size_hint=(1, None), height=dp(36), spacing=dp(3))
        for option in STATUS_OPTIONS:
            is_current = option == order["status"]
            btn = Button(
                text=option.capitalize(), font_size="8sp",
                background_color=(0.2, 0.6, 0.3, 1) if is_current else (0.5, 0.5, 0.8, 1),
                background_normal="", color=(1, 1, 1, 1)
            )
            btn.bind(on_press=lambda instance, option=option: on_status_change(order, option))
            status_row.add_widget(btn)
        self.add_widget(status_row)

        if order["status"] == "cancelled":
            delete_btn = Button(
                text="Remove from my list", size_hint=(1, None), height=dp(34),
                background_color=(0.8, 0.2, 0.2, 1), background_normal="", color=(1, 1, 1, 1), font_size="11sp"
            )
            delete_btn.bind(on_press=lambda instance: on_delete(order))
            self.add_widget(delete_btn)

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
        header.add_widget(Label(text="Store Orders", font_size="16sp", bold=True, color=(0.2, 0.3, 0.6, 1)))
        outer.add_widget(header)

        self.message_label = Label(text="", color=(0.8, 0.2, 0.2, 1), size_hint=(1, None), height=dp(24), font_size="13sp")
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
        self.message_label.color = (0.3, 0.3, 0.3, 1)
        self.message_label.text = "Loading..."
        Order.get_seller_orders(self.on_orders_loaded)

    def on_orders_loaded(self, orders, error):
        if error:
            self.message_label.color = (0.8, 0.2, 0.2, 1)
            self.message_label.text = error
            self.orders_layout.clear_widgets()
            return
        self.message_label.text = "" if orders else "No orders yet"
        self.orders_layout.clear_widgets()
        for order in orders:
            self.orders_layout.add_widget(SellerOrderRow(
                order=order, on_status_change=self.change_status, on_delete=self.delete_order
            ))

    def show_error(self, text):
        self.message_label.color = (0.8, 0.2, 0.2, 1)
        self.message_label.text = text

    def change_status(self, order, new_status):
        if new_status == order["status"]:
            return

        def on_result(data, status_code):
            if status_code != 200:
                error_data = data if isinstance(data, dict) else {}
                self.show_error(str(error_data.get("error", "Could not update status")))
                return
            self.message_label.color = (0.2, 0.6, 0.3, 1)
            self.message_label.text = ""
            self.load_orders()

        Order.update_status(order["id"], new_status, on_result)

    def delete_order(self, order):
        def on_result(success):
            if not success:
                self.show_error("Could not remove this order")
                return
            self.load_orders()

        Order.delete(order["id"], on_result)

    def go_back(self, instance):
        self.manager.current = "product_list"
