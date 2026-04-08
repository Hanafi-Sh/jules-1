from app.db.session import engine, Base
from app.models import db_models

def init_db():
    Base.metadata.create_all(bind=engine)
