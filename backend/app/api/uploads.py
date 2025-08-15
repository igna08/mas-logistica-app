import uuid
import boto3
import os
from botocore.exceptions import ClientError
from flask import Blueprint, request, jsonify, current_app
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required

bp = Blueprint('uploads', __name__, url_prefix='/api/uploads')

@bp.route('/presign', methods=['POST'])
@cross_origin()  # Add CORS support
def create_presigned_post():
    """
    Generate a pre-signed URL S3 POST request to upload a file.
    Takes a JSON body with 'filename' and 'content_type'.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"msg": "Request body must be JSON"}), 400
            
        filename = data.get('filename')
        content_type = data.get('content_type')

        if not filename or not content_type:
            return jsonify({"msg": "filename and content_type are required"}), 400

        # Validate content type (optional but recommended)
        allowed_types = [
            'image/jpeg', 'image/png', 'image/gif', 'image/webp',
            'application/pdf', 'text/plain', 'application/json'
        ]
        if content_type not in allowed_types:
            return jsonify({"msg": f"Content type {content_type} not allowed"}), 400

        # Generate a unique key for the object in S3
        unique_filename = f"uploads/{uuid.uuid4()}/{filename}"

        # Validate S3 configuration
        required_config = ['S3_ENDPOINT_URL', 'S3_ACCESS_KEY_ID', 'S3_SECRET_ACCESS_KEY', 'S3_BUCKET_NAME', 'S3_REGION']
        missing_config = [key for key in required_config if not current_app.config.get(key)]
        if missing_config:
            current_app.logger.error(f"Missing S3 configuration: {missing_config}")
            return jsonify({"msg": "Server configuration error"}), 500

        # Create S3 client with error handling
        try:
            s3_client = boto3.client(
                's3',
                endpoint_url=current_app.config.get('S3_ENDPOINT_URL'),
                aws_access_key_id=current_app.config.get('S3_ACCESS_KEY_ID'),
                aws_secret_access_key=current_app.config.get('S3_SECRET_ACCESS_KEY'),
                region_name=current_app.config.get('S3_REGION')
            )
        except boto3.exceptions.NoCredentialsError:
            current_app.logger.error("S3 credentials not found or invalid")
            return jsonify({"msg": "Server configuration error"}), 500

        bucket_name = current_app.config.get('S3_BUCKET_NAME')

        # Test bucket access first
        try:
            s3_client.head_bucket(Bucket=bucket_name)
        except ClientError as e:
            error_code = int(e.response['Error']['Code'])
            if error_code == 404:
                current_app.logger.error(f"Bucket {bucket_name} not found")
                return jsonify({"msg": "Storage configuration error"}), 500
            elif error_code == 403:
                current_app.logger.error(f"Access denied to bucket {bucket_name}")
                return jsonify({"msg": "Storage access error"}), 500
            else:
                current_app.logger.error(f"Error accessing bucket: {e}")
                return jsonify({"msg": "Storage error"}), 500

        # Generate the pre-signed POST with proper conditions
        try:
            conditions = [
                {"Content-Type": content_type},
                ["content-length-range", 1, 10485760]  # 1 byte to 10MB
            ]
            
            response = s3_client.generate_presigned_post(
                Bucket=bucket_name,
                Key=unique_filename,
                Fields={
                    "Content-Type": content_type,
                },
                Conditions=conditions,
                ExpiresIn=3600  # URL expires in 1 hour
            )
            
            # Add the final URL where the file will be accessible
            file_url = f"{current_app.config.get('S3_ENDPOINT_URL')}/{bucket_name}/{unique_filename}"
            response['file_url'] = file_url
            
        except ClientError as e:
            current_app.logger.error(f"Error generating presigned URL: {e}")
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            return jsonify({"msg": f"Could not generate upload URL: {error_code}"}), 500

        current_app.logger.info(f"Generated presigned URL for file: {unique_filename}")
        return jsonify(response), 200

    except Exception as e:
        current_app.logger.error(f"Unexpected error in create_presigned_post: {str(e)}")
        return jsonify({"msg": "Internal server error"}), 500


@bp.route('/upload', methods=['POST'])
@cross_origin()
def upload_file():
    """
    Upload a file directly to S3 through the backend.
    Accepts multipart/form-data with file field.
    No JWT required for now - can be added if needed.
    """
    try:
        if 'file' not in request.files:
            return jsonify({"msg": "No file provided"}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({"msg": "No file selected"}), 400

        # Validate file type
        allowed_types = [
            'image/jpeg', 'image/png', 'image/gif', 'image/webp',
            'application/pdf', 'text/plain', 'application/json'
        ]
        
        if file.content_type not in allowed_types:
            return jsonify({"msg": f"Content type {file.content_type} not allowed"}), 400

        # Validate file size (10MB max)
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > 10485760:  # 10MB
            return jsonify({"msg": "File too large (max 10MB)"}), 400

        # Generate unique filename
        unique_filename = f"uploads/{uuid.uuid4()}/{file.filename}"

        # Validate S3 configuration
        required_config = ['S3_ENDPOINT_URL', 'S3_ACCESS_KEY_ID', 'S3_SECRET_ACCESS_KEY', 'S3_BUCKET_NAME', 'S3_REGION']
        missing_config = [key for key in required_config if not current_app.config.get(key)]
        if missing_config:
            current_app.logger.error(f"Missing S3 configuration: {missing_config}")
            return jsonify({"msg": "Server configuration error"}), 500

        # Create S3 client
        try:
            s3_client = boto3.client(
                's3',
                endpoint_url=current_app.config.get('S3_ENDPOINT_URL'),
                aws_access_key_id=current_app.config.get('S3_ACCESS_KEY_ID'),
                aws_secret_access_key=current_app.config.get('S3_SECRET_ACCESS_KEY'),
                region_name=current_app.config.get('S3_REGION')
            )
        except boto3.exceptions.NoCredentialsError:
            current_app.logger.error("S3 credentials not found or invalid")
            return jsonify({"msg": "Server configuration error"}), 500

        bucket_name = current_app.config.get('S3_BUCKET_NAME')

        # Test bucket access first
        try:
            s3_client.head_bucket(Bucket=bucket_name)
        except ClientError as e:
            error_code = int(e.response['Error']['Code'])
            if error_code == 404:
                current_app.logger.error(f"Bucket {bucket_name} not found")
                return jsonify({"msg": "Storage configuration error"}), 500
            elif error_code == 403:
                current_app.logger.error(f"Access denied to bucket {bucket_name}")
                return jsonify({"msg": "Storage access error"}), 500
            else:
                current_app.logger.error(f"Error accessing bucket: {e}")
                return jsonify({"msg": "Storage error"}), 500

        # Upload file directly
        try:
            s3_client.upload_fileobj(
                file,
                bucket_name,
                unique_filename,
                ExtraArgs={
                    'ContentType': file.content_type
                }
            )
            
            # Generate the final URL
            file_url = f"{current_app.config.get('S3_ENDPOINT_URL')}/{bucket_name}/{unique_filename}"
            
            current_app.logger.info(f"File uploaded successfully: {unique_filename}")
            return jsonify({
                "file_url": file_url,
                "filename": unique_filename,
                "msg": "File uploaded successfully"
            }), 200
            
        except ClientError as e:
            current_app.logger.error(f"Error uploading to S3: {e}")
            return jsonify({"msg": "Failed to upload file to storage"}), 500

    except Exception as e:
        current_app.logger.error(f"Unexpected error in upload_file: {str(e)}")
        return jsonify({"msg": "Internal server error"}), 500