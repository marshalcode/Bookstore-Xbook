import sqlite3
import time

def connect_to_database():
    return sqlite3.connect('Bookstore.db')

def add_to_wishlist(customer_id, isbn):
    conn = connect_to_database()
    retries = 10
    while retries:
        try:
            with conn:
                cursor = conn.cursor()
                sql = '''INSERT INTO Wishlist (KDNR_ID, ISBN_ID) VALUES (?, ?);'''
                cursor.execute(sql, (customer_id, isbn))
            return
        except sqlite3.OperationalError as e:
            if 'database is locked' in str(e):
                retries -= 1
                time.sleep(2)
            else:
                raise
    conn.close()

def get_view_wishlist(conn, customer_id):

    sql = '''
    SELECT Book.ISBN, Title.Title, Autor.Autor, Book.Image_URL, Book.Preis, Book.Quantity
    FROM Wishlist
    JOIN Book ON Wishlist.ISBN_ID = Book.ISBN
    JOIN Title ON Book.Titel_ID = Title.ID
    JOIN Autor ON Book.Autor_ID = Autor.AutorID
    WHERE Wishlist.KDNR_ID = ?;
    '''
    cursor = conn.execute(sql, (customer_id,))
    books = cursor.fetchall()

    return books

def remove_from_wishlist(customer_id, isbn):
    conn = connect_to_database()
    retries = 10
    while retries:
        try:
            with conn:
                cursor = conn.cursor()
                sql = '''DELETE FROM Wishlist WHERE KDNR_ID = ? AND ISBN_ID = ?;'''
                cursor.execute(sql, (customer_id, isbn))
            return
        except sqlite3.OperationalError as e:
            if 'database is locked' in str(e):
                retries -= 1
                time.sleep(2)
            else:
                raise
    conn.close()

def move_to_basket(customer_id, isbn):
    conn = connect_to_database()
    retries = 10
    while retries:
        try:
            with conn:
                cursor = conn.cursor()
                sql_delete = '''DELETE FROM Wishlist WHERE KDNR_ID = ? AND ISBN_ID = ?;'''
                cursor.execute(sql_delete, (customer_id, isbn))
                sql_insert = '''INSERT INTO Basket (Customer_ID, ISBN) VALUES (?, ?);'''
                cursor.execute(sql_insert, (customer_id, isbn))
            return
        except sqlite3.OperationalError as e:
            if 'database is locked' in str(e):
                retries -= 1
                time.sleep(2)
            else:
                raise
    conn.close()