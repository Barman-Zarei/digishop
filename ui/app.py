from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from ui.screens.login_screen import LoginScreen
from ui.screens.register_screen import RegisterScreen
from ui.screens.product_list_screen import ProductListScreen
from ui.screens.product_detail_screen import ProductDetailScreen
from ui.screens.cart_screen import CartScreen
from ui.screens.checkout_screen import CheckoutScreen
from ui.screens.become_seller_screen import BecomeSellerScreen
from ui.screens.add_product_screen import AddProductScreen
from ui.screens.seller_orders_screen import SellerOrdersScreen
from ui.screens.my_products_screen import MyProductsScreen
from ui.screens.my_orders_screen import MyOrdersScreen


class DigiShopApp(App):
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
        sm.add_widget(SellerOrdersScreen(name="seller_orders"))
        sm.add_widget(MyProductsScreen(name="my_products"))
        sm.add_widget(MyOrdersScreen(name="my_orders"))
        return sm


if __name__ == "__main__":
    DigiShopApp().run()
