from unittest.mock import patch
import uuid
from app.models import Usuario, Vehiculo, Recorrido

def login(test_client, email, password):
    """Helper function to log in a user."""
    return test_client.post('/api/auth/login', json={"email": email, "password": password})

def setup_closed_recorrido(session):
    """Helper function to create users and a closed recorrido."""
    admin = Usuario(nombre="Test Admin", email="admin@test.com", rol="admin")
    admin.set_password("password")
    chofer = Usuario(nombre="Test Chofer", email="chofer@test.com", rol="chofer")
    chofer.set_password("password")
    vehiculo = Vehiculo(patente="AITEST")
    recorrido = Recorrido(chofer=chofer, vehiculo=vehiculo, status='cerrado', km_inicial=100, km_final=200)
    session.add_all([admin, chofer, vehiculo, recorrido])
    session.commit()
    return admin, recorrido

def test_ai_summary_endpoint(test_client, session):
    """
    GIVEN a logged-in admin and a recorrido
    WHEN the ai-summary endpoint is called
    THEN it should return a summary from the mocked AI service.
    """
    admin, recorrido = setup_closed_recorrido(session)
    login(test_client, "admin@test.com", "password")

    with patch('app.api.recorridos.OpenAI') as mock_openai:
        mock_instance = mock_openai.return_value
        mock_instance.chat.completions.create.return_value.choices[0].message.content = "This is a test AI summary."

        resp = test_client.post(f'/api/recorridos/{recorrido.id}/ai-summary')

        assert resp.status_code == 200
        assert resp.json['summary'] == "This is a test AI summary."
        mock_instance.chat.completions.create.assert_called_once()

@patch('app.tasks.extract_receipt_data.delay')
def test_ocr_task_trigger(mock_task_delay, test_client, session):
    """
    GIVEN a chofer ending a trip with a fuel photo
    WHEN the 'fin_recorrido' endpoint is called
    THEN the 'extract_receipt_data' Celery task should be triggered.
    """
    chofer = Usuario(nombre="OCR Chofer", email="ocr@test.com", rol="chofer")
    chofer.set_password("password")
    vehiculo = Vehiculo(patente="OCRTEST")
    recorrido = Recorrido(chofer=chofer, vehiculo=vehiculo, status='abierto', km_inicial=1000)
    session.add_all([chofer, vehiculo, recorrido])
    session.commit()

    login(test_client, "ocr@test.com", "password")

    fin_data = {
        "km_final": 1200,
        "combustible_foto": "https://example.com/receipt.jpg"
    }
    test_client.post(f'/api/recorridos/{recorrido.id}/fin', json=fin_data)

    # Assert that the task's .delay() method was called once with the correct arguments
    mock_task_delay.assert_called_once_with(str(recorrido.id), "https://example.com/receipt.jpg")
