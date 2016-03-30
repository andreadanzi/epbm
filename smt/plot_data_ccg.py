# -*- coding: utf-8 -*-
import math
import logging
import logging.handlers
import ConfigParser, os
from pymongo import MongoClient
from alignment_set import AlignmentSet
from project import Project
from domain import Domain
import csv, re
import sys, getopt
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from collections import defaultdict
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
    # cambio font size
    mpl.rcParams.update({'font.size': 6})
    if bLoggedIn:
        logger.info("Logged in")
        pd = db.Project.find_one({"project_code":"MFW001_0-010 Metro Paris-Ligne 15_T2A"})
        if pd:
            logger.info("Project %s found" % pd["project_name"])
            p = Project(db, pd)
            p.load()
            found_domains = Domain.find(db, {"project_id": p._id})
            for dom in found_domains:
                dm = Domain(db,dom)
                dm.load()
                # Example of query
                asets = db.AlignmentSet.find({"domain_id": dm._id})
                for aset in asets:
                    a_set = AlignmentSet(db,aset)
                    a_set.load()
                    sCode = a_set.item["code"]
                    als = db.Alignment.find({"alignment_set_id":a_set._id},{"PK":True,"P_TAMEZ":True,"COB":True,"P_EPB":True,"P_WT":True,"BLOWUP":True, "PH":True, "DEM":True,"SETTLEMENT_MAX":True, \
                    "TILT_MAX":True, "EPS_H_MAX":True, "VOLUME_LOSS":True, "K_PECK":True, "REFERENCE_STRATA":True, "SETTLEMENTS":True, "SENSIBILITY":True, "DAMAGE_CLASS":True, "VULNERABILITY":True,  \
                    "CONSOLIDATION_VALUE":True, "gamma_face":True, "gamma_tun":True}).sort("PK", 1)
                    a_list = list(als)
                    pks = []
                    pklabel = []
                    pkxticks = []
                    for d in a_list:
                        pk_value = round(d['PK']/10., 0) *10.
                        pks.append(pk_value)
                        hundreds = int(pk_value-int(pk_value/1000.)*1000)
                        if hundreds%100 == 0:
                            pkxticks.append(pk_value)
                            pklabel.append("%d+%03d" % (int(pk_value/1000.),hundreds ))
                    if sCode=='smi':
                        d_press = 0.5 # bar tra calotta e asse
                        d_press_wt = 0.35
                    else:
                        d_press = 0.7 # bar tra calotta e asse
                        d_press_wt = 0.5
                    
                    # scalo di fattore 100
#                    p_wts =[d['P_WT']/100 - d_press_wt for d in a_list]
                    p_wts = [(max(0., d['P_WT']/100. - d_press_wt)) for d in a_list]
                    # scalo di fattore 100
                    p_epms =[max(0., d['P_EPB']/100. - d_press) for d in a_list]
                    # scalo di fattore 100
                    p_tamezs=[max(0., d['P_TAMEZ']/100. - d_press) for d in a_list]
                    cobs =[max(0., d['COB']/100. - d_press) for d in a_list]
                    # scalo di fattore 100
                    blowups =[max(0., d['BLOWUP']/100. - d_press) for d in a_list]
                    # amplifico di fattore 100
                    volume_losss =[d['VOLUME_LOSS']*100. for d in a_list]
                    k_pecks =[d['K_PECK'] for d in a_list]
                    # amplifico di fattore 1000
                    max_settlements =[d['SETTLEMENT_MAX']*1000. for d in a_list]
                    tilts =[d['TILT_MAX']*1000. for d in a_list]
                    epshs =[d['EPS_H_MAX']*1000. for d in a_list]
                    consolidations =[d['CONSOLIDATION_VALUE'] for d in a_list]
                    sensibilities =[d['SENSIBILITY'] for d in a_list]
                    damages =[d['DAMAGE_CLASS'] for d in a_list]
                    vulnerabilities =[d['VULNERABILITY'] for d in a_list]
                    young_tuns =[d['gamma_tun'] for d in a_list]
                    young_faces =[d['gamma_face'] for d in a_list]

#                    # plot
#                    fig = plt.figure()
#                    fig.set_size_inches(12, 3.54)
#                    plt.plot(pks,young_tuns, label='E_TUN - GPa')
#                    plt.plot(pks,young_faces, label='E_FACE - GPa')
#                    y_min = math.floor(min(min(young_tuns),min(young_faces))/1.)*1. 
#                    y_max = math.ceil(max(max(young_tuns),max(young_faces))/1.)*1. 
#                    my_aspect = 50./(abs(y_max-y_min)/9.) # 50 m di profilo sono 1 cm in tavola, in altezza ho 9 cm a disposizione
#                    plt.axis([max(pks),min(pks),y_min,y_max])
#                    plt.xticks(pkxticks, pklabel, rotation='vertical')
#                    ax = plt.gca()
#                    ax.set_aspect(my_aspect)
#                    start, stop = ax.get_ylim()
#                    ticks = np.arange(start, stop + 1., 1.)
#                    ax.set_yticks(ticks)
#                    #ax.grid(True)
#                    plt.legend()
#                    #fig.set_dpi(1600)
#                    outputFigure(sPath, ("profilo_young_%s.svg" % sCode))
#                    logger.info("profilo_young.svg plotted in %s" % sPath)
#                    plt.show()

                    fig = plt.figure()
                    fig.set_size_inches(12, 3.54)
                    #plt.plot(pks,cobs, label='COB - bar')
                    plt.plot(pks,p_epms, label='P_EPB - bar')
                    plt.plot(pks,blowups, label='BLOWUP - bar')
                    plt.plot(pks,p_wts, label='P_WT - bar')
                    plt.plot(pks,p_tamezs, label='P_TAMEZ - bar')
                    y_min = math.floor(min(min(p_wts),min(cobs), min(p_epms), min(blowups))/.5)*.5-.5 
                    y_max = math.ceil(max(max(p_wts),max(cobs), max(p_epms), max(blowups))/.5)*.5+.5 
                    my_aspect = 50./(abs(y_max-y_min)/9.) # 50 m di profilo sono 1 cm in tavola, in altezza ho 9 cm a disposizione
                    plt.axis([max(pks),min(pks),y_min,y_max])
                    plt.xticks(pkxticks, pklabel, rotation='vertical')
                    ax = plt.gca()
                    ax.set_aspect(my_aspect)
                    start, stop = ax.get_ylim()
                    ticks = np.arange(start, stop + .5, .5)
                    ax.set_yticks(ticks)
                    #ax.grid(True)
                    plt.legend()
                    #fig.set_dpi(1600)
                    outputFigure(sPath, ("profilo_pressioni_%s.svg" % sCode))
                    logger.info("profilo_pressioni.svg plotted in %s" % sPath)
                    plt.show()
#                    """
                    plt.plot(pks,volume_losss, label='VL percent')
                    plt.plot(pks,k_pecks, label='k peck')
                    y_min = math.floor(min(min(volume_losss), min(k_pecks))/.05)*.05-.05 
                    y_max = math.ceil(max(max(volume_losss), max(k_pecks))/.05)*.05+.05 
                    plt.axis([max(pks),min(pks),y_min,y_max])
                    plt.xticks(pkxticks, pklabel, rotation='vertical')
                    ax = plt.gca()
                    my_aspect = 50./(abs(y_max-y_min)/9.0) # 50 m di profilo sono 1 cm in tavola, in altezza ho 9 cm a disposizione
                    ax.set_aspect(my_aspect)
                    start, stop = ax.get_ylim()
                    ticks = np.arange(start, stop + .05, .05)
                    ax.set_yticks(ticks)
                    #ax.grid(True)
                    #plt.legend()
                    #fig.set_dpi(1600)
                    outputFigure(sPath, ("profilo_peck_%s.svg" % sCode))
                    logger.info("profilo_peck.svg plotted in %s" % sPath)
                    plt.show()

                    plt.plot(pks,max_settlements, label='SETTLEMENT_MAX (mm)')
                    y_min = 0. # math.floor(min(max_settlements))-1. 
                    y_max = 30. # math.ceil(max(max_settlements))+1. 
                    plt.axis([max(pks),min(pks),y_min,y_max])
                    plt.xticks(pkxticks, pklabel, rotation='vertical')
                    ax = plt.gca()
                    my_aspect = 50./(abs(y_max-y_min)/4.5) # 50 m di profilo sono 1 cm in tavola, in altezza ho 9 cm a disposizione
                    ax.set_aspect(my_aspect)
                    start, stop = ax.get_ylim()
                    ticks = np.arange(start, stop + 5., 5.)
                    ax.set_yticks(ticks)
                    #ax.grid(True)
                    #plt.legend()
                    #fig.set_dpi(1600)
                    outputFigure(sPath, ("profilo_cedimenti_%s.svg" % sCode))
                    logger.info("profilo_cedimenti.svg plotted in %s" % sPath)
                    plt.show()

                    plt.plot(pks,tilts, label='BETA (0/00)')
                    plt.plot(pks,epshs, label='EPS_H (0/00)')
                    y_min = 0. # math.floor(min(max_settlements))-1. 
                    y_max = 3.5 # math.ceil(max(max_settlements))+1. 
                    plt.axis([max(pks),min(pks),y_min,y_max])
                    plt.xticks(pkxticks, pklabel, rotation='vertical')
                    ax = plt.gca()
                    my_aspect = 50./(abs(y_max-y_min)/4.5) # 50 m di profilo sono 1 cm in tavola, in altezza ho 9 cm a disposizione
                    ax.set_aspect(my_aspect)
                    start, stop = ax.get_ylim()
                    ticks = np.arange(start, stop + .5, .5)
                    ax.set_yticks(ticks)
                    #ax.grid(True)
                    #plt.legend()
                    #fig.set_dpi(1600)
                    outputFigure(sPath, ("profilo_distorsioni_%s.svg" % sCode))
                    logger.info("profilo_distorsioni.svg plotted in %s" % sPath)
                    plt.show()

                    plt.plot(pks,sensibilities, label='SENSIBILITY (1-3)')
                    y_min = -0.5 
                    y_max = 3.5  
                    plt.axis([max(pks),min(pks),y_min,y_max])
                    plt.xticks(pkxticks, pklabel, rotation='vertical')
                    ax = plt.gca()
                    my_aspect = 50./(abs(y_max-y_min)/3.) # 50 m di profilo sono 1 cm in tavola, in altezza ho 9 cm a disposizione
                    ax.set_aspect(my_aspect)
                    #start, stop = ax.get_ylim()
                    #ticks = np.arange(start, stop + 1., 1.)
                    ticks =[0., 1., 2., 3.]
                    ax.set_yticks(ticks)
                    #ax.grid(True)
                    #plt.legend()
                    #fig.set_dpi(1600)
                    outputFigure(sPath, ("profilo_sensibilita_%s.svg" % sCode))
                    logger.info("profilo_sensibilita.svg plotted in %s" % sPath)
                    plt.show()

                    plt.plot(pks,damages, label='DAMAGE CLASS (1-3)')
                    y_min = -0.5 
                    y_max = 3.5  
                    plt.axis([max(pks),min(pks),y_min,y_max])
                    plt.xticks(pkxticks, pklabel, rotation='vertical')
                    ax = plt.gca()
                    my_aspect = 50./(abs(y_max-y_min)/3.) # 50 m di profilo sono 1 cm in tavola, in altezza ho 9 cm a disposizione
                    ax.set_aspect(my_aspect)
                    #start, stop = ax.get_ylim()
                    #ticks = np.arange(start, stop + 1., 1.)
                    ticks =[0., 1., 2., 3.]
                    ax.set_yticks(ticks)
                    #ax.grid(True)
                    #plt.legend()
                    #fig.set_dpi(1600)
                    outputFigure(sPath, ("profilo_danni_%s.svg" % sCode))
                    logger.info("profilo_danni.svg plotted in %s" % sPath)
                    plt.show()

                    plt.plot(pks,vulnerabilities, label='VULNERABILITY (1-3)')
                    y_min = -0.5 
                    y_max = 3.5  
                    plt.axis([max(pks),min(pks),y_min,y_max])
                    plt.xticks(pkxticks, pklabel, rotation='vertical')
                    ax = plt.gca()
                    my_aspect = 50./(abs(y_max-y_min)/3.) # 50 m di profilo sono 1 cm in tavola, in altezza ho 9 cm a disposizione
                    ax.set_aspect(my_aspect)
                    #start, stop = ax.get_ylim()
                    #ticks = np.arange(start, stop + 1., 1.)
                    ticks =[0., 1., 2., 3.]
                    ax.set_yticks(ticks)
                    #ax.grid(True)
                    #plt.legend()
                    #fig.set_dpi(1600)
                    outputFigure(sPath, ("profilo_vulnerabilita_%s.svg" % sCode))
                    logger.info("profilo_vulnerabilita.svg plotted in %s" % sPath)
                    plt.show()

                    plt.plot(pks,consolidations, label='CONSOLIDATION (0-1)')
                    y_min = -0.3 
                    y_max = 1.3  
                    plt.axis([max(pks),min(pks),y_min,y_max])
                    plt.xticks(pkxticks, pklabel, rotation='vertical')
                    ax = plt.gca()
                    my_aspect = 50./(abs(y_max-y_min)/1.) # 50 m di profilo sono 1 cm in tavola, in altezza ho 9 cm a disposizione
                    ax.set_aspect(my_aspect)
                    #start, stop = ax.get_ylim()
                    #ticks = np.arange(start, stop + 1., 1.)
                    ticks =[0., 1.]
                    ax.set_yticks(ticks)
                    #ax.grid(True)
                    #plt.legend()
                    #fig.set_dpi(1600)
                    outputFigure(sPath, ("profilo_consolidamenti_%s.svg" % sCode))
                    logger.info("profilo_consolidamenti.svg plotted in %s" % sPath)
                    plt.show()
#                    """

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
