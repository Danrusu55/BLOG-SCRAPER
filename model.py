from imports import *
from sqlalchemy import create_engine, Column, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


Base = declarative_base()

class Keyword(Base):
    __tablename__ = 'keywords'
    id = Column('id',Integer, primary_key=True)
    keyword = Column('keyword',String,unique=True)
    lastScraped = Column('lastscraped',DateTime)

engine = create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.format(dbUser,dbPass,hostName,db),echo=True)
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()

keywords = session.query(Keyword).all()

for keyword in keywords:
	print(keyword.keyword)
