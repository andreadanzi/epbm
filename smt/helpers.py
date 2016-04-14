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
import osgeo.osr as osr
from pymongo import MongoClient

from utils import toFloat

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
        csv_reader = csv.DictReader(csv_file, delimiter=';')
        rows = []
        for row in csv_reader:
            for key, value in row.iteritems():
                # HACK: bldg_code deve restare stringa - oppure uso sempre toFloat?
                if key != "bldg_code":
                    row[key] = toFloat(value)
            rows.append(row)
        return rows


def write_dict_list_to_csv(csv_file, csv_columns, dict_data):
    '''
    writes a csv files starting from a dictionary list and a list of headers/columns names
    '''
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns, delimiter=";")
            writer.writeheader()
            for data in dict_data:
                writer.writerow(data)
    except IOError as (errno, strerror):
            print "I/O error({0}): {1}".format(errno, strerror)
    return

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

def create_shapefile(output_shp, layername, epsg, logger, fields_dict=None):
    '''
    crea uno shape con le informazioni degli edifici del progetto presenti nel database
    funziona solo per oggetti buildings che hanno la definizione della geometria
    salvata come parametro "WKT"
    '''
    driver = ogr.GetDriverByName("ESRI Shapefile")
    data_source = driver.CreateDataSource(output_shp)
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(epsg)
    layer = data_source.CreateLayer(layername, srs, ogr.wkbPolygon)
    if fields_dict:
        for field_name, field_type in fields_dict.iteritems():
            add_shp_field(layer, field_name, field_type, logger)
    return data_source, layer

def append_fields_to_shapefile(shape_data, shp_headers, logger):
    '''
    adds new fields of type real to a shapefile datasource from a string list
    '''
    layer = shape_data.GetLayer() #get possible layers.
    layer_defn = layer.GetLayerDefn()
    shp_fields = [layer_defn.GetFieldDefn(i).GetName() for i in range(layer_defn.GetFieldCount())]
    # se non esistono creo i campi
    for field_name, field_type in shp_headers.iteritems():
        if field_name[:10] not in shp_fields:
            add_shp_field(layer, field_name[:10], field_type, logger)
    return layer

def add_shp_field(layer, field_name, field_type, logger):
    '''
    aggiunge il campo del tipo appropriato al layer di un shapefile
    '''
    if field_type in ["string", "text"]:
        cur_field = ogr.FieldDefn(field_name, ogr.OFTString)
        cur_field.SetWidth(254)
        layer.CreateField(cur_field)
    elif field_type in ["float", "real", "decimal"]:
        layer.CreateField(ogr.FieldDefn(field_name, ogr.OFTReal))
    elif field_type in ["int", "integer"]:
        layer.CreateField(ogr.FieldDefn(field_name, ogr.OFTInteger))
    logger.debug("field %s created", field_name)

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

def create_feature_from_wkt(layer, wkt):
    '''
    create a new feature starting from WKT string
    '''
    feature = ogr.Feature(layer.GetLayerDefn())
    shape = ogr.CreateGeometryFromWkt(wkt)
    feature.SetGeometry(shape)
    layer.CreateFeature(feature)
    return feature
