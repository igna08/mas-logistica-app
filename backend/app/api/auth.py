import uuid
from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies, jwt_required, get_jwt_identity, get_jwt
from app.models.usuario import Usuario
from app.extensions import db
from app.utils.rbac import requires_roles

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"msg": "Email y password son requeridos"}), 400

    user = Usuario.query.filter_by(email=data['email']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({"msg": "Credenciales inválidas"}), 401

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"rol": user.rol}
    )

    resp = jsonify({"login": True, "rol": user.rol})
    set_access_cookies(resp, access_token)
    return resp, 200

@bp.route('/logout', methods=['POST'])
def logout():
    resp = jsonify({"logout": True})
    unset_jwt_cookies(resp)
    return resp, 200

@bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    current_user_id_str = get_jwt_identity()
    try:
        current_user_id = uuid.UUID(current_user_id_str)
    except ValueError:
        return jsonify({"msg": "Invalid user ID format"}), 400

    user = db.session.get(Usuario, current_user_id)
    if not user:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    return jsonify({
        "id": user.id,
        "nombre": user.nombre,
        "email": user.email,
        "rol": user.rol
    }), 200

@bp.route('/register', methods=['POST'])
@jwt_required()
@requires_roles('admin')
def register():
    # Only admins can create new users
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password') or not data.get('nombre') or not data.get('rol'):
        return jsonify({"msg": "Faltan campos requeridos"}), 400

    if Usuario.query.filter_by(email=data['email']).first():
        return jsonify({"msg": "El email ya está en uso"}), 409

    new_user = Usuario(
        email=data['email'],
        nombre=data['nombre'],
        rol=data['rol']
    )
    new_user.set_password(data['password'])

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "Usuario creado exitosamente", "id": new_user.id}), 201
