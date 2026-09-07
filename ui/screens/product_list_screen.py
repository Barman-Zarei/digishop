from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle, RoundedRectangle

from models.product import Product
from models.cart import CartItem
from ui.screens.login_screen import clear_session


class ProductCard(BoxLayout):
    def __init__(self, product, on_card_press, on_add_press, **kwargs):
        super().__init__(orientation="vertical", padding=10, spacing=6, **kwargs)
        self.product = product
        self.size_hint_y = None
        self.height = 260

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[12])
        self.bind(size=self.update_bg, pos=self.update_bg)

        image_path = product.get("image_path") or "assets/no_image.png"
        image = Image(source=image_path, size_hint=(1, 0.5), allow_stretch=True)

        name_label = Label(
            text=product["name"],
            font_size="16sp",
            color=(0.1, 0.1, 0.1, 1),
            size_hint=(1, 0.15),
            bold=True
        )

        price_label = Label(
            text=f"${product['price']}",
            font_size="15sp",
            color=(0.3, 0.5, 0.9, 1),
            size_hint=(1, 0.12)
        )

        buttons_row = BoxLayout(size_hint=(1, 0.23), spacing=6)

        view_button = Button(
            text="View",
            background_color=(0.3, 0.4, 0.7, 1),
            background_normal="",
            color=(1, 1, 1, 1)
        )
        view_button.bind(on_press=lambda instance: on_card_press(product))

        add_button = Button(
            text="Add to Cart",
            background_color=(0.3, 0.7, 0.4, 1),
            background_normal="",
            color=(1, 1, 1, 1)
        )
        add_button.bind(on_press=lambda instance: on_add_press(product))

        buttons_row.add_widget(view_button)
        buttons_row.add_widget(add_button)

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
        self.all_products = []

        with self.canvas.before:
            Color(0.96, 0.97, 1, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_bg, pos=self.update_bg)

        outer = BoxLayout(orientation="vertical", padding=15, spacing=10)

        header = BoxLayout(size_hint=(1, 0.08), spacing=6)
        title = Label(
            text="DigiShop",
            font_size="22sp",
            color=(0.2, 0.3, 0.6, 1),
            bold=True
        )
        sell_button = Button(
            text="Sell",
            size_hint=(0.2, 1),
            background_color=(0.6, 0.4, 0.8, 1),
            background_normal="",
            color=(1, 1, 1, 1)
        )
        sell_button.bind(on_press=self.go_to_sell)
        cart_button = Button(
            text="Cart",
            size_hint=(0.2, 1),
            background_color=(0.9, 0.6, 0.2, 1),
            background_normal="",
            color=(1, 1, 1, 1)
        )
        cart_button.bind(on_press=self.go_to_cart)
        logout_button = Button(
            text="Logout",
            size_hint=(0.2, 1),
            background_color=(0.8, 0.3, 0.3, 1),
            background_normal="",
            color=(1, 1, 1, 1)
        )
        logout_button.bind(on_press=self.on_logout)
        header.add_widget(title)
        header.add_widget(sell_button)
        header.add_widget(cart_button)
        header.add_widget(logout_button)
        outer.add_widget(header)

        search_row = BoxLayout(size_hint=(1, 0.08), spacing=6)
        self.search_input = TextInput(
            hint_text="Search products...",
            multiline=False,
            padding=[15, 12, 15, 12]
        )
        self.search_input.bind(text=self.on_search_text_change)
        search_row.add_widget(self.search_input)
        outer.add_widget(search_row)

        filter_row = BoxLayout(size_hint=(1, 0.08), spacing=6)
        all_button = Button(
            text="All",
            background_color=(0.3, 0.4, 0.7, 1),
            background_normal="",
            color=(1, 1, 1, 1)
        )
        all_button.bind(on_press=self.clear_filter)
        low_price_button = Button(
            text="Under $50",
            background_color=(0.4, 0.6, 0.5, 1),
            background_normal="",
            color=(1, 1, 1, 1)
        )
        low_price_button.bind(on_press=lambda instance: self.filter_by_price(0, 50))
        mid_price_button = Button(
            text="$50-$200",
            background_color=(0.4, 0.6, 0.5, 1),
            background_normal="",
            color=(1, 1, 1, 1)
        )
        mid_price_button.bind(on_press=lambda instance: self.filter_by_price(50, 200))
        high_price_button = Button(
            text="Over $200",
            background_color=(0.4, 0.6, 0.5, 1),
            background_normal="",
            color=(1, 1, 1, 1)
        )
        high_price_button.bind(on_press=lambda instance: self.filter_by_price(200, None))
        filter_row.add_widget(all_button)
        filter_row.add_widget(low_price_button)
        filter_row.add_widget(mid_price_button)
        filter_row.add_widget(high_price_button)
        outer.add_widget(filter_row)

        self.message_label = Label(
            text="",
            color=(0.2, 0.6, 0.3, 1),
            size_hint=(1, 0.06)
        )
        outer.add_widget(self.message_label)

        scroll = ScrollView(size_hint=(1, 0.7))
        self.grid = GridLayout(cols=2, spacing=12, padding=6, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter("height"))
        scroll.add_widget(self.grid)
        outer.add_widget(scroll)

        self.add_widget(outer)

    def update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def on_pre_enter(self, *args):
        self.load_products()

    def load_products(self):
        self.all_products = Product.get_all()
        self.search_input.text = ""
        self.render_products(self.all_products)

    def render_products(self, products):
        self.grid.clear_widgets()
        for product in products:
            card = ProductCard(
                product=product,
                on_card_press=self.go_to_detail,
                on_add_press=self.add_to_cart
            )
            self.grid.add_widget(card)

    def on_search_text_change(self, instance, value):
        keyword = value.strip().lower()
        if not keyword:
            self.render_products(self.all_products)
            return

        filtered = [p for p in self.all_products if keyword in p["name"].lower()]
        self.render_products(filtered)

    def filter_by_price(self, min_price, max_price):
        if max_price is None:
            filtered = [p for p in self.all_products if float(p["price"]) >= min_price]
        else:
            filtered = [p for p in self.all_products if min_price <= float(p["price"]) < max_price]
        self.render_products(filtered)

    def clear_filter(self, instance):
        self.search_input.text = ""
        self.render_products(self.all_products)

    def go_to_detail(self, product):
        detail_screen = self.manager.get_screen("product_detail")
        detail_screen.set_product(product)
        self.manager.current = "product_detail"

    def add_to_cart(self, product):
        app = App.get_running_app()
        customer = app.current_customer

        if customer is None:
            self.message_label.color = (0.8, 0.2, 0.2, 1)
            self.message_label.text = "Please login first"
            return

        try:
            CartItem.add(
                customer_id=customer["id"],
                product_id=product["id"],
                seller_id=product["seller_id"],
                quantity=1
            )
            self.message_label.color = (0.2, 0.6, 0.3, 1)
            self.message_label.text = f"{product['name']} added to cart"
        except Exception as e:
            self.message_label.color = (0.8, 0.2, 0.2, 1)
            self.message_label.text = f"Error: {e}"

    def go_to_cart(self, instance):
        self.manager.current = "cart"

    def go_to_sell(self, instance):
        app = App.get_running_app()
        if app.current_seller is not None:
            self.manager.current = "add_product"
        else:
            self.manager.current = "become_seller"

    def on_logout(self, instance):
        app = App.get_running_app()
        clear_session(app)
        self.manager.current = "login"
