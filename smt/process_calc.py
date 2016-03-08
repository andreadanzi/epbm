# -*- coding: utf-8 -*-
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
import glob,io
import csv, re
import sys, getopt
from minimongo import Model, Index
import googlemaps
# create main logger
logger = logging.getLogger('smt_main')
logger.setLevel(logging.DEBUG)
# create a rotating file handler which logs even debug messages 
fh = logging.handlers.RotatingFileHandler('process_calc.log',maxBytes=5000000, backupCount=5)
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


def process_calc(path):
    # connect to MongoDB
    client = MongoClient()
    db = client[database]
    # DB authentication
    bLoggedIn = db.authenticate(username,password,source=source_database)
    if bLoggedIn:
        logger.info("Authenticated")
        pd = db.Project.find_one({"project_code":"MFW001_0-010 Metro Paris-Ligne 15_T2A"})
        if pd:
            logger.info("Project %s found" % pd["project_name"])
            p = Project(db, pd)
            p.load()
            found_domains = Domain.find(db, {"project_id": p._id})
            for dom in found_domains:
                d = Domain(db,dom)
                d.load()
                # Example of calculation
                als = Alignment.find(db,{"domain_id":d._id})
                logger.info("Found %d PKs" % len( list(als) ) )
    else:
        logger.error("Authentication failed")
        
                
def main(argv):
    sPath = "NONE"
    sSyntax = os.path.basename(__file__) +" -p <folder path>"
    try:
        opts, args = getopt.getopt(argv,"hp:",["path="])
    except getopt.GetoptError:
        print sSyntax
        sys.exit(1)
    if len(opts) < 1:
        print sSyntax
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print sSyntax
            sys.exit()
        elif opt in ("-p", "--path"):
            sPath = arg
            if os.path.isdir(sPath):
                process_calc(sPath)
            else:
                print sSyntax
                print "Directory %s does not exists!" % sPath
                sys.exit(3)
    
    
    
if __name__ == "__main__":
    main(sys.argv[1:])