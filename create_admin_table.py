import mysql.connector
from werkzeug.security import generate_password_hash

def setup_admins_table():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="yash2622007",
        database="government_schemes"
    )
    cursor = conn.cursor(dictionary=True)

    print("Creating admins table if not exists...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("SELECT * FROM admins WHERE username = 'admin'")
    existing = cursor.fetchone()
    if not existing:
        hashed_pw = generate_password_hash("admin123")
        cursor.execute(
            "INSERT INTO admins (username, password) VALUES (%s, %s)",
            ("admin", hashed_pw)
        )
        print("Default admin created: username='admin', password='admin123'")
    else:
        print("Admin user already exists.")

    conn.commit()
    conn.close()
    print("Admin setup complete.")

if __name__ == "__main__":
    setup_admins_table()
