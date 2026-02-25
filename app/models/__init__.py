# app/models/__init__.py
from app.database.db import Base
from app.models.user import User
from app.models.tariff import Tariff
from app.models.subscription import Subscription

# Это заставит Python загрузить все классы в память до того,
# как FastAPI или Alembic обратятся к любой из моделей.