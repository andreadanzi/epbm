# -*- coding: utf-8 -*-
import os
import sys
import getopt
import logging
import logging.handlers
import ConfigParser
from datetime import datetime
from pymongo import MongoClient

from alignment import Alignment
from alignment_set import AlignmentSet
from project import Project
from domain import Domain

PROJECT_CODE = "MDW029_S_E_05"

# create main logger
logger = logging.getLogger('smt_main')
logger.setLevel(logging.DEBUG)
# create a rotating file handler which logs even debug messages
fh = logging.handlers.RotatingFileHandler('process_calc.log', maxBytes=5000000, backupCount=5)
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
# reading config file
sCFGName = 'smt.cfg'
smtConfig = ConfigParser.RawConfigParser()
smtConfig.read(sCFGName)
# setup DB parameter
host = smtConfig.get('MONGODB', 'host')
database = smtConfig.get('MONGODB', 'database')
source_database = smtConfig.get('MONGODB', 'source_database')
username = smtConfig.get('MONGODB', 'username')
password = smtConfig.get('MONGODB', 'password')

def process_calc(bAuthenticate):
    # connect to MongoDB
    client = MongoClient()
    db = client[database]
    # DB authentication if required
    if bAuthenticate:
        bLoggedIn = db.authenticate(username, password, source=source_database)
    else:
        bLoggedIn = True
    if bLoggedIn:
        logger.info("Authenticated")
        pd = db.Project.find_one({"project_code":PROJECT_CODE})
        if pd:
            logger.info("Project %s found", pd["project_name"])
            p = Project(db, pd)
            p.load()
            found_domains = Domain.find(db, {"project_id": p._id})
            for dom in found_domains:
                d = Domain(db, dom)
                d.load()
                asets = db.AlignmentSet.find({"domain_id": d._id})
                for aset in asets:
                    a_set = AlignmentSet(db, aset)
                    a_set.load()
                    #sCode = a_set.item["code"]
                    als = Alignment.find(db, {"alignment_set_id":a_set._id}).sort("PK", 1)
                    cnt = 0.
                    cnt_tot = als.count()
                    for al in als:
                        a = Alignment(db, al)
                        a.setProject(p.item)
                        a.load()
                        cnt += 1.
                        sys.stdout.write("\r{:5s} pk= {:.0f} progress= {:.0%}".format(a_set.item["code"], a.item["PK"], cnt/cnt_tot))
                        sys.stdout.flush()
                        a.perform_calc(str(datetime.now()))
    else:
        logger.error("Authentication failed")

def main(argv):
    bAuthenticate = False
    sSyntax = os.path.basename(__file__) +" [-a for authentication]"
    try:
        opts, args = getopt.getopt(argv, "ha")
    except getopt.GetoptError:
        print sSyntax
        sys.exit(1)
#    if len(opts) < 1:
#        print sSyntax
#        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print sSyntax
            sys.exit()
        elif opt == '-a':
            bAuthenticate = True
    process_calc(bAuthenticate)


if __name__ == "__main__":
    main(sys.argv[1:])
