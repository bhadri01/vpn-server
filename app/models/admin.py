from sqlalchemy import Column, Integer, String
from core.database import Base

# Define a sample model
class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    secret_key = Column(String, index=True)
    uri = Column(String, index=True)

