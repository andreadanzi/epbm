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
from matplotlib.mlab import griddata
from collections import defaultdict
from shapely.geometry import LineString
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
# Colori da associare alle aree degli strati di riferimento
main_colors = {
                'MC':'#1f77b4',
                'MCA':'#ff7f0e', 
                'SO2':'#2ca02c',
                'MFL5':'#d62728',  
                'CG':'#9467bd',
                'MIG':'#8c564b',  
                'SB':'#e377c2', 
                'MA':'#7f7f7f',
                'SO4':'#bcbd22', 
                'MFL4':'#dbdb8d', 
                'SO':'#17becf', 
                'MFL3':'#9edae5'}

def mid_point(p1,p2):
    x = (p1[0] + p2[0])/2.
    y = (p1[1] + p2[1])/2.
    return x,y

def asse2p(p1,p2,x):
    coef = np.polyfit(p1,p2,1)    
    m = mid_point(p1,p2)
    fm = -1/coef[0]
    fb = m[0]/coef[0]+m[1]
    return fm*x+fb

def pfromdistance(p1,p2,d):
    coef = np.polyfit(p1,p2,1)    
    m = mid_point(p1,p2)
    fb = m[0]/coef[0]+m[1]
    fm = -1/coef[0]
    a= 1+fm**2
    b=-2*fm*fb-2*fm*m[1]-2*m[0]
    c=m[0]**2+m[1]**2+fb**2-2*fb*m[1]-d**2
    coeff = [a, b, c]
    res_x = np.roots(coeff)
    res_y = asse2p(p1,p2,res_x)
    return (res_x[0],res_y[0]),(res_x[1],res_y[1])
        
def plot_line( ob, color="green"):
    parts = hasattr(ob, 'geoms') and ob or [ob]
    for part in parts:
        x, y = part.xy
        plt.plot(x, y,'o', color=color, zorder=1) 
        #plt.plot(x, y, color=color, linewidth=2, solid_capstyle='round', zorder=1)    


def plot_coords( x, y, color='#999999', zorder=1):
    plt.plot(x, y, 'o', color=color, zorder=zorder)


def outputFigure(sDiagramsFolderPath, sFilename, format="svg"):
    imagefname=os.path.join(sDiagramsFolderPath,sFilename)
    if os.path.exists(imagefname):
        os.remove(imagefname)
    plt.savefig(imagefname,format=format, bbox_inches='tight', pad_inches=0)

def fillBetweenStrata(a_list):
    currentStrata = None
    x=[]
    y1=[]
    y2=[]
    facecolors=['orange','yellow']
    for i, a_item in enumerate(a_list):
        z_base = a_item['REFERENCE_STRATA']['POINTS']['base']['coordinates'][2]
        z_top = a_item['REFERENCE_STRATA']['POINTS']['top']['coordinates'][2]  
        code = a_item['REFERENCE_STRATA']['CODE']
        if not currentStrata:
            currentStrata = code        
        elif currentStrata == code:
            pass
        else:
            plt.fill_between(x, y1, y2,facecolor=main_colors[currentStrata], interpolate=True,label=currentStrata)
            x=[]
            y1=[]
            y2=[]
            currentStrata = code
        x.append(a_item['PK'])
        y1.append(z_base)
        y2.append(z_top)        

def plot_data(bAuthenticate, sPath):
    # connect to MongoDB
    client = MongoClient()
    db = client[database]
    # DB authentication if required
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
                als = db.Alignment.find({"domain_id":d._id},{"PK":True,"COB":True,"BLOWUP":True, "PH":True, "DEM":True, "REFERENCE_STRATA":True}).sort("PK", 1)
                a_list = list(als)
                pks =[d['PK'] for d in a_list]
                # scalo di fattore 100
                cobs =[d['COB']/100 for d in a_list]
                # scalo di fattore 100
                blowups =[d['BLOWUP']/100 for d in a_list]
                phs =[d['PH']['coordinates'][2] for d in a_list]
                dems =[d['DEM']['coordinates'][2] for d in a_list]
                pkys =[d['PH']['coordinates'][1] for d in a_list]
                pkxs =[d['PH']['coordinates'][0] for d in a_list]                
                # plot
                fig = plt.figure()
                plt.title("Profilo")
                fillBetweenStrata(a_list)
                plt.plot(pks,phs, linewidth=2,label='Tracciato')
                plt.plot(pks,dems,  linewidth=2,label='DEM' )
                plt.plot(pks,cobs, label='COB / 100')
                plt.plot(pks,blowups, label='BLOWUP / 100')
                plt.axis([min(pks),max(pks),min(phs)-10,max(dems)+10])
                plt.legend()
                outputFigure(sPath, "profilo.svg")
                logger.info("profilo.svg plotted in %s" % sPath)
                plt.show()
                # stampa planimetria
                plt.title("Planimetria") 
                # plt.plot(pkxs,pkys, linewidth=2,label='Tracciato')
                line_points = [(x,pkys[i]) for i,x in enumerate(pkxs) ]
                line = LineString(line_points)
                print "line ha %d coords" % len(line.coords)
                offset_left = line.parallel_offset(20, 'left', join_style=2, mitre_limit=20)
                offset_center = offset_left.parallel_offset(20, 'right', join_style=2, mitre_limit=20)
                print "offset_left ha %d coords" % len(offset_left.coords)
                offset_right = line.parallel_offset(20, 'right', join_style=2, mitre_limit=20)
                print "offset_right ha %d coords" % len(offset_right.coords)
                plot_line(offset_center)
                plot_line(offset_left, color="blue")
                plot_line(offset_right, color="red")
                x, y = list(line.coords)[0]
                plot_coords(x, y)
                plt.axis("equal")
                plt.legend()
                plt.show()
                logger.info("plot_data terminated!")
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
                sPath = None
                sys.exit(3)
    if sPath:
        plot_data(bAuthenticate, sPath)
    
    
if __name__ == "__main__":
    main(sys.argv[1:])
