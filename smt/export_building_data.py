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
import ConfigParser
import csv
from pymongo import MongoClient
import osgeo.ogr as ogr

from building import Building

DEFAULT_OUTPUT_FILE_PATH = "../data/buildings_data_export.csv"
DEFAULT_SHAPEFILE_PATH = "../data/gis/Elementi_Analizzati.shp"

def init_logger(logger_name, file_path):
    '''
    creates main logger and a rotating file handler which logs even debug messages
    '''
    logger = logging.getLogger(logger_name)
    if not getattr(logger, 'handler_set', None):
        logger.setLevel(logging.DEBUG)
        file_handler = logging.handlers.RotatingFileHandler(file_path, maxBytes=5000000,
                                                            backupCount=5)
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.handler_set = True
    return logger

def get_config(cfg_name):
    '''
    reads the config file cfg_name and returns a config parser object
    '''
    smt_config = ConfigParser.RawConfigParser()
    smt_config.read(cfg_name)
    return smt_config

def open_shapefile(path, logger):
    '''
    opens a shapefile and returns the datasource
    '''
    if os.path.exists(path):
        driver = ogr.GetDriverByName("ESRI Shapefile")
        shape_data = driver.Open(path, 1)
        if shape_data is None:
            logger.error("Cannnot open shapefile %s", path)
            return None
        else:
            return shape_data

def append_fields_to_shapefile(shape_data, fields, logger):
    '''
    adds new fields of type real to a shapefile datasource from a string list
    '''
    layer = shape_data.GetLayer() #get possible layers.
    layer_defn = layer.GetLayerDefn()
    shp_fields = [layer_defn.GetFieldDefn(i).GetName() for i in range(layer_defn.GetFieldCount())]
    # se non esistono creo i campi
    for field_abbr in [field[:10] for field in fields]:
        if field_abbr not in shp_fields:
            layer.CreateField(ogr.FieldDefn(field_abbr, ogr.OFTReal))
            logger.debug("field %s created", field_abbr)
    return layer

def find_first_feature(layer, field, value):
    '''
    finds the first feature by field value
    '''
    searchstring = "%s = '%s'" % (field, value)
    layer.SetAttributeFilter(str(searchstring))
    if layer.GetFeatureCount() > 0:
        return layer.GetNextFeature()
    else:
        return None

def export_buildings_data(authenticate, csv_path, shp_path):
    '''
    funzione che fa il vero lavoro
    '''
    logger = init_logger('smt_main', 'export_building_data.log')
    smt_config = get_config('smt.cfg')
    # connect to MongoDB
    client = MongoClient()
    mongodb = client[smt_config.get('MONGODB', 'database')]
    # DB authentication if required
    if authenticate:
        logged_in = mongodb.authenticate(smt_config.get('MONGODB', 'username'),
                                         smt_config.get('MONGODB', 'password'),
                                         source=smt_config.get('MONGODB', 'source_database'))
    else:
        logged_in = True
    if logged_in:
       # EXPORT BUILDINGS CALCULATED DATA
        with open(csv_path, 'wb') as out_csvfile:
            writer = csv.writer(out_csvfile, delimiter=";")
            header = ["bldg_code", "vulnerability", "sc_lev", "damage_class",
                      "settlement_max", "tilt_max", "esp_h_max"]
            writer.writerow(header)
            bcurr = Building.find(mongodb, {"$or":[{"vulnerability":{"$exists":True}},
                                                   {"sc_lev":{"$exists":True}},
                                                   {"damage_class":{"$exists":True}},
                                                   {"settlement_max":{"$exists":True}},
                                                   {"tilt_max":{"$exists":True}},
                                                   {"esp_h_max":{"$exists":True}}]})
            if bcurr.count == 0:
                logger.error("No Buildings with useful data found!")
            else:
                shape_data = open_shapefile(shp_path, logger)
                if shape_data:
                    layer = append_fields_to_shapefile(shape_data, header[1:], logger)
                for item in bcurr:
                    building = Building(mongodb, item)
                    building.load()
                    bldg_code = building.item["bldg_code"]
                    if layer:
                        bldg_feature = find_first_feature(layer, "bldg_code", bldg_code)
                        if not bldg_feature:
                            logger.warn("No feature with bldg_code %s found", bldg_code)
                    logger.debug("Processing building %s", bldg_code)
                    row = []
                    for field in header:
                        field_value = building.item.get(field, None)
                        row.append(str(field_value))
                        if bldg_feature and field_value and field != "bldg_code":
                            logger.debug("Trying to set field %s of building %s to value %0.10f",
                                         field[:10], bldg_code, field_value)
                            bldg_feature.SetField(field[:10], field_value)
                    writer.writerow(row)
                    if layer and bldg_feature:
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
    authenticate = False
    syntax = os.path.basename(__file__) + \
              " -o <output path> -s <shapefile path> [-a for autentication -h for help]"
    try:
        opts, _ = getopt.getopt(argv, "haos:", ["output=", "shapefile="])
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
    if path:
        export_buildings_data(authenticate, path, shapefile_path)


if __name__ == "__main__":
    main(sys.argv[1:])
