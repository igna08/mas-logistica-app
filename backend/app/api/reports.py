from flask import Blueprint, jsonify, request
from app.extensions import db
from app.models import Usuario, Vehiculo, Recorrido
from app.schemas.recorrido import Recorrido as RecorridoSchema
from sqlalchemy import func, extract
from datetime import datetime

from app.utils.rbac import requires_roles
from flask_jwt_extended import jwt_required

bp = Blueprint('reports_api', __name__, url_prefix='/api/reports')

@bp.route('/', methods=['GET'])
@jwt_required()
@requires_roles('admin', 'mantenimiento')
def get_filtered_recorridos():
    """
    Returns a filtered list of recorridos as JSON.
    """
    query = Recorrido.query

    # Filtering logic
    chofer_id = request.args.get('chofer')
    vehiculo_id = request.args.get('vehiculo')
    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')

    if chofer_id:
        query = query.filter(Recorrido.chofer_id == chofer_id)
    if vehiculo_id:
        query = query.filter(Recorrido.vehiculo_id == vehiculo_id)
    if fecha_desde:
        query = query.filter(Recorrido.fecha_inicio >= fecha_desde)
    if fecha_hasta:
        query = query.filter(Recorrido.fecha_inicio <= fecha_hasta)

    recorridos = query.order_by(Recorrido.fecha_inicio.desc()).all()

    # We need to manually serialize because the nested objects (chofer, vehiculo) need to be accessed
    results = []
    for r in recorridos:
        recorrido_data = RecorridoSchema.model_validate(r).model_dump()
        recorrido_data['chofer_nombre'] = r.chofer.nombre
        recorrido_data['vehiculo_patente'] = r.vehiculo.patente
        results.append(recorrido_data)

    return jsonify(results)
