# -*- coding: utf-8 -*-
'''
modulo per eseguire i calcoli
'''
import os
import sys
import getopt
import logging
import logging.handlers
from datetime import datetime
import helpers
from alignment import Alignment
from alignment_set import AlignmentSet
from project import Project
from reference_strata import ReferenceStrata

# danzi.tn@20160407 set della nuova collection ReferenceStrata per il Sampling
# danzi.tn@20160418 pulizia sui Buildings del progetto dei dati di analisi=>clear_building_analysis
# python process_calc.py -c MDW029_S_E_05 -a -n 1 -t s
def process_calc(project_code, bAuthenticate, nSamples, type_of_analysis):
    logger = helpers.init_logger('smt_main', 'process_calc.log', logging.DEBUG)
    smt_config = helpers.get_config('smt.cfg')
    logged_in, mongodb = helpers.init_db(smt_config, True)
    if logged_in:
        logger.info("Authenticated")
        pd = mongodb.Project.find_one({"project_code":project_code})
        if pd:
            logger.info("Project %s found", pd["project_name"])
            p = Project(mongodb, pd)
            p.load()
            # danzi.tn@20160407 recupero dei dati presenti in ReferenceStrata
            rs_items = ReferenceStrata.find(mongodb, {"project_id": p._id})
            if rs_items:
                b_values_dtype_names = ("vulnerability_base",
                                        "damage_class_base",
                                        "settlement_max_base",
                                        "tilt_max_base",
                                        "esp_h_max_base",
                                        "k_peck",
                                        "vulnerability",
                                        "damage_class",
                                        "settlement_max",
                                        "tilt_max",
                                        "esp_h_max",
                                        "eps_crit",
                                        "eps_0",
                                        "p_tbm",
                                        "blowup",
                                        "tamez",
                                        "vulnerability_class_vibration",
                                        "damage_class_vibration",
                                        "vibration_speed_mm_s")
                p.clear_building_analysis(b_values_dtype_names)
                custom_type = smt_config.get('INPUT_DATA_ANALYSIS', 'CUSTOM_TYPE')
                sCustom_type = "(%s)" % custom_type
                custom_type_tuple = eval(sCustom_type)

                base_percentile = smt_config.getfloat('BASE_DATA_ANALYSIS', 'BASE_PERCENTILE')
                samples = ReferenceStrata.gen_samples_strata(mongodb, nSamples, project_code,
                                                             type_of_analysis, base_percentile,
                                                             custom_type_tuple)

                base_vulnerability = smt_config.getint('BASE_DATA_ANALYSIS', 'BASE_VULNERABILITY')
                a_data_analysis_perc = smt_config.get('A_DATA_ANALYSIS', 'PERCENTILES')
                a_data_analysis_bins = smt_config.get('A_DATA_ANALYSIS', 'BINS')
                b_data_analysis_perc = smt_config.get('B_DATA_ANALYSIS', 'PERCENTILES')
                b_data_analysis_bins = smt_config.get('B_DATA_ANALYSIS', 'BINS')
                s_data_analysis_perc = smt_config.get('S_DATA_ANALYSIS', 'PERCENTILES')
                s_data_analysis_bins = smt_config.get('S_DATA_ANALYSIS', 'BINS')
                buildings_limits = dict(smt_config.items('BUILDINGS_LIMITS'))
                a_bins = dict(smt_config.items('A_BINS'))
                b_bins = dict(smt_config.items('B_BINS'))
                samples["DATA_ANALYSIS"] = {
                    "base_vulnerability":base_vulnerability,
                    "a":{
                        "per":eval(a_data_analysis_perc),
                        "bins":eval(a_data_analysis_bins)
                        },
                    "b":{
                        "per":eval(b_data_analysis_perc),
                        "bins":eval(b_data_analysis_bins)
                        },
                    "s":{
                        "per":eval(s_data_analysis_perc),
                        "bins":eval(s_data_analysis_bins)
                        },
                    "buildings_limits" : buildings_limits,
                    "a_bins": a_bins,
                    "b_bins": b_bins
                    }
                # danzi.tn@20160407e
                # aghensi@20160621 tolto domini
#                found_domains = Domain.find(mongodb, {"project_id": p._id})
#                for dom in found_domains:
#                    d = Domain(mongodb, dom)
#                    d.load()
#                    asets = mongodb.AlignmentSet.find({"domain_id": d._id})
                asets = mongodb.AlignmentSet.find({"project_id": p._id})
                for aset in asets:
                    a_set = AlignmentSet(mongodb, aset)
                    a_set.load()
                    #sCode = a_set.item["code"]
                    als = Alignment.find(mongodb, {"alignment_set_id":a_set._id}).sort("PK", 1)
                    cnt = 0.
                    cnt_tot = als.count()
                    for al in als:
                        a = Alignment(mongodb, al)
                        a.setProject(p.item)
                        # danzi.tn@20160407 set dai samples nella PK
                        a.setSamples(samples)
                        a.load()
                        cnt += 1.
                        sys.stdout.write("\r{:5s} pk= {:.02f} progress= {:.0%}".format(a_set.item["code"], a.item["PK"], cnt/cnt_tot))
                        sys.stdout.flush()
                        a.perform_calc(str(datetime.now()))
            else:
                logger.error("ReferenceStrata for Project %s not found", project_code)
        else:
            logger.error("Project %s not found", project_code)
    else:
        logger.error("Authentication failed")

def main(argv):
    bAuthenticate = False
    project_code = None
    type_of_analysis = 's'
    nSamples = 1
    sSyntax = os.path.basename(__file__) +" -c <project code> [-a for authentication] [-n <positive number_of_samples>] [-t s for standard, c for custom]"
    try:
        opts, args = getopt.getopt(argv, "hac:n:t:", ["code=", "nsamples=", "type="])
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
        elif opt in ("-t", "--type"):
            type_of_analysis = arg
        elif opt in ("-n", "--nsamples"):
            nSamples = int(arg)
            if nSamples <= 0:
                print sSyntax
                sys.exit()
        elif opt in ("-c", "--code"):
            project_code = arg
    if project_code:
        process_calc(project_code, bAuthenticate, nSamples, type_of_analysis)

if __name__ == "__main__":
    main(sys.argv[1:])
