# -*- coding: utf-8 -*-
import logging
import logging.handlers
import ConfigParser, os
import datetime
from pymongo import MongoClient
from alignment import Alignment
from alignment_set import AlignmentSet
from project import Project
from building import Building
from building_class import BuildingClass
from underground_structure_class import UndergroundStructureClass
from underground_utility_class import UndergroundUtilityClass
from overground_infrastructure_class import OvergroundInfrastructureClass
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
Building.delete_all(db)
BuildingClass.delete_all(db)
Alignment.delete_all(db)
AlignmentSet.delete_all(db)
Domain.delete_all(db)
Project.delete_all(db)
# Search for project_code = "MFW001_0-010 Metro Paris-Ligne 15_T2A"
Project.ImportFromCSVFile("../data/project.csv", db)
pd = db.Project.find_one({"project_code":"MFW001_0-010 Metro Paris-Ligne 15_T2A"})
p = None
if not pd:
    p = Project(db, {"project_name":u"Société du Grand Paris Ligne 15 T2A","project_code":"MFW001_0-010 Metro Paris-Ligne 15_T2A" })
    p.item["created"] = datetime.datetime.utcnow()
    p.save()
else:
    p = Project(db, pd)
# Import domain inside the project: one-to-many relationship by references
p.import_domains("../data/domain.csv")
cr = Domain.find(db, {"project_id": p._id})
# Import Buildings
Building.ImportFromCSVFile("../data/buildings_orig.csv", db)
# danzi.tn@20160312 import delle PK di riferimento sui building
#Building.import_building_pks(db,"../data/Edifici_Analizzati_Attributi.csv")
# gabriele@20160318 nuovo import rispetto ai nuovi output di Ghensi
Building.import_building_pks(db,"../data/Elementi_Tracciato_pkdist.csv")
Building.import_building_pks(db,"../data/Elementi_Raccordo_pkdist.csv")

BuildingClass.ImportFromCSVFile("../data/building_class.csv", db)
UndergroundStructureClass.ImportFromCSVFile("../data/underground_structure_class.csv", db)
UndergroundUtilityClass.ImportFromCSVFile("../data/underground_utility_class.csv", db)
OvergroundInfrastructureClass.ImportFromCSVFile("../data/overground_infrastructure_class.csv", db)
bldgs = Building.find(db, {})
for bl in bldgs:
    b = Building(db, bl)
    b.assign_class()

for c in cr:
    d = Domain(db,c)
    d.load()
    d.import_alignment_set("../data/alignment_set.csv")
    asets = db.AlignmentSet.find({"domain_id": d._id})
    for aset in asets:
        a_set = AlignmentSet(db,aset)
        a_set.load()
        sCode = a_set.item["code"]
        sRelCsvCode = a_set.item["rel_csv_code"]
        # Import reference strata inside the alignment set: one-to-one relationship by embedding
        a_set.import_reference_strata("../data/reference_strata.csv" )
        # Import alignment inside the alignment set: one-to-many relationship by references
        a_set.import_alignment("../data/profilo_progetto-%s.csv" % sCode)
        # Import stratigraphy inside the alignment: one-to-many relationship by embedding
        a_set.import_strata("../data/stratigrafia-%s.csv" % sRelCsvCode)
        # Import water folders inside the alignment: one-to-many relationship by embedding
        a_set.import_falda("../data/falda-%s.csv" % sRelCsvCode)
        # Import tunnel sections inside the alignment: one-to-many relationship by embedding
        a_set.import_sezioni("../data/sezioni_progetto-%s.csv" % sRelCsvCode)
        # Import TBM inside the alignment: one-to-many relationship by embedding
        a_set.import_tbm("../data/tbm_progetto-%s.csv" % sRelCsvCode)
        als = Alignment.find(db,{"alignment_set_id":a_set._id})
        for al in als:
            a = Alignment(db,al)
            a.setProject(p.item)
            a.load()
            a.assign_reference_strata()
            a.define_tun_param()
            a.assign_buildings(a.define_buffer())
            
