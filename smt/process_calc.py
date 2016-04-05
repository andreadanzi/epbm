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

def process_calc(project_code, bAuthenticate):
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
                        a.load()
                        cnt += 1.
                        sys.stdout.write("\r{:5s} pk= {:.0f} progress= {:.0%}".format(a_set.item["code"], a.item["PK"], cnt/cnt_tot))
                        sys.stdout.flush()
                        a.perform_calc(str(datetime.now()))
    else:
        logger.error("Authentication failed")

def main(argv):
    bAuthenticate = False
    project_code = None
    sSyntax = os.path.basename(__file__) +" -c <project code> [-a for authentication]"
    try:
        opts, args = getopt.getopt(argv, "hac:", ["code="])
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
    if project_code:
        process_calc(project_code, bAuthenticate)

if __name__ == "__main__":
    main(sys.argv[1:])
