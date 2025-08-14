from flask import Blueprint, jsonify
from app.extensions import db
from app.models import Recorrido, Vehiculo
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from collections import defaultdict

from app.utils.rbac import requires_roles
from flask_jwt_extended import jwt_required

bp = Blueprint('admin_dashboard_api', __name__, url_prefix='/api/admin/dashboard')

@bp.route('/chart-data', methods=['GET'])
@jwt_required()
@requires_roles('admin')
def chart_data():
    """
    Provides data aggregated for the admin dashboard charts.
    """
    # Kilometers per month for the last 6 months
    today = datetime.utcnow()
    six_months_ago = today - timedelta(days=180)

    kms_per_month_query = db.session.query(
        extract('year', Recorrido.fecha_inicio).label('year'),
        extract('month', Recorrido.fecha_inicio).label('month'),
        func.sum(Recorrido.km_final - Recorrido.km_inicial).label('total_km')
    ).filter(
        Recorrido.fecha_inicio >= six_months_ago,
        Recorrido.km_final.isnot(None)
    ).group_by('year', 'month').order_by('year', 'month').all()

    km_chart_labels = []
    km_chart_data = []
    for row in kms_per_month_query:
        # Format as 'YYYY-MM'
        km_chart_labels.append(f"{int(row.year)}-{int(row.month):02d}")
        km_chart_data.append(float(row.total_km))

    # Fuel cost per vehicle
    fuel_per_vehicle_query = db.session.query(
        Vehiculo.patente,
        func.sum(Recorrido.combustible_costo).label('total_costo')
    ).join(Vehiculo, Recorrido.vehiculo_id == Vehiculo.id).filter(
        Recorrido.combustible_costo.isnot(None)
    ).group_by(Vehiculo.patente).order_by(func.sum(Recorrido.combustible_costo).desc()).all()

    fuel_chart_labels = [row.patente for row in fuel_per_vehicle_query]
    fuel_chart_data = [float(row.total_costo) for row in fuel_per_vehicle_query]

    return jsonify({
        "km_chart": {
            "labels": km_chart_labels,
            "data": km_chart_data,
        },
        "fuel_chart": {
            "labels": fuel_chart_labels,
            "data": fuel_chart_data,
        }
    })
