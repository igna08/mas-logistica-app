import json
import uuid
from decimal import Decimal
from app.models import Usuario, Vehiculo, Recorrido

def setup_test_data(session):
    """Helper function to create a chofer and a vehiculo."""
    chofer = Usuario(nombre="Test Chofer", email="chofer@test.com", rol="chofer")
    chofer.set_password("password")

    vehiculo = Vehiculo(patente="TEST001", modelo="Test Model")

    session.add(chofer)
    session.add(vehiculo)
    session.commit()
    return chofer, vehiculo

def login_user(test_client, email, password):
    """Helper function to log in a user."""
    resp = test_client.post('/api/auth/login', json={"email": email, "password": password})
    assert resp.status_code == 200
    return resp

def test_iniciar_recorrido_success(test_client, session):
    """
    GIVEN a logged-in chofer and an available vehicle
    WHEN the '/api/recorridos/inicio' endpoint is called
    THEN a new recorrido should be created with state 'abierto'.
    """
    chofer, vehiculo = setup_test_data(session)
    login_user(test_client, "chofer@test.com", "password")

    inicio_data = {
        "vehiculo_id": str(vehiculo.id),
        "km_inicial": 10000
    }
    resp = test_client.post('/api/recorridos/inicio', json=inicio_data)

    assert resp.status_code == 201
    data = resp.json
    assert data['status'] == 'abierto'
    assert data['vehiculo_id'] == str(vehiculo.id)
    assert data['chofer_id'] == str(chofer.id)

    # Verify in DB
    recorrido_id_obj = uuid.UUID(data['id'])
    recorrido_db = session.get(Recorrido, recorrido_id_obj)
    assert recorrido_db is not None
    assert recorrido_db.status == 'abierto'

def test_iniciar_recorrido_fail_if_open(test_client, session):
    """
    GIVEN a chofer with an already open recorrido
    WHEN the '/api/recorridos/inicio' endpoint is called again
    THEN the request should fail.
    """
    chofer, vehiculo = setup_test_data(session)
    vehiculo2 = Vehiculo(patente="TEST002")
    session.add(vehiculo2)
    session.commit()

    login_user(test_client, "chofer@test.com", "password")

    # Create the first recorrido
    test_client.post('/api/recorridos/inicio', json={"vehiculo_id": str(vehiculo.id), "km_inicial": 100})

    # Attempt to create a second one
    resp = test_client.post('/api/recorridos/inicio', json={"vehiculo_id": str(vehiculo2.id), "km_inicial": 200})

    assert resp.status_code == 409
    assert "chofer ya tiene un recorrido abierto" in resp.json['msg']

def test_fin_recorrido_success(test_client, session):
    """
    GIVEN an open recorrido
    WHEN the '/api/recorridos/<id>/fin' endpoint is called
    THEN the recorrido should be 'cerrado'.
    """
    chofer, vehiculo = setup_test_data(session)
    login_user(test_client, "chofer@test.com", "password")

    # Create a recorrido to close
    inicio_resp = test_client.post('/api/recorridos/inicio', json={"vehiculo_id": str(vehiculo.id), "km_inicial": 10000})
    recorrido_id = inicio_resp.json['id']

    # End the recorrido
    fin_data = {
        "km_final": 10200
    }
    fin_resp = test_client.post(f'/api/recorridos/{recorrido_id}/fin', json=fin_data)

    assert fin_resp.status_code == 200
    assert fin_resp.json['status'] == 'cerrado'
    assert Decimal(fin_resp.json['km_final']) == Decimal('10200')

    # Verify in DB
    recorrido_id_obj = uuid.UUID(recorrido_id)
    recorrido_db = session.get(Recorrido, recorrido_id_obj)
    assert recorrido_db.status == 'cerrado'

def test_fin_recorrido_fail_bad_km(test_client, session):
    """
    GIVEN an open recorrido
    WHEN the 'fin' endpoint is called with km_final < km_inicial
    THEN the request should fail.
    """
    chofer, vehiculo = setup_test_data(session)
    login_user(test_client, "chofer@test.com", "password")

    inicio_resp = test_client.post('/api/recorridos/inicio', json={"vehiculo_id": str(vehiculo.id), "km_inicial": 10000})
    recorrido_id = inicio_resp.json['id']

    fin_data = {
        "km_final": 9000 # Less than initial
    }
    fin_resp = test_client.post(f'/api/recorridos/{recorrido_id}/fin', json=fin_data)

    assert fin_resp.status_code == 400
    assert "debe ser mayor al inicial" in fin_resp.json['msg']

def test_approve_recorrido(test_client, session):
    """
    GIVEN a 'cerrado' recorrido and a logged-in maintenance user
    WHEN the '/approve' endpoint is called
    THEN the recorrido status should be 'aprobado'.
    """
    chofer, vehiculo = setup_test_data(session)
    mantenimiento = Usuario(nombre="Test Maint", email="maint@test.com", rol="mantenimiento")
    mantenimiento.set_password("password")
    session.add(mantenimiento)
    session.commit()

    # Create and close a recorrido
    login_user(test_client, "chofer@test.com", "password")
    inicio_resp = test_client.post('/api/recorridos/inicio', json={"vehiculo_id": str(vehiculo.id), "km_inicial": 100})
    recorrido_id = inicio_resp.json['id']
    test_client.post(f'/api/recorridos/{recorrido_id}/fin', json={"km_final": 200})
    test_client.post('/api/auth/logout')

    # Login as maintenance and approve
    login_user(test_client, "maint@test.com", "password")
    approve_resp = test_client.post(f'/api/recorridos/{recorrido_id}/approve')

    assert approve_resp.status_code == 200

    recorrido_db = session.get(Recorrido, uuid.UUID(recorrido_id))
    assert recorrido_db.status == 'aprobado'
