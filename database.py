from sqlalchemy.ext import declarative
from sqlalchemy import orm
import sqlalchemy


DATABASE_URL = "sqlite:///./database.db"
engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative.declarative_base()

 