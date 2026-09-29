from database import Base
from sqlalchemy import Column, Integer, String, Float,  Boolean, ForeignKey


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    
    
class Expenses(Base):
    __tablename__ = 'Expense'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    amount = Column(Float)
    type = Column(String)
    category = Column(String)
    date = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))