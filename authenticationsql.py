import sqlite3
import bcrypt

def connect_to_database():
    conn = sqlite3.connect('Bookstore.db')
    return conn
def check_credentials(email, password):
    conn = connect_to_database()
    cursor = conn.cursor()
    query = "SELECT KDNR, Mail, Password FROM Customer WHERE Mail = ?;"
    cursor.execute(query, (email,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password(user[2], password):
        return user[0]
    else:
        return None
def register_user(email, password, surname, name, zip_id, street):
    conn = connect_to_database()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Customer (Mail, Password, Surname, Name, ZIP_ID, Street) VALUES (?, ?, ?, ?, ?, ?)",
            (email, password, surname, name, zip_id, street))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def check_password(stored_password, provided_password):
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)

# all users have password name (with a capital letter) and 1234
# admin@gmail.com pass: superadmin