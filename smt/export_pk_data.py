# -*- coding: utf-8 -*-
'''
Esporta i dati lungo i tracciati
aghensi@20160414 riscritto con gestione percentili via smt.cfg
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

def export_pk_data_csv(authenticate, project_code, sPath):
    logger = helpers.init_logger('smt_main', 'export_pk_data.log', logging.DEBUG)
    smt_config = helpers.get_config('smt.cfg')
    outputdir = os.path.join(helpers.get_project_basedir(project_code), "out")
    #custom_type_tuple = eval(smt_config.get('INPUT_DATA_ANALYSIS', 'CUSTOM_TYPE'))
    logged_in, mongodb = helpers.init_db(smt_config, authenticate)
    if logged_in:
        logger.info("Logged in")
        pd = mongodb.Project.find_one({"project_code":project_code})
        if pd:
            logger.info("Project %s found", pd["project_name"])
            p = Project(mongodb, pd)
            p.load()
            for dom in Domain.find(mongodb, {"project_id": p._id}):
                dm = Domain(mongodb, dom)
                dm.load()
                for aset in mongodb.AlignmentSet.find({"domain_id": dm._id}):
                    a_set = AlignmentSet(mongodb, aset)
                    a_set.load()
                    als = mongodb.Alignment.find({"alignment_set_id":a_set._id},
                                                 {"PK":True, "COB":True, "P_EPB":True, "P_WT":True,
                                                  "BLOWUP":True, "VOLUME_LOSS":True, "K_PECK":True,
                                                  "SETTLEMENT_MAX":True, "TILT_MAX":True,
                                                  "EPS_H_MAX":True, "CONSOLIDATION_VALUE":True,
                                                  "SENSIBILITY":True, "DAMAGE_CLASS":True,
                                                  "VULNERABILITY":True}).sort("PK", 1)
                    rows = helpers.flatten_dicts_list(list(als))
                    helpers.write_dict_list_to_csv(
                        os.path.join(outputdir, "{}_data_export.csv".format(a_set.item["code"])),
                        helpers.get_dicts_list_keys(rows),
                        rows
                        )
                logger.info("export_data_csv terminated!")
    else:
        logger.error("Authentication failed")
    helpers.destroy_logger(logger)

def main(argv):
    project_code = None
    sPath = None
#    type_of_analysis = None
    bAuthenticate = False
    sSyntax = os.path.basename(__file__) + \
              " -c <project code> -o <output csv file name> [-a for autentication -h for help]"
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
        elif opt in ("-o", "--output"):
            sPath = arg
    if sPath:
        export_pk_data_csv(bAuthenticate, project_code, sPath)


if __name__ == "__main__":
    main(sys.argv[1:])
