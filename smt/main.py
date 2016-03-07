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


# create logger with 
logger = logging.getLogger('smt_main')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.handlers.RotatingFileHandler('main.log',maxBytes=500000, backupCount=5)
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

sCFGName = 'smt.cfg'
smtConfig = ConfigParser.RawConfigParser()
smtConfig.read(sCFGName)

host = smtConfig.get('MONGODB','host')
database = smtConfig.get('MONGODB','database')
source_database = smtConfig.get('MONGODB','source_database')
username = smtConfig.get('MONGODB','username')
password = smtConfig.get('MONGODB','password')
client = MongoClient()
db = client[database]
db.authenticate(username,password,source=source_database)
pd = db.Project.find_one({"project_name":"Progetto di Test"})
p = None
if not pd:
    p = Project(db, {"project_name":"Progetto di Test","project_code":"123" })
    p.save()
else:
    print pd
    p = Project(db, pd)
# p.import_alignment("../data/alignment.csv")
p.import_domains("../data/domain.csv")
cr = Domain.find(db, {"project_id": p._id})
for c in cr:
    d = Domain(db,c)
    d.load()
    d.import_reference_strata("../data/reference_strata.csv")
    d.import_alignment("../data/profilo_progetto.csv")
    d.import_strata("../data/stratigrafia.csv")
    d.import_falda("../data/falda.csv")
Building.ImportFromCSVFile("../data/buildings.csv", db)

als = Alignment.find(db,{})
for al in als:
    a = Alignment(db,al)
    a.load()
    a.perform_calc("Here I am")