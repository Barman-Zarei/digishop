# DigiShop

A local desktop e-commerce app built with **Kivy** (UI) and **MySQL** (database), written in Python.

DigiShop lets users register as customers, browse products, add items to a cart, and place orders. Any user can also become a seller and list their own products for sale.

## Features

- User registration and login (with session persistence — stay logged in between app restarts)
- Browse products in a card-based, scrollable grid
- Search products by name
- Filter products by price range
- View product details and adjust quantity before adding to cart
- Shopping cart (update quantity, remove items)
- Checkout — automatically splits an order per seller if the cart contains products from multiple sellers
- Become a seller and add new products
- Logout

## Project Structure

```
digishop/
├── db/
│   └── connection.py       # MySQL connection handling
├── models/
│   ├── user.py
│   ├── customer.py
│   ├── seller.py
│   ├── product.py
│   ├── cart.py
│   └── order.py
├── ui/
│   ├── screens/
│   │   ├── login_screen.py
│   │   ├── register_screen.py
│   │   ├── product_list_screen.py
│   │   ├── product_detail_screen.py
│   │   ├── cart_screen.py
│   │   ├── checkout_screen.py
│   │   ├── become_seller_screen.py
│   │   └── add_product_screen.py
│   └── app.py               # ScreenManager and app entry point
├── schema.sql                # Database schema
├── requirements.txt
├── .env.example
└── main.py                   # Run this to start the app
```

## Prerequisites

- Python 3.8+
- MySQL Server (running locally or accessible remotely)

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/Barman-Zarei/digishop.git
   cd digishop
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Create the database**

   Log into MySQL and run the schema file:

   ```bash
   mysql -u root -p < schema.sql
   ```

   This creates a `digishop` database with all required tables.

4. **Configure environment variables**

   Copy the example env file and fill in your MySQL credentials:

   ```bash
   cp .env.example .env
   ```

   Edit `.env`:

   ```
   DB_HOST=localhost
   DB_USER=your_user_name_here
   DB_PASSWORD=your_password_here
   DB_NAME=digishop
   ```

## Running the App

From the project root:

```bash
python main.py
```

## Tech Stack

- **Kivy** — cross-platform GUI framework
- **MySQL** — relational database
- **mysql-connector-python** — MySQL driver for Python
- **python-dotenv** — loads environment variables from `.env`
- **bcrypt** — password hashing

## Notes

- `.env` and `session.json` are excluded from version control (see `.gitignore`) since they contain sensitive/local data.
- Passwords are hashed with bcrypt before being stored — plain-text passwords are never saved.
