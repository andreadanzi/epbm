# -*- coding: utf-8 -*-
import logging
import csv
from base import BaseSmtModel
from alignment import Alignment
from utils import toFloat

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
            for row in align_reader:
                row["domain_id"] = self._id
                for key, value in row.iteritems():
                    row[key] = toFloat(value)
                row["PH"] = { "type": "Point", "coordinates": [toFloat(row["x"]), toFloat(row["y"]), toFloat(row["z"])] }
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
            for row in strata_reader:
                cur_pk = float(row["PK"])
                if cur_pk == pk:
                    # still on the same pk
                    pass
                else:
                    # new pk
                    if ac:
                        align = Alignment(self.db,ac)
                        align.save()
                        ac = None
                    pk = cur_pk
                    ac = a_collection.find_one({"PK":pk, "domain_id":self._id})
                if row["Descrizione"] == "DEM":
                    ac["DEM"] = { "type": "Point", "coordinates": [toFloat(row["x"]), toFloat(row["y"]), toFloat(row["top"])] }
                else:
                    if "Strata" in ac:
                        ac["Strata"].append( { row["Descrizione"] : {"top":{ "type": "Point", "coordinates": [toFloat(row["x"]), toFloat(row["y"]), toFloat(row["top"])] },"base": { "type": "Point", "coordinates": [toFloat(row["x"]), toFloat(row["y"]), toFloat(row["base"])] }}} )
                    else:
                        ac["Strata"] = [ {row["Descrizione"]: {"top":{ "type": "Point", "coordinates": [toFloat(row["x"]), toFloat(row["y"]), toFloat(row["top"])] },"base": { "type": "Point", "coordinates": [toFloat(row["x"]), toFloat(row["y"]), toFloat(row["base"])] }}}]

    def import_falda(self, csvFilePath):
        with open(csvFilePath, 'rb') as csvfile:
            rows = []
            falda_reader = csv.DictReader(csvfile, delimiter=';')
            pk = -1.0
            a_collection = self.db["Alignment"]
            ac = None
            for row in falda_reader:
                pk = float(row["PK"])                                    
                ac = a_collection.find_one({"PK":pk,"domain_id":self._id})
                if ac:
                    ac["Falda"] = { "type": "Point", "coordinates": [toFloat(row["x"]), toFloat(row["y"]), toFloat(row["z"])] }
                    align = Alignment(self.db,ac)
                    align.save()

    
    def doit (self,parm):
        pass


    