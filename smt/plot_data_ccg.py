# -*- coding: utf-8 -*-
import math
import logging
import logging.handlers
import os
import sys
import getopt
from collections import defaultdict
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import csv

from alignment_set import AlignmentSet
from project import Project
from domain import Domain
import helpers

# danzi.tn@20160310 plot secondo distanze dinamiche
# Colori da associare alle aree degli strati di riferimento
MAIN_COLORS = {'MC':'#1f77b4',
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

def mid_point(p1, p2):
    x = (p1[0] + p2[0])/2.
    y = (p1[1] + p2[1])/2.
    return x, y

def asse2p(p1, p2, x):
    mid = mid_point(p1, p2)
    if p2[0] == p1[0]:
        return mid[1]
    if p2[1] == p1[1]:
        return None
    m = (p2[1]-p1[1])/(p2[0]-p1[0])
    m_asse = -1/m
    return m_asse*(x-mid[0]) + mid[1]

def pfromdistance(p1, p2, d):
    mid = mid_point(p1, p2)
    if p2[0] == p1[0]:
        return (p1[0] - d, mid[1]), (p1[0]+d, mid[1])
    if p2[1] == p1[1]:
        return (mid[0], p1[1]+d), (mid[0], p1[1] - d)
    m = (p2[1]-p1[1])/(p2[0]-p1[0])
    mx = mid[0]
    a = 1.
    b = -2.*mx
    c = mx**2-d**2*m**2/(m**2+1)
    coeff = [a, b, c]
    res_x = np.roots(coeff)
    res_y0 = asse2p(p1, p2, res_x[0])
    res_y1 = asse2p(p1, p2, res_x[1])
    return (res_x[0], res_y0), (res_x[1], res_y1)

def plot_line(ob, color="green"):
    parts = hasattr(ob, 'geoms') and ob or [ob]
    for part in parts:
        x, y = part.xy
        plt.plot(x, y, 'o', color=color, zorder=1)
        #plt.plot(x, y, color=color, linewidth=2, solid_capstyle='round', zorder=1)

def plot_coords(x, y, color='#999999', zorder=1):
    plt.plot(x, y, 'o', color=color, zorder=zorder)

def outputFigure(sDiagramsFolderPath, sFilename, formato="svg"):
    imagefname = os.path.join(sDiagramsFolderPath, sFilename)
    if os.path.exists(imagefname):
        os.remove(imagefname)
    plt.savefig(imagefname, format=formato, bbox_inches='tight', pad_inches=0)

def processSettlements(a_list):
    distanceIndex = defaultdict(list)
    for a_item in a_list:
        for item in a_item["SETTLEMENTS"]:
            distanceIndex[item["code"]].append(item["value"])
    distanceKeys = distanceIndex.keys()
    distanceKeys.sort()
    return distanceKeys, distanceIndex

def fillBetweenStrata(a_list):
    currentStrata = None
    x = []
    y1 = []
    y2 = []
#    facecolors = ['orange', 'yellow']
    for a_item in a_list:
        z_base = a_item['REFERENCE_STRATA']['POINTS']['base']['coordinates'][2]
        z_top = a_item['REFERENCE_STRATA']['POINTS']['top']['coordinates'][2]
        code = a_item['REFERENCE_STRATA']['CODE']
        if not currentStrata:
            currentStrata = code
        elif currentStrata == code:
            pass
        else:
            plt.fill_between(x, y1, y2, facecolor=MAIN_COLORS[currentStrata], interpolate=True,
                             label=currentStrata)
            x = []
            y1 = []
            y2 = []
            currentStrata = code
        x.append(a_item['PK'])
        y1.append(z_base)
        y2.append(z_top)

def plot_data(project_code, authenticate, type_of_analysis):
    logger = helpers.init_logger('smt_main', 'plot_data.log', logging.DEBUG)
    smt_config = helpers.get_config('smt.cfg')
    # aghensi@20160414 aggiunto gestione percentili via smt.cfg
    custom_type_tuple = eval(smt_config.get('INPUT_DATA_ANALYSIS', 'CUSTOM_TYPE'))
    logged_in, mongodb = helpers.init_db(smt_config, authenticate)
    outputdir = os.path.join(helpers.get_project_basedir(project_code), "out")
    mpl.rcParams.update({'font.size': 6})
    if logged_in:
        logger.info("Logged in")
        pd = mongodb.Project.find_one({"project_code":project_code})
        if pd:
            logger.info("Project %s found", pd["project_name"])
            p = Project(mongodb, pd)
            p.load()
            found_domains = Domain.find(mongodb, {"project_id": p._id})
            for dom in found_domains:
                dm = Domain(mongodb, dom)
                dm.load()
                # Example of query
                asets = mongodb.AlignmentSet.find({"domain_id": dm._id})
                for aset in asets:
                    a_set = AlignmentSet(mongodb, aset)
                    a_set.load()
                    als = mongodb.Alignment.find({"alignment_set_id":a_set._id},
                                                 {"PK":True, "COB":True, "P_EPB":True, "P_WT":True,
                                                  "BLOWUP":True, "VOLUME_LOSS":True, "K_PECK":True,
                                                  "SETTLEMENT_MAX":True, "TILT_MAX":True,
                                                  "EPS_H_MAX":True, "CONSOLIDATION_VALUE":True,
                                                  "SENSIBILITY":True, "DAMAGE_CLASS":True,
                                                  "VULNERABILITY":True}).sort("PK", 1)
                    if type_of_analysis == 'c' and len(custom_type_tuple) >= 0:
                        a_list = list(als)
                        for percentile in custom_type_tuple:
                            plot_alignset_data(a_list, str(percentile), a_set.item["code"],
                                               outputdir, logger)
                    elif type_of_analysis == 's':
                        plot_alignset_data(list(als), 'avg', a_set.item["code"],
                                           outputdir, logger)
    else:
        logger.error("Authentication failed")
    helpers.destroy_logger(logger)

def plot_alignset_data(a_list, percentile, sCode, outputdir, logger):
    pks = []
    pklabel = []
    pkxticks = []
    for d in a_list:
        pk_value = round(d['PK']/10., 0) *10.
        pks.append(pk_value)
        hundreds = int(pk_value-int(pk_value/1000.)*1000)
        if hundreds%100 == 0:
            pkxticks.append(pk_value)
            pklabel.append("%d+%03d" % (int(pk_value/1000.), hundreds))
    if sCode == 'smi':
        d_press = 0.5 # bar tra calotta e asse
        d_press_wt = 0.35
    else:
        d_press = 0.7 # bar tra calotta e asse
        d_press_wt = 0.5
    suffix = "{}-{}".format(sCode, percentile)
    # scalo di fattore 100
    # p_wts =[d['P_WT']/100 - d_press_wt for d in a_list]
    p_wts = [(max(0., d['P_WT'][percentile]/100. - d_press_wt)) for d in a_list]
    # scalo di fattore 100
    p_epms = [max(0., d['P_EPB'][percentile]/100. - d_press) for d in a_list]
    # scalo di fattore 100
#    p_tamezs = [max(0., d['P_TAMEZ']/100. - d_press) for d in a_list]
    cobs = [max(0., d['COB'][percentile]/100. - d_press) for d in a_list]
    # scalo di fattore 100
    blowups = [max(0., d['BLOWUP'][percentile]/100. - d_press) for d in a_list]
    # amplifico di fattore 100
    volume_losss = [d['VOLUME_LOSS'][percentile]*100. for d in a_list]
    k_pecks = [d['K_PECK'][percentile] for d in a_list]
    # amplifico di fattore 1000
    max_settlements = [d['SETTLEMENT_MAX'][percentile]*1000. for d in a_list]
    tilts = [d['TILT_MAX'][percentile]*1000. for d in a_list]
    epshs = [d['EPS_H_MAX'][percentile]*1000. for d in a_list]
    consolidations = [d['CONSOLIDATION_VALUE'][percentile] for d in a_list]
    sensibilities = [d['SENSIBILITY'][percentile] for d in a_list]
    damages = [d['DAMAGE_CLASS'][percentile] for d in a_list]
    vulnerabilities = [d['VULNERABILITY'][percentile] for d in a_list]
#    young_tuns = [d['gamma_tun'] for d in a_list]
#    young_faces = [d['gamma_face'] for d in a_list]
#                   {"name":"profilo_young", "width":30., "height":9.,
#                    "scale":50, "rounding":.5,
#                    "campi":[{"label":"E_TUN - GPa", "valori":young_tuns},
#                             {"label":"E_FACE - GPa", "valori":young_faces}]},

    all_options = [{"name":"profilo_pressioni", "width":30., "height":9.,
                    "scale":50, "rounding":.5,
                    "campi":[{"label":"COB (bar)", "valori":cobs},
                             {"label":"P_EPB (bar)", "valori":p_epms},
                             {"label":"BLOWUP (bar)", "valori":blowups},
                             {"label":"P_WT (bar)", "valori":p_wts}]},
                   {"name":"profilo_peck", "width":30., "height":9.,
                    "scale":50, "rounding":.05,
                    "campi":[{"label":"VL percent", "valori":volume_losss},
                             {"label":"k peck", "valori":k_pecks}]},
                   {"name":"profilo_cedimenti", "width":30., "height":4.5,
                    "scale":50, "rounding":5.,
                    "campi":[{"label":"SETTLEMENT_MAX (mm)", "valori":max_settlements}]},
                   {"name":"profilo_distorsioni", "width":30., "height":4.5,
                    "scale":50, "rounding":.5,
                    "campi":[{"label":"BETA (0/00)", "valori":tilts},
                             {"label":"EPS_H (0/00)", "valori":epshs}]},
                   {"name":"profilo_sensibilita", "width":30., "height":3.,
                    "scale":50, "rounding":1,
                    "campi":[{"label":"SENSIBILITY (1-3)", "valori":sensibilities}]},
                   {"name":"profilo_danni", "width":30., "height":3.,
                    "scale":50, "rounding":1,
                    "campi":[{"label":"DAMAGE CLASS (1-3)", "valori":damages}]},
                   {"name":"profilo_vulnerabilita", "width":30., "height":3.,
                    "scale":50, "rounding":1,
                    "campi":[{"label":"VULNERABILITY (1-3)", "valori":vulnerabilities}]},
                   {"name":"profilo_vulnerabilita", "width":30., "height":1.,
                    "scale":50, "rounding":1,
                    "campi":[{"label":"CONSOLIDATION (0-1)", "valori":consolidations}]}]
    for options in all_options:
        plot_single_graph(suffix, pks, pkxticks, pklabel, options, outputdir, logger)
        #export_to_csv(suffix, pks, options, outputdir)
    logger.info("plot_data terminated!")

def plot_single_graph(suffix, pks, pkxticks, pklabel, options, outputdir, logger):
    rounding = options["rounding"]
    fig = plt.figure()
    fig.set_size_inches(options["width"]/2.54, options["height"]/2.54)
    min_value = float("inf")
    max_value = float("-inf")
    for campo in options["campi"]:
        plt.plot(pks, campo["valori"], label=campo["label"])
        min_value = min(min_value, min(campo["valori"]))
        max_value = max(max_value, max(campo["valori"]))
    y_min = math.floor(min_value/rounding)*rounding-rounding
    y_max = math.ceil(max_value/rounding)*rounding+rounding
    # 50 m di profilo sono 1 cm in tavola, in altezza ho 9 cm a disposizione
    my_aspect = options["scale"]/(abs(y_max-y_min)/(options["height"]))
    plt.axis([min(pks), max(pks), y_min, y_max])
    plt.xticks(pkxticks, pklabel, rotation='vertical')
    ax = plt.gca()
    ax.set_aspect(my_aspect)
    start, stop = ax.get_ylim()
    ticks = np.arange(start, stop + rounding, rounding)
    ax.set_yticks(ticks)
    #ax.grid(True)
    plt.legend()
    #fig.set_dpi(1600)
    outputFigure(outputdir, "{}_{}.svg".format(options["name"], suffix))
    logger.info("profilo_pressioni.svg plotted in %s", outputdir)
    #plt.show()
    plt.close()

#def export_to_csv(suffix, pks, options, outputdir):
#    headers = ["pk"]
#    values = [pks]
#    outputpath = os.path.join(outputdir, "{}-{}.csv".format(options["name"], suffix))
#    for campo in options["campi"]:
#        headers.append(campo["label"])
#        values.append(campo["valori"])
#    with open(outputpath, 'wb') as out_csvfile:
#        writer = csv.writer(out_csvfile, delimiter=";")
#        writer.writerow(headers)
#        for row in zip(*values):
#            writer.writerow(row)

def main(argv):
    project_code = None
    authenticate = False
    type_of_analysis = None
    syntax = "Usage: " + os.path.basename(__file__) + \
             " -c <project code> [-a for autentication -h for help]"
    try:
        opts = getopt.getopt(argv, "hac:t:", ["code=", "type="])[0]
    except getopt.GetoptError:
        print syntax
        sys.exit(1)
    if len(opts) < 1:
        print syntax
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print syntax
            sys.exit()
        elif opt == '-a':
            authenticate = True
        elif opt in ("-c", "--code"):
            project_code = arg
        elif opt in ("-t", "--type"):
            type_of_analysis = arg
    plot_data(project_code, authenticate, type_of_analysis)

if __name__ == "__main__":
    main(sys.argv[1:])
