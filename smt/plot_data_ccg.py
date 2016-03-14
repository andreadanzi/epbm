# -*- coding: utf-8 -*-
import logging
import logging.handlers
import ConfigParser, os
from datetime import datetime
from pymongo import MongoClient
from alignment import Alignment
from alignment_set import AlignmentSet
from project import Project
from building import Building
from domain import Domain
from bson.objectid import ObjectId
import glob,io
import csv, re
import sys, getopt
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from collections import defaultdict
from shapely.geometry import LineString
# danzi.tn@20160310 plot secondo distanze dinamiche
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
                'MFL3':'#9edae5',
                'R':'#7f7f7f',
                'AA':'#bcbd22',}

def mid_point(p1,p2):
    x = (p1[0] + p2[0])/2.
    y = (p1[1] + p2[1])/2.
    return x,y
    
                
def asse2p(p1,p2,x):
    mid = mid_point(p1,p2)
    if p2[0]==p1[0]:
        return mid[1]
    if p2[1]==p1[1]:
        return None
    m = (p2[1]-p1[1])/(p2[0]-p1[0])
    m_asse = -1/m
    return m_asse*(x-mid[0]) + mid[1]

def pfromdistance(p1,p2,d):
    mid = mid_point(p1,p2)
    if p2[0]==p1[0]:
        return (p1[0] - d,mid[1]) , (p1[0]+d,mid[1])
    if p2[1]==p1[1]:
        return (mid[0],p1[1]+d) , (mid[0],p1[1] - d)
    m = (p2[1]-p1[1])/(p2[0]-p1[0])
    mx = mid[0]
    a = 1.
    b = -2.*mx
    c = mx**2-d**2*m**2/(m**2+1)
    coeff = [a, b, c]
    res_x = np.roots(coeff)
    res_y0 = asse2p(p1,p2,res_x[0])
    res_y1 = asse2p(p1,p2,res_x[1])
    return (res_x[0],res_y0),(res_x[1],res_y1)
        
                
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

def processSettlements(a_list):
    distanceIndex = defaultdict(list)
    for i, a_item in enumerate(a_list):
        for item in a_item["SETTLEMENTS"]:
            distanceIndex[item["code"]].append(item["value"])
    distanceKeys = distanceIndex.keys()
    distanceKeys.sort()
    return distanceKeys, distanceIndex
    
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
                asets = db.AlignmentSet.find({"domain_id": d._id})
                for aset in asets:
                    a_set = AlignmentSet(db,aset)
                    a_set.load()
                    sCode = a_set.item["code"]
                    als = db.Alignment.find({"alignment_set_id":a_set._id},{"PK":True,"COB":True, "P_EPB":True,"BLOWUP":True, "PH":True, "DEM":True,"SETTLEMENT_MAX":True, "VOLUME_LOSS":True, "K_PECK":True, "REFERENCE_STRATA":True, "SETTLEMENTS":True}).sort("PK", 1)
                    a_list = list(als)
                    pks =[d['PK'] for d in a_list]
                    # scalo di fattore 100
                    p_epms =[d['P_EPB']/100 for d in a_list]
                    # scalo di fattore 100
                    cobs =[d['COB']/100 for d in a_list]
                    # scalo di fattore 100
                    blowups =[d['BLOWUP']/100 for d in a_list]
                    # amplifico di fattore 100
                    volume_losss =[d['VOLUME_LOSS']*100 for d in a_list]
                    k_pecks =[d['K_PECK'] for d in a_list]
                    # amplifico di fattore 1000
                    max_settlements =[d['SETTLEMENT_MAX']*1000 for d in a_list]
                    phs =[d['PH']['coordinates'][2] for d in a_list]
                    dems =[d['DEM']['coordinates'][2] for d in a_list]
                    pkys =[d['PH']['coordinates'][1] for d in a_list]
                    pkxs =[d['PH']['coordinates'][0] for d in a_list]   
                    # punti medi
                    pmidx = []
                    pmidy = []
                    # punti a distanza 20 e 40
                    keys, dictValues = processSettlements(a_list)
                    pkxs_d_1 = defaultdict(list)
                    pkys_d_1 = defaultdict(list)
                    pkzs_d_1 = defaultdict(list)
                    pkxs_d_2 = defaultdict(list)
                    pkys_d_2 = defaultdict(list)
                    pkzs_d_2 = defaultdict(list)
                    mypoints = np.zeros((0,2))
                    myvalues = np.zeros(0,'f')
                    for i,x in enumerate(pkxs):
                        if i==0:
                            pass
                        else:
                            p1 = (pkxs[i-1],pkys[i-1])
                            p2 = (pkxs[i],pkys[i])
                            pm = mid_point(p1,p2)
                            pmidx.append(pm[0])
                            pmidy.append(pm[1])
                            for key in keys:
                                val = (dictValues[key][i-1] + dictValues[key][i]) * 0.5
                                ret_d = pfromdistance(p1,p2,key)
                                x1 = ret_d[0][0]
                                x2 = ret_d[1][0]
                                y1 = ret_d[0][1]
                                y2 = ret_d[1][1]
                                pkxs_d_1[key].append(x1)
                                pkxs_d_2[key].append(x2)
                                pkys_d_1[key].append(y1)
                                pkys_d_2[key].append(y2) 
                                mypoints = np.append(mypoints,[[x1,y1]],axis=0)
                                myvalues = np.append(myvalues,[val],axis=0)
                                mypoints = np.append(mypoints,[[x2,y2]],axis=0)
                                myvalues = np.append(myvalues,[val],axis=0)
                    gx, gy =  np.mgrid[min(pkxs):max(pkxs),min(pkys):max(pkys)]
                    m_interp_cubic = griddata(mypoints, myvalues, (gx, gy),method='cubic')
                    # plot
                    fig = plt.figure()
                    plt.title("Profilo pressioni %s" % sCode)
                    ### visualizza gli strati di riferimento
                    # fillBetweenStrata(a_list)
                    
                    ################################################
                    plt.plot(pks,phs, linewidth=2,label='Tracciato')
                    plt.plot(pks,dems,  linewidth=2,label='DEM' )
                    plt.plot(pks,cobs, label='COB - bar')
                    plt.plot(pks,p_epms, label='P_EPB - bar')
                    plt.plot(pks,blowups, label='BLOWUP - bar')
                    plt.axis([min(pks),max(pks),min(phs)-10,max(dems)+10])
                    plt.legend()
                    outputFigure(sPath, "profilo_pressioni.svg")
                    logger.info("profilo_pressioni.svg plotted in %s" % sPath)
                    plt.show()

                    plt.title("Profilo cedimenti %s" % sCode)
                    plt.plot(pks,phs, linewidth=2,label='Tracciato')
                    plt.plot(pks,dems,  linewidth=2,label='DEM' )
                    plt.plot(pks,volume_losss, label='VL percent')
                    plt.plot(pks,k_pecks, label='k peck')
                    plt.plot(pks,max_settlements, label='SETTLEMENT_MAX (mm)')
                    plt.axis([min(pks),max(pks),min(phs)-10,max(dems)+10])
                    plt.legend()
                    outputFigure(sPath, "profilo_cedimenti.svg")
                    logger.info("profilo_cedimenti.svg plotted in %s" % sPath)
                    plt.show()
                    # stampa planimetria
                    plt.title("Planimetria") 
                    plt.plot(pkxs,pkys, "bo")
                    plt.plot(pkxs,pkys, "r-",label='Tracciato %s' % a_set.item["code"])
                    # Punti medi
                    plt.plot(pmidx,pmidy, "gx")

                    plt.title("Profilo peck %s" % sCode)
                    plt.plot(pks,phs, linewidth=2,label='Tracciato')
                    plt.plot(pks,dems,  linewidth=2,label='DEM' )
                    plt.plot(pks,volume_losss, label='VL percent')
                    plt.plot(pks,k_pecks, label='k peck')
                    plt.axis([min(pks),max(pks),min(phs)-10,max(dems)+10])
                    plt.legend()
                    outputFigure(sPath, "profilo_peck.svg")
                    logger.info("profilo_peck.svg plotted in %s" % sPath)
                    plt.show()
#                    # stampa planimetria
#                    plt.title("Planimetria") 
#                    plt.plot(pkxs,pkys, "bo")
#                    plt.plot(pkxs,pkys, "r-",label='Tracciato %s' % a_set.item["code"])
#                    # Punti medi
#                    plt.plot(pmidx,pmidy, "gx")
#
#  
#                    for key in keys:
#                        pkzs_d_1[key] = dictValues[key]
#                        pkzs_d_2[key] = dictValues[key]
#                        plt.plot(pkxs_d_1[key],pkys_d_1[key], "ro")
#                        plt.plot(pkxs_d_2[key],pkys_d_2[key], "yo")
#                    
#                    plt.axis("equal")
#                    plt.legend()
#                    plt.show()
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
