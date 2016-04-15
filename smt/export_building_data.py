# -*- coding: utf-8 -*-
'''
export_buildngs_data
esporta il file CSV con i valori calcolati degli edifici
TODO: esportare direttamente il file SHP
'''
import os
import sys
import getopt
import logging
import logging.handlers

from project import Project
from building import Building
import helpers

def export_buildings_data(project_code, authenticate, csv_name, shp_name, fields_name):
    '''
    funzione che fa il vero lavoro
    '''
    logger = helpers.init_logger('smt_main', 'export_building_data.log', logging.DEBUG)
    smt_config = helpers.get_config('smt.cfg')
    logged_in, mongodb = helpers.init_db(smt_config, authenticate)
    if not logged_in:
        logger.error("Not authenticated")
        return
    data_basedir = helpers.get_project_basedir(project_code)
    fields_path = os.path.join(data_basedir, "in", fields_name)
    csv_path = os.path.join(data_basedir, "out", csv_name)
    if not os.path.exists(fields_path):
        logger.error("file delle impostazioni di output %s non trovato", fields_path)
        return
    dati = helpers.get_csv_dict_list(fields_path)
    if not all(key in dati[0] for key in ("field", "csv_field", "shp_field",
                                          "field_type", "multiplier")):
        logger.error("%s non contiene tutti i campi richiesti", fields_path)
        return
    # EXPORT BUILDINGS CALCULATED DATA

    projdb = mongodb.Project.find_one({"project_code":project_code})
    if not projdb:
        logger.error("Il progetto dal codice %s non esiste!", project_code)
        return
    project = Project(mongodb, projdb)
    # se non esiste l'attributo epsg di progetto uso Monte Mario di default (3004)
    bcurr = Building.find(mongodb, {"project_id": project._id})
    if bcurr.count() == 0:
        logger.error("Nessun Edificio Trovato per il progetto %s!", project_code)
        return
    headers, csv_data, shp_headers, shp_data = get_bldg_data(dati, bcurr, mongodb, logger)
    helpers.write_dict_list_to_csv(csv_path, headers, csv_data)
    if shp_name:
        shp_path = os.path.join(data_basedir, "gis", shp_name)
        update_bldg_shp(shp_path, shp_headers, shp_data, logger)
    helpers.destroy_logger(logger)

def get_bldg_data(quali_dati, bcurr, mongodb, logger):
    '''
    legge dal database i dati degli edifici,
    restituisce una lista di dizionari e una lista di nomi di colonna
    per scrivere il file csv e creare lo shapefile
    '''
    headers = set([])
    csv_data = []
    shp_data = []
    shp_headers = {}
    for item in bcurr:
        building = Building(mongodb, item)
        building.load()
        bldg_code = building.item["bldg_code"]
        logger.debug("Reading building %s data", bldg_code)
        out_item = {}
        shp_item = {}
        for dato in quali_dati:
            if dato["field"].split("_", 1)[0] in ["d", "pk"]:
                if "PK_INFO" in building.item:
                    for subitem in building.item["PK_INFO"]:
                        full_field_name = "{}-{}".format(dato["field"], subitem['alignment_code'])
                        headers.add(full_field_name)
                        out_item[full_field_name] = subitem[dato["field"]]
                        full_shp_field_name = "{}-{}".format(dato["shp_field"], subitem['alignment_code'])
                        shp_item[full_shp_field_name] = subitem[dato["field"]]
                        shp_headers[full_shp_field_name] = dato["field_type"]
            else:
                if dato["field"] in item:
                    if isinstance(item[dato["field"]], dict):
                        # leggo ogni elemento
                        for subkey, value in item[dato["field"]].iteritems():
                            full_field_name = "{}_{}".format(dato["field"], subkey)
                            full_shp_field_name = "{}{}".format(dato["shp_field"], subkey)
                            headers.add(full_field_name)
                            if dato["field_type"] in ["string", "text"]:
                                out_item[full_field_name] = value
                                shp_item[full_shp_field_name] = value
                            else:
                                out_item[full_field_name] = value*float(dato["multiplier"])
                                shp_item[full_shp_field_name] = out_item[full_field_name]
                            shp_headers[full_shp_field_name] = dato["field_type"]
                    else:
                        headers.add(dato["field"])
                        if dato["field_type"] in ["string", "text"]:
                            out_item[dato["field"]] = item[dato["field"]]
                            shp_item[dato["shp_field"]] = out_item[dato["field"]]
                        else:
                            out_item[dato["field"]] = item[dato["field"]]*float(dato["multiplier"])
                            shp_item[dato["shp_field"]] = out_item[dato["field"]]
                        shp_headers[dato["shp_field"]] = dato["field_type"]
        csv_data.append(out_item)
        shp_data.append(shp_item)
    return list(headers), csv_data, shp_headers, shp_data

def update_bldg_shp(shp_path, shp_headers, shp_dicts, logger):
    '''
    aggiorna gli attributi di uno shapefile partendo da una lista di dizionari (dati),
    una lista di headers e un dizionario
    '''
    #epsg = project.item.get("epsg", 3004)
    layer = None
    bldg_feature = None
    shape_data = None
    shape_data = helpers.open_shapefile(shp_path, logger)
    if not shape_data:
        return
    layer = helpers.append_fields_to_shapefile(shape_data, shp_headers, logger)
    if not layer:
        return
    for building in shp_dicts:
        bldg_feature = helpers.find_first_feature(layer, "bldg_code", building["bldg_code"])
        if not bldg_feature:
            logger.warning("No feature with bldg_code %s found", building["bldg_code"])
        else:
            for key, value in building.iteritems():
                #logger.debug("Trying to set field %s of building %s to value %0.10f",
                #             dato["shp_field"][:10], bldg_code, field_value)
                bldg_feature.SetField(key[:10], value)
            layer.SetFeature(bldg_feature)
    shape_data.Destroy()
    logger.info("Buildings data Exported")

#                else:
#            if "WKT" in building.item:
#                bldg_feature = helpers.create_feature_from_wkt(layer, building.item["WKT"])
#            else:
#                logger.warning("Feature with bldg_code %s not created, missing WKT definition",
#                               bldg_code)
#    else:
#        wktcurr = Building.find(mongodb,
#                                {"$and": [{"project_id": project._id},
#                                          {"WKT": {"$exists": True}},
#                                          {"PK_INFO":{"$exists": True}}]})
#        if wktcurr.count() > 0:
#            # Problema: Anaconda non riesce a trovare i file di GDAL per
#            shape_data, layer = helpers.create_shapefile(shp_path, "Buildings",
#                                                         epsg, logger)


def main(argv):
    '''
    funzione principale
    '''
    project_code = None
    csv_name = None
    shapefile_name = None
    fields_name = None
    authenticate = False
    syntax = "Usage: " + os.path.basename(__file__) + " -c <project code> -o <output csv name> -f"\
             " <field settings name> [-s <shapefile name> -a for autentication -h for help]"
    try:
        opts, _ = getopt.getopt(argv, "hac:o:s:f:", ["code=", "output=", "shapefile=", "fields="])
    except getopt.GetoptError:
        print syntax
        sys.exit(1)
    if len(opts) < 4:
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
        elif opt in ("-o", "--output"):
            csv_name = arg
        elif opt in ("-s", "--shapefile"):
            shapefile_name = arg
        elif opt in ("-f", "--fields"):
            fields_name = arg
    export_buildings_data(project_code, authenticate, csv_name, shapefile_name, fields_name)


if __name__ == "__main__":
    main(sys.argv[1:])
