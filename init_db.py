# init_db.py
from fitness.app.core.database import Base, engine
from fitness.app.models.users import User
from app.models.supplements import Supplement
# позже добавишь: from app.models.user_supplements import UserSupplement

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()