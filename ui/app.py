from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from ui.screens.login_screen import LoginScreen, try_auto_login
from ui.screens.register_screen import RegisterScreen
from ui.screens.product_list_screen import ProductListScreen
from ui.screens.product_detail_screen import ProductDetailScreen
from ui.screens.cart_screen import CartScreen
from ui.screens.checkout_screen import CheckoutScreen
from ui.screens.become_seller_screen import BecomeSellerScreen
from ui.screens.add_product_screen import AddProductScreen


class DigiShopApp(App):
    current_user = None
    current_customer = None
    current_seller = None

    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(RegisterScreen(name="register"))
        sm.add_widget(ProductListScreen(name="product_list"))
        sm.add_widget(ProductDetailScreen(name="product_detail"))
        sm.add_widget(CartScreen(name="cart"))
        sm.add_widget(CheckoutScreen(name="checkout"))
        sm.add_widget(BecomeSellerScreen(name="become_seller"))
        sm.add_widget(AddProductScreen(name="add_product"))

        if try_auto_login(self):
            sm.current = "product_list"

        return sm


if __name__ == "__main__":
    DigiShopApp().run()
