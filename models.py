import datetime
import os,logging
import peewee_async
from peewee import Model, CharField, DateTimeField, PrimaryKeyField, IntegerField

# DECLARING VARIABLES

path = os.path.dirname(os.path.abspath(__file__))
db = 'outreacher'
hostName = 'localhost'
logFile = path + 'log.txt'
logging.basicConfig(filename=logFile,level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
dbUser = os.environ['MYSQL_USER']
dbPass = os.environ['MYSQL_PASS']
fbToken = os.environ['FACEBOOK_ACCESS_TOKEN']

mysql = peewee_async.MySQLDatabase(host=hostName, user=dbUser, password=dbPass, database=db)
objects = peewee_async.Manager(mysql)


class Keyword(Model):
	id = PrimaryKeyField()
	keyword = CharField(max_length=250, unique=True)
	lastscraped = DateTimeField(null=True)
	lastscrapedfacebook = DateTimeField(null=True)

	class Meta:
		database = mysql
		db_table = 'keywords'


class Influencer(Model):
	id = PrimaryKeyField()
	name = CharField(250)
	handle = CharField(250)
	picture = CharField(250)
	websiteurl = CharField(250)
	blogurl = CharField(250)
	websitetitle = CharField(250)
	websitedescription = CharField(250)
	keywordusedtofind = CharField(250)
	email = CharField(250)
	phone = CharField(250)
	location = CharField(250)
	pagecontact = CharField(250)
	pageabout = CharField(250)
	facebook = CharField(250)
	twitter = CharField(250)
	pinterest = CharField(250)
	youtube = CharField(250)
	instagram = CharField(250)
	linkedin = CharField(250)
	googleplus = CharField(250)
	statsfb = CharField(250)
	statstwitter = CharField(250)
	statsyoutube = CharField(250)
	statsinstagram = CharField(250)
	seoda = IntegerField(11)
	seorootbacklinks = IntegerField(11)
	seototalbacklinks = IntegerField(11)
	seovisitors = IntegerField(11)
	seoage = CharField(250)
	keyword1 = CharField(250)
	keyword2 = CharField(250)
	keyword3 = CharField(250)
	keyword4 = CharField(250)
	keyword5 = CharField(250)
	firstcollected = DateTimeField(null=True)
	lastscraped = DateTimeField(null=True)

	class Meta:
		database = mysql
		db_table = 'influencers'

class MajesticUrl(Model):
	id = PrimaryKeyField()
	websiteurl = CharField(250)
	lastscraped = DateTimeField(null=True)

	class Meta:
		database = mysql
		db_table = 'majesticurls'
