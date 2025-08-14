import uuid
from flask import Blueprint, request, jsonify
from app.models import Usuario
from app.extensions import db
from app.utils.rbac import requires_roles
from flask_jwt_extended import jwt_required
from app.schemas.usuario import Usuario as UsuarioSchema, UsuarioUpdate # I might need a more specific admin update schema

bp = Blueprint('admin_users', __name__, url_prefix='/api/admin/users')

@bp.route('/', methods=['GET'])
@jwt_required()
@requires_roles('admin')
def list_users():
    """List all users. Admin only."""
    users = Usuario.query.all()
    return jsonify([UsuarioSchema.model_validate(u).model_dump() for u in users]), 200

@bp.route('/<uuid:user_id>', methods=['GET'])
@jwt_required()
@requires_roles('admin')
def get_user(user_id):
    """Get details of a single user. Admin only."""
    user = db.session.get(Usuario, user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    return jsonify(UsuarioSchema.model_validate(user).model_dump()), 200

@bp.route('/<uuid:user_id>', methods=['PUT'])
@jwt_required()
@requires_roles('admin')
def update_user(user_id):
    """Update a user's role or active status. Admin only."""
    user = db.session.get(Usuario, user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    data = request.get_json()
    # Using a generic dict for now, a specific AdminUsuarioUpdate schema would be better
    if 'rol' in data:
        user.rol = data['rol']
    if 'activo' in data:
        user.activo = data['activo']

    db.session.commit()
    db.session.refresh(user)
    return jsonify(UsuarioSchema.model_validate(user).model_dump()), 200


@bp.route('/<uuid:user_id>', methods=['DELETE'])
@jwt_required()
@requires_roles('admin')
def deactivate_user(user_id):
    """Deactivate a user (soft delete). Admin only."""
    user = db.session.get(Usuario, user_id)
    if not user:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    user.activo = False
    db.session.commit()
    return jsonify({"msg": "Usuario desactivado con éxito."}), 200

@bp.route('/<uuid:user_id>/approve', methods=['POST'])
@jwt_required()
@requires_roles('admin')
def approve_user(user_id):
    """Approve a pending user. Admin only."""
    user = db.session.get(Usuario, user_id)
    if not user:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    if user.activo:
        return jsonify({"msg": "El usuario ya está activo"}), 409

    user.activo = True
    db.session.commit()
    return jsonify({"msg": "Usuario aprobado con éxito."}), 200
