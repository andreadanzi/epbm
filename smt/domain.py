# -*- coding: utf-8 -*-
import logging
import csv
from base import BaseSmtModel
from alignment import Alignment
from utils import toFloat
import datetime

class Domain(BaseSmtModel):
    def _init_utils(self,**kwargs):
        self.logger.debug('created an instance of %s' % self.__class__.__name__)
    
    def delete_referencing(self):
        a_collection = self.db["Alignment"]
        a_collection.remove({"domain_id":self._id})
    
    def delete(self):
        super(Domain,self).delete()
        self.delete_referencing()
        
    def import_alignment(self, csvFilePath):
        with open(csvFilePath, 'rb') as csvfile:
            rows = []
            align_reader = csv.DictReader(csvfile, delimiter=';')
            align_list = list(align_reader)
            self.logger.debug('import_alignment - starting reading %d rows from %s' % (len(align_list),csvFilePath))
            for row in align_list:
                row["domain_id"] = self._id
                for key, value in row.iteritems():
                    row[key] = toFloat(value)
                row["PH"] = { "type": "Point", "coordinates": [toFloat(row["x"]), toFloat(row["y"]), toFloat(row["z"])] }
                row["created"] = datetime.datetime.utcnow()
                row["updated"] = datetime.datetime.utcnow()
                rows.append(row)
            self.delete_referencing()
            a_collection = self.db["Alignment"]
            a_collection.insert(rows)
    
    
    def import_strata(self, csvFilePath):
        with open(csvFilePath, 'rb') as csvfile:
            rows = []
            strata_reader = csv.DictReader(csvfile, delimiter=';')
            pk = -1.0
            a_collection = self.db["Alignment"]
            ac = None
            strata_list = list(strata_reader)
            self.logger.debug('import_strata - starting reading %d rows from %s' % (len(strata_list),csvFilePath))
            for row in strata_list:
                cur_pk = float(row["PK"])
                if cur_pk == pk:
                    # still on the same pk
                    pass
                else:
                    # new pk
                    if ac:
                        ac["updated"] = datetime.datetime.utcnow()
                        align = Alignment(self.db,ac)
                        align.save()
                        ac = None
                    pk = cur_pk
                    ac = a_collection.find_one({"PK":pk, "domain_id":self._id})
                if row["Descrizione"] == "DEM":
                    ac["DEM"] = { "type": "Point", "coordinates": [toFloat(row["x"]), toFloat(row["y"]), toFloat(row["top"])] }
                else:
                    geoparameters = self.item["REFERENCE_STRATA"][row["Descrizione"].upper()]
                    if "STRATA" in ac:
                        ac["STRATA"].append( { "CODE": row["Descrizione"].upper(), "PARAMETERS": geoparameters ,"POINTS" : {"top":{ "type": "Point", "coordinates": [toFloat(row["x"]), toFloat(row["y"]), toFloat(row["top"])] },"base": { "type": "Point", "coordinates": [toFloat(row["x"]), toFloat(row["y"]), toFloat(row["base"])] }}} )
                    else:
                        ac["STRATA"] = [ {"CODE": row["Descrizione"].upper(), "PARAMETERS":geoparameters , "POINTS" : {"top":{ "type": "Point", "coordinates": [toFloat(row["x"]), toFloat(row["y"]), toFloat(row["top"])] },"base": { "type": "Point", "coordinates": [toFloat(row["x"]), toFloat(row["y"]), toFloat(row["base"])] }}}]

    def import_falda(self, csvFilePath):
        with open(csvFilePath, 'rb') as csvfile:
            rows = []
            falda_reader = csv.DictReader(csvfile, delimiter=';')
            pk = -1.0
            a_collection = self.db["Alignment"]
            ac = None
            falda_list = list(falda_reader)
            self.logger.debug('import_falda - starting reading %d rows from %s' % (len(falda_list),csvFilePath))
            for row in falda_list:
                pk = float(row["PK"])                                    
                ac = a_collection.find_one({"PK":pk,"domain_id":self._id})
                if ac:
                    ac["FALDA"] = { "type": "Point", "coordinates": [toFloat(row["x"]), toFloat(row["y"]), toFloat(row["z"])] }
                    ac["updated"] = datetime.datetime.utcnow()
                    align = Alignment(self.db,ac)
                    align.save()

    def import_reference_strata(self, csvFilePath):
        with open(csvFilePath, 'rb') as csvfile:
            rows = []
            reference_strata_reader = csv.DictReader(csvfile, delimiter=';')
            a_collection = self.db["Alignment"]
            ac = None
            reference_strata_list = list(reference_strata_reader)
            geocodes = {}
            self.logger.debug('import_reference_strata - starting reading %d rows from %s' % (len(reference_strata_list),csvFilePath))
            for row in reference_strata_list:
                items = {}
                code = "NULL"
                for key, value in row.iteritems():
                    if key == "code":
                        code = row["code"]
                    else:
                        items[key] = toFloat(value)
                geocodes[code.upper()] = items
            self.item["REFERENCE_STRATA"] = geocodes
            self.save()
                    
    def doit (self,parm):
        pass


    