# -*- coding: utf-8 -*-
import logging
import csv, sys
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
        sensibility = self.item["sc_lev"]
        ccurr = self.db.BuildingClass.find({"sc_lev":sensibility}).sort("dc_lev")
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
            collection = db[cls.__name__]
            with open("%s.out.csv" % txtFilePath, 'wb') as out_csvfile:
                writer = csv.writer(out_csvfile,delimiter=";")
                header = ["SHAPEID","FID","CODE","PK_MIN","PK_MAX","D_MIN","D_MAX"]
                writer.writerow(header)
                building_code = None
                prop_array=[]
                b_num = 0
                pk_min = sys.float_info.max
                pk_max = 0.0
                d_min = sys.float_info.max
                d_max = sys.float_info.min
                for i, line in enumerate(content[1:]):
                    splitted = line.split(";")
                    # codice edificio
                    bldg_code = splitted[6]
                    # per la prima iterazione il codice edificio di riferimento deve essere assegnato
                    if i==0:
                        building_code = bldg_code
                    # se il codice edificio di riferimento è diverso dal codice corrente allora bisogna salvare le informazioni
                    if bldg_code != building_code:
                        ccurr = db.Building.find({ "bldg_code": building_code})
                        if ccurr.count == 0:
                            logger.error( "Building with bldg_code = %s not found!" % building_code)
                        for bItem in ccurr:
                            building = Building(db,bItem)
                            building.load()
                            building.item["PK_INFO"] = {"pk_min":pk_min,"pk_max":pk_max, "pk_array": prop_array}
                            building.item["pk_min"] = pk_min
                            building.item["pk_max"] = pk_max
                            building.item["d_min"] = d_min
                            building.item["d_max"] = d_max
                            building.item["updated"] = datetime.datetime.utcnow()
                            building.save()
                            b_num = b_num+1
                        # inizializzo l'array
                        prop_array=[]
                        # asssegno il codice corrente al codice di riferimento
                        building_code = bldg_code
                        pk_min = sys.float_info.max
                        pk_max = 0.0
                        d_min = sys.float_info.max
                        d_max = sys.float_info.min
                        # {"$and":[{"PK":{"$gte":pk_min}},{"PK":{"$lt":pk_max}}]}
                    info_dict = {"shape_id":toFloat(splitted[0]),"fid":toFloat(splitted[1]), "pk_min":toFloat(splitted[-4]),"pk_max":toFloat(splitted[-3]),"d_min":toFloat(splitted[-2]),"d_max":toFloat(splitted[-1].strip())}
                    if pk_min > info_dict["pk_min"]:
                        pk_min = info_dict["pk_min"]
                    if pk_max < info_dict["pk_max"]:
                        pk_max = info_dict["pk_max"]
                    if d_min > info_dict["d_min"]:
                        d_min = info_dict["d_min"]
                    if d_max < info_dict["d_max"]:
                        d_max = info_dict["d_max"]
                    prop_array.append(info_dict)
                    row=[splitted[0],splitted[1],splitted[6],splitted[-4],splitted[-3],splitted[-2],splitted[-1].strip()]
                    writer.writerow(row)
                logger.info( "%d Buildings found" % b_num)
