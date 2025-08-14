from app.models import Usuario, Vehiculo

def login(test_client, email, password):
    """Helper function to log in a user."""
    return test_client.post('/api/auth/login', json={"email": email, "password": password})

def setup_data(session):
    """Helper function to create users and a vehicle."""
    admin = Usuario(nombre="Test Admin", email="admin@test.com", rol="admin")
    admin.set_password("password")
    chofer = Usuario(nombre="Test Chofer", email="chofer@test.com", rol="chofer")
    chofer.set_password("password")
    vehiculo = Vehiculo(patente="ASSIGN_TEST")
    session.add_all([admin, chofer, vehiculo])
    session.commit()
    return admin, chofer, vehiculo

def test_assign_driver(test_client, session):
    """
    GIVEN a logged-in admin, a chofer, and a vehicle
    WHEN the assign endpoint is called
    THEN the chofer should be assigned to the vehicle.
    """
    admin, chofer, vehiculo = setup_data(session)
    login(test_client, "admin@test.com", "password")

    assign_data = {
        "chofer_id": str(chofer.id),
        "vehiculo_id": str(vehiculo.id)
    }
    resp = test_client.post('/api/assignments/', json=assign_data)
    assert resp.status_code == 200

    session.refresh(vehiculo)
    assert chofer in vehiculo.choferes_asignados

def test_unassign_driver(test_client, session):
    """
    GIVEN a driver assigned to a vehicle
    WHEN the unassign endpoint is called
    THEN the chofer should be unassigned from the vehicle.
    """
    admin, chofer, vehiculo = setup_data(session)
    vehiculo.choferes_asignados.append(chofer)
    session.commit()

    login(test_client, "admin@test.com", "password")

    unassign_data = {
        "chofer_id": str(chofer.id),
        "vehiculo_id": str(vehiculo.id)
    }
    resp = test_client.delete('/api/assignments/', json=unassign_data)
    assert resp.status_code == 200

    session.refresh(vehiculo)
    assert chofer not in vehiculo.choferes_asignados
