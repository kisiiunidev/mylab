import os
from datetime import datetime
from pathlib import Path

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'coffee-website-secret-key-2024')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///coffee_shop.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True

    # Mail settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('SHOP_EMAIL', 'info@coffeecorner.com')

    # Coffee shop info
    SHOP_NAME = os.environ.get('SHOP_NAME', 'Coffee Corner')
    SHOP_EMAIL = os.environ.get('SHOP_EMAIL', 'info@coffeecorner.com')
    SHOP_PHONE = os.environ.get('SHOP_PHONE', '+1234567890')
    SHOP_ADDRESS = os.environ.get('SHOP_ADDRESS', '123 Coffee Street, Brew City')

    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = Path(__file__).parent / 'static' / 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

    # Coffee bean types
    COFFEE_TYPES = ['Espresso', 'Americano', 'Latte', 'Cappuccino', 'Mocha', 'Macchiato', 'Flat White']

    # Brew methods
    BREW_METHODS = ['Drip', 'French Press', 'Espresso', 'Aeropress', 'Moka Pot', 'Cold Brew']

    @staticmethod
    def init_upload_folder():
        Config.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)