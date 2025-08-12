import uuid
from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from app.models.control import Control as ControlModel
from app.models.recorrido import Recorrido as RecorridoModel
from app.schemas.control import ControlCreate, Control as ControlSchema
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.rbac import requires_roles

bp = Blueprint('controles', __name__, url_prefix='/api')

@bp.route('/controles', methods=['POST'])
@jwt_required()
@requires_roles('chofer')
def create_control():
    """Create a new control for a recorrido."""
    chofer_id_str = get_jwt_identity()
    try:
        chofer_id = uuid.UUID(chofer_id_str)
    except ValueError:
        return jsonify({"msg": "Invalid user ID format"}), 400

    try:
        data = ControlCreate.model_validate(request.json)
    except ValidationError as e:
        return jsonify(e.errors()), 400

    # Verify that the recorrido exists, is open, and belongs to the current chofer
    recorrido = RecorridoModel.query.filter_by(
        id=data.recorrido_id,
        chofer_id=chofer_id,
        estado='abierto'
    ).first()

    if not recorrido:
        return jsonify({"msg": "Recorrido no válido, no encontrado o no pertenece al chofer"}), 404

    nuevo_control = ControlModel(**data.model_dump())
    db.session.add(nuevo_control)
    db.session.commit()
    db.session.refresh(nuevo_control)

    return jsonify(ControlSchema.model_validate(nuevo_control).model_dump()), 201


@bp.route('/recorridos/<uuid:recorrido_id>/controles', methods=['GET'])
@jwt_required()
def get_controles_for_recorrido(recorrido_id):
    """Get all controls for a specific recorrido."""
    # Verify that the recorrido exists before querying controls
    RecorridoModel.query.get_or_404(recorrido_id)

    controles = ControlModel.query.filter_by(recorrido_id=recorrido_id).all()
    results = [ControlSchema.model_validate(c).model_dump() for c in controles]

    return jsonify(results), 200
