from kivy.metrics import dp

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle, RoundedRectangle

from models.product import Product


class MyProductRow(BoxLayout):
    def __init__(self, product, on_edit, on_delete, **kwargs):
        super().__init__(orientation="horizontal", padding=dp(10), spacing=dp(10), **kwargs)
        self.product = product
        self.size_hint_y = None
        self.height = dp(80)

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(10)])
        self.bind(size=self.update_bg, pos=self.update_bg)

        info = BoxLayout(orientation="vertical", size_hint=(0.5, 1))
        info.add_widget(Label(text=product["name"], color=(0.1, 0.1, 0.1, 1), font_size="14sp", bold=True))
        info.add_widget(Label(
            text=f"Toman {product['price']} - Stock: {product['stock_quantity']}",
            color=(0.4, 0.4, 0.4, 1), font_size="12sp"
        ))

        edit_button = Button(text="Edit", size_hint=(0.25, 1), background_color=(0.3, 0.4, 0.7, 1), background_normal="", color=(1, 1, 1, 1), font_size="12sp")
        edit_button.bind(on_press=lambda instance: on_edit(product))

        delete_button = Button(text="Delete", size_hint=(0.25, 1), background_color=(0.9, 0.3, 0.3, 1), background_normal="", color=(1, 1, 1, 1), font_size="12sp")
        delete_button.bind(on_press=lambda instance: on_delete(product))

        self.add_widget(info)
        self.add_widget(edit_button)
        self.add_widget(delete_button)

    def update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos


class MyProductsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(0.96, 0.97, 1, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_bg, pos=self.update_bg)

        outer = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))

        header = BoxLayout(size_hint=(1, None), height=dp(44))
        back_button = Button(text="< Back", size_hint=(0.25, 1), background_color=(0, 0, 0, 0), background_normal="", color=(0.3, 0.4, 0.7, 1), font_size="13sp")
        back_button.bind(on_press=self.go_back)
        header.add_widget(back_button)
        header.add_widget(Label(text="My Products", font_size="15sp", bold=True, color=(0.2, 0.3, 0.6, 1)))
        add_button = Button(text="+ Add New", size_hint=(0.32, 1), background_color=(0.3, 0.7, 0.4, 1), background_normal="", color=(1, 1, 1, 1), font_size="12sp")
        add_button.bind(on_press=self.go_to_add_product)
        header.add_widget(add_button)
        outer.add_widget(header)

        self.message_label = Label(text="", color=(0.2, 0.6, 0.3, 1), size_hint=(1, None), height=dp(24), font_size="13sp")
        outer.add_widget(self.message_label)

        scroll = ScrollView(size_hint=(1, 1))
        self.products_layout = BoxLayout(orientation="vertical", spacing=dp(10), size_hint_y=None, padding=[0, dp(5), 0, dp(5)])
        self.products_layout.bind(minimum_height=self.products_layout.setter("height"))
        scroll.add_widget(self.products_layout)
        outer.add_widget(scroll)

        self.add_widget(outer)

    def update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def on_pre_enter(self, *args):
        self.load_products()

    def load_products(self):
        self.message_label.color = (0.2, 0.6, 0.3, 1)
        self.message_label.text = "Loading..."
        Product.get_mine(self.on_products_loaded)

    def on_products_loaded(self, products, error):
        if error:
            self.message_label.color = (0.8, 0.2, 0.2, 1)
            self.message_label.text = error
            self.products_layout.clear_widgets()
            return

        self.message_label.color = (0.2, 0.6, 0.3, 1)
        self.message_label.text = "" if products else "You have no products yet"
        self.products_layout.clear_widgets()

        for product in products:
            row = MyProductRow(product=product, on_edit=self.open_edit_popup, on_delete=self.confirm_delete)
            self.products_layout.add_widget(row)

    def open_edit_popup(self, product):
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(15))

        name_input = TextInput(text=product["name"], multiline=False, size_hint=(1, 0.2), font_size="14sp")
        description_input = TextInput(text=product.get("description") or "", multiline=False, size_hint=(1, 0.2), font_size="14sp")
        price_input = TextInput(text=str(product["price"]), multiline=False, input_filter="float", size_hint=(1, 0.2), font_size="14sp")
        stock_input = TextInput(text=str(product["stock_quantity"]), multiline=False, input_filter="int", size_hint=(1, 0.2), font_size="14sp")
        popup_error_label = Label(text="", color=(0.8, 0.2, 0.2, 1), size_hint=(1, 0.1), font_size="12sp")

        content.add_widget(Label(text="Name", size_hint=(1, 0.08), color=(0.1, 0.1, 0.1, 1)))
        content.add_widget(name_input)
        content.add_widget(Label(text="Description", size_hint=(1, 0.08), color=(0.1, 0.1, 0.1, 1)))
        content.add_widget(description_input)
        content.add_widget(Label(text="Price", size_hint=(1, 0.08), color=(0.1, 0.1, 0.1, 1)))
        content.add_widget(price_input)
        content.add_widget(Label(text="Stock", size_hint=(1, 0.08), color=(0.1, 0.1, 0.1, 1)))
        content.add_widget(stock_input)
        content.add_widget(popup_error_label)

        buttons_row = BoxLayout(size_hint=(1, 0.2), spacing=dp(10))
        save_button = Button(text="Save", background_color=(0.3, 0.7, 0.4, 1), background_normal="", color=(1, 1, 1, 1))
        cancel_button = Button(text="Cancel", background_color=(0.8, 0.3, 0.3, 1), background_normal="", color=(1, 1, 1, 1))
        buttons_row.add_widget(save_button)
        buttons_row.add_widget(cancel_button)
        content.add_widget(buttons_row)

        popup = Popup(title=f"Edit: {product['name']}", content=content, size_hint=(0.85, 0.75), auto_dismiss=False)

        def on_save(instance):
            try:
                price_value = float(price_input.text)
            except ValueError:
                popup_error_label.text = "Price must be a valid number"
                return
            if price_value <= 0:
                popup_error_label.text = "Price must be greater than 0"
                return

            try:
                stock_value = int(stock_input.text)
            except ValueError:
                popup_error_label.text = "Stock must be a valid number"
                return
            if stock_value < 0:
                popup_error_label.text = "Stock cannot be negative"
                return

            save_button.disabled = True
            Product.update(
                product["id"],
                lambda data, status_code: self.on_update_result(data, status_code, popup),
                name=name_input.text.strip(),
                price=price_value,
                stock_quantity=stock_value,
                description=description_input.text.strip()
            )

        save_button.bind(on_press=on_save)
        cancel_button.bind(on_press=lambda instance: popup.dismiss())

        popup.open()

    def on_update_result(self, data, status_code, popup):
        popup.dismiss()
        if status_code != 200:
            self.message_label.color = (0.8, 0.2, 0.2, 1)
            error_data = data if isinstance(data, dict) else {}
            self.message_label.text = str(error_data.get("error", "Could not update product"))
            return
        self.message_label.color = (0.2, 0.6, 0.3, 1)
        self.message_label.text = "Product updated"
        self.load_products()

    def confirm_delete(self, product):
        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(15))
        content.add_widget(Label(text=f"Delete '{product['name']}'?", color=(0.1, 0.1, 0.1, 1)))

        buttons_row = BoxLayout(size_hint=(1, 0.4), spacing=dp(10))
        yes_button = Button(text="Yes, Delete", background_color=(0.9, 0.3, 0.3, 1), background_normal="", color=(1, 1, 1, 1))
        no_button = Button(text="Cancel", background_color=(0.6, 0.6, 0.6, 1), background_normal="", color=(1, 1, 1, 1))
        buttons_row.add_widget(yes_button)
        buttons_row.add_widget(no_button)
        content.add_widget(buttons_row)

        popup = Popup(title="Confirm Delete", content=content, size_hint=(0.8, 0.35), auto_dismiss=False)

        def on_confirm(instance):
            Product.delete(product["id"], lambda success: self.on_delete_result(success, popup))

        yes_button.bind(on_press=on_confirm)
        no_button.bind(on_press=lambda instance: popup.dismiss())

        popup.open()

    def on_delete_result(self, success, popup):
        popup.dismiss()
        if not success:
            self.message_label.color = (0.8, 0.2, 0.2, 1)
            self.message_label.text = "Error deleting product"
            return
        self.message_label.color = (0.2, 0.6, 0.3, 1)
        self.message_label.text = "Product removed from your store"
        self.load_products()

    def go_to_add_product(self, instance):
        self.manager.current = "add_product"

    def go_back(self, instance):
        self.manager.current = "product_list"
