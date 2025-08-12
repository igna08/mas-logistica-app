from functools import wraps
from flask_jwt_extended import get_jwt
from flask import jsonify

def requires_roles(*roles):
    """
    A decorator to protect endpoints based on user roles.
    Example: @requires_roles('admin', 'mantenimiento')
    """
    def wrapper(fn):
        @wraps(fn)
        def decorated_function(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get("rol")
            if user_role not in roles:
                return jsonify(msg="No autorizado para realizar esta acción"), 403
            return fn(*args, **kwargs)
        return decorated_function
    return wrapper
