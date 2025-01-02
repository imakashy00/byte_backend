from re import S
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Boolean, Enum
from schema.schema import Status
from dotenv import load_dotenv
import os
load_dotenv()
engine = create_engine(os.getenv('POSTGRES_DATABASE_URL'))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Connect the database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# Database Models for Users and tasks
class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)


# Database Models for tasks
class Tasks(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    status= Column(Enum(Status), default=Status.PENDING)