from app.models import Usuario

def login(test_client, email, password):
    """Helper function to log in a user."""
    return test_client.post('/api/auth/login', json={"email": email, "password": password})

def test_unauthenticated_redirect(test_client, session):
    """
    GIVEN an unauthenticated user
    WHEN accessing a protected page
    THEN they should be redirected to the login page.
    """
    resp = test_client.get('/admin/dashboard', follow_redirects=False)
    assert resp.status_code == 302
    assert '/login' in resp.location

    resp = test_client.get('/chofer/dashboard', follow_redirects=False)
    assert resp.status_code == 302
    assert '/login' in resp.location

def test_admin_dashboard_access(test_client, session):
    """
    GIVEN an admin user
    WHEN they log in and access their dashboard
    THEN the request should be successful.
    """
    admin = Usuario(nombre="Test Admin", email="admin@test.com", rol="admin")
    admin.set_password("password")
    session.add(admin)
    session.commit()

    login(test_client, "admin@test.com", "password")

    # Check redirection from root
    resp = test_client.get('/', follow_redirects=False)
    assert resp.status_code == 302
    assert '/admin/dashboard' in resp.location

    # Check direct access
    resp = test_client.get('/admin/dashboard')
    assert resp.status_code == 200
    assert 'Vehículos Activos' in resp.data.decode('utf-8') # Check for content in a card

def test_chofer_dashboard_access(test_client, session):
    """
    GIVEN a chofer user
    WHEN they log in and access their dashboard
    THEN the request should be successful.
    """
    chofer = Usuario(nombre="Test Chofer", email="chofer@test.com", rol="chofer")
    chofer.set_password("password")
    session.add(chofer)
    session.commit()

    login(test_client, "chofer@test.com", "password")

    # Check redirection from root
    resp = test_client.get('/', follow_redirects=False)
    assert resp.status_code == 302
    assert '/chofer/dashboard' in resp.location

    # Check direct access
    resp = test_client.get('/chofer/dashboard')
    assert resp.status_code == 200
    assert 'Estado Actual' in resp.data.decode('utf-8') # Check for content in the main card
