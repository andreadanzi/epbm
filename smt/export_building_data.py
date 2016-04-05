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
import csv

from building import Building
import helpers

PROJECT_CODE = "MDW029_S_E_05"
DATA_BASEDIR = helpers.get_project_basedir(PROJECT_CODE)
DEFAULT_SETTINGS_CSV_PATH = os.path.join(DATA_BASEDIR, "in", "buildings_fields.csv")
DEFAULT_OUTPUT_FILE_PATH = os.path.join(DATA_BASEDIR, "out", "buildings_data_export.csv")
DEFAULT_SHAPEFILE_PATH = os.path.join(DATA_BASEDIR, "gis", "Elementi_Analizzati.shp")


def export_buildings_data(authenticate, csv_path, shp_path, fields_path):
    '''
    funzione che fa il vero lavoro
    '''
    logger = helpers.init_logger('smt_main', 'export_building_data.log', logging.DEBUG)
    smt_config = helpers.get_config('smt.cfg')
    logged_in, mongodb = helpers.init_db(smt_config, authenticate)
    if logged_in:
        dati = helpers.get_csv_dict_list(fields_path)
        # TODO: controllo che le keys siano field, csv_field, shp_field e multiplier
        # EXPORT BUILDINGS CALCULATED DATA
        with open(csv_path, 'wb') as out_csvfile:
            writer = csv.writer(out_csvfile, delimiter=";")
            writer.writerow([x["csv_field"] for x in dati])
            bcurr = Building.find(mongodb, {"PK_INFO":{"$exists":True}})
            if bcurr.count == 0:
                logger.error("No Buildings found!")
            else:
                shape_data = helpers.open_shapefile(shp_path, logger)
                if shape_data:
                    layer = helpers.append_fields_to_shapefile(shape_data,
                                                               [x["shp_field"] for x in dati],
                                                               logger)
                for item in bcurr:
                    building = Building(mongodb, item)
                    building.load()
                    bldg_code = building.item["bldg_code"]
                    if shape_data and layer:
                        bldg_feature = helpers.find_first_feature(layer, "bldg_code", bldg_code)
                        if not bldg_feature:
                            logger.warn("No feature with bldg_code %s found", bldg_code)
                    logger.debug("Processing building %s", bldg_code)
                    row = []
                    for dato in dati:
                        if dato["field"] == "bldg_code":
                            field_value = building.item["bldg_code"]
                        elif dato["field"].split("_", 1)[0] in ["d", "pk"]:
                            field, align = dato["field"].split("-", 1)
                            pk_array = building.item["PK_INFO"]["pk_array"]
                            # TODO: aggiungere intelligenza quando ho più tracciati
#                           if align == "smi":
#                               field_value = next((l[field] for l in pk_array if l['pk_min'] > 2150000), None)
#                           else:
#                                field_value = next((l[field] for l in pk_array if l['pk_min'] < 2150000), None)
                            field_value = next((l[field] for l in pk_array), None)
                        else:
                            # logger.debug("processing attribute %s of building %s",
                            #              dato["field"], bldg_code)
                            field_value = building.item.get(dato["field"], 0)*float(dato["multiplier"])
                        row.append(str(field_value))
                        if shape_data and bldg_feature and field_value and dato["field"] != "bldg_code":
                            logger.debug("Trying to set field %s of building %s to value %0.10f",
                                         dato["shp_field"][:10], bldg_code, field_value)
                            bldg_feature.SetField(dato["shp_field"][:10], field_value)
                    writer.writerow(row)
                    if shape_data and layer and bldg_feature:
                        layer.SetFeature(bldg_feature)
                if shape_data:
                    shape_data.Destroy()
                logger.info("Buildings data Exported")

def main(argv):
    '''
    funzione principale
    '''
    path = DEFAULT_OUTPUT_FILE_PATH
    shapefile_path = DEFAULT_SHAPEFILE_PATH
    fields_path = DEFAULT_SETTINGS_CSV_PATH
    authenticate = False
    syntax = os.path.basename(__file__) + " -o <output path> -s <shapefile path> -f <field settings path> [-a for autentication -h for help]"
    try:
        opts, _ = getopt.getopt(argv, "haosf:", ["output=", "shapefile=", "fields="])
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
        elif opt == '-a':
            authenticate = True
        elif opt in ("-p", "--path"):
            path = arg
        elif opt in ("-s", "--shapefile"):
            shapefile_path = arg
        elif opt in ("-f", "--fields"):
            fields_path = arg
    if path:
        export_buildings_data(authenticate, path, shapefile_path, fields_path)


if __name__ == "__main__":
    main(sys.argv[1:])
