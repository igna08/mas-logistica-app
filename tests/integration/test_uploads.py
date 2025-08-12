import json
from unittest.mock import patch
from app.models import Usuario

def test_presign_endpoint(test_client, session):
    """
    GIVEN a logged-in user
    WHEN the '/api/uploads/presign' endpoint is called
    THEN it should return a valid pre-signed POST URL structure.
    """
    # Create and log in a user
    user = Usuario(nombre="Upload User", email="uploader@test.com", rol="chofer")
    user.set_password("password")
    session.add(user)
    session.commit()

    login_resp = test_client.post('/api/auth/login', json={
        "email": "uploader@test.com",
        "password": "password"
    })
    assert login_resp.status_code == 200

    # Mock the boto3 S3 client
    with patch('boto3.client') as mock_boto_client:
        # Configure the mock to return a predictable response
        mock_s3_instance = mock_boto_client.return_value
        mock_s3_instance.generate_presigned_post.return_value = {
            'url': 'https://mock-bucket.s3.amazonaws.com/',
            'fields': {
                'Content-Type': 'image/jpeg',
                'key': 'test.jpg',
                'AWSAccessKeyId': 'FAKE_KEY',
                'policy': 'FAKE_POLICY',
                'signature': 'FAKE_SIGNATURE',
            }
        }

        # Call the endpoint
        presign_data = {
            "filename": "test.jpg",
            "content_type": "image/jpeg"
        }
        resp = test_client.post('/api/uploads/presign', json=presign_data)

        # Assertions
        assert resp.status_code == 200
        data = resp.json
        assert data['url'] == 'https://mock-bucket.s3.amazonaws.com/'
        assert 'fields' in data
        assert data['fields']['key'] == 'test.jpg'

        # Verify that our mock was called correctly
        mock_boto_client.assert_called_once_with(
            's3',
            endpoint_url=None, # In testing, these are None from config
            aws_access_key_id=None,
            aws_secret_access_key=None,
            region_name=None
        )
        mock_s3_instance.generate_presigned_post.assert_called_once()
