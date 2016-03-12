import logging
import logging.handlers
import ConfigParser, os
from datetime import datetime
from pymongo import MongoClient
from alignment import Alignment
from project import Project
from building import Building
from domain import Domain
from bson.objectid import ObjectId
# danzi.tn@20160312 import solo delle PK di riferimento sui building
# create main logger
logger = logging.getLogger('smt_main')
logger.setLevel(logging.INFO)
# create a rotating file handler which logs even debug messages 
fh = logging.handlers.RotatingFileHandler('import_building_pks.log',maxBytes=5000000, backupCount=5)
fh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
# reading config file
sCFGName = 'smt.cfg'
smtConfig = ConfigParser.RawConfigParser()
smtConfig.read(sCFGName)
# setup DB parameter
host = smtConfig.get('MONGODB','host')
database = smtConfig.get('MONGODB','database')
source_database = smtConfig.get('MONGODB','source_database')
username = smtConfig.get('MONGODB','username')
password = smtConfig.get('MONGODB','password')
# connect to MongoDB
client = MongoClient()
db = client[database]
# DB authentication
db.authenticate(username,password,source=source_database)
# IMPORT BUILDINGS PKS
Building.import_building_pks(db,"../data/Edifici_Analizzati_Attributi.csv")