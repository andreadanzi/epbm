'''
helpers.py
modulo funzioni riutilizzabili
'''
import os
import logging
import logging.handlers
import ConfigParser
import csv
import osgeo.ogr as ogr
from pymongo import MongoClient

# COMMON FUNCTIONS

def get_project_basedir(project_code):
    '''
    returns the path of the Project data base dir
    '''
    return os.path.join(os.path.dirname(__file__), "..", "data", project_code)

def init_logger(logger_name, file_path, log_level):
    '''
    creates main logger and a rotating file handler
    '''
    logger = logging.getLogger(logger_name)
    if not len(logger.handlers):
        logger.setLevel(log_level)
        file_handler = logging.handlers.RotatingFileHandler(file_path, maxBytes=5000000,
                                                            backupCount=5)
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.handler_set = True
    return logger

def init_db(smt_config, authenticate):
    '''
    connects to mongoDB
    '''
    client = MongoClient()
    mongodb = client[smt_config.get('MONGODB', 'database')]
    # DB authentication if required
    if authenticate:
        logged_in = mongodb.authenticate(smt_config.get('MONGODB', 'username'),
                                         smt_config.get('MONGODB', 'password'),
                                         source=smt_config.get('MONGODB', 'source_database'))
    else:
        logged_in = True
    return logged_in, mongodb

def get_config(cfg_name):
    '''
    reads the config file cfg_name and returns a config parser object
    '''
    smt_config = ConfigParser.RawConfigParser()
    smt_config.read(cfg_name)
    return smt_config

# CSV FUNCTIONS
def get_csv_dict_list(path):
    '''
    reads a csv file and returns a list of dictionaries using the first row as keys
    '''
    with open(path, 'rb') as csv_file:
        return list(csv.DictReader(csv_file, delimiter=';'))

# SHAPEFILE FUNCTIONS

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
