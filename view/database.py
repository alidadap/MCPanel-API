from sqlalchemy import Column, Integer, String, create_engine, delete
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Users(Base):
    __tablename__ = 'panel_users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True)
    password = Column(String(255))  
    access = Column(String(255))  
    email = Column(String(255))  


engine = create_engine("sqlite:///MCPanel.db",connect_args={"check_same_thread": False}, echo=True)

Base.metadata.create_all(engine) # type: ignore

Session = sessionmaker(bind=engine)
session = Session()