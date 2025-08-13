import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError

from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioUpdate, Usuario as UsuarioSchema
from app.extensions import db

bp = Blueprint('users', __name__, url_prefix='/api/users')

@bp.route('/me', methods=['PUT'])
@jwt_required()
def update_me():
    """Update the current user's profile."""
    current_user_id_str = get_jwt_identity()
    try:
        current_user_id = uuid.UUID(current_user_id_str)
    except ValueError:
        return jsonify({"msg": "Invalid user ID format"}), 400

    user = db.session.get(Usuario, current_user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    try:
        update_data = UsuarioUpdate.model_validate(request.json)
    except ValidationError as e:
        return jsonify(e.errors()), 400

    # Update only the fields that were provided
    if update_data.nombre is not None:
        user.nombre = update_data.nombre
    if update_data.profile_picture_url is not None:
        user.profile_picture_url = update_data.profile_picture_url

    db.session.commit()
    db.session.refresh(user)

    return jsonify(UsuarioSchema.model_validate(user).model_dump()), 200
