from kivy.metrics import dp

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.graphics import Color, Rectangle, RoundedRectangle

from models.product import Product
from models.cart import CartItem
from models.user import User
from api import client


class ProductCard(BoxLayout):
    def __init__(self, product, on_card_press, on_add_press, **kwargs):
        super().__init__(orientation="vertical", padding=dp(10), spacing=dp(6), **kwargs)
        self.product = product
        self.size_hint_y = None
        self.height = dp(260)

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(12)])
        self.bind(size=self.update_bg, pos=self.update_bg)

        image_path = product.get("image_path") or "assets/no_image.png"
        image = AsyncImage(source=image_path, size_hint=(1, 0.5), fit_mode="contain")

        name_label = Label(
            text=product["name"], font_size="15sp", color=(0.1, 0.1, 0.1, 1),
            size_hint=(1, 0.15), bold=True, text_size=(None, None), shorten=True, shorten_from="right"
        )
        out_of_stock = product.get("stock_quantity", 0) <= 0
        price_text = f"Toman {product['price']}" + ("  (Out of stock)" if out_of_stock else "")
        price_label = Label(
            text=price_text, font_size="13sp",
            color=(0.8, 0.2, 0.2, 1) if out_of_stock else (0.3, 0.5, 0.9, 1),
            size_hint=(1, 0.12)
        )

        buttons_row = BoxLayout(size_hint=(1, 0.23), spacing=dp(6))

        view_button = Button(text="View", background_color=(0.3, 0.4, 0.7, 1), background_normal="", color=(1, 1, 1, 1), font_size="13sp")
        view_button.bind(on_press=lambda instance: on_card_press(product))

        self.add_button = Button(
            text="Out of stock" if out_of_stock else "Add to Cart",
            background_color=(0.7, 0.7, 0.7, 1) if out_of_stock else (0.3, 0.7, 0.4, 1),
            background_normal="", color=(1, 1, 1, 1), font_size="13sp",
            disabled=out_of_stock
        )
        self.add_button.bind(on_press=lambda instance: on_add_press(product, self.add_button))

        buttons_row.add_widget(view_button)
        buttons_row.add_widget(self.add_button)

        self.add_widget(image)
        self.add_widget(name_label)
        self.add_widget(price_label)
        self.add_widget(buttons_row)

    def update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos


class ProductListScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_search = None
        self.current_min_price = None
        self.current_max_price = None
        self._request_token = 0


        with self.canvas.before:
            Color(0.96, 0.97, 1, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_bg, pos=self.update_bg)

        outer = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))

        header = BoxLayout(size_hint=(1, None), height=dp(44), spacing=dp(6))
        my_orders_button = Button(text="My Buys", size_hint=(0.18, 1), background_color=(0.5, 0.6, 0.9, 1), background_normal="", color=(1, 1, 1, 1), font_size="11sp")
        my_orders_button.bind(on_press=lambda instance: setattr(self.manager, "current", "my_orders"))
        header.add_widget(my_orders_button)
        title = Label(text="DigiShop", font_size="18sp", color=(0.2, 0.3, 0.6, 1), bold=True)
        sell_button = Button(text="Sell", size_hint=(0.18, 1), background_color=(0.6, 0.4, 0.8, 1), background_normal="", color=(1, 1, 1, 1), font_size="12sp")
        sell_button.bind(on_press=self.go_to_sell)
        orders_button = Button(text="Orders", size_hint=(0.2, 1), background_color=(0.5, 0.5, 0.9, 1), background_normal="", color=(1, 1, 1, 1), font_size="12sp")
        orders_button.bind(on_press=self.go_to_orders)
        cart_button = Button(text="Cart", size_hint=(0.18, 1), background_color=(0.9, 0.6, 0.2, 1), background_normal="", color=(1, 1, 1, 1), font_size="12sp")
        cart_button.bind(on_press=self.go_to_cart)
        logout_button = Button(text="Logout", size_hint=(0.18, 1), background_color=(0.8, 0.3, 0.3, 1), background_normal="", color=(1, 1, 1, 1), font_size="12sp")
        logout_button.bind(on_press=self.on_logout)
        header.add_widget(title)
        header.add_widget(sell_button)
        header.add_widget(orders_button)
        header.add_widget(cart_button)
        header.add_widget(logout_button)
        outer.add_widget(header)

        search_row = BoxLayout(size_hint=(1, None), height=dp(48), spacing=dp(6))
        self.search_input = TextInput(hint_text="Search products...", multiline=False, padding=[dp(15), dp(12)], font_size="14sp")
        self.search_input.bind(on_text_validate=self.on_search_submit)
        search_row.add_widget(self.search_input)
        outer.add_widget(search_row)

        filter_row = BoxLayout(size_hint=(1, None), height=dp(40), spacing=dp(6))
        all_button = Button(text="All", background_color=(0.3, 0.4, 0.7, 1), background_normal="", color=(1, 1, 1, 1), font_size="12sp")
        all_button.bind(on_press=self.clear_filter)
        low_price_button = Button(text="Under 5M", background_color=(0.4, 0.6, 0.5, 1), background_normal="", color=(1, 1, 1, 1), font_size="10sp")
        low_price_button.bind(on_press=lambda instance: self.filter_by_price(0, 5000000))
        mid_price_button = Button(text="5M-20M", background_color=(0.4, 0.6, 0.5, 1), background_normal="", color=(1, 1, 1, 1), font_size="10sp")
        mid_price_button.bind(on_press=lambda instance: self.filter_by_price(5000000, 20000000))
        high_price_button = Button(text="20M-50M", background_color=(0.4, 0.6, 0.5, 1), background_normal="", color=(1, 1, 1, 1), font_size="10sp")
        high_price_button.bind(on_press=lambda instance: self.filter_by_price(20000000, 50000000))
        very_high_price_button = Button(text="50M-100M", background_color=(0.4, 0.6, 0.5, 1), background_normal="", color=(1, 1, 1, 1), font_size="10sp")
        very_high_price_button.bind(on_press=lambda instance: self.filter_by_price(50000000, 100000000))
        very_very_high_price_button = Button(text="100M-250M", background_color=(0.4, 0.6, 0.5, 1), background_normal="", color=(1, 1, 1, 1), font_size="10sp")
        very_very_high_price_button.bind(on_press=lambda instance: self.filter_by_price(100000000, 250000000))
        very_very_very_high_price_button = Button(text="Over 250M", background_color=(0.4, 0.6, 0.5, 1), background_normal="", color=(1, 1, 1, 1), font_size="10sp")
        very_very_high_price_button.bind(on_press=lambda instance: self.filter_by_price(250000000, None))
        filter_row.add_widget(all_button)
        filter_row.add_widget(low_price_button)
        filter_row.add_widget(mid_price_button)
        filter_row.add_widget(high_price_button)
        filter_row.add_widget(very_high_price_button)
        filter_row.add_widget(very_very_high_price_button)
        filter_row.add_widget(very_very_very_high_price_button)
        outer.add_widget(filter_row)

        self.message_label = Label(text="", color=(0.2, 0.6, 0.3, 1), size_hint=(1, None), height=dp(24), font_size="13sp")
        outer.add_widget(self.message_label)

        scroll = ScrollView(size_hint=(1, 1))
        self.grid = GridLayout(cols=2, spacing=dp(12), padding=dp(6), size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter("height"))
        scroll.add_widget(self.grid)
        outer.add_widget(scroll)

        self.add_widget(outer)

    def update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def on_pre_enter(self, *args):
        # Reloads with whatever search/filter is still active instead of
        # silently discarding it (previously reset the search box to empty).
        self.fetch_products()

    def fetch_products(self):
        self._request_token += 1
        current_token = self._request_token
        self.message_label.text = "Loading..."
        Product.get_all(
            lambda products, error, token=current_token: self.on_products_loaded(products, error, token),
            search=self.current_search, min_price=self.current_min_price, max_price=self.current_max_price
        )

    def on_products_loaded(self, products, error, token):
        if token != self._request_token:
            return  # a newer request has already superseded this one
        if error:
            self.message_label.color = (0.8, 0.2, 0.2, 1)
            self.message_label.text = error
            self.render_products([])
            return
        self.message_label.text = ""
        self.render_products(products)

    def render_products(self, products):
        self.grid.clear_widgets()
        for product in products:
            card = ProductCard(product=product, on_card_press=self.go_to_detail, on_add_press=self.add_to_cart)
            self.grid.add_widget(card)

    def on_search_submit(self, instance):
        self.current_search = self.search_input.text.strip() or None
        self.fetch_products()

    def filter_by_price(self, min_price, max_price):
        self.current_min_price = min_price
        self.current_max_price = max_price
        self.fetch_products()

    def clear_filter(self, instance):
        self.search_input.text = ""
        self.current_search = None
        self.current_min_price = None
        self.current_max_price = None
        self.fetch_products()

    def go_to_detail(self, product):
        detail_screen = self.manager.get_screen("product_detail")
        detail_screen.set_product(product)
        self.manager.current = "product_detail"

    def add_to_cart(self, product, button):
        if not client.is_logged_in():
            self.message_label.color = (0.8, 0.2, 0.2, 1)
            self.message_label.text = "Please login first"
            return

        button.disabled = True
        CartItem.add(product["id"], 1, lambda data, status_code: self.on_add_to_cart_result(data, status_code, button))

    def on_add_to_cart_result(self, data, status_code, button):
        button.disabled = False
        if status_code != 201:
            self.message_label.color = (0.8, 0.2, 0.2, 1)
            error_data = data if isinstance(data, dict) else {}
            self.message_label.text = str(error_data.get("error", data))
            return
        self.message_label.color = (0.2, 0.6, 0.3, 1)
        self.message_label.text = "Added to cart"

    def go_to_cart(self, instance):
        self.manager.current = "cart"

    def go_to_orders(self, instance):
        if client.is_seller():
            self.manager.current = "seller_orders"
        else:
            self.manager.current = "my_orders"

    def go_to_sell(self, instance):
        if client.is_seller():
            self.manager.current = "my_products"
        else:
            self.manager.current = "become_seller"

    def on_logout(self, instance):
        User.logout()
        self.manager.current = "login"
