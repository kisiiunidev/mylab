import os
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, abort
from flask_mail import Mail
from extensions import DB, CSRF
from config import Config
from models import User, Coffee, BlogPost, Order, OrderItem
from storage import setup_storage

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
DB.init_app(app)
CSRF.init_app(app)

# Initialize mail
mail = Mail(app)

# Initialize storage
try:
    storage = setup_storage(app)
except RuntimeError as e:
    print(f"Error setting up storage: {e}", file=sys.stderr)
    # Fallback to basic local storage
    class BasicLocalStorage:
        def upload(self, file, filename):
            from pathlib import Path
            upload_folder = Path(__file__).parent / 'static' / 'uploads'
            upload_folder.mkdir(parents=True, exist_ok=True)
            filepath = upload_folder / filename
            file.save(filepath)
            return str(filepath)

        def get_url(self, filename):
            return f"/static/uploads/{filename}"

        def delete(self, filename):
            from pathlib import Path
            filepath = Path(__file__).parent / 'static' / 'uploads' / filename
            if filepath.exists():
                filepath.unlink()

    storage = BasicLocalStorage()

# Create upload folder if it doesn't exist
Config.init_upload_folder()

# Create database tables
with app.app_context():
    DB.create_all()

# Sample data initialization
def init_sample_data():
    if Coffee.query.first() is None:
        sample_coffees = [
            Coffee(
                name="Ethiopian Yirgacheffe",
                description="Bright and fruity with notes of citrus and berries",
                price=24.99,
                image_url="https://images.unsplash.com/photo-1559925393-8be0ce8fe6b4?w=400",
                stock_quantity=50,
                roast_level="light",
                coffee_type="arabica"
            ),
            Coffee(
                name="Colombian Supremo",
                description="Rich and balanced with chocolate undertones",
                price=22.50,
                image_url="https://images.unsplash.com/photo-1495474472287-fb4f2495d957?w=400",
                stock_quantity=35,
                roast_level="medium",
                coffee_type="arabica"
            ),
            Coffee(
                name="Brazilian Santos",
                description="Smooth and nutty with low acidity",
                price=19.99,
                image_url="https://images.unsplash.com/photo-1517705008128-0a1d503024b5?w=400",
                stock_quantity=40,
                roast_level="medium",
                coffee_type="arabica"
            ),
            Coffee(
                name="Sumatra Mandheling",
                description="Full-bodied and earthy with hints of spice",
                price=26.00,
                image_url="https://images.unsplash.com/photo-1447933584960-e3a5e68d3ec4?w=400",
                stock_quantity=25,
                roast_level="dark",
                coffee_type="arabica"
            )
        ]

        for coffee in sample_coffees:
            DB.session.add(coffee)

        DB.session.commit()

# Initialize sample data
with app.app_context():
    init_sample_data()

# Helper functions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

# Routes
@app.route('/')
def home():
    # Get featured coffees
    featured_coffees = Coffee.query.order_by(Coffee.created_at.desc()).limit(3).all()

    # Get recent blog posts
    recent_posts = BlogPost.query.filter_by(is_published=True).order_by(BlogPost.published_at.desc()).limit(3).all()

    return render_template('index.html',
                         featured_coffees=featured_coffees,
                         recent_posts=recent_posts)

@app.route('/coffees')
def coffees():
    coffee_type = request.args.get('type')
    roast_level = request.args.get('roast')

    query = Coffee.query

    if coffee_type:
        query = query.filter_by(coffee_type=coffee_type)
    if roast_level:
        query = query.filter_by(roast_level=roast_level)

    coffees = query.all()
    return render_template('coffees.html',
                         coffees=coffees,
                         coffee_types=Config.COFFEE_TYPES,
                         brew_methods=Config.BREW_METHODS)

@app.route('/coffee/<int:id>')
def coffee_detail(id):
    coffee = Coffee.query.get_or_404(id)
    return render_template('coffee_detail.html', coffee=coffee)

@app.route('/blog')
def blog():
    page = request.args.get('page', 1, type=int)
    posts_per_page = 6

    posts = BlogPost.query.filter_by(is_published=True).order_by(BlogPost.published_at.desc()) \
                         .paginate(page=page, per_page=posts_per_page)

    return render_template('blog.html', posts=posts)

@app.route('/blog/<int:id>')
def blog_post(id):
    post = BlogPost.query.get_or_404(id)
    if not post.is_published:
        abort(404)
    return render_template('blog_post.html', post=post)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # In a real application, you would send an email here
        flash('Thank you for your message! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/cart')
def cart():
    cart_items = session.get('cart', {})

    # Calculate total
    total = 0
    for coffee_id, quantity in cart_items.items():
        coffee = Coffee.query.get(int(coffee_id))
        if coffee:
            total += coffee.price * quantity

    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/add_to_cart/<int:id>', methods=['POST'])
def add_to_cart(id):
    coffee = Coffee.query.get_or_404(id)
    cart = session.get('cart', {})

    if str(id) in cart:
        cart[str(id)] += 1
    else:
        cart[str(id)] = 1

    session['cart'] = cart
    flash(f'Added {coffee.name} to your cart!', 'success')
    return redirect(request.url_for('coffee_detail', id=id))

@app.route('/remove_from_cart/<int:id>')
def remove_from_cart(id):
    cart = session.get('cart', {})
    if str(id) in cart:
        del cart[str(id)]
        session['cart'] = cart
        flash('Item removed from cart.', 'info')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        # Validate form data
        required_fields = ['name', 'email', 'phone', 'address']
        for field in required_fields:
            if not request.form.get(field):
                flash(f'Please provide your {field}.', 'error')
                return redirect(url_for('checkout'))

        # Create order
        order = Order(
            customer_name=request.form.get('name'),
            customer_email=request.form.get('email'),
            customer_phone=request.form.get('phone'),
            shipping_address=request.form.get('address'),
            total_amount=session.get('cart_total', 0)
        )

        DB.session.add(order)
        DB.session.commit()

        # Add order items
        cart = session.get('cart', {})
        for coffee_id, quantity in cart.items():
            coffee = Coffee.query.get(int(coffee_id))
            if coffee:
                order_item = OrderItem(
                    order_id=order.id,
                    coffee_id=int(coffee_id),
                    quantity=quantity,
                    price=coffee.price
                )
                DB.session.add(order_item)

                # Update stock
                coffee.stock_quantity -= quantity

        DB.session.commit()

        # Clear cart
        session.pop('cart', None)
        session.pop('cart_total', None)

        flash('Your order has been placed successfully!', 'success')
        return redirect(url_for('order_confirmation', order_id=order.id))

    return render_template('checkout.html')

@app.route('/order-confirmation/<int:id>')
def order_confirmation(id):
    order = Order.query.get_or_404(id)
    return render_template('order_confirmation.html', order=order)

@app.route('/account')
def account():
    if 'user_id' not in session:
        flash('Please log in to access your account.', 'info')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()

    return render_template('account.html', user=user, orders=orders)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()

        if user and user.check_password(request.form.get('password')):
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            flash('You have been logged in successfully!', 'success')
            return redirect(url_for('account'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Check if user exists
        if User.query.filter_by(username=request.form.get('username')).first():
            flash('Username already exists.', 'error')
            return redirect(url_for('register'))

        if User.query.filter_by(email=request.form.get('email')).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('register'))

        # Create new user
        user = User(
            username=request.form.get('username'),
            email=request.form.get('email')
        )
        user.set_password(request.form.get('password'))

        DB.session.add(user)
        DB.session.commit()

        session['user_id'] = user.id
        session['is_admin'] = user.is_admin

        flash('Your account has been created successfully!', 'success')
        return redirect(url_for('account'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('is_admin', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/admin')
def admin():
    if not session.get('is_admin'):
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('home'))

    coffees = Coffee.query.all()
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    orders = Order.query.order_by(Order.created_at.desc()).all()

    return render_template('admin.html', coffees=coffees, posts=posts, orders=orders)

@app.route('/admin/add-coffee', methods=['GET', 'POST'])
def add_coffee():
    if not session.get('is_admin'):
        abort(403)

    if request.method == 'POST':
        coffee = Coffee(
            name=request.form.get('name'),
            description=request.form.get('description'),
            price=float(request.form.get('price')),
            stock_quantity=int(request.form.get('stock_quantity')),
            roast_level=request.form.get('roast_level'),
            coffee_type=request.form.get('coffee_type')
        )

        DB.session.add(coffee)
        DB.session.commit()

        flash('Coffee added successfully!', 'success')
        return redirect(url_for('admin'))

    return render_template('add_coffee.html')

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    DB.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Try to get port from command line argument, default to 9000
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=9000)
    args = parser.parse_args()

    # Use werkzeug's reloader for development
    from werkzeug.serving import run_simple
    try:
        run_simple('0.0.0.0', args.port, app, use_reloader=True, use_debugger=True)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"Port {args.port} is already in use. Trying a different port...")
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', 0))
                free_port = s.getsockname()[1]
                print(f"Using free port: {free_port}")
                run_simple('0.0.0.0', free_port, app, use_reloader=True, use_debugger=True)
        else:
            raise
