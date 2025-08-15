import uuid
from flask import Blueprint, request, jsonify
from app.models import Usuario
from app.extensions import db
from app.utils.rbac import requires_roles
from flask_jwt_extended import jwt_required
from app.schemas.usuario import Usuario as UsuarioSchema, UsuarioUpdate
from pydantic import ValidationError

bp = Blueprint('admin_users', __name__, url_prefix='/api/admin/users')

@bp.route('/', methods=['GET'])
@jwt_required()
@requires_roles('admin')
def list_users():
    """List all users. Admin only."""
    try:
        users = Usuario.query.all()
        return jsonify([UsuarioSchema.model_validate(u).model_dump() for u in users]), 200
    except Exception as e:
        return jsonify({"msg": "Error retrieving users", "error": str(e)}), 500

@bp.route('/<uuid:user_id>', methods=['GET'])
@jwt_required()
@requires_roles('admin')
def get_user(user_id):
    """Get details of a single user. Admin only."""
    try:
        user = db.session.get(Usuario, user_id)
        if not user:
            return jsonify({"msg": "User not found"}), 404
        return jsonify(UsuarioSchema.model_validate(user).model_dump()), 200
    except Exception as e:
        return jsonify({"msg": "Error retrieving user", "error": str(e)}), 500

@bp.route('/<uuid:user_id>', methods=['PUT'])
@jwt_required()
@requires_roles('admin')
def update_user(user_id):
    """Update a user's information. Admin only."""
    try:
        user = db.session.get(Usuario, user_id)
        if not user:
            return jsonify({"msg": "User not found"}), 404

        data = request.get_json()
        if not data:
            return jsonify({"msg": "No data provided"}), 400

        # Validate input data
        valid_roles = ['chofer', 'mantenimiento', 'admin']
        
        # Update nombre if provided
        if 'nombre' in data:
            if not data['nombre'] or not data['nombre'].strip():
                return jsonify({"msg": "El nombre no puede estar vacío"}), 400
            user.nombre = data['nombre'].strip()

        # Update rol if provided
        if 'rol' in data:
            if data['rol'] not in valid_roles:
                return jsonify({"msg": f"Rol inválido. Debe ser uno de: {', '.join(valid_roles)}"}), 400
            user.rol = data['rol']
        
        # Update activo status if provided
        if 'activo' in data:
            if not isinstance(data['activo'], bool):
                return jsonify({"msg": "El campo 'activo' debe ser verdadero o falso"}), 400
            user.activo = data['activo']

        db.session.commit()
        db.session.refresh(user)
        
        return jsonify({
            "msg": "Usuario actualizado exitosamente",
            "user": UsuarioSchema.model_validate(user).model_dump()
        }), 200

    except ValidationError as e:
        return jsonify({"msg": "Error de validación", "errors": e.errors()}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error al actualizar usuario", "error": str(e)}), 500

@bp.route('/<uuid:user_id>', methods=['DELETE'])
@jwt_required()
@requires_roles('admin')
def deactivate_user(user_id):
    """Deactivate a user (soft delete). Admin only."""
    user = db.session.get(Usuario, user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    user.activo = False
    db.session.commit()
    return jsonify({"msg": "User deactivated successfully"}), 200

@bp.route('/<uuid:user_id>/approve', methods=['POST'])
@jwt_required()
@requires_roles('admin')
def approve_user(user_id):
    """Approve a pending user. Admin only."""
    user = db.session.get(Usuario, user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    if user.activo:
        return jsonify({"msg": "User is already active"}), 409

    user.activo = True
    db.session.commit()
    return jsonify({"msg": "User approved successfully"}), 200
