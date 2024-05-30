import sqlite3
import re
import secrets
from flask import Flask, request, redirect, url_for, render_template, session, flash
from flask_session import Session

from authenticationsql import check_credentials, register_user, hash_password
from bookssql import get_book_details, get_full_books_info, get_best_sellers, get_recommendations_of_the_day, get_books_by_genre
from booksearchsql import search_books
from accountsql import get_user_details
from wishlistsql import add_to_wishlist, get_view_wishlist, remove_from_wishlist, move_to_basket
from basketsql import add_to_basket, get_view_basket, remove_from_basket
from paymentsql import get_books_in_basket, update_book_quantity, add_order

app = Flask(__name__)

app.secret_key = secrets.token_hex(24)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

def connect_to_database():
    return sqlite3.connect('Bookstore.db')

@app.route('/')
def home():
    best_sellers = get_best_sellers()
    recommendations = get_recommendations_of_the_day()
    user_id = session.get('user_id')
    return render_template('home.html', best_sellers=best_sellers, recommendations=recommendations, user_id=user_id)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_id = check_credentials(email, password)

        if user_id:
            session['user_id'] = user_id
            session['email'] = email
            if email == 'admin@gmail.com' and password == 'superadmin':
                return redirect(url_for('admin_orders'))
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error=True)
    else:
        return render_template('login.html', error=False)

@app.route('/admin/orders')
def admin_orders():
    if 'user_id' in session and session['email'] == 'admin@gmail.com':
        conn = connect_to_database()
        cursor = conn.cursor()
        query = 'SELECT OrderID, KDNR_ID, ISBN_ID, Amount, Date, Total_price, Status FROM Order_Book ORDER BY Order_Book.Date DESC;'
        cursor.execute(query)
        orders = cursor.fetchall()
        conn.close()
        orders_list = []
        for order in orders:
            orders_list.append({
                'OrderID': order[0],
                'KDNR_ID': order[1],
                'ISBN_ID': order[2],
                'Amount': order[3],
                'Date': order[4],
                'Total_price': order[5],
                'Status': order[6]
            })
        return render_template('admin_orders.html', orders=orders_list)
    else:
        return redirect(url_for('login_page'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('email', None)
    return redirect(url_for('home'))

@app.route('/book/<isbn>')
def book_details(isbn):
    book = get_book_details(isbn)
    user_id = session.get('user_id')
    return render_template('book_details.html', book=book, user_id=user_id)

@app.route('/books')
def all_books():
    genre_id = request.args.get('genre_id')
    user_id = session.get('user_id')

    if genre_id:
        books = get_books_by_genre(genre_id)
    else:
        books = get_full_books_info()
    return render_template('books.html', books=books, user_id=user_id)

@app.route('/search', methods=['POST'])
def search():
    search_query = request.form.get('search_query')
    found, results = search_books(search_query)

    if found:
        return render_template('search_results.html', books=results)
    else:
        return render_template('search_results.html')

@app.route('/account')
def account():
    user_id = session.get('user_id')
    if user_id:
        user_details = get_user_details(user_id)
        if user_details:
            return render_template('account.html', user=user_details)
    return redirect(url_for('login_page'))

@app.route('/add_to_wishlist', methods=['POST'])
def add_to_wishlist_route():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    user_id = session['user_id']
    isbn = request.form.get('isbn')

    add_to_wishlist(user_id, isbn)

    return redirect(url_for('book_details', isbn=isbn))

@app.route('/view_wishlist')
def view_wishlist_route():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    user_id = session['user_id']
    conn = connect_to_database()

    books = []
    try:
        books = get_view_wishlist(conn, user_id)
    finally:
        conn.close()

    return render_template('view_wishlist.html', books=books, user_id=user_id)

@app.route('/remove_from_wishlist', methods=['POST'])
def remove_from_wishlist_route():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    user_id = session['user_id']
    isbn = request.form.get('isbn')

    remove_from_wishlist(user_id, isbn)

    return redirect(url_for('view_wishlist_route'))

@app.route('/move_to_basket', methods=['POST'])
def move_to_basket_route():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    user_id = session['user_id']
    isbn = request.form.get('isbn')

    move_to_basket(user_id, isbn)

    return redirect(url_for('view_wishlist_route'))

@app.route('/add_to_basket', methods=['POST'])
def add_to_basket_route():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    user_id = session['user_id']
    isbn = request.form.get('isbn')

    add_to_basket(user_id, isbn)

    return redirect(url_for('book_details', isbn=isbn))

@app.route('/view_basket')
def view_basket_route():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    user_id = session['user_id']

    conn = connect_to_database()

    books = []
    try:
        books = get_view_basket(conn, user_id)
        total_price = round(sum(book[4] for book in books), 2)
    finally:
        conn.close()

    return render_template('view_basket.html', books=books, user_id=user_id, total_price=total_price)

@app.route('/remove_from_basket', methods=['POST'])
def remove_from_basket_route():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    user_id = session['user_id']
    isbn = request.form.get('isbn')

    remove_from_basket(user_id, isbn)

    return redirect(url_for('view_basket_route'))

@app.route('/checkout', methods=['POST'])
def checkout():
    user_id = session.get('user_id')

    if not user_id:
        return redirect(url_for('login'))

    books = get_books_in_basket(user_id)

    session['books_in_basket'] = books

    conn = connect_to_database()
    try:
        for book in books:
            update_book_quantity(conn, book[0], 1)
    finally:
        conn.close()

    return redirect(url_for('payment'))

@app.route('/payment')
def payment():
    user_id = session['user_id']
    books = session.get('books_in_basket', [])
    total_price = round(sum(book[2] for book in books), 2)
    return render_template('payment.html', total_price=total_price, user_id=user_id)

@app.route('/process_payment', methods=['POST'])
def process_payment():
    payment_method = request.form['payment_method']
    user_id = session['user_id']
    books = session.get('books_in_basket', [])

    conn = connect_to_database()

    try:
        if payment_method == 'paypal':
            pass
        elif payment_method == 'sepa':
            pass
        elif payment_method == 'giropay':
            pass
        elif payment_method == 'creditcard':
            pass

        total_price = round(sum(book[2] for book in books), 2)

        for book in books:
            add_order(conn, user_id, book[0], 1, total_price)

        sql = '''DELETE FROM Basket WHERE Customer_ID = ?;'''
        conn.execute(sql, (user_id,))
        conn.commit()
    finally:
        conn.close()

    return redirect(url_for('payment_confirmation'))

@app.route('/payment_confirmation')
def payment_confirmation():
    return render_template('payment_confirmation.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        surname = request.form['surname']
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        zip_id = request.form['zip_id']
        street = request.form['street']

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return render_template('register.html', error="Invalid email address.")

        if len(password) < 8:
            return render_template('register.html', error="Password must be at least 8 characters long.")

        hashed_password = hash_password(password)

        if register_user(email, hashed_password, surname, name, zip_id, street):
            return render_template('register.html', success="You have successfully registered! Please log in.")
        else:
            return render_template('register.html', error="Registration failed. Email might already be in use.")

    return render_template('register.html')

@app.route('/cookies-policy')
def cookies_policy():
    user_id = session.get('user_id')
    return render_template('cookies_policy.html', user_id=user_id)

@app.route('/terms-conditions')
def terms_conditions():
    user_id = session.get('user_id')
    return render_template('terms_conditions.html', user_id=user_id)

if __name__ == '__main__':
    app.run(debug=True)
