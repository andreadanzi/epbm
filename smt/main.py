# -*- coding: utf-8 -*-
'''
main.py
crea e popola il database MongoDB prendendo le informazioni dai file CSV
'''
import logging
import logging.handlers
import os
import sys
import getopt
import datetime

from alignment import Alignment
from alignment_set import AlignmentSet
from project import Project
from building import Building
from building_class import BuildingClass
#from underground_structure_class import UndergroundStructureClass
#from underground_utility_class import UndergroundUtilityClass
#from overground_infrastructure_class import OvergroundInfrastructureClass
#from vibration_class import VibrationClass
from domain import Domain
import helpers

# TODO: chiedo PROJECT_CODE da linea comando, leggo gli altri dati da CSV contenuti nella cartella chiamata con quel codice
PROJECT_CODE = "MDW029_S_E_05"
PROJECT_NAME = u"Prolungamento della rete ferroviaria nella tratta metropolitana di Catania dalla stazione centrale f.s. all'aeroporto tratta stesicoro-aeroporto lotto 1"

def import_all_data(project_code):
    logger = helpers.init_logger('smt_main', 'main.log', logging.DEBUG)
    smt_config = helpers.get_config('smt.cfg')
    logged_in, mongodb = helpers.init_db(smt_config, True)
    project_basedir = helpers.get_project_basedir(project_code)

    # TODO: come preservare gli altri progetti?
    Building.delete_all(mongodb)
    BuildingClass.delete_all(mongodb)
    Alignment.delete_all(mongodb)
    AlignmentSet.delete_all(mongodb)
    Domain.delete_all(mongodb)
    Project.delete_all(mongodb)



    Project.ImportFromCSVFile(os.path.join(project_basedir, "in" ,"project.csv"), mongodb)
    pd = mongodb.Project.find_one({"project_code":project_code})
    p = None
    if not pd:
        p = Project(mongodb, {"project_name":PROJECT_NAME, "project_code":PROJECT_CODE})
        p.item["created"] = datetime.datetime.utcnow()
        p.save()
    else:
        p = Project(mongodb, pd)
    # Import domain inside the project: one-to-many relationship by references
    p.import_domains("../data/MDW029_S_E_05/in/domain.csv")
    cr = Domain.find(mongodb, {"project_id": p._id})
    # Import Buildings
    Building.ImportFromCSVFile("../data/MDW029_S_E_05/in/buildings-tun.csv", mongodb)
    Building.import_building_pks(mongodb, "../data/MDW029_S_E_05/in/buildings-tun.csv")
    BuildingClass.ImportFromCSVFile("../data/MDW029_S_E_05/in/building_class.csv", mongodb)
    #UndergroundStructureClass.ImportFromCSVFile("../data/underground_structure_class.csv", db)
    #UndergroundUtilityClass.ImportFromCSVFile("../data/underground_utility_class.csv", db)
    #OvergroundInfrastructureClass.ImportFromCSVFile("../data/overground_infrastructure_class.csv", db)
    #VibrationClass.ImportFromCSVFile("../data/vibration_class.csv", db)
    bldgs = Building.find(mongodb, {})
    for bl in bldgs:
        b = Building(mongodb, bl)
        b.assign_class()

    for c in cr:
        d = Domain(mongodb, c)
        d.load()
        d.import_alignment_set("../data/MDW029_S_E_05/in/alignment_set.csv")
        asets = mongodb.AlignmentSet.find({"domain_id": d._id})
        for aset in asets:
            a_set = AlignmentSet(mongodb, aset)
            a_set.load()
            sCode = a_set.item["code"]
            sRelCsvCode = a_set.item["rel_csv_code"]
            # Import reference strata inside the alignment set: one-to-one relationship by embedding
            a_set.import_reference_strata("../data/MDW029_S_E_05/in/reference_strata.csv")
            # Import alignment inside the alignment set: one-to-many relationship by references
            a_set.import_alignment("../data/MDW029_S_E_05/in/profilo_progetto-%s.csv" % sCode)
            # Import stratigraphy inside the alignment: one-to-many relationship by embedding
            a_set.import_strata("../data/MDW029_S_E_05/in/stratigrafia-%s.csv" % sRelCsvCode)
            # Import water folders inside the alignment: one-to-many relationship by embedding
            a_set.import_falda("../data/MDW029_S_E_05/in/falda-%s.csv" % sRelCsvCode)
            # Import tunnel sections inside the alignment: one-to-many relationship by embedding
            a_set.import_sezioni("../data/MDW029_S_E_05/in/sezioni_progetto-%s.csv" % sRelCsvCode)
            # Import TBM inside the alignment: one-to-many relationship by embedding
            a_set.import_tbm("../data/MDW029_S_E_05/in/tbm_progetto-%s.csv" % sRelCsvCode)
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
    syntax = os.path.basename(__file__) + " -o <project code>"
    try:
        opts, _ = getopt.getopt(argv, "hc:", ["code="])
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
    if project_code:
        import_all_data(project_code)


if __name__ == "__main__":
    main(sys.argv[1:])
