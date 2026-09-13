# DigiShop

A mobile marketplace app built with **Kivy** (Python), backed by a **Django REST API** and **PostgreSQL** database. Users can browse products, manage a shopping cart, place orders, and sell their own products — all from a single cross-platform app (desktop or Android APK).

## Architecture

[Kivy App (Desktop / APK)]
│ HTTPS + JWT
▼
- [Django REST API] ──────► [PostgreSQL (hosted on Render)]
- The Kivy app never talks to the database directly — it only communicates with the Django API over HTTP.
- Authentication is handled with **JWT** (access + refresh tokens).
- The backend is deployed on **Render**; the database is a managed **PostgreSQL** instance also on Render.

## Features

- User registration & login (JWT-based)
- Browse products with search and price filters
- Product detail view with quantity selector
- Shopping cart (add / update quantity / remove)
- Checkout — automatically splits an order per seller if the cart contains items from multiple sellers
- Become a seller, add products (with real image upload)
- Sellers can view, edit, and delete their own products
- Sellers can view their incoming orders and update order status (pending / confirmed / shipped / delivered / cancelled) or delete an order

## Project Structure

digishop/
├── main.py # Kivy app entry point
├── requirements.txt # Kivy app dependencies
├── buildozer.spec # Android build configuration
│
├── api/
│ └── client.py # HTTP client, token/session management
│
├── models/ # API-backed data layer (no direct DB access)
│ ├── user.py
│ ├── product.py
│ ├── cart.py
│ └── order.py
│
├── ui/
│ ├── app.py # ScreenManager setup
│ └── screens/ # One file per screen
│
├── .github/workflows/
│ └── build-apk.yml # CI: builds an Android APK on every push
│
└── backend/ # Django REST API project
├── manage.py
├── requirements.txt
├── runtime.txt # Pinned Python version for Render
├── digishop_backend/ # Django project settings
├── accounts/ # User, Customer, Seller + JWT auth
├── products/ # Product CRUD
├── cart/ # Cart management
└── orders/ # Order creation & seller order management


## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Python, Kivy |
| Backend | Django, Django REST Framework |
| Auth | JWT (djangorestframework-simplejwt) |
| Database | PostgreSQL |
| Hosting | Render |
| Mobile build | Buildozer + GitHub Actions |

## Setup — Backend

1. Navigate to the backend folder:
```bash
   cd backend
```
2. Install dependencies:
```bash
   pip install -r requirements.txt
```
3. Copy the example config and fill in your own values:
```bash
   cp digishop_backend/config.example.py digishop_backend/config.py
```
4. Run migrations:
```bash
   python manage.py migrate
```
5. Start the development server:
```bash
   python manage.py runserver
```

## Setup — Kivy App

1. From the project root, install dependencies:
```bash
   pip install -r requirements.txt
```
2. In `api/client.py`, set `API_BASE_URL` to your backend's address (local or deployed).
3. Run the app:
```bash
   python main.py
```

## Building the Android APK

Every push to `master` triggers a GitHub Actions workflow (`.github/workflows/build-apk.yml`) that builds a debug APK using Buildozer. Once the workflow finishes, download the APK from the **Actions** tab under that run's artifacts.

## Security Notes

- The Kivy app / APK never stores database credentials — it only knows the public API URL.
- Database credentials and the Django secret key are kept in environment variables on Render (or a local `config.py`, which is git-ignored) — never committed to the repository.
- All protected endpoints require a valid JWT access token.

## Known Limitations

- Render's free tier does not provide persistent file storage, so uploaded product images may be cleared on server restarts.
- Sessions are kept in memory only (not persisted to disk), so the app requires a fresh login each time it's restarted.
