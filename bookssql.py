import sqlite3
import threading

db_lock = threading.Lock()

def connect_to_database():
    conn = sqlite3.connect('Bookstore.db')
    return conn

def get_full_books_info():
    conn = connect_to_database()
    cursor = conn.cursor()
    sql = '''
    SELECT Book.ISBN, Title.Title, Autor.Autor, Book.Image_URL, Book.Preis, Book.Quantity
    FROM Book
    JOIN Autor ON Book.Autor_ID = Autor.AutorID
    JOIN Title ON Book.Titel_ID = Title.ID
    ORDER BY RANDOM()
    '''
    cursor.execute(sql)
    books = cursor.fetchall()
    conn.close()

    return books

def get_book_details(isbn):
    conn = connect_to_database()
    cursor = conn.cursor()
    sql = '''
        SELECT Book.ISBN, Title.Title, Autor.Autor, Book.Description_book, Genre.Genre, Book.Image_URL, 
               Book.Keywords, Book.PAGES, Book.Preis, Publisher.Publisher, Book.Quantity, Language.Lang, 
               Book.Year_book
        FROM Book
        JOIN Autor ON Book.Autor_ID = Autor.AutorID
        JOIN Genre ON Book.Genre_ID = Genre.ID
        JOIN Publisher ON Book.Publisher_ID = Publisher.ID
        JOIN Language ON Book.Sprache_ID = Language.ID
        JOIN Title ON Book.Titel_ID = Title.ID
        WHERE Book.ISBN = ?;
        '''
    cursor.execute(sql, (isbn,))
    book = cursor.fetchone()
    conn.close()

    return book

def get_best_sellers(limit=9):
    with db_lock, connect_to_database() as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT Book.ISBN, Title.Title, Autor.Autor, Book.Image_URL, Book.Preis, Book.Quantity
        FROM Book
        JOIN Title ON Book.Titel_ID = Title.ID
        JOIN Autor ON Book.Autor_ID = Autor.AutorID
        ORDER BY RANDOM()
        LIMIT ?
        ''', (limit,))
        best_sellers = cursor.fetchall()

    return best_sellers

def get_recommendations_of_the_day(limit=3):
    with db_lock, connect_to_database() as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT Book.ISBN, Title.Title, Autor.Autor, Book.Image_URL, Book.Preis, Book.Quantity
        FROM Book
        JOIN Title ON Book.Titel_ID = Title.ID
        JOIN Autor ON Book.Autor_ID = Autor.AutorID
        ORDER BY RANDOM()
        LIMIT ?
        ''', (limit,))
        recommendations = cursor.fetchall()

    return recommendations

def get_books_by_genre(genre_id):
    conn = connect_to_database()
    cursor = conn.cursor()

    sql = '''
    SELECT Book.ISBN, Title.Title, Autor.Autor, Book.Image_URL, Book.Preis, Book.Quantity
    FROM Book
    JOIN Autor ON Book.Autor_ID = Autor.AutorID
    JOIN Title ON Book.Titel_ID = Title.ID
    WHERE Book.Genre_ID = ?;
    '''
    cursor.execute(sql, (genre_id,))
    books = cursor.fetchall()
    conn.close()

    return books
