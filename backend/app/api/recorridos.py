import uuid
from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from app.models.recorrido import Recorrido as RecorridoModel
from app.models.vehiculo import Vehiculo as VehiculoModel
from app.schemas.recorrido import RecorridoCreate, RecorridoEnd, Recorrido as RecorridoSchema
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.rbac import requires_roles

bp = Blueprint('recorridos', __name__, url_prefix='/api/recorridos')

@bp.route('/inicio', methods=['POST'])
@jwt_required()
@requires_roles('chofer')
def iniciar_recorrido():
    """Start a new recorrido."""
    chofer_id_str = get_jwt_identity()
    try:
        chofer_id = uuid.UUID(chofer_id_str)
    except ValueError:
        return jsonify({"msg": "Invalid user ID format"}), 400

    try:
        data = RecorridoCreate.model_validate(request.json)
    except ValidationError as e:
        return jsonify(e.errors()), 400

    # Validate that the vehicle exists and is active
    vehiculo = db.session.get(VehiculoModel, data.vehiculo_id)
    if not vehiculo or not vehiculo.activo:
        return jsonify({"msg": "Vehículo no disponible o no existe"}), 404

    # Validate that there is no open recorrido for the chofer or the vehiculo
    open_recorrido_chofer = RecorridoModel.query.filter_by(chofer_id=chofer_id, status='abierto').first()
    if open_recorrido_chofer:
        return jsonify({"msg": "El chofer ya tiene un recorrido abierto"}), 409

    open_recorrido_vehiculo = RecorridoModel.query.filter_by(vehiculo_id=data.vehiculo_id, status='abierto').first()
    if open_recorrido_vehiculo:
        return jsonify({"msg": "El vehículo ya tiene un recorrido abierto"}), 409

    # Create new recorrido
    nuevo_recorrido = RecorridoModel(
        chofer_id=chofer_id,
        **data.model_dump()
    )

    db.session.add(nuevo_recorrido)
    db.session.commit()
    db.session.refresh(nuevo_recorrido)

    return jsonify(RecorridoSchema.model_validate(nuevo_recorrido).model_dump()), 201


@bp.route('/<uuid:recorrido_id>/fin', methods=['POST'])
@jwt_required()
@requires_roles('chofer')
def fin_recorrido(recorrido_id):
    """End a recorrido."""
    chofer_id_str = get_jwt_identity()
    try:
        chofer_id = uuid.UUID(chofer_id_str)
    except ValueError:
        return jsonify({"msg": "Invalid user ID format"}), 400

    recorrido = RecorridoModel.query.filter_by(id=recorrido_id, chofer_id=chofer_id, status='abierto').first()
    if not recorrido:
        return jsonify({"msg": "Recorrido no encontrado o no autorizado"}), 404

    try:
        data = RecorridoEnd.model_validate(request.json)
    except ValidationError as e:
        return jsonify(e.errors()), 400

    if data.km_final <= recorrido.km_inicial:
        return jsonify({"msg": "El kilometraje final debe ser mayor al inicial"}), 400

    # Update recorrido with final data
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(recorrido, key, value)

    recorrido.status = 'cerrado'
    recorrido.fecha_fin = db.func.now()

    db.session.commit()
    db.session.refresh(recorrido)

    return jsonify(RecorridoSchema.model_validate(recorrido).model_dump()), 200


@bp.route('/', methods=['GET'])
@jwt_required()
def listar_recorridos():
    """List all recorridos with filters."""
    # Basic implementation without filters for now
    recorridos = RecorridoModel.query.order_by(RecorridoModel.fecha_inicio.desc()).all()
    results = [RecorridoSchema.model_validate(r).model_dump(exclude={'controles', 'alertas'}) for r in recorridos]
    return jsonify(results), 200


@bp.route('/<uuid:recorrido_id>', methods=['GET'])
@jwt_required()
def detalle_recorrido(recorrido_id):
    """Get details of a specific recorrido, including controls and alerts."""
    recorrido = db.session.get(RecorridoModel, recorrido_id)
    if not recorrido:
        return jsonify({"msg": "Recorrido not found"}), 404
    return jsonify(RecorridoSchema.model_validate(recorrido).model_dump()), 200

@bp.route('/<uuid:recorrido_id>/approve', methods=['POST'])
@jwt_required()
@requires_roles('admin', 'mantenimiento')
def approve_recorrido(recorrido_id):
    """Approve a completed recorrido. Admin/Mantenimiento only."""
    recorrido = db.session.get(RecorridoModel, recorrido_id)
    if not recorrido:
        return jsonify({"msg": "Recorrido not found"}), 404

    if recorrido.status != 'cerrado':
        return jsonify({"msg": f"Recorrido is not pending approval (status: {recorrido.status})"}), 409

    recorrido.status = 'aprobado'
    db.session.commit()
    return jsonify({"msg": "Recorrido approved successfully"}), 200

@bp.route('/<uuid:recorrido_id>/reject', methods=['POST'])
@jwt_required()
@requires_roles('admin', 'mantenimiento')
def reject_recorrido(recorrido_id):
    """Mark a recorrido as needing review/rejection. Admin/Mantenimiento only."""
    recorrido = db.session.get(RecorridoModel, recorrido_id)
    if not recorrido:
        return jsonify({"msg": "Recorrido not found"}), 404

    if recorrido.status != 'cerrado':
        return jsonify({"msg": f"Recorrido is not pending approval (status: {recorrido.status})"}), 409

    recorrido.status = 'revision_requerida'
    # Here you might also create an Alerta for the chofer
    db.session.commit()
    return jsonify({"msg": "Recorrido marked for revision"}), 200
