import uuid
from flask import Blueprint, request, jsonify
from app.models import Usuario, Vehiculo
from app.extensions import db
from app.utils.rbac import requires_roles
from flask_jwt_extended import jwt_required

bp = Blueprint('assignments', __name__, url_prefix='/api/assignments')

@bp.route('/', methods=['POST'])
@jwt_required()
@requires_roles('admin', 'mantenimiento')
def assign_driver_to_vehicle():
    """Assign a driver to a vehicle."""
    data = request.get_json()
    chofer_id = data.get('chofer_id')
    vehiculo_id = data.get('vehiculo_id')

    if not chofer_id or not vehiculo_id:
        return jsonify({"msg": "chofer_id and vehiculo_id are required"}), 400

    chofer = db.session.get(Usuario, uuid.UUID(chofer_id))
    vehiculo = db.session.get(Vehiculo, uuid.UUID(vehiculo_id))

    if not chofer or not vehiculo:
        return jsonify({"msg": "User or Vehicle not found"}), 404

    if chofer.rol != 'chofer':
        return jsonify({"msg": "Can only assign users with 'chofer' role"}), 400

    vehiculo.choferes_asignados.append(chofer)
    db.session.commit()

    return jsonify({"msg": f"Driver {chofer.nombre} assigned to vehicle {vehiculo.patente}"}), 200


@bp.route('/', methods=['DELETE'])
@jwt_required()
@requires_roles('admin', 'mantenimiento')
def unassign_driver_from_vehicle():
    """Unassign a driver from a vehicle."""
    data = request.get_json()
    chofer_id = data.get('chofer_id')
    vehiculo_id = data.get('vehiculo_id')

    if not chofer_id or not vehiculo_id:
        return jsonify({"msg": "chofer_id and vehiculo_id are required"}), 400

    chofer = db.session.get(Usuario, uuid.UUID(chofer_id))
    vehiculo = db.session.get(Vehiculo, uuid.UUID(vehiculo_id))

    if not chofer or not vehiculo:
        return jsonify({"msg": "User or Vehicle not found"}), 404

    if chofer in vehiculo.choferes_asignados:
        vehiculo.choferes_asignados.remove(chofer)
        db.session.commit()
        return jsonify({"msg": f"Driver {chofer.nombre} unassigned from vehicle {vehiculo.patente}"}), 200
    else:
        return jsonify({"msg": "Driver is not assigned to this vehicle"}), 404
