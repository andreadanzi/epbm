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
from building_class import BuildingClass
from underground_structure_class import UndergroundStructureClass
from underground_utility_class import UndergroundUtilityClass
from overground_infrastructure_class import OvergroundInfrastructureClass
from vibration_class import VibrationClass
from domain import Domain
import helpers


#PROJECT_CODE = "MDW029_S_E_05"
#PROJECT_NAME = '''
#Prolungamento della rete ferroviaria nella tratta metropolitana di Catania
#dalla stazione centrale f.s. all'aeroporto tratta stesicoro-aeroporto lotto 1"
#'''

def import_all_data(project_code, project_name):
    '''
    funzione principale per l'inizializzazione del progetto
    '''
    logger = helpers.init_logger('smt_main', 'main.log', logging.DEBUG)
    smt_config = helpers.get_config('smt.cfg')
    logged_in, mongodb = helpers.init_db(smt_config, True)
    importdir = os.path.join(helpers.get_project_basedir(project_code), "in")

    # TODO: come preservare gli altri progetti? aggiungere attributi a oggetti per legarli tra loro
    Building.delete_all(mongodb)
    BuildingClass.delete_all(mongodb)
    Alignment.delete_all(mongodb)
    AlignmentSet.delete_all(mongodb)
    Domain.delete_all(mongodb)
    Project.delete_all(mongodb)

    Project.ImportFromCSVFile(os.path.join(importdir, "project.csv"), mongodb)
    pd = mongodb.Project.find_one({"project_code":project_code})
    p = None
    if not pd:
        p = Project(mongodb, {"project_name":project_name, "project_code":project_code})
        p.item["created"] = datetime.datetime.utcnow()
        p.save()
    else:
        p = Project(mongodb, pd)
    # Import domain inside the project: one-to-many relationship by references
    p.import_domains(os.path.join(importdir, "domain.csv"))
    cr = Domain.find(mongodb, {"project_id": p._id})
    # Import Buildings
    Building.ImportFromCSVFile(os.path.join(importdir, "buildings-tun.csv"), mongodb)
    Building.import_building_pks(mongodb, os.path.join(importdir, "buildings-tun.csv"))
    BuildingClass.ImportFromCSVFile(os.path.join(importdir, "building_class.csv"), mongodb)
    UndergroundStructureClass.ImportFromCSVFile(os.path.join(importdir, "underground_structure_class.csv"), mongodb)
    UndergroundUtilityClass.ImportFromCSVFile(os.path.join(importdir, "underground_utility_class.csv"), mongodb)
    OvergroundInfrastructureClass.ImportFromCSVFile(os.path.join(importdir, "overground_infrastructure_class.csv"), mongodb)
    VibrationClass.ImportFromCSVFile(os.path.join(importdir, "vibration_class.csv"), mongodb)
    bldgs = Building.find(mongodb, {})
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
        opts, ignorethis = getopt.getopt(argv, "hc:n:", ["code=", "name="])
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
