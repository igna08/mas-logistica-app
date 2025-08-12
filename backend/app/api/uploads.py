import boto3
import os
from botocore.exceptions import ClientError
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required

bp = Blueprint('uploads', __name__, url_prefix='/api/uploads')

@bp.route('/presign', methods=['POST'])
@jwt_required()
def create_presigned_post():
    """
    Generate a pre-signed URL S3 POST request to upload a file.
    Takes a JSON body with 'filename' and 'content_type'.
    """
    data = request.get_json()
    filename = data.get('filename')
    content_type = data.get('content_type')

    if not filename or not content_type:
        return jsonify({"msg": "filename and content_type are required"}), 400

    # It's good practice to generate a unique key for the object in S3
    # For example, using uuid.uuid4()
    # object_name = f"uploads/{uuid.uuid4()}/{filename}"
    object_name = filename # For simplicity in this example

    s3_client = boto3.client(
        's3',
        endpoint_url=current_app.config.get('S3_ENDPOINT_URL'),
        aws_access_key_id=current_app.config.get('S3_ACCESS_KEY_ID'),
        aws_secret_access_key=current_app.config.get('S3_SECRET_ACCESS_KEY'),
        region_name=current_app.config.get('S3_REGION')
    )

    bucket_name = current_app.config.get('S3_BUCKET_NAME')

    # Generate the pre-signed POST
    try:
        response = s3_client.generate_presigned_post(
            Bucket=bucket_name,
            Key=object_name,
            Fields={"Content-Type": content_type},
            Conditions=[{"Content-Type": content_type}],
            ExpiresIn=3600  # URL expires in 1 hour
        )
    except ClientError as e:
        current_app.logger.error(f"Error generating presigned URL: {e}")
        return jsonify({"msg": "Could not generate upload URL"}), 500

    return jsonify(response), 200
