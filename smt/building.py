# -*- coding: utf-8 -*-
import logging
import csv, sys, os
import datetime
from base import BaseSmtModel
from utils import toFloat
# danzi.tn@20160312 import delle PK di riferimento sui building
# nota che gli edifici possono dividersi su più PK anche diverse, così come le distanze min e max dipendono da quali PK vengono intercettate
# per questo vengono salvate le informazioni come array in PK_INFO , mentre in pk_min, pk_max, d_min e d_max che stanno sull'elemento dradice vengono inseriti i valori assoluti più bassi e più alti
class Building(BaseSmtModel):
    def _init_utils(self,**kwargs):
        self.logger.debug('created an instance of %s' % self.__class__.__name__)

# assign_building_class
    def assign_class(self):
        retVal="XXX"
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
        self.save()
        return retVal

    
    def doit (self,parm):
        pass


    @classmethod
    def import_building_pks(cls,db, txtFilePath):
        logger = logging.getLogger('smt_main.import_building_pks')
        with open(txtFilePath) as f:
            content = f.readlines()
            #db.Alignment.insert(rows)
            #collection = db[cls.__name__]
            with open("%s.out.csv" % txtFilePath, 'wb') as out_csvfile:
                writer = csv.writer(out_csvfile,delimiter=";")
                header = ["BLDG_CODE","PK_MIN","PK_MAX","D_MIN","D_MAX"]
                writer.writerow(header)
                b_num = 0
                for i, line in enumerate(content[1:]):
                    splitted = line.split(";")
                    s_index = splitted[0]
                    if s_index != "WTK":
                        #Il nuovo CSV ha una sola riga per elemento, processo direttamente
                        building_code = splitted[1]
                        pk_min = toFloat(splitted[-4])                     
                        pk_max = toFloat(splitted[-3])
                        d_min = toFloat(splitted[-2])
                        d_max = toFloat(splitted[-1].strip())
                        #serve il proparray?
                        prop_array=[{"shape_id":0,"pk_min":pk_min,"pk_max":pk_max,"d_min":d_min,"d_max":d_max}]
                        ccurr = db.Building.find({ "bldg_code": building_code})
                        if ccurr.count == 0:
                            logger.error( "Building with bldg_code = %s not found!" % building_code)
                        for bItem in ccurr:
                            building = Building(db,bItem)
                            building.load()
                            if "PK_INFO" in building.item:
                                pk_array = building.item["PK_INFO"]["pk_array"]
                                # prop_array = prop_array.extend(pk_array)
                                building.item["PK_INFO"]["pk_array"] = pk_array + prop_array
                            else:
                                building.item["PK_INFO"] = {"pk_array": prop_array}
                                building.item["pk_min"] = pk_min
                                building.item["pk_max"] = pk_max
                                building.item["d_min"] = d_min
                                building.item["d_max"] = d_max
                                building.item["updated"] = datetime.datetime.utcnow()
                            building.save()
                            b_num = b_num+1
                        # inizializzo l'array
                        row=[building_code,pk_min,pk_max,d_min,d_max]
                        writer.writerow(row)
                logger.info( "%d Buildings found" % b_num)
             
 
