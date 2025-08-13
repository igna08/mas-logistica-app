from app.models import Usuario

def login(test_client, email, password):
    """Helper function to log in a user."""
    return test_client.post('/api/auth/login', json={"email": email, "password": password})

def test_admin_user_list(test_client, session):
    """
    GIVEN a logged-in admin
    WHEN they access the user list endpoint
    THEN they should see all users.
    """
    admin = Usuario(nombre="Test Admin", email="admin@test.com", rol="admin")
    admin.set_password("password")
    chofer = Usuario(nombre="Test Chofer", email="chofer@test.com", rol="chofer")
    chofer.set_password("password")
    session.add_all([admin, chofer])
    session.commit()

    login(test_client, "admin@test.com", "password")

    resp = test_client.get('/api/admin/users/')
    assert resp.status_code == 200
    assert len(resp.json) == 2

def test_admin_deactivate_user(test_client, session):
    """
    GIVEN a logged-in admin
    WHEN they call the deactivate endpoint for a user
    THEN the user's 'activo' flag should be False.
    """
    admin = Usuario(nombre="Test Admin", email="admin@test.com", rol="admin")
    admin.set_password("password")
    chofer = Usuario(nombre="Test Chofer", email="chofer@test.com", rol="chofer")
    chofer.set_password("password")
    session.add_all([admin, chofer])
    session.commit()

    login(test_client, "admin@test.com", "password")

    resp = test_client.delete(f'/api/admin/users/{chofer.id}')
    assert resp.status_code == 200

    session.refresh(chofer)
    assert chofer.activo is False

def test_non_admin_cannot_access(test_client, session):
    """
    GIVEN a non-admin user
    WHEN they attempt to access an admin endpoint
    THEN they should receive a 403 Forbidden error.
    """
    chofer = Usuario(nombre="Test Chofer", email="chofer@test.com", rol="chofer")
    chofer.set_password("password")
    session.add(chofer)
    session.commit()

    login(test_client, "chofer@test.com", "password")

    resp = test_client.get('/api/admin/users/')
    assert resp.status_code == 403
