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
from domain import Domain
from reference_strata import ReferenceStrata
from smt_stat import get_triang
from scipy.stats import truncnorm

# danzi.tn@20160407 set della nuova collection ReferenceStrata per il Sampling
def process_calc(project_code, bAuthenticate,nSamples):
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
                samples = ReferenceStrata.gen_samples_strata(mongodb, nSamples, project_code)
                # danzi.tn@20160407e
                found_domains = Domain.find(mongodb, {"project_id": p._id})         
                for dom in found_domains:
                    d = Domain(mongodb, dom)
                    d.load()
                    asets = mongodb.AlignmentSet.find({"domain_id": d._id})
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
                            sys.stdout.write("\r{:5s} pk= {:.0f} progress= {:.0%}".format(a_set.item["code"], a.item["PK"], cnt/cnt_tot))
                            sys.stdout.flush()
                            a.perform_calc(str(datetime.now()))
            else:
                logger.error("ReferenceStrata for Project %s not found" % project_code)
        else:
            logger.error("Project %s not found" % project_code)
    else:
        logger.error("Authentication failed")

def main(argv):
    bAuthenticate = False
    project_code = None
    nSamples = 1
    sSyntax = os.path.basename(__file__) +" -c <project code> [-a for authentication] [-n <positive number_of_samples>]"
    try:
        opts, args = getopt.getopt(argv, "hac:n:", ["code=","nsamples="])
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
        elif opt in ("-n", "--nsamples"):
            nSamples = int(arg)
            if nSamples <= 0:
                print sSyntax
                sys.exit()
        elif opt in ("-c", "--code"):
            project_code = arg
    if project_code:
        process_calc(project_code, bAuthenticate,nSamples)

if __name__ == "__main__":
    main(sys.argv[1:])
