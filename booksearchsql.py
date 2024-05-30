import sqlite3

def search_books(search_query):
    if search_query is None:
        return False, None
    try:
        conn = sqlite3.connect('Bookstore.db')
        cursor = conn.cursor()
        query = """
                SELECT Book.ISBN, Title.Title, Autor.Autor, Book.Image_URL, Book.Preis, Book.Quantity, Keywords
                FROM Book
                JOIN Autor ON Book.Autor_ID = Autor.AutorID
                JOIN Title ON Book.Titel_ID = Title.ID
                WHERE Title.Title LIKE ? OR Autor.Autor LIKE ? OR ISBN = ? OR Keywords LIKE ?;
            """
        search_term = '%' + search_query + '%'
        cursor.execute(query, (search_term, search_term, search_query, search_term))
        results = cursor.fetchall()
        conn.close()

        if results:
            return True, results
        else:
            return False, None
    except sqlite3.Error as e:
        print("Error SQL:", e)
        return False, None