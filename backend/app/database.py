from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


DATABASE_URL = (
    "postgresql+psycopg://postgres:1266@localhost:5432/knowledge_agent"
)


class Base(DeclarativeBase):
    pass


engine = create_engine(
    DATABASE_URL,
    echo=False,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()