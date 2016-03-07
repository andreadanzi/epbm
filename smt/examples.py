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
# create main logger
logger = logging.getLogger('smt_examples')
logger.setLevel(logging.DEBUG)
# create a rotating file handler which logs even debug messages 
fh = logging.handlers.RotatingFileHandler('examples.log',maxBytes=5000000, backupCount=5)
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
# Search for project_name = "Progetto di Test"
pd = db.Project.find_one({"project_name":"Progetto di Test"})
p = Project(db, pd)
p.load()
found_domains = Domain.find(db, {"project_id": p._id})
for dom in found_domains:
    d = Domain(db,dom)
    d.load()
    # Example of calculation
    als = Alignment.find(db,{"domain_id":d._id})
    for al in als:
        a = Alignment(db,al)
        a.load()
        a.perform_calc("PG0123")

    # Example of find
    alist = Alignment.find(db,{"REFERENCE_STRATA.CODE":"MCA"})
    print len(list(alist))

    # Example of aggregation
    aggrList = Alignment.aggregate_by_strata(db, d._id)
    for ii in aggrList:
        print ii