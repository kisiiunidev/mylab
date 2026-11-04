from datetime import datetime
from extensions import DB
from werkzeug.security import generate_password_hash, check_password_hash

class User(DB.Model):
    __tablename__ = 'users'

    id = DB.Column(DB.Integer, primary_key=True)
    username = DB.Column(DB.String(80), unique=True, nullable=False)
    email = DB.Column(DB.String(120), unique=True, nullable=False)
    password_hash = DB.Column(DB.String(128), nullable=False)
    is_admin = DB.Column(DB.Boolean, default=False)
    created_at = DB.Column(DB.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat()
        }

class Coffee(DB.Model):
    __tablename__ = 'coffees'

    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(100), nullable=False)
    description = DB.Column(DB.Text, nullable=False)
    price = DB.Column(DB.Float, nullable=False)
    image_url = DB.Column(DB.String(255))
    stock_quantity = DB.Column(DB.Integer, default=0)
    roast_level = DB.Column(DB.String(20))  # light, medium, dark
    coffee_type = DB.Column(DB.String(20))  # arabica, robusta, blend
    created_at = DB.Column(DB.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'image_url': self.image_url,
            'stock_quantity': self.stock_quantity,
            'roast_level': self.roast_level,
            'coffee_type': self.coffee_type,
            'created_at': self.created_at.isoformat()
        }

class BlogPost(DB.Model):
    __tablename__ = 'blog_posts'

    id = DB.Column(DB.Integer, primary_key=True)
    title = DB.Column(DB.String(200), nullable=False)
    content = DB.Column(DB.Text, nullable=False)
    excerpt = DB.Column(DB.String(300))
    author = DB.Column(DB.String(100), default='Coffee Corner')
    featured_image = DB.Column(DB.String(255))
    published_at = DB.Column(DB.DateTime, default=datetime.utcnow)
    is_published = DB.Column(DB.Boolean, default=True)
    created_at = DB.Column(DB.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'excerpt': self.excerpt,
            'author': self.author,
            'featured_image': self.featured_image,
            'published_at': self.published_at.isoformat(),
            'is_published': self.is_published,
            'created_at': self.created_at.isoformat()
        }

class Order(DB.Model):
    __tablename__ = 'orders'

    id = DB.Column(DB.Integer, primary_key=True)
    user_id = DB.Column(DB.Integer, DB.ForeignKey('users.id'), nullable=True)
    customer_name = DB.Column(DB.String(100), nullable=False)
    customer_email = DB.Column(DB.String(120), nullable=False)
    customer_phone = DB.Column(DB.String(20))
    shipping_address = DB.Column(DB.Text)
    total_amount = DB.Column(DB.Float, nullable=False)
    status = DB.Column(DB.String(20), default='pending')  # pending, confirmed, shipped, cancelled
    created_at = DB.Column(DB.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'customer_name': self.customer_name,
            'customer_email': self.customer_email,
            'customer_phone': self.customer_phone,
            'shipping_address': self.shipping_address,
            'total_amount': self.total_amount,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

class OrderItem(DB.Model):
    __tablename__ = 'order_items'

    id = DB.Column(DB.Integer, primary_key=True)
    order_id = DB.Column(DB.Integer, DB.ForeignKey('orders.id'), nullable=False)
    coffee_id = DB.Column(DB.Integer, DB.ForeignKey('coffees.id'), nullable=False)
    quantity = DB.Column(DB.Integer, nullable=False)
    price = DB.Column(DB.Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'coffee_id': self.coffee_id,
            'quantity': self.quantity,
            'price': self.price
        }