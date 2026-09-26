import mysql.connector
from werkzeug.security import generate_password_hash

def run():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="yash2622007",
        database="government_schemes"
    )
    cursor = conn.cursor(dictionary=True)

    print("Checking columns in schemes table...")
    cursor.execute("DESCRIBE schemes")
    existing_cols = [row['Field'] for row in cursor.fetchall()]

    new_cols = [
        ("gender", "VARCHAR(20) DEFAULT 'Any'"),
        ("house_owner", "VARCHAR(20) DEFAULT 'Any'"),
        ("state", "VARCHAR(100) DEFAULT 'All'")
    ]

    for col_name, col_def in new_cols:
        if col_name not in existing_cols:
            print(f"Adding column {col_name} to schemes...")
            cursor.execute(f"ALTER TABLE schemes ADD COLUMN {col_name} {col_def}")
        else:
            print(f"Column {col_name} already exists.")

    print("Creating users table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(20) DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    print("Creating saved_schemes table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS saved_schemes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            scheme_id INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_user_scheme (user_id, scheme_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (scheme_id) REFERENCES schemes(id) ON DELETE CASCADE
        )
    """)

    print("Checking default admin account...")
    cursor.execute("SELECT * FROM users WHERE email = 'admin@ourscheme.gov.in'")
    admin = cursor.fetchone()
    if not admin:
        admin_pass = generate_password_hash("admin123")
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
            ("Admin User", "admin@ourscheme.gov.in", admin_pass, "admin")
        )
        print("Default admin created: admin@ourscheme.gov.in / admin123")
    else:
        print("Admin user already exists.")

    print("Populating structured criteria for schemes...")
    queries = [
        "UPDATE schemes SET min_age=14, max_age=35, occupation='Student', gender='Any', farmer='Any', disability='Any', area_type='Any', social_category='Any', house_owner='Any', state='All' WHERE category_id=1",
        "UPDATE schemes SET min_age=18, max_age=80, farmer='Yes', occupation='Farmer', gender='Any', disability='Any', area_type='Any', social_category='Any', house_owner='Any', state='All' WHERE category_id=2",
        "UPDATE schemes SET min_age=0, max_age=80, gender='Female', farmer='Any', disability='Any', area_type='Any', social_category='Any', house_owner='Any', state='All' WHERE category_id=3",
        "UPDATE schemes SET min_age=18, max_age=45, occupation='Any', gender='Any', farmer='Any', disability='Any', area_type='Any', social_category='Any', house_owner='Any', state='All' WHERE category_id=4",
        "UPDATE schemes SET min_age=60, max_age=100, gender='Any', farmer='Any', disability='Any', area_type='Any', social_category='Any', house_owner='Any', state='All' WHERE category_id=5",
        "UPDATE schemes SET min_age=0, max_age=100, max_income=500000, gender='Any', farmer='Any', disability='Any', area_type='Any', social_category='Any', house_owner='Any', state='All' WHERE category_id=6",
        "UPDATE schemes SET min_age=18, max_age=80, house_owner='No', max_income=600000, gender='Any', farmer='Any', disability='Any', area_type='Any', social_category='Any', state='All' WHERE category_id=7",
        "UPDATE schemes SET min_age=18, max_age=70, occupation='Business Owner', gender='Any', farmer='Any', disability='Any', area_type='Any', social_category='Any', house_owner='Any', state='All' WHERE category_id=8",
        "UPDATE schemes SET min_age=18, max_age=70, gender='Any', farmer='Any', disability='Any', area_type='Any', social_category='Any', house_owner='Any', state='All' WHERE category_id=9",
        "UPDATE schemes SET min_age=14, max_age=70, social_category='SC,ST,OBC', gender='Any', farmer='Any', disability='Any', area_type='Any', house_owner='Any', state='All' WHERE category_id=10",
        "UPDATE schemes SET min_age=0, max_age=100, disability='Yes', gender='Any', farmer='Any', area_type='Any', social_category='Any', house_owner='Any', state='All' WHERE category_id=11",
        "UPDATE schemes SET min_age=0, max_age=18, gender='Any', farmer='Any', disability='Any', area_type='Any', social_category='Any', house_owner='Any', state='All' WHERE category_id=12",
        "UPDATE schemes SET min_age=18, max_age=80, area_type='Rural', gender='Any', farmer='Any', disability='Any', social_category='Any', house_owner='Any', state='All' WHERE category_id=13",
        "UPDATE schemes SET min_age=18, max_age=80, area_type='Urban', gender='Any', farmer='Any', disability='Any', social_category='Any', house_owner='Any', state='All' WHERE category_id=14",
        "UPDATE schemes SET min_age=18, max_age=80, gender='Any', farmer='Any', disability='Any', area_type='Any', social_category='Any', house_owner='Any', state='All' WHERE category_id=15",
        "UPDATE schemes SET min_age=18, max_age=80, max_income=300000, gender='Any', farmer='Any', disability='Any', area_type='Any', social_category='Any', house_owner='Any', state='All' WHERE category_id=16",
        "UPDATE schemes SET min_age=0, max_age=10, gender='Female' WHERE scheme_name LIKE '%Sukanya Samriddhi%'",
        "UPDATE schemes SET social_category='OBC', occupation='Student', min_age=15, max_age=30, max_income=250000 WHERE scheme_name LIKE '%OBC Students%'",
        "UPDATE schemes SET social_category='SC', occupation='Student', min_age=14, max_age=30, max_income=250000 WHERE scheme_name LIKE '%SC Students%'",
        "UPDATE schemes SET social_category='SC', occupation='Student', min_age=21, max_age=35 WHERE scheme_name LIKE '%National Fellowship for SC%'",
        "UPDATE schemes SET min_age=18, max_age=40 WHERE scheme_name LIKE '%Atal Pension Yojana%'",
        "UPDATE schemes SET min_age=18, max_age=50 WHERE scheme_name LIKE '%Jeevan Jyoti%'",
        "UPDATE schemes SET min_age=18, max_age=70 WHERE scheme_name LIKE '%Suraksha Bima%'",
        "UPDATE schemes SET occupation='Self Employed', area_type='Urban', min_age=18 WHERE scheme_name LIKE '%SVANidhi%'",
        "UPDATE schemes SET min_age=18, social_category='SC,ST' WHERE scheme_name LIKE '%Stand-Up India%'",
        "UPDATE schemes SET min_age=60, max_age=100, max_income=200000 WHERE scheme_name LIKE '%Old Age Pension%' OR scheme_name LIKE '%Annapurna%'"
    ]

    for q in queries:
        cursor.execute(q)

    conn.commit()
    print("Migration completed successfully!")

    cursor.execute("SELECT COUNT(*) as populated FROM schemes WHERE min_age IS NOT NULL")
    print("Populated schemes:", cursor.fetchone())

    conn.close()

if __name__ == "__main__":
    run()
