from functools import wraps
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, g
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
import uuid

from app.models import Usuario, Vehiculo, Recorrido
from app.extensions import db

bp = Blueprint('main', __name__)

def get_current_user_role():
    """
    A helper function to get the current user and their role from the JWT.
    Stores the user in Flask's `g` object for the duration of the request.
    Returns the user object or None.
    """
    if hasattr(g, 'current_user'):
        return g.current_user

    try:
        verify_jwt_in_request(optional=True)
        user_identity = get_jwt_identity()
        if user_identity:
            user_id = uuid.UUID(user_identity)
            user = db.session.get(Usuario, user_id)
            g.current_user = user
            return user
    except Exception:
        g.current_user = None
        return None

    g.current_user = None
    return None

@bp.context_processor
def inject_user_and_now():
    """Inject 'current_user' and 'now' into all templates."""
    return dict(current_user=get_current_user_role(), now=datetime.utcnow)

def login_required_for_templates(f):
    """A decorator for template routes that require a logged-in user."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if get_current_user_role() is None:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/')
def index():
    """Redirects to the login page or a role-based dashboard."""
    user = get_current_user_role()
    if not user:
        return redirect(url_for('main.login'))

    if user.rol == 'admin':
        return redirect(url_for('main.admin_dashboard'))
    elif user.rol == 'mantenimiento':
        return redirect(url_for('main.mantenimiento_panel'))
    else: # chofer
        return redirect(url_for('main.chofer_dashboard'))

@bp.route('/login')
def login():
    """Renders the login page."""
    return render_template('login.html')

@bp.route('/admin/dashboard')
@login_required_for_templates
def admin_dashboard():
    # Placeholder data for now
    return render_template('admin/dashboard.html')

@bp.route('/mantenimiento/panel')
@login_required_for_templates
def mantenimiento_panel():
    recorridos_pendientes = Recorrido.query.filter_by(estado='cerrado').order_by(Recorrido.fecha_fin.desc()).all()
    # A real implementation would have another state like 'en_revision'
    return render_template('mantenimiento/panel.html', recorridos=recorridos_pendientes)

@bp.route('/chofer/dashboard')
@login_required_for_templates
def chofer_dashboard():
    user = get_current_user_role()
    # Find if the chofer has an open recorrido
    open_recorrido = Recorrido.query.filter_by(chofer_id=user.id, estado='abierto').first()
    return render_template('chofer/dashboard.html', open_recorrido=open_recorrido)

@bp.route('/recorrido/nuevo')
@login_required_for_templates
def nuevo_recorrido():
    # A driver can't start a new trip if they already have one open
    user = get_current_user_role()
    open_recorrido = Recorrido.query.filter_by(chofer_id=user.id, estado='abierto').first()
    if open_recorrido:
        # Maybe redirect to the active trip page? For now, redirect to dashboard.
        return redirect(url_for('main.chofer_dashboard'))

    vehiculos = Vehiculo.query.filter_by(activo=True).all()
    return render_template('chofer/inicio_recorrido.html', vehiculos=vehiculos)

@bp.route('/recorrido/<uuid:recorrido_id>/fin')
@login_required_for_templates
def fin_recorrido_form(recorrido_id):
    recorrido = db.session.get(Recorrido, recorrido_id)
    # Add validation to ensure the user is the correct chofer
    user = get_current_user_role()
    if not recorrido or recorrido.chofer_id != user.id or recorrido.estado != 'abierto':
        return redirect(url_for('main.chofer_dashboard'))

    return render_template('chofer/fin_recorrido.html', recorrido=recorrido)
