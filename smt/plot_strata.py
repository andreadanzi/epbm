# -*- coding: utf-8 -*-
'''
Crea grafico stratigrafia con le informazioni
'''
import logging
import logging.handlers
import os
import sys
import getopt
import plotly.offline as py
import plotly.graph_objs as go

from alignment_set import AlignmentSet
from project import Project
from domain import Domain
import helpers

def export_pk_data_csv(authenticate, project_code):
    logger = helpers.init_logger('smt_main', 'strata_graph.log', logging.DEBUG)
    smt_config = helpers.get_config('smt.cfg')
#    data_basedir = helpers.get_project_basedir(project_code)
#    outputdir = os.path.join(data_basedir, "out")

    #custom_type_tuple = eval(smt_config.get('INPUT_DATA_ANALYSIS', 'CUSTOM_TYPE'))
    logged_in, mongodb = helpers.init_db(smt_config, authenticate)
    if logged_in:
        logger.info("Logged in")
        pd = mongodb.Project.find_one({"code":project_code})
        if pd:
            logger.info("Project %s found", pd["project_name"])
            p = Project(mongodb, pd)
            p.load()
            pkbuffer = 5 #cambiare con lettura buffer in progetto/allineamento!
            for dom in Domain.find(mongodb, {"project_id": p._id}):
                dm = Domain(mongodb, dom)
                dm.load()
                for aset in mongodb.AlignmentSet.find({"domain_id": dm._id}):
                    a_set = AlignmentSet(mongodb, aset)
                    a_set.load()
                    als = list(mongodb.Alignment.find({"alignment_set_id":a_set._id},
                                                      {"PK":True, "STRATA": True}).sort("PK", 1))
                    maxY = float("-inf")
                    minY = float("inf")
                    x = []
                    y = []
                    text = []
                    shapes = []
                    for pks in als:
                        for strata in pks["STRATA"]:
                            ztop = strata["POINTS"]["top"]["coordinates"][2]
                            maxY = max(maxY, ztop)
                            zbase = strata["POINTS"]["base"]["coordinates"][2]
                            minY = min(minY, zbase)
                            x.append(pks["PK"])
                            y.append((ztop + zbase)/2)
                            # TODO: aggiungere tutte le info in text
                            text.append(strata["CODE"])
                            # TODO: dove inserisco i parametri?
                            shapes.append({
                                "type":"rect",
                                "x0": pks["PK"] - pkbuffer,
                                "y0": zbase,
                                "x1": pks["PK"] + pkbuffer,
                                "y1": ztop,
                                #"line":{"color":"red", "width":1},
                                "fillcolor": "red", #cambiare in base a CODE
                                })
                    layout = {
                        "xaxis": {
                            "range": [als[0]["PK"] - pkbuffer, als[-1]["PK"] - pkbuffer],
                            "showgrid": False,
                            },
                        "yaxis": {
                            "range":[minY, maxY],
                            "showgrid": False,
                            },
                        "width": 1800,
                        "height": 600,
                        "shapes": shapes
                        }
                    trace0 = go.Scatter(x=x, y=y, text=text, mode='markers')
                    fig = {"data": [trace0], "layout": layout}
                    plot_url = py.plot(fig, filename='shapes-rectangle')
        logger.info("%s terminated!", os.path.basename(__file__))
    else:
        logger.error("Authentication failed")
    helpers.destroy_logger(logger)

def main(argv):
    project_code = None
#    type_of_analysis = None
    bAuthenticate = False
    sSyntax = os.path.basename(__file__) + " -c <project code> [-a for autentication -h for help]"
    try:
        opts, args = getopt.getopt(argv, "hac:o:", ["code=", "output="])
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
        elif opt in ("-c", "--code"):
            project_code = arg
    export_pk_data_csv(bAuthenticate, project_code)


if __name__ == "__main__":
    main(sys.argv[1:])

