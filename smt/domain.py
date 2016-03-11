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
    
    def import_alignment_set(self, csvFilePath):
        with open(csvFilePath, 'rb') as csvfile:
            rows = []
            align_reader = csv.DictReader(csvfile, delimiter=';')
            for row in align_reader:
                if row["domain_code"] == self.item["code"]:
                    for key, value in row.iteritems():
                        row[key] = toFloat(value)
                    row["created"] = datetime.datetime.utcnow()
                    row["updated"] = datetime.datetime.utcnow()
                    row["domain_id"] = self._id
                    rows.append(row)
            #db.Alignment.insert(rows)
            collection = self.db["AlignmentSet"]
            collection.remove({"domain_id":self._id})
            collection.insert(rows)
    
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
            if ac:
                ac["updated"] = datetime.datetime.utcnow()
                align = Alignment(self.db,ac)
                align.save()

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
                    align = Alignment(self.db,ac)
                    align.save()
                    self.logger.debug('import_falda - FALDA saved for pk=%f and domain %s' % (pk,self._id))
                else:
                    self.logger.debug('import_falda - nothing found for pk=%f and domain %s' % (pk,self._id))

    def import_sezioni(self, csvFilePath):
        with open(csvFilePath, 'rb') as csvfile:
            rows = []
            sezioni_reader = csv.DictReader(csvfile, delimiter=';')
            pk = -1.0
            a_collection = self.db["Alignment"]
            ac = None
            sezioni_list = list(sezioni_reader)
            self.logger.debug('import_sezioni - starting reading %d rows from %s' % (len(sezioni_list),csvFilePath))
            for row in sezioni_list:
                pk = float(row["PK"])                                    
                ac = a_collection.find_one({"PK":pk,"domain_id":self._id})
                if ac:
                    ac["SECTIONS"] = { "Excavation":{"Radius":toFloat(row["Excavation Radius"])}, "Lining":{"Internal_Radius":toFloat(row["Lining Internal Radius"]), "Thickness":toFloat(row["Lining Thickness"]), "Offset":toFloat(row["Lining Offset"])}}
                    align = Alignment(self.db,ac)
                    align.save()
    
    #tbm_progetto.csv
    def import_tbm(self, csvFilePath):
        with open(csvFilePath, 'rb') as csvfile:
            rows = []
            tbm_reader = csv.DictReader(csvfile, delimiter=';')
            pk = -1.0
            a_collection = self.db["Alignment"]
            ac = None
            tbm_list = list(tbm_reader)
            self.logger.debug('import_tbm - starting reading %d rows from %s' % (len(tbm_list),csvFilePath))
            for row in tbm_list:
                pk = float(row["PK"])                                    
                ac = a_collection.find_one({"PK":pk,"domain_id":self._id})
                if ac:
                    #excav_diameter	bead_thickness	taper	tail_skin_thickness	delta	gamma_muck shield_length
                    ac["TBM"] = {"excav_diameter":toFloat(row["excav_diameter"]),"bead_thickness":toFloat(row["bead_thickness"]),"taper":toFloat(row["taper"]),"tail_skin_thickness":toFloat(row["tail_skin_thickness"]),"delta":toFloat(row["delta"]),"gamma_muck":toFloat(row["gamma_muck"]),"shield_length":toFloat(row["shield_length"])}
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


    
