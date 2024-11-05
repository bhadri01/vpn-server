from sqlalchemy import Column, Integer, String
from core.database import Base

# Define a sample model
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    device_name = Column(String, index=True)
    ip_address = Column(String, index=True)
    client_private_key = Column(String)
    client_public_key = Column(String)
    conf = Column(String)
    created_at = Column(String)