from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from app.models.vehiculo import Vehiculo as VehiculoModel
from app.schemas.vehiculo import VehiculoCreate, VehiculoUpdate, Vehiculo as VehiculoSchema
from app.extensions import db
from flask_jwt_extended import jwt_required
from app.utils.rbac import requires_roles

bp = Blueprint('vehiculos', __name__, url_prefix='/api/vehiculos')

@bp.route('/', methods=['POST'])
@jwt_required()
@requires_roles('admin')
def create_vehiculo():
    """Create a new vehicle. Admin only."""
    try:
        vehiculo_data = VehiculoCreate.model_validate(request.json)
    except ValidationError as e:
        return jsonify(e.errors()), 400

    if VehiculoModel.query.filter_by(patente=vehiculo_data.patente).first():
        return jsonify({"msg": "La patente ya existe"}), 409

    new_vehiculo = VehiculoModel(**vehiculo_data.model_dump())
    db.session.add(new_vehiculo)
    db.session.commit()
    db.session.refresh(new_vehiculo)

    return jsonify(VehiculoSchema.model_validate(new_vehiculo).model_dump()), 201


@bp.route('/', methods=['GET'])
@jwt_required()
def get_vehiculos():
    """Get a list of all vehicles."""
    vehiculos = VehiculoModel.query.all()
    # Pydantic v2 .model_dump() is equivalent to v1 .dict()
    results = [VehiculoSchema.model_validate(v).model_dump() for v in vehiculos]
    return jsonify(results), 200


@bp.route('/<uuid:vehiculo_id>', methods=['GET'])
@jwt_required()
def get_vehiculo(vehiculo_id):
    """Get a single vehicle by ID."""
    vehiculo = VehiculoModel.query.get_or_404(vehiculo_id)
    return jsonify(VehiculoSchema.model_validate(vehiculo).model_dump()), 200


@bp.route('/<uuid:vehiculo_id>', methods=['PUT'])
@jwt_required()
@requires_roles('admin')
def update_vehiculo(vehiculo_id):
    """Update a vehicle. Admin only."""
    vehiculo = VehiculoModel.query.get_or_404(vehiculo_id)

    try:
        update_data = VehiculoUpdate.model_validate(request.json)
    except ValidationError as e:
        return jsonify(e.errors()), 400

    # model_dump(exclude_unset=True) ensures we only update provided fields
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(vehiculo, key, value)

    db.session.commit()
    db.session.refresh(vehiculo)

    return jsonify(VehiculoSchema.model_validate(vehiculo).model_dump()), 200
