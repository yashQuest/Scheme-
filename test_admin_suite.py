from app import app, get_db

def test_admin():
    client = app.test_client()

    print("\n--- 1. Testing Route Protection (Unauthenticated Access) ---")
    for protected_url in ["/admin", "/admin/schemes", "/admin/schemes/add", "/admin/contacts"]:
        res = client.get(protected_url, follow_redirects=False)
        assert res.status_code == 302, f"Expected 302 redirect for {protected_url}, got {res.status_code}"
        assert "/admin/login" in res.headers.get("Location", "")
        print(f"[PASS] Unauthenticated {protected_url} correctly redirected to /admin/login")

    print("\n--- 2. Testing Admin Login ---")
    # Bad credentials
    bad_login = client.post("/admin/login", data={"username": "admin", "password": "wrongpassword"}, follow_redirects=True)
    assert bad_login.status_code == 200
    assert b"Invalid login credentials" in bad_login.data
    print("[PASS] Invalid admin login correctly rejected")

    # Correct credentials
    login_res = client.post("/admin/login", data={"username": "admin", "password": "admin123"}, follow_redirects=True)
    assert login_res.status_code == 200
    assert b"Dashboard Overview" in login_res.data
    assert b"Total Schemes" in login_res.data
    print("[PASS] Admin login succeeded, redirected to dashboard")

    print("\n--- 3. Testing Admin Dashboard Metrics ---")
    dash_res = client.get("/admin")
    assert dash_res.status_code == 200
    assert b"Total Schemes" in dash_res.data
    assert b"Categories" in dash_res.data
    assert b"Contact Messages" in dash_res.data
    print("[PASS] GET /admin displayed dynamic summary cards")

    print("\n--- 4. Testing Scheme Management (View & Search) ---")
    schemes_res = client.get("/admin/schemes")
    assert schemes_res.status_code == 200
    assert b"Government Schemes List" in schemes_res.data
    assert b"Add Scheme" in schemes_res.data
    print("[PASS] GET /admin/schemes listed schemes table")

    # Search filter
    search_res = client.get("/admin/schemes?q=kisan")
    assert search_res.status_code == 200
    assert b"Kisan Credit Card" in search_res.data
    print("[PASS] GET /admin/schemes?q=kisan filtered correctly")

    print("\n--- 5. Testing Add Scheme ---")
    get_add = client.get("/admin/schemes/add")
    assert get_add.status_code == 200
    assert b"Add New Government Scheme" in get_add.data
    assert b"category_id" in get_add.data

    add_payload = {
        "scheme_name": "Automated Test Admin Scheme 2026",
        "category_id": "1",
        "description": "Created during automated verification.",
        "eligibility": "Open to all verified applicants.",
        "benefits": "Financial aid of Rs. 15000.",
        "required_document": "Aadhaar Card, Income Certificate",
        "official_link": "https://example.gov.in/test",
        "image": "Photo/home.jpg",
        "min_age": "18",
        "max_age": "30",
        "max_income": "250000",
        "gender": "Any",
        "farmer": "No",
        "disability": "No",
        "area_type": "Any",
        "social_category": "Any",
        "house_owner": "Any",
        "occupation": "Student",
        "state": "All"
    }
    post_add = client.post("/admin/schemes/add", data=add_payload, follow_redirects=True)
    assert post_add.status_code == 200
    assert b"Scheme added successfully" in post_add.data
    assert b"Automated Test Admin Scheme 2026" in post_add.data
    print("[PASS] POST /admin/schemes/add inserted new scheme")

    # Retrieve new scheme ID from database
    with app.app_context():
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id FROM schemes WHERE scheme_name = 'Automated Test Admin Scheme 2026'")
        created_scheme = cursor.fetchone()
        test_scheme_id = created_scheme["id"]

    print(f"\n--- 6. Testing Edit Scheme (ID: {test_scheme_id}) ---")
    get_edit = client.get(f"/admin/schemes/edit/{test_scheme_id}")
    assert get_edit.status_code == 200
    assert b"Automated Test Admin Scheme 2026" in get_edit.data

    edit_payload = dict(add_payload)
    edit_payload["scheme_name"] = "Automated Test Admin Scheme 2026 (Updated)"
    post_edit = client.post(f"/admin/schemes/edit/{test_scheme_id}", data=edit_payload, follow_redirects=True)
    assert post_edit.status_code == 200
    assert b"Scheme updated successfully" in post_edit.data
    assert b"Automated Test Admin Scheme 2026 (Updated)" in post_edit.data
    print("[PASS] POST /admin/schemes/edit updated scheme")

    print(f"\n--- 7. Testing Delete Scheme (ID: {test_scheme_id}) ---")
    post_del = client.post(f"/admin/schemes/delete/{test_scheme_id}", follow_redirects=True)
    assert post_del.status_code == 200
    assert b"Scheme deleted successfully" in post_del.data

    with app.app_context():
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id FROM schemes WHERE id = %s", (test_scheme_id,))
        assert cursor.fetchone() is None
    print("[PASS] POST /admin/schemes/delete deleted scheme")

    print("\n--- 8. Testing Contact Messages Management ---")
    # Insert a dummy contact message for test
    with app.app_context():
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "INSERT INTO contacts (Name, email, subject, message) VALUES (%s, %s, %s, %s)",
            ("Test Contact Sender", "sender@test.com", "Test Inquiry", "Testing admin contacts view")
        )
        db.commit()
        cursor.execute("SELECT SrNo FROM contacts WHERE email = 'sender@test.com'")
        test_contact_id = cursor.fetchone()["SrNo"]

    contacts_res = client.get("/admin/contacts")
    assert contacts_res.status_code == 200
    assert b"Test Contact Sender" in contacts_res.data
    assert b"Testing admin contacts view" in contacts_res.data
    print("[PASS] GET /admin/contacts listed messages")

    # Delete contact message
    del_contact_res = client.post(f"/admin/contacts/delete/{test_contact_id}", follow_redirects=True)
    assert del_contact_res.status_code == 200
    assert b"Contact message deleted successfully" in del_contact_res.data

    with app.app_context():
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT SrNo FROM contacts WHERE SrNo = %s", (test_contact_id,))
        assert cursor.fetchone() is None
    print("[PASS] POST /admin/contacts/delete removed contact message")

    print("\n--- 9. Testing Admin Logout ---")
    logout_res = client.get("/admin/logout", follow_redirects=True)
    assert logout_res.status_code == 200
    assert b"Logged out successfully" in logout_res.data
    assert b"Secure Login" in logout_res.data
    print("[PASS] GET /admin/logout successfully cleared session")

    # Verify cannot access /admin after logout
    recheck = client.get("/admin", follow_redirects=False)
    assert recheck.status_code == 302
    print("[PASS] Session invalidated after logout")

    print("\n--- 10. Verifying Public Website Pages Unbroken ---")
    for public_url in ["/home", "/schemes", "/find/1", "/Eligibility", "/ContactUs", "/AboutUs"]:
        pub_res = client.get(public_url)
        assert pub_res.status_code == 200, f"Failed on {public_url}: {pub_res.status_code}"
        print(f"[PASS] Public route {public_url} intact and returned 200 OK")

    print("\n==========================================")
    print("ALL ADMIN TESTS PASSED! (100% Verified)")
    print("==========================================")

if __name__ == "__main__":
    test_admin()
