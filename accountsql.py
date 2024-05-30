import sqlite3

def get_user_details(user_id):
    conn = sqlite3.connect('Bookstore.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Customer.KDNR, Customer.Mail, Customer.Surname, Customer.Name, Customer.ZIP_ID, Customer.Street, ZIPCode.Stadt
        FROM Customer
        JOIN ZIPCode ON Customer.ZIP_ID = ZIPCode.ZIP_Code
        WHERE Customer.KDNR = ?
    """, (user_id,))
    user = cursor.fetchone()

    if user:
        user_details = {
            'id': user[0],
            'email': user[1],
            'surname': user[2],
            'name': user[3],
            'zip_id': user[4],
            'street': user[5],
            'city': user[6],
            'orders': []
        }
        cursor.execute("""
        SELECT 
        Order_Book.OrderID, 
        Order_Book.Amount, 
        Order_Book.Date, 
        Order_Book.ISBN_ID, 
        Title.Title AS BookTitle, 
        Book.Image_URL AS CoverImage, 
        Order_Book.Total_price,
        Order_Book.Status
        FROM Order_Book
        JOIN Book ON Order_Book.ISBN_ID = Book.ISBN
        JOIN Title ON Book.Titel_ID = Title.ID
        WHERE Order_Book.KDNR_ID = ?
        ORDER BY Order_Book.Date DESC;
        """, (user_id,))
        orders = cursor.fetchall()
        for order in orders:
            user_details['orders'].append({
                'order_id': order[0],
                'amount': order[1],
                'date': order[2],
                'isbn': order[3],
                'title': order[4],
                'cover_image': order[5],
                'total_price': order[6],
                'status': order[7]
            })
        conn.close()
        return user_details
    conn.close()
    return None
