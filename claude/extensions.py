from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

# Initialize extensions
DB = SQLAlchemy()
CSRF = CSRFProtect()