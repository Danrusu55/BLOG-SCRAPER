# -*- coding: utf-8 -*-
from datetime import datetime
import logging, os, random, mysql, time, re, sys,traceback,threading,smtplib,subprocess,string,getopt,requests,csv,pprint,multiprocessing
# import http.client
from io import open
from mysql.connector import errorcode
from mysql.connector.pooling import MySQLConnectionPool
from mysql.connector import connect
from bs4 import BeautifulSoup
import asyncio
from proxybroker import Broker
from urllib.parse import urlsplit
from fuzzywuzzy import fuzz
import urllib.request
import lxml
import numpy
from imports import *
from sqlalchemy import create_engine, Column, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
import pymysql, pymysql.cursors
import facebook, twitter

# DECLARING VARIABLES

path = os.path.dirname(os.path.abspath(__file__))
db = 'outreacher'
hostName = 'localhost'
logFile = path + 'log.txt'
logging.basicConfig(filename=logFile,level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
dbUser = os.environ['MYSQL_USER']
dbPass = os.environ['MYSQL_PASS']
fbToken = os.environ['FACEBOOK_ACCESS_TOKEN']
#twToken = os.environ['TWITTER_ACCESS_TOKEN']
#twToken_secret = os.environ['TWITTER_TOKEN_SECRET']
#twConsumer_key = os.environ['TWITTER_CONSUMER_KEY']
#twConsumer_secret = os.environ['TWITTER_CONSUMER_SECRET']


# DB ORM SESSION

Base = declarative_base()

class Keyword(Base):
    __tablename__ = 'keywords'
    id = Column('id',Integer, primary_key=True)
    keyword = Column('keyword',String(250),unique=True)
    lastscraped = Column('lastscraped',DateTime)
    lastscrapedfacebook = Column('lastscrapedfacebook',DateTime)

class MajesticUrl(Base):
    __tablename__ = 'majesticurls'
    id = Column('id',Integer, primary_key=True)
    websiteurl = Column('websiteurl',String(250),unique=True)
    lastscraped = Column('lastscraped',DateTime)

class Website(Base):
    __tablename__ = 'websites'
    id = Column('id',Integer, primary_key=True)
    websiteurl = Column('websiteurl',String(250),unique=True)
    blogurl = Column('blogurl',String(250))
    fbid = Column('fbid',String(250))
    keywordusedtofind = Column('keywordusedtofind',String(250))
    scrapedon = Column('scrapedon',DateTime,default=datetime.utcnow)

class Influencer(Base):
    __tablename__ = 'influencers'
    id = Column('id',Integer, primary_key=True)
    name = Column('name',String(250))
    handle = Column('handle',String(250))
    picture = Column('picture',String(250))
    websiteurl = Column('websiteurl',String(250),unique=True)
    blogurl = Column('blogurl',String(250))
    websitetitle = Column('websitetitle',String(250))
    websitedescription = Column('websitedescription',String(250))
    keywordusedtofind = Column('keywordusedtofind',String(250))
    email = Column('email',String(250))
    phone = Column('phone',String(250))
    location = Column('location',String(250))
    pagecontact = Column('pagecontact',String(250))
    pageabout = Column('pageabout',String(250))
    facebook = Column('facebook',String(250))
    twitter = Column('twitter',String(250))
    pinterest = Column('pinterest',String(250))
    youtube = Column('youtube',String(250))
    instagram = Column('instagram',String(250))
    linkedin = Column('linkedin',String(250))
    googleplus = Column('googleplus',String(250))
    statsfb = Column('statsfb',String(250))
    statstwitter = Column('statstwitter',String(250))
    statsyoutube = Column('statsyoutube',String(250))
    statsinstagram = Column('statsinstagram',String(250))
    seoda = Column('seoda',Integer)
    seorootbacklinks = Column('seorootbacklinks',Integer)
    seovisitors = Column('seovisitors',Integer)
    seoda = Column('seoda',Integer)
    keyword1 = Column('keyword1',String(250))
    keyword2 = Column('keyword2',String(250))
    keyword3 = Column('keyword3',String(250))
    keyword4 = Column('keyword4',String(250))
    keyword5 = Column('keyword5',String(250))
    lastscraped = Column('lastscraped',DateTime)

engine = create_engine('mysql+pymysql://{0}:{1}@{2}/{3}'.format(dbUser,dbPass,hostName,db),echo=False,pool_recycle=3600)
Base.metadata.create_all(bind=engine)
#Session = sessionmaker(bind=engine)
session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# PPRINT

pp = pprint.PrettyPrinter(indent=4)

# FOR URLLIB

data = None
proxy = urllib.request.ProxyHandler({'https': '108.59.14.208:13080', 'http': '108.59.14.208:13080'})
opener = urllib.request.build_opener(proxy)
urllib.request.install_opener(opener)

with open('ignore_sites.txt','r') as file:
    ignoreSites = file.read().splitlines()



