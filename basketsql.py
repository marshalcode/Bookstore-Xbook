import sqlite3
import time

def connect_to_database():
    return sqlite3.connect('Bookstore.db')

def add_to_basket(customer_id, isbn):
    conn = connect_to_database()
    retries = 10
    while retries:
        try:
            with conn:
                cursor = conn.cursor()
                sql = '''INSERT INTO Basket (Customer_ID, ISBN) VALUES (?, ?);'''
                cursor.execute(sql, (customer_id, isbn))
            return
        except sqlite3.OperationalError as e:
            if 'database is locked' in str(e):
                retries -= 1
                time.sleep(2)
            else:
                raise
    conn.close()

def get_view_basket(conn, customer_id):
    sql = '''
    SELECT Book.ISBN, Title.Title, Autor.Autor, Book.Image_URL, Book.Preis, Book.Quantity
    FROM Basket
    JOIN Book ON Basket.ISBN = Book.ISBN
    JOIN Title ON Book.Titel_ID = Title.ID
    JOIN Autor ON Book.Autor_ID = Autor.AutorID
    WHERE Basket.Customer_ID = ?;
    '''
    cursor = conn.execute(sql, (customer_id,))
    books = cursor.fetchall()

    return books

def remove_from_basket(customer_id, isbn):
    conn = connect_to_database()
    retries = 10
    while retries:
        try:
            with conn:
                cursor = conn.cursor()
                sql = '''DELETE FROM Basket WHERE Customer_ID = ? AND ISBN = ?;'''
                cursor.execute(sql, (customer_id, isbn))
            return
        except sqlite3.OperationalError as e:
            if 'database is locked' in str(e):
                retries -= 1
                time.sleep(2)
            else:
                raise
    conn.close()