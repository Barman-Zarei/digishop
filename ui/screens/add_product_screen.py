from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.graphics import Color, Rectangle

from models.product import Product


class AddProductScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_image_path = None

        with self.canvas.before:
            Color(0.96, 0.97, 1, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_bg, pos=self.update_bg)

        outer = BoxLayout(orientation="vertical", padding=30, spacing=12)

        header = BoxLayout(size_hint=(1, 0.1))
        back_button = Button(text="< Back", size_hint=(0.3, 1), background_color=(0, 0, 0, 0), background_normal="", color=(0.3, 0.4, 0.7, 1))
        back_button.bind(on_press=self.go_back)
        header.add_widget(back_button)
        header.add_widget(Label(text="Add Product", font_size="22sp", bold=True, color=(0.2, 0.3, 0.6, 1)))
        outer.add_widget(header)

        self.name_input = TextInput(hint_text="Product Name", multiline=False, size_hint=(1, 0.1), padding=[15, 15, 15, 15])
        self.description_input = TextInput(hint_text="Description", multiline=False, size_hint=(1, 0.1), padding=[15, 15, 15, 15])
        self.price_input = TextInput(hint_text="Price", multiline=False, input_filter="float", size_hint=(1, 0.1), padding=[15, 15, 15, 15])
        self.stock_input = TextInput(hint_text="Stock Quantity", multiline=False, input_filter="int", size_hint=(1, 0.1), padding=[15, 15, 15, 15])

        outer.add_widget(self.name_input)
        outer.add_widget(self.description_input)
        outer.add_widget(self.price_input)
        outer.add_widget(self.stock_input)

        image_row = BoxLayout(size_hint=(1, 0.1), spacing=8)
        pick_image_button = Button(text="Choose Image", background_color=(0.5, 0.5, 0.8, 1), background_normal="", color=(1, 1, 1, 1))
        pick_image_button.bind(on_press=self.open_file_chooser)
        self.image_status_label = Label(text="No image selected", color=(0.4, 0.4, 0.4, 1))
        image_row.add_widget(pick_image_button)
        image_row.add_widget(self.image_status_label)
        outer.add_widget(image_row)

        self.message_label = Label(text="", color=(0.8, 0.2, 0.2, 1), size_hint=(1, 0.08))
        outer.add_widget(self.message_label)

        self.submit_button = Button(
            text="Add Product", size_hint=(1, 0.15),
            background_color=(0.3, 0.7, 0.4, 1), background_normal="", color=(1, 1, 1, 1), font_size="17sp"
        )
        self.submit_button.bind(on_press=self.on_submit)
        outer.add_widget(self.submit_button)

        self.add_widget(outer)

    def update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def open_file_chooser(self, instance):
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        chooser = FileChooserListView(filters=["*.png", "*.jpg", "*.jpeg"])
        content.add_widget(chooser)

        buttons_row = BoxLayout(size_hint=(1, 0.15), spacing=10)
        select_button = Button(text="Select", background_color=(0.3, 0.7, 0.4, 1), background_normal="", color=(1, 1, 1, 1))
        cancel_button = Button(text="Cancel", background_color=(0.8, 0.3, 0.3, 1), background_normal="", color=(1, 1, 1, 1))
        buttons_row.add_widget(select_button)
        buttons_row.add_widget(cancel_button)
        content.add_widget(buttons_row)

        popup = Popup(title="Choose an Image", content=content, size_hint=(0.9, 0.9))

        def on_select(instance):
            if chooser.selection:
                self.selected_image_path = chooser.selection[0]
                self.image_status_label.text = self.selected_image_path.split("/")[-1]
            popup.dismiss()

        select_button.bind(on_press=on_select)
        cancel_button.bind(on_press=lambda instance: popup.dismiss())

        popup.open()

    def validate_inputs(self):
        if not self.name_input.text.strip():
            return "Product name cannot be empty"
        if not self.price_input.text.strip():
            return "Price cannot be empty"
        if not self.stock_input.text.strip():
            return "Stock quantity cannot be empty"
        return None

    def on_submit(self, instance):
        error = self.validate_inputs()
        if error:
            self.message_label.color = (0.8, 0.2, 0.2, 1)
            self.message_label.text = error
            return

        self.submit_button.disabled = True
        self.message_label.color = (0.3, 0.3, 0.3, 1)
        self.message_label.text = "Uploading..."

        Product.create(
            name=self.name_input.text.strip(),
            price=float(self.price_input.text),
            stock_quantity=int(self.stock_input.text),
            description=self.description_input.text.strip(),
            image_file_path=self.selected_image_path,
            callback=self.on_result
        )

    def on_result(self, data, status_code):
        self.submit_button.disabled = False

        if status_code != 201:
            self.message_label.color = (0.8, 0.2, 0.2, 1)
            self.message_label.text = str(data.get("error", data))
            return

        self.message_label.color = (0.2, 0.6, 0.3, 1)
        self.message_label.text = "Product added successfully"
        self.clear_form()

    def clear_form(self):
        self.name_input.text = ""
        self.description_input.text = ""
        self.price_input.text = ""
        self.stock_input.text = ""
        self.selected_image_path = None
        self.image_status_label.text = "No image selected"

    def go_back(self, instance):
        self.manager.current = "product_list"
