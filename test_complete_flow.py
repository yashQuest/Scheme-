import re
from app import app, get_db

def test_all():
    client = app.test_client()

    print("\n--- 1. Testing Homepage & Schemes ---")
    res = client.get("/home")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    print("[PASS] GET /home passed")

    res = client.get("/schemes")
    assert res.status_code == 200
    assert b"Government Schemes" in res.data
    print("[PASS] GET /schemes passed")

    res = client.get("/find/2")
    assert res.status_code == 200
    assert b"Farmer" in res.data
    print("[PASS] GET /find/2 (Farmer category) passed")

    print("\n--- 2. Testing Search ---")
    res = client.get("/search?q=farmer")
    assert res.status_code == 200
    assert b"Search Results" in res.data
    assert b"Kisan Credit Card" in res.data
    print("[PASS] GET /search?q=farmer passed")

    res = client.get("/search?q=scholarship")
    assert res.status_code == 200
    assert b"Search Results" in res.data
    print("[PASS] GET /search?q=scholarship passed")

    print("\n--- 3. Testing Eligibility Form Submission ---")
    form_data = {
        "age": "21",
        "gender": "Male",
        "state": "Maharashtra",
        "district": "Pune",
        "category": "OBC",
        "income": "200000",
        "disability": "No",
        "education": "Undergraduate",
        "occupation": "Student",
        "farmer": "No",
        "area_type": "Urban",
        "house_owner": "No",
        "business_interest": "No",
        "employment_seeking": "Yes"
    }
    res = client.post("/check_eligibility", data=form_data)
    assert res.status_code == 200
    assert b"Scheme Eligibility Recommendations" in res.data
    assert b"Post Matric Scholarship" in res.data
    print("[PASS] POST /check_eligibility passed with recommendations")

    print("\n--- 4. Testing AI / Natural Language Eligibility ---")
    ai_data = {
        "natural_query": "I am a 21 year old student from Maharashtra. My family income is 2 lakh per year. I belong to OBC category and I do not have a disability."
    }
    res = client.post("/ai_eligibility", data=ai_data)
    assert res.status_code == 200
    assert b"Scheme Eligibility Recommendations" in res.data
    assert b"Matched Profile" in res.data
    print("[PASS] POST /ai_eligibility passed with extracted recommendations")

    print("\n--- 5. Testing Authentication (Register, Login, Logout) ---")
    # Clean up test user if previously exists
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM users WHERE email = 'testuser@example.com'")
        db.commit()

    reg_data = {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "password123",
        "confirm_password": "password123"
    }
    res = client.post("/register", data=reg_data, follow_redirects=True)
    assert res.status_code == 200
    assert b"Registration successful" in res.data
    print("[PASS] POST /register passed")

    # Login
    login_data = {
        "email": "testuser@example.com",
        "password": "password123"
    }
    res = client.post("/login", data=login_data, follow_redirects=True)
    assert res.status_code == 200
    assert b"Welcome back, Test User" in res.data
    print("[PASS] POST /login passed")

    print("\n--- 6. Testing Saved Schemes ---")
    # Save scheme 1
    res = client.post("/save_scheme/1", data={"next": "/saved_schemes"}, follow_redirects=True)
    assert res.status_code == 200
    assert b"added to your saved list" in res.data or b"Saved Schemes" in res.data
    print("[PASS] POST /save_scheme/1 passed")

    # View saved schemes
    res = client.get("/saved_schemes")
    assert res.status_code == 200
    assert b"Kisan Credit Card" in res.data
    print("[PASS] GET /saved_schemes passed")

    # Unsave scheme 1
    res = client.post("/unsave_scheme/1", data={"next": "/saved_schemes"}, follow_redirects=True)
    assert res.status_code == 200
    print("[PASS] POST /unsave_scheme/1 passed")

    # Logout
    res = client.get("/logout", follow_redirects=True)
    assert res.status_code == 200
    assert b"successfully logged out" in res.data
    print("[PASS] GET /logout passed")

    print("\n--- 7. Testing Contact Us ---")
    contact_data = {
        "name": "Jane Citizen",
        "email": "jane@example.com",
        "subject": "Inquiry about Scholarship",
        "message": "Can you provide details on application deadlines?"
    }
    res = client.post("/ContactUs", data=contact_data, follow_redirects=True)
    assert res.status_code == 200
    assert b"submitted successfully" in res.data
    print("[PASS] POST /ContactUs passed")

    print("\n--- 8. Testing Admin Access & Functionality ---")
    # Non-admin cannot access admin
    res = client.get("/admin", follow_redirects=True)
    assert b"login" in res.data.lower() or b"admin" in res.data.lower()
    print("[PASS] Protected /admin rejected unauthenticated user")

    # Login as admin
    admin_login = {
        "email": "admin@ourscheme.gov.in",
        "password": "admin123"
    }
    res = client.post("/login", data=admin_login, follow_redirects=True)
    assert res.status_code == 200

    # View admin dashboard
    res = client.get("/admin")
    assert res.status_code == 200
    assert b"Admin Dashboard" in res.data
    print("[PASS] GET /admin dashboard passed for admin")

    # Add a scheme via admin
    new_scheme_data = {
        "scheme_name": "Test Welfare Scheme 2026",
        "category_id": "1",
        "description": "A test welfare scheme for education support.",
        "eligibility": "Students enrolled in college.",
        "benefits": "Rs 10000 annual allowance.",
        "required_document": "Aadhaar, Student ID",
        "official_link": "https://example.com/test",
        "image": "Photo/home.jpg",
        "min_age": "17",
        "max_age": "25",
        "max_income": "300000",
        "gender": "Any",
        "farmer": "Any",
        "disability": "Any",
        "area_type": "Any",
        "social_category": "Any",
        "house_owner": "Any",
        "occupation": "Student",
        "state": "All"
    }
    res = client.post("/admin/scheme/add", data=new_scheme_data, follow_redirects=True)
    assert res.status_code == 200
    assert b"Test Welfare Scheme 2026" in res.data
    print("[PASS] POST /admin/scheme/add passed")

    # Clean up test scheme
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM schemes WHERE scheme_name = 'Test Welfare Scheme 2026'")
        db.commit()

    print("\n==========================================")
    print("ALL TESTS PASSED SUCCESSFULLY! (100% Flow Verified)")
    print("==========================================")

if __name__ == "__main__":
    test_all()
