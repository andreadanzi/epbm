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
logger = logging.getLogger('smt_main')
logger.setLevel(logging.DEBUG)
# create a rotating file handler which logs even debug messages 
fh = logging.handlers.RotatingFileHandler('main.log',maxBytes=5000000, backupCount=5)
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
p = None
if not pd:
    p = Project(db, {"project_name":"Progetto di Test","project_code":"123" })
    p.save()
else:
    p = Project(db, pd)
# Import domain inside the project: one-to-many relationship by references
p.import_domains("../data/domain.csv")
cr = Domain.find(db, {"project_id": p._id})
for c in cr:
    d = Domain(db,c)
    d.load()
    # Import reference strata inside the domain: one-to-one relationship by embedding
    d.import_reference_strata("../data/reference_strata.csv")
    # Import alignment inside the domain: one-to-many relationship by references
    d.import_alignment("../data/profilo_progetto.csv")
    # Import stratigraphy inside the alignment: one-to-many relationship by embedding
    d.import_strata("../data/stratigrafia.csv")
    # Import water folders inside the alignment: one-to-many relationship by embedding
    d.import_falda("../data/falda.csv")
# Import Buildings
Building.ImportFromCSVFile("../data/buildings.csv", db)

# Example of calculation
als = Alignment.find(db,{})
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