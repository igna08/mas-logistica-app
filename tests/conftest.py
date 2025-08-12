import pytest
from app import create_app, db as _db

@pytest.fixture(scope='session')
def app():
    """A session-wide test application."""
    _app = create_app('testing')

    with _app.app_context():
        yield _app


@pytest.fixture(scope='function')
def test_client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture(scope='function')
def db(app):
    """A database for the tests."""
    with app.app_context():
        _db.create_all()

        yield _db

        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope='function')
def session(db):
    """
    This fixture is a bit redundant if tests just use db.session,
    but it makes the dependency explicit.
    """
    yield db.session
