# -*- coding: utf-8 -*-
'''
main.py
crea e popola il database MongoDB prendendo le informazioni dai file CSV
'''
import os
import sys
import getopt
import datetime
import logging
import logging.handlers

from alignment import Alignment
from alignment_set import AlignmentSet
from project import Project
from building import Building
from domain import Domain
import helpers

#PROJECT_CODE = "MDW029_S_E_05"

def import_all_data(project_code, project_name):
    '''
    funzione principale per l'inizializzazione del progetto
    '''
    logger = helpers.init_logger('smt_main', 'main.log', logging.DEBUG)
    smt_config = helpers.get_config('smt.cfg')
    mongodb = helpers.init_db(smt_config, True)[1]
    importdir = os.path.join(helpers.get_project_basedir(project_code), "in")

    pd = mongodb.Project.find_one({"project_code":project_code})
    if pd:
        logger.info("Deleting project %s", pd["project_name"])
        p = Project(mongodb, pd)
        p.delete()

    Project.ImportFromCSVFile(os.path.join(importdir, "project.csv"), mongodb)
    pd = mongodb.Project.find_one({"project_code":project_code})
    p = None
    # TODO: questo pezzo di codice non dovrebbe servire se imposto bene i CSV!
    if not pd:
        p = Project(mongodb, {"project_name":project_name, "project_code":project_code})
        p.item["created"] = datetime.datetime.utcnow()
        p.save()
    else:
        p = Project(mongodb, pd)
    # Import domain inside the project: one-to-many relationship by references
    p.import_objects("Domain", os.path.join(importdir, "domain.csv"))
    cr = Domain.find(mongodb, {"project_id": p._id})
    # Import Buildings
    p.import_buildings(os.path.join(importdir, "buildings.csv"))
    # Import Classes
    p.import_objects("BuildingClass", os.path.join(importdir, "building_class.csv"))
    p.import_objects("UndergroundStructureClass",
                     os.path.join(importdir, "underground_structure_class.csv"))
    p.import_objects("UndergroundUtilityClass",
                     os.path.join(importdir, "underground_utility_class.csv"))
    p.import_objects("OvergroundInfrastructureClass",
                     os.path.join(importdir, "overground_infrastructure_class.csv"))
    p.import_objects("VibrationClass", os.path.join(importdir, "vibration_class.csv"))

    bldgs = Building.find(mongodb, {"project_id": p._id})
    for bl in bldgs:
        b = Building(mongodb, bl)
        b.assign_class()

    for c in cr:
        d = Domain(mongodb, c)
        d.load()
        d.import_alignment_set(os.path.join(importdir, "alignment_set.csv"))
        asets = mongodb.AlignmentSet.find({"domain_id": d._id})
        for aset in asets:
            a_set = AlignmentSet(mongodb, aset)
            a_set.load()
            sCode = a_set.item["code"]
            sRelCsvCode = a_set.item["rel_csv_code"]
            # Import reference strata inside the alignment set: one-to-one relationship by embedding
            a_set.import_reference_strata(os.path.join(importdir, "reference_strata.csv"))
            # Import alignment inside the alignment set: one-to-many relationship by references
            a_set.import_alignment(os.path.join(importdir, "profilo_progetto-%s.csv" % sCode))
            # Import stratigraphy inside the alignment: one-to-many relationship by embedding
            a_set.import_strata(os.path.join(importdir, "stratigrafia-%s.csv" % sRelCsvCode))
            # Import water folders inside the alignment: one-to-many relationship by embedding
            a_set.import_falda(os.path.join(importdir, "falda-%s.csv" % sRelCsvCode))
            # Import tunnel sections inside the alignment: one-to-many relationship by embedding
            a_set.import_sezioni(os.path.join(importdir, "sezioni_progetto-%s.csv" % sRelCsvCode))
            # Import TBM inside the alignment: one-to-many relationship by embedding
            a_set.import_tbm(os.path.join(importdir, "tbm_progetto-%s.csv" % sRelCsvCode))
            # Import buildings deistances relative to this aligmentset
            a_set.import_building_pks(os.path.join(importdir, "buildings-%s.csv" % sRelCsvCode))
            als = Alignment.find(mongodb, {"alignment_set_id":a_set._id})
            for al in als:
                a = Alignment(mongodb, al)
                a.setProject(p.item)
                a.load()
                a.assign_reference_strata()
                a.define_tun_param()
                a.define_face_param()
                a.assign_buildings(a.define_buffer())

def main(argv):
    '''
    funzione principale
    '''
    project_code = None
    project_name = None
    syntax = os.path.basename(__file__) + " -c <project code> -n <project name>"
    try:
        opts = getopt.getopt(argv, "hc:n:", ["code=", "name="])[0]
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
        elif opt in ("-c", "--code"):
            project_code = arg
        elif opt in ("-n", "--name"):
            project_name = arg
    if project_code:
        import_all_data(project_code, project_name)


if __name__ == "__main__":
    main(sys.argv[1:])
