from flask_sqlalchemy import SQLAlchemy
from pgvector.psycopg import register_vector
from sqlalchemy import event


db = SQLAlchemy()


def init_database(app):
    db.init_app(app)

    with app.app_context():
        engine = db.engine

        @event.listens_for(engine, "connect")
        def register_pgvector(dbapi_connection, _connection_record):
            register_vector(dbapi_connection)
