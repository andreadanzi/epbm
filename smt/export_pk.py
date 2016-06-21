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
# danzi.tn@20160308 export PK di tutti i dati
# create main logger
logger = logging.getLogger('smt_main')
logger.setLevel(logging.DEBUG)
# create a rotating file handler which logs even debug messages
fh = logging.handlers.RotatingFileHandler('export_pk.log',maxBytes=5000000, backupCount=5)
fh.setLevel(logging.DEBUG)
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
# Search for project_code = "MFW001_0-010 Metro Paris-Ligne 15_T2A"
pd = db.Project.find_one({"code":"MFW001_0-010 Metro Paris-Ligne 15_T2A"})
p = Project(db, pd)
p.load()
found_domains = Domain.find(db, {"project_id": p._id})
for dom in found_domains:
    d = Domain(db,dom)
    d.load()
    # Export Alignments db, domain_id, csvPk
    bDone = Alignment.export_data_by_pk(db,d._id,"../data/query_pk.csv","../data/out_pk.csv")
    print bDone