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
import numpy as np
import matplotlib.pyplot as plt
# create main logger
logger = logging.getLogger('smt_main')
logger.setLevel(logging.DEBUG)
# create a rotating file handler which logs even debug messages 
fh = logging.handlers.RotatingFileHandler('plto_data.log',maxBytes=5000000, backupCount=5)
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


def plot_data(bAuthenticate, sPath):
    # connect to MongoDB
    client = MongoClient()
    db = client[database]
    # DB authentication
    if bAuthenticate:
        bLoggedIn = db.authenticate(username,password,source=source_database)
    else:
        bLoggedIn = True
    if bLoggedIn:
        logger.info("Logged in")
        pd = db.Project.find_one({"project_code":"MFW001_0-010 Metro Paris-Ligne 15_T2A"})
        if pd:
            logger.info("Project %s found" % pd["project_name"])
            p = Project(db, pd)
            p.load()
            found_domains = Domain.find(db, {"project_id": p._id})
            for dom in found_domains:
                d = Domain(db,dom)
                d.load()
                # Example of query
                als = db.Alignment.find({"domain_id":d._id},{"PK":True,"COB":True,"BLOWUP":True, "PH":True, "DEM":True}).sort("PK", 1)
                a_list = list(als)
                pks =[d['PK'] for d in a_list]
                # scalo di fattore 100
                cobs =[d['COB']/100 - 14*4.9/100 for d in a_list]
                # scalo di fattore 100
                blowups =[d['BLOWUP']/100- 14*4.9/100 for d in a_list]
                phs =[d['PH']['coordinates'][2] for d in a_list]
                dems =[d['DEM']['coordinates'][2] for d in a_list]
                fig, ax1 = plt.subplots()
                ax1.plot(pks,cobs, label='COB',  color='b')
                ax1.plot(pks,blowups, label='BLOWUP',  color='r')
                ax2 = ax1.twinx()
                ax2.plot(pks,phs, linewidth=2,label='Tracciato', color='k')
                ax2.plot(pks,dems,  linewidth=2,label='DEM', color='g' )
                ax1.set_ylim([0, 10])
                ax1.set_ylabel('bar @ top')
                ax2.set_ylim(-40,max(dems)+10)
                ax2.set_ylabel('m')

                
                
                plt.title("Profilo")
                #plt.plot(pks,phs, linewidth=2,label='Tracciato')
                #plt.plot(pks,dems,  linewidth=2,label='DEM' )
                #plt.plot(pks,cobs, label='COB / 10')
                #plt.plot(pks,blowups, label='BLOWUP / 10')
                #plt.axis([min(pks),max(pks),min(phs)-10,max(dems)+10])
                ax1.legend()
                plt.show()
                logger.info("Found %d PKs" % len( a_list ) )
    else:
        logger.error("Authentication failed")
        
                
def main(argv):
    sPath = None
    bAuthenticate = False
    sSyntax = os.path.basename(__file__) +" -p <output folder path> [-a for autentication -h for help]"
    try:
        opts, args = getopt.getopt(argv,"hap:",["path="])
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
                sys.exit(3)
    if sPath:
        plot_data(bAuthenticate, sPath)
    
    
if __name__ == "__main__":
    main(sys.argv[1:])
