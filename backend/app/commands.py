import click
from flask.cli import with_appcontext
from .models import Usuario
from .extensions import db

@click.command(name='seed')
@with_appcontext
def seed():
    """Seeds the database with an initial admin user."""

    # Check if an admin user already exists
    if Usuario.query.filter_by(rol='admin').first():
        print("An admin user already exists. Aborting.")
        return

    # Create the admin user
    admin_email = 'admin@example.com'
    admin_password = 'password' # In a real app, get this from env or prompt

    admin = Usuario(
        nombre='Admin User',
        email=admin_email,
        rol='admin',
        activo=True
    )
    admin.set_password(admin_password)

    db.session.add(admin)
    db.session.commit()

    print(f"Admin user created successfully!")
    print(f"  Email: {admin_email}")
    print(f"  Password: {admin_password}")
    print("Please change this password after your first login.")
