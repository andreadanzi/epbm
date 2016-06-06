# -*- coding: utf-8 -*-
import csv
import datetime
import os
from math import atan2, degrees, cos, sin
from shapely.geometry import asShape, mapping
from shapely.ops import transform

from helpers import transform_to_wgs
from base import BaseSmtModel
#from alignment import Alignment
from utils import toFloat


class Domain(BaseSmtModel):
    def _init_utils(self, **kwargs):
        self.logger.debug('created an instance of %s', self.__class__.__name__)


    def delete_referencing(self):
        a_collection = self.db["Alignment"]
        a_collection.remove({"domain_id":self._id})


    def delete(self):
        super(Domain, self).delete()
        self.delete_referencing()


    def import_alignment_set(self, csv_file_path):
        if not os.path.exists(csv_file_path):
            self.logger.warning('il file %s non esiste', csv_file_path)
            return
        with open(csv_file_path, 'rb') as csvfile:
            rows = []
            align_reader = csv.DictReader(csvfile, delimiter=';')
            for row in align_reader:
                # danzi.tn@20160408 i codici sono sempre UPPERCASE
                if row["domain_code"].upper() == self.item["code"]:
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


#    def import_alignment(self, csv_file_path):
#        with open(csv_file_path, 'rb') as csvfile:
#            rows = []
#            align_reader = csv.DictReader(csvfile, delimiter=';')
#            align_list = list(align_reader)
#            self.logger.debug('import_alignment - starting reading %d rows from %s',
#                              len(align_list), csv_file_path)
#            for row in align_list:
#                row["domain_id"] = self._id
#                for key, value in row.iteritems():
#                    row[key] = toFloat(value)
#                row["PH"] = {
#                    "type": "Point",
#                    "coordinates": [toFloat(row["x"]), toFloat(row["y"]), toFloat(row["z"])]
#                    }
#                row["created"] = datetime.datetime.utcnow()
#                row["updated"] = datetime.datetime.utcnow()
#                rows.append(row)
#            self.delete_referencing()
#            a_collection = self.db["Alignment"]
#            a_collection.insert(rows)


#    def import_strata(self, csv_file_path):
#        with open(csv_file_path, 'rb') as csvfile:
#            strata_reader = csv.DictReader(csvfile, delimiter=';')
#            pk = -1.0
#            a_collection = self.db["Alignment"]
#            ac = None
#            strata_list = list(strata_reader)
#            self.logger.debug('import_strata - starting reading %d rows from %s',
#                              len(strata_list), csv_file_path)
#            for row in strata_list:
#                cur_pk = float(row["PK"])
#                if cur_pk == pk:
#                    # still on the same pk
#                    pass
#                else:
#                    # new pk
#                    if ac:
#                        ac["updated"] = datetime.datetime.utcnow()
#                        align = Alignment(self.db, ac)
#                        align.save()
#                        ac = None
#                    pk = cur_pk
#                    ac = a_collection.find_one({"PK":pk, "domain_id":self._id})
#                if row["Descrizione"] == "DEM":
#                    ac["DEM"] = {
#                        "type": "Point",
#                        "coordinates": [toFloat(row["x"]), toFloat(row["y"]), toFloat(row["top"])]
#                        }
#                else:
#                    geoparameters = self.item["REFERENCE_STRATA"][row["Descrizione"].upper()]
#                    this_strata = {
#                        "CODE": row["Descrizione"].upper(),
#                        "PARAMETERS":geoparameters,
#                        "POINTS": {
#                            "top": {
#                                "type": "Point",
#                                "coordinates": [
#                                    toFloat(row["x"]),
#                                    toFloat(row["y"]),
#                                    toFloat(row["top"])
#                                    ]
#                                },
#                            "base": {
#                                "type": "Point",
#                                "coordinates": [
#                                    toFloat(row["x"]),
#                                    toFloat(row["y"]),
#                                    toFloat(row["base"])
#                                    ]
#                                }
#                            }
#                        }
#                    if "STRATA" in ac:
#                        ac["STRATA"].append(this_strata)
#                    else:
#                        ac["STRATA"] = [this_strata]
#            if ac:
#                ac["updated"] = datetime.datetime.utcnow()
#                align = Alignment(self.db, ac)
#                align.save()


#    def import_falda(self, csv_file_path):
#        with open(csv_file_path, 'rb') as csvfile:
#            falda_reader = csv.DictReader(csvfile, delimiter=';')
#            pk = -1.0
#            a_collection = self.db["Alignment"]
#            ac = None
#            falda_list = list(falda_reader)
#            self.logger.debug('import_falda - starting reading %d rows from %s',
#                              len(falda_list), csv_file_path)
#            for row in falda_list:
#                pk = float(row["PK"])
#                ac = a_collection.find_one({"PK":pk, "domain_id":self._id})
#                if ac:
#                    ac["FALDA"] = {
#                        "type": "Point",
#                        "coordinates": [
#                            toFloat(row["x"]),
#                            toFloat(row["y"]),
#                            toFloat(row["z"])]}
#                    align = Alignment(self.db, ac)
#                    align.save()
#                    self.logger.debug('import_falda - FALDA saved for pk=%f and domain %s',
#                                      pk, self._id)
#                else:
#                    self.logger.debug('import_falda - nothing found for pk=%f and domain %s',
#                                      pk, self._id)
#
#
#    def import_sezioni(self, csv_file_path):
#        with open(csv_file_path, 'rb') as csvfile:
#            sezioni_reader = csv.DictReader(csvfile, delimiter=';')
#            pk = -1.0
#            a_collection = self.db["Alignment"]
#            ac = None
#            sezioni_list = list(sezioni_reader)
#            self.logger.debug('import_sezioni - starting reading %d rows from %s',
#                              len(sezioni_list), csv_file_path)
#            for row in sezioni_list:
#                pk = float(row["PK"])
#                ac = a_collection.find_one({"PK":pk, "domain_id":self._id})
#                if ac:
#                    ac["SECTIONS"] = {
#                        "Excavation":{"Radius":toFloat(row["Excavation Radius"])},
#                        "Lining":{
#                            "Internal_Radius":toFloat(row["Lining Internal Radius"]),
#                            "Thickness":toFloat(row["Lining Thickness"]),
#                            "Offset":toFloat(row["Lining Offset"])}}
#                    align = Alignment(self.db, ac)
#                    align.save()
#
#
#    #tbm_progetto.csv
#    def import_tbm(self, csv_file_path):
#        with open(csv_file_path, 'rb') as csvfile:
#            tbm_reader = csv.DictReader(csvfile, delimiter=';')
#            pk = -1.0
#            a_collection = self.db["Alignment"]
#            ac = None
#            tbm_list = list(tbm_reader)
#            self.logger.debug('import_tbm - starting reading %d rows from %s',
#                              len(tbm_list), csv_file_path)
#            for row in tbm_list:
#                pk = float(row["PK"])
#                ac = a_collection.find_one({"PK":pk, "domain_id":self._id})
#                if ac:
#                    ac["TBM"] = {
#                        "excav_diameter":toFloat(row["excav_diameter"]),
#                        "bead_thickness":toFloat(row["bead_thickness"]),
#                        "taper":toFloat(row["taper"]),
#                        "tail_skin_thickness":toFloat(row["tail_skin_thickness"]),
#                        "delta":toFloat(row["delta"]),
#                        "gamma_muck":toFloat(row["gamma_muck"]),
#                        "shield_length":toFloat(row["shield_length"])}
#                    align = Alignment(self.db, ac)
#                    align.save()


    def import_reference_strata(self, csv_file_path):
        if not os.path.exists(csv_file_path):
            self.logger.warning('il file %s non esiste', csv_file_path)
            return
        with open(csv_file_path, 'rb') as csvfile:
            reference_strata_reader = csv.DictReader(csvfile, delimiter=';')
            reference_strata_list = list(reference_strata_reader)
            geocodes = {}
            self.logger.debug('import_reference_strata - starting reading %d rows from %s',
                              len(reference_strata_list), csv_file_path)
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

    # aghensi@20160503 - aggiunti subdomains da utilizzare per filtro punti e rototraslazione
    def import_subdomains(self, csv_file_path, epsg):
        '''
        importa i sottodomini da file CSV e memorizza le matrici di trasformazione da e per M3E
        i vertici del sottodominio sono salvati in "boundaries" e pronti per essere utilizzati
        con la query campo: {$geoWithin: {$polygon: boundaries}}
        '''
        if not os.path.exists(csv_file_path):
            self.logger.warning('il file %s non esiste', csv_file_path)
            return
        with open(csv_file_path, 'rb') as csvfile:
            subdomain_reader = csv.DictReader(csvfile, delimiter=';')
            subdomain_list = list(subdomain_reader)
            subdomains = []
            self.logger.debug('import_subdomains - starting reading %d rows from %s',
                              len(subdomain_list), csv_file_path)
            transf = transform_to_wgs(epsg)
            for row in subdomain_list:
                x_1 = toFloat(row["x1"])
                y_1 = toFloat(row["y1"])
                x_2 = toFloat(row["x2"])
                y_2 = toFloat(row["y2"])
                tetha = degrees(atan2(y_2 - y_1, x_2 - x_1))
                cos_t = cos(tetha)
                sin_t = sin(tetha)
                trasl_rot_matrix = [cos_t, -sin_t, 0, x_1*cos_t-y_1*sin_t,
                                    sin_t, cos_t, 0, y_1*cos_t+x_1*sin_t,
                                    0, 0, 1, 0]
                rot_trasl_matrix = [-cos_t, sin_t, 0, -x_1,
                                    -sin_t, -cos_t, 0, -y_1,
                                    0, 0, 1, 0]
                boundary = {
                    "type": "Polygon",
                    "coordinates": [
                        [x_1, y_1],
                        [x_2, y_2],
                        [toFloat(row["x3"]), toFloat(row["y3"])],
                        [toFloat(row["x4"]), toFloat(row["y4"])],
                        [x_1, y_1]
                        ]
                    }
                subdomain = {
                    "code": row["code"],
                    "boundaries": boundary,
                    # uso shapely e proj per salvare coordinate WGS
                    "bound_wgs": mapping(transform(transf, asShape(boundary))),
                    "domain_id": self._id,
                    "project_id": self.item["project_id"],
                    "export_matrix": trasl_rot_matrix,
                    "import_matrix": rot_trasl_matrix
                    }
                # memorizzo gli altri valori
                for key, value in row.iteritems():
                    if not key in ("code", "x1", "y1", "x2", "y2", "x3", "y3", "x4", "y4"):
                        subdomain[key] = toFloat(value)
                subdomains.append(subdomain)
            if len(subdomains) > 0:
                collection = self.db["Subdomain"]
                #collection.remove({"domain_id":self._id})
                collection.insert(subdomains)


    def doit(self, parm):
        pass



