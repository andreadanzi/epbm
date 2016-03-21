# -*- coding: utf-8 -*-
import logging
import logging.handlers
import ConfigParser
import os
import csv
import sys
import getopt
from pymongo import MongoClient

from alignment_set import AlignmentSet
from project import Project
from domain import Domain

# create main logger
logger = logging.getLogger('smt_main')
logger.setLevel(logging.DEBUG)
# create a rotating file handler which logs even debug messages
fh = logging.handlers.RotatingFileHandler('export_pk_data.log',
                                          maxBytes=5000000, backupCount=5)
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
# Colori da associare alle aree degli strati di riferimento

def export_data_csv(bAuthenticate, sPath):
    # connect to MongoDB
    client = MongoClient()
    db = client[database]
    # DB authentication if required
    if bAuthenticate:
        bLoggedIn = db.authenticate(username, password, source=source_database)
    else:
        bLoggedIn = True
    if bLoggedIn:
        logger.info("Logged in")
        pd = db.Project.find_one({"project_code":"MFW001_0-010 Metro Paris-Ligne 15_T2A"})
        if pd:
            logger.info("Project %s found" % pd["project_name"])
            p = Project(db, pd)
            p.load()
            for dom in Domain.find(db, {"project_id": p._id}):
                dm = Domain(db, dom)
                dm.load()
                for aset in db.AlignmentSet.find({"domain_id": dm._id}):
                    a_set = AlignmentSet(db, aset)
                    a_set.load()
                    sCode = a_set.item["code"]
                    a_list = list(db.Alignment.find({"alignment_set_id":a_set._id},
                                                    {"PK":True, "VOLUME_LOSS":True,
                                                     "SETTLEMENT_MAX":True, "K_PECK":True,
                                                     "phi_tun":True, "ci_tun":True, "COB":True,
                                                     "BLOWUP":True, "P_EPB": True, "P_WT": True,
                                                     "BUILDINGS":True}).sort("PK", 1))
                    rows = []
                    bldg_rows = []
                    for d in a_list:
                        rows.append([d["PK"], d.get("VOLUME_LOSS", ""), d.get("SETTLEMENT_MAX", ""),
                                     d.get("K_PECK", ""), d.get("phi_tun", ""), d.get("ci_tun", ""),
                                     d.get("COB", ""), d.get("BLOWUP", ""), d.get("P_EPB", ""),
                                     d.get("P_WT", "")])
                        buildings = d.get("BUILDINGS")
                        if buildings:
                            for b in buildings:
                                bldg_rows.append([d["PK"], b["bldg_code"],
                                                  b.get("vulnerability", ""), b.get("sc_lev", ""),
                                                  b.get("damage_class", ""),
                                                  b.get("settlement_max", ""),
                                                  b.get("tilt_max", ""), b.get("esp_h_max", "")])
                    with open(os.path.join(sPath, sCode + "_data_export.csv"), 'wb') as out_csvfile:
                        writer = csv.writer(out_csvfile, delimiter=";")
                        writer.writerow(["PK", "VOLUME_LOSS", "SETTLEMENT_MAX", "K_PECK", "phi_tun",
                                         "ci_tun", "COB", "BLOWUP", "P_EPB", "P_WT"])
                        writer.writerows(rows)
                    with open(os.path.join(sPath, sCode + "_buildings_data_export.csv"),
                              'wb') as out_csvfile:
                        writer = csv.writer(out_csvfile, delimiter=";")
                        writer.writerow(["PK", "bldg_code", "vulnerability", "sc_lev",
                                         "damage_class", "settlement_max", "tilt_max", "esp_h_max"])
                        writer.writerows(bldg_rows)
                logger.info("export_data_csv terminated!")
    else:
        logger.error("Authentication failed")

def main(argv):
    sPath = None
    bAuthenticate = False
    sSyntax = os.path.basename(__file__) + \
              " -p <output folder path> [-a for autentication -h for help]"
    try:
        opts, args = getopt.getopt(argv, "hap:", ["path="])
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
        elif opt == '-a':
            bAuthenticate = True
        elif opt in ("-p", "--path"):
            sPath = arg
            if not os.path.isdir(sPath):
                print sSyntax
                print "Directory %s does not exists!" % sPath
                sPath = None
                sys.exit(3)
    if sPath:
        export_data_csv(bAuthenticate, sPath)


if __name__ == "__main__":
    main(sys.argv[1:])
