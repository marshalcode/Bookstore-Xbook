import sqlite3
import random

def connect_to_database():
    return sqlite3.connect('Bookstore.db')

def get_books_in_basket(customer_id):
    conn = connect_to_database()

    try:
        sql = '''
        SELECT Book.ISBN, Book.Quantity, Book.Preis
        FROM Basket
        JOIN Book ON Basket.ISBN = Book.ISBN
        WHERE Basket.Customer_ID = ?;
        '''
        cursor = conn.execute(sql, (customer_id,))
        books = cursor.fetchall()
        return books
    finally:
        conn.close()

def update_book_quantity(conn, isbn, quantity):
    sql = '''UPDATE Book SET Quantity = Quantity - ? WHERE ISBN = ?'''
    conn.execute(sql, (quantity, isbn))
    conn.commit()

def get_random_status():
    return random.choice(['Paid', 'Shipped', 'Received'])

def add_order(conn, customer_id, isbn, amount, total_price):
    status = get_random_status()

    sql = '''INSERT INTO Order_Book (ISBN_ID, KDNR_ID, Amount, Date, Total_price, Status)
             VALUES (?, ?, ?, date('now'), ?, ?)'''
    cursor = conn.cursor()
    cursor.execute(sql, (isbn, customer_id, amount, total_price, status))
    conn.commit()