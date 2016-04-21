# -*- coding: utf-8 -*-
'''
Crea grafico stratigrafia con le informazioni
'''
import logging
import logging.handlers
import os
import sys
import getopt

from alignment_set import AlignmentSet
from project import Project
from domain import Domain
import helpers

def export_pk_data_csv(authenticate, project_code):
    logger = helpers.init_logger('smt_main', 'strata_graph.log', logging.DEBUG)
    smt_config = helpers.get_config('smt.cfg')

    #custom_type_tuple = eval(smt_config.get('INPUT_DATA_ANALYSIS', 'CUSTOM_TYPE'))
    logged_in, mongodb = helpers.init_db(smt_config, authenticate)
    if not logged_in:
        logger.error("Authentication failed")
        helpers.destroy_logger(logger)
        return

    logger.info("Logged in")
    pd = mongodb.Project.find_one({"project_code":project_code})
    if not pd:
        logger.error("Project %s not found!", pd["project_name"])
        helpers.destroy_logger(logger)
        return

    logger.info("Project %s found", pd["project_name"])
    p = Project(mongodb, pd)
    p.load()
    data_basedir = os.path.join(helpers.get_project_basedir(project_code), "out")
    if not os.path.exists(data_basedir):
        os.makedirs(data_basedir)

    pkbuffer = 5 #TODO cambiare con lettura buffer in progetto/allineamento!
    for dom in Domain.find(mongodb, {"project_id": p._id}):
        dm = Domain(mongodb, dom)
        dm.load()
        for aset in mongodb.AlignmentSet.find({"domain_id": dm._id}):
            a_set = AlignmentSet(mongodb, aset)
            a_set.load()
            als = list(mongodb.Alignment.find({"alignment_set_id":a_set._id},
                                              {"PK":True, "STRATA": True}).sort("PK", 1))
            if not als:
                continue
            shp_path = os.path.join(data_basedir, "strata.shp")
            fields_dict = {
                "PK": "float",
                "CODE": "string",
                "phimin": "float",
                "Cumax": "float",
                "phi_tr": "float",
                "cmin": "float",
                "Emin": "float",
                "Emax": "float",
                "imin": "float",
                "k0max": "float",
                "Cumin": "float",
                "kmin": "float",
                "k0min": "float",
                "kmax": "float",
                "c_tr": "float",
                "imax": "float",
                "n": "float",
                "inom": "float",
                "etounnel": "float",
                "cmax": "float",
                "k0": "float",
                "phimax": "float",
                }
            shape_data, layer = helpers.create_shapefile(shp_path, "strata", 3004, logger, fields_dict)
            for pks in als:
                x0 = pks["PK"] - pkbuffer
                x1 = pks["PK"] + pkbuffer
                for strata in pks["STRATA"]:
                    y0 = strata["POINTS"]["base"]["coordinates"][2]*10
                    y1 = strata["POINTS"]["top"]["coordinates"][2]*10
                    strataFeature = helpers.create_rectangular_feature(layer, x0, y0, x1, y1)
                    for key in fields_dict:
                        if key == "PK":
                            strataFeature.SetField("PK", pks["PK"])
                        elif key == "CODE":
                            strataFeature.SetField("CODE", strata["CODE"])
                        else:
                            strataFeature.SetField(key[:10], strata["PARAMETERS"][key])
                    layer.SetFeature(strataFeature)
                    #layer.SyncToDisk()
                    strataFeature.Destroy()
            shape_data.Destroy()
    logger.info("%s terminated!", os.path.basename(__file__))
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

