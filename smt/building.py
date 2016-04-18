# -*- coding: utf-8 -*-
'''
Classe Edificio
 danzi.tn@20160312 import delle PK di riferimento sui building
'''
#import logging
#import csv
#import datetime
from base import BaseSmtModel
#from utils import toFloat
# danzi.tn@20160418 pulizia sul Building dei dati di analisi => clear_analysis
class Building(BaseSmtModel):
    '''
    classe edificio
    '''
    def _init_utils(self, **kwargs):
        #self.logger.debug('created an instance of %s' % self.__class__.__name__)
        pass

# assign_building_class
    def assign_class(self):
        retVal = "XXX"
        typology = self.item["typology"]
        sensibility = self.item["sc_lev"]
        if typology == "building":
            ccurr = self.db.BuildingClass.find({"sc_lev":sensibility}).sort("dc_lev")
        elif typology == "overground_infrastructure":
            ccurr = self.db.OvergroundInfrastructureClass.find({"sc_lev":sensibility}).sort("dc_lev")
        elif typology == "underground_structure":
            ccurr = self.db.UndergroundStructureClass.find({"sc_lev":sensibility}).sort("dc_lev")
        elif typology == "underground_utility":
            ccurr = self.db.UndergroundUtilityClass.find({"sc_lev":sensibility}).sort("dc_lev")
        class_array = []
        for c in ccurr:
            class_array.append(c)
        self.item["DAMAGE_LIMITS"] = class_array
        #Gabriele@20160330 Vibration analysis
        # per il momento uso la sensibilita' generale dell'edificio
#        sensibility = self.item["sc_vbr_lev"]
#        ccurr = self.db.VibrationClass.find({"sc_lev":sensibility}).sort("dc_lev")
#        class_array = []
#        for c in ccurr:
#            class_array.append(c)
#        self.item["VIBRATION_LIMITS"] = class_array
        self.save()
        return retVal

    def clear_analysis(self, b_values_dtype_names):
        for key in b_values_dtype_names:
            if key in self.item:
                self.item[key] = {}
                self.logger.debug("_clear_buildings_data on %s->%s" % (self.item["bldg_code"], key))
        
        
    def doit(self, parm):
        pass

# aghensi@20160406 funzione spostata in alignment_set
#    @classmethod
#    def import_building_pks(cls, db, txtFilePath):
#        logger = logging.getLogger('smt_main.import_building_pks')
#        with open(txtFilePath, 'rb') as csv_file:
#            csv_reader = csv.DictReader(csv_file, delimiter=';')
#            b_num = 0
#            for row in csv_reader:
#                building_code = row["bldg_code"]
#                pk_min = toFloat(row["pk_min"])
#                pk_max = toFloat(row["pk_max"])
#                d_min = toFloat(row["d_min"])
#                d_max = toFloat(row["d_max"])
#                # TODO: serve ancora shape_id?
#                prop_array = [{"shape_id":0, "pk_min":pk_min, "pk_max":pk_max, "d_min":d_min,
#                               "d_max":d_max}]
#                ccurr = db.Building.find({"bldg_code": building_code})
#                if ccurr.count == 0:
#                    logger.error("Building with bldg_code = %s not found!", building_code)
#                for bItem in ccurr:
#                    logger.debug("Buliding %s found", building_code)
#                    building = Building(db, bItem)
#                    building.load()
#                    if "PK_INFO" in building.item:
#                        pk_array = building.item["PK_INFO"]["pk_array"]
#                        # prop_array = prop_array.extend(pk_array)
#                        building.item["PK_INFO"]["pk_array"] = pk_array + prop_array
#                    else:
#                        building.item["PK_INFO"] = {"pk_array": prop_array}
#                        building.item["pk_min"] = pk_min
#                        building.item["pk_max"] = pk_max
#                        building.item["d_min"] = d_min
#                        building.item["d_max"] = d_max
#                        building.item["updated"] = datetime.datetime.utcnow()
#                    building.save()
#                    b_num = b_num + 1
#            logger.info("%d Buildings found" % b_num)


