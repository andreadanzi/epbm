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
                rows.append(row)
            self.delete_referencing()
            a_collection = self.db["Alignment"]
            a_collection.insert(rows)
    
    """
    {
       "_id": ObjectId("56dab5992a13da217c4258d8"),
       "Descrizione": "Profilo Progetto",
       "domain_id": ObjectId("56dab5992a13da217c4254a1"),
       "x": 1653513.8,
       "y": 8176671.48,
       "PK": 2129998,
       "z": 69.1,
       "ID": "Profilo Progetto"
    }   
    
    STRATA
    ID	Descrizione	PK	x	y	top	base
    DEM	DEM	2121458	1660560,85	8178140,68	37,15	37,15
    R (3)	R	2121458	1660560,85	8178140,68	37,15	32,35
    Aa (14)	Aa	2121458	1660560,85	8178140,68	32,35	28,51
    CG	CG	2121458	1660560,85	8178140,68	28,51	25,81
    SS	SS	2121458	1660560,85	8178140,68	25,81	23,34
    FG	FG	2121458	1660560,85	8178140,68	23,34	17,76
    AP	AP	2121458	1660560,85	8178140,68	17,76	1,8
    MP (2)	MP	2121458	1660560,85	8178140,68	1,8	-3,68

    """
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
                    ac = a_collection.find_one({"PK":pk})
                if row["Descrizione"] == "DEM":
                    ac["DEM"] = { "type": "Point", "coordinates": [row["x"], row["y"], row["top"]] }
                else:
                    if "Strata" in ac:
                        ac["Strata"].append( { row["Descrizione"] : {"top":{ "type": "Point", "coordinates": [row["x"], row["y"], row["top"]] },"base": { "type": "Point", "coordinates": [row["x"], row["y"], row["base"]] }}} )
                    else:
                        ac["Strata"] = [ {row["Descrizione"]: {"top":{ "type": "Point", "coordinates": [row["x"], row["y"], row["top"]] },"base": { "type": "Point", "coordinates": [row["x"], row["y"], row["base"]] }}}]

    
    def doit (self,parm):
        pass


    