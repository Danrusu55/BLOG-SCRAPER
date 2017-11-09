# -*- coding: utf-8 -*-
from datetime import datetime
import logging, os, random, mysql, time, re, sys,traceback,threading,smtplib,subprocess,string,getopt,requests,csv,pprint,multiprocessing
# import http.client
from io import open
from mysql.connector import errorcode
from mysql.connector.pooling import MySQLConnectionPool
from mysql.connector import connect
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import asyncio
from proxybroker import Broker
from urllib.parse import urlsplit
from fuzzywuzzy import fuzz
import urllib.request
import lxml
import numpy
# from fake_useragent import UserAgent
# ua = UserAgent()


# DECLARING VARIABLES

path = os.path.dirname(os.path.abspath(__file__))
db = 'outreacher'
hostName = 'localhost'
logFile = path + 'log.txt'
logging.basicConfig(filename=logFile,level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
dbUser = os.environ['MYSQL_USER']
dbPass = os.environ['MYSQL_PASS']

# DB CONNECTION
cnx = mysql.connector.connect(user=dbUser,password=dbPass, host=hostName,database=db)
cursor = cnx.cursor()

# PPRINT
pp = pprint.PrettyPrinter(indent=4)

# FOR URLLIB
data = None
proxy = urllib.request.ProxyHandler({'https': '108.59.14.203:13010', 'http': '108.59.14.203:13010'})
opener = urllib.request.build_opener(proxy)
urllib.request.install_opener(opener)

with open('ignore_sites.txt','r') as file:
	ignoreSites = file.read().splitlines()
