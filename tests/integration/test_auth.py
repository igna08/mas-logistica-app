import json
from app.models import Usuario

def test_register_and_login(test_client, session):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/api/auth/register' page is requested (POST) by an admin
    THEN check that a new user is created and can log in.
    """
    # This test is simplified. A real test would first log in as an admin.
    # For now, we test the registration logic directly.
    # The RBAC decorator is tested separately.

    # Register a new user
    register_data = {
        "nombre": "Test User",
        "email": "test@example.com",
        "password": "password123",
        "rol": "chofer"
    }
    # Note: In a real scenario, this endpoint would be protected and require an admin token.
    # We are assuming for this test that the endpoint is accessible for now.
    # To properly test this, we would need to create an admin user first.

    # Let's create an admin user directly to test the protected route
    admin = Usuario(nombre="Admin", email="admin@test.com", rol="admin")
    admin.set_password("adminpass")
    session.add(admin)
    session.commit()

    # Login as admin to get token
    login_resp = test_client.post('/api/auth/login', json={
        "email": "admin@test.com",
        "password": "adminpass"
    })
    assert login_resp.status_code == 200

    # Now, as admin, register a new user
    register_resp = test_client.post('/api/auth/register', json=register_data)
    assert register_resp.status_code == 201

    # Check that the user was created in the database
    user = Usuario.query.filter_by(email="test@example.com").first()
    assert user is not None
    assert user.rol == "chofer"

    # Logout admin
    test_client.post('/api/auth/logout')

    # Test login with the new user's credentials
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    login_resp = test_client.post('/api/auth/login', json=login_data)
    assert login_resp.status_code == 200
    assert login_resp.json['login'] is True

def test_login_failure(test_client, session):
    """
    GIVEN a user exists
    WHEN the '/api/auth/login' is requested with wrong password
    THEN check for a 401 error.
    """
    user = Usuario(nombre="Test User", email="test@fail.com", rol="chofer")
    user.set_password("correct_password")
    session.add(user)
    session.commit()

    login_data = {
        "email": "test@fail.com",
        "password": "wrong_password"
    }
    resp = test_client.post('/api/auth/login', json=login_data)
    assert resp.status_code == 401
    assert resp.json['msg'] == "Credenciales inválidas"

def test_me_endpoint(test_client, session):
    """
    GIVEN a logged-in user
    WHEN the '/api/auth/me' endpoint is requested
    THEN check that it returns the correct user information.
    """
    user = Usuario(nombre="Current User", email="me@test.com", rol="mantenimiento")
    user.set_password("password")
    session.add(user)
    session.commit()

    # Login to get the JWT cookie
    test_client.post('/api/auth/login', json={"email": "me@test.com", "password": "password"})

    # Request the /me endpoint
    resp = test_client.get('/api/auth/me')
    assert resp.status_code == 200
    data = resp.json
    assert data['nombre'] == "Current User"
    assert data['email'] == "me@test.com"
    assert data['rol'] == "mantenimiento"
