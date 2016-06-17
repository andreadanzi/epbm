# -*- coding: utf-8 -*-
'''classe dell'alignment set (tracciato)'''
import os
import csv
import datetime
from shapely.geometry import asShape, mapping
from shapely.ops import transform
from minimongo import Index
from base import BaseSmtModel
from alignment import Alignment
from utils import toFloat
from building import Building
from helpers import transform_to_wgs

class AlignmentSet(BaseSmtModel):
    '''classe dell'alignment set (tracciato)'''
    class Meta(object):
        '''impostazioni minimongo'''
        database = 'smt'
        indices = (Index('code'))


    def delete_referencing(self, alignments=False, buildings=False):
        '''
        cancella gli alignments appartenenti a questo alignment set
            e le informazioni relative nei buildings

        Args:
            * alignments (bool): cancella tutti gli alignments dell'alignment set
            * buildings (bool): cancella le info relative all'alignment set nei buildings
        '''
        if alignments:
            Alignment.collection.remove({"alignment_set_id":self._id})
        # aghensi@20160407 eliminazione della PK_INFO relativa a quell'allineamento
        if buildings:
            for bldg in Building.collection.find({"alignment_set_id":self._id}):
                bldg.pk_info[:] = [x for x in bldg.pk_info if x.alignment_set_id != self._id]
                bldg.save()


    def delete(self):
        '''cancella l'alignment set e tutti i riferimenti'''
        super(AlignmentSet, self).delete()
        self.delete_referencing(True, True)


    def import_alignment(self, csv_file_path, epsg):
        '''importa gli alignments da file CSV)'''
        with open(csv_file_path, 'rb') as csvfile:
            rows = []
            align_reader = csv.DictReader(csvfile, delimiter=';')
            self.logger.debug('import_alignment - starting reading %d rows from %s',
                              len(list(align_reader)), csv_file_path)
            transf = transform_to_wgs(epsg)
            for row in align_reader:
                doc = {}
                doc["alignment_set_id"] = self._id
                doc["alignment_set_code"] = self.code
                for key, value in row.iteritems():
                    doc[key.lower()] = toFloat(value)
                doc["ph"] = {"type": "Point", "coordinates": [(row["x"]), (row["y"]), (row["z"])]}
                # aghensi@20160503 creato campo coordinate WGS84 per l'indice spaziale
                doc["ph_wgs"] = mapping(transform(transf, asShape(row["ph"])))
                doc["created"] = datetime.datetime.utcnow()
                doc["updated"] = datetime.datetime.utcnow()
                rows.append(doc)
            Alignment.collection.insert(rows)


    def import_strata(self, csv_file_path):
        '''importa la stratigrafia da file csv'''
        with open(csv_file_path, 'rb') as csvfile:
            strata_reader = csv.DictReader(csvfile, delimiter=';')
            pk = -1.0
            align = None
            strata_list = list(strata_reader)
            self.logger.debug('import_strata - starting reading %d rows from %s',
                              len(strata_list), csv_file_path)
            for row in strata_list:
                cur_pk = float(row["PK"])
                if cur_pk == pk:
                    # still on the same pk
                    pass
                else:
                    # new pk
                    if align:
                        align.updated = datetime.datetime.utcnow()
                        align.save()
                        align = None
                    pk = cur_pk
                    align = Alignment.collection.find_one({"pk":pk, "alignment_set_id":self._id})
                if align:
                    if row["Descrizione"] == "DEM":
                        align.dem = {
                            "type": "Point",
                            "coordinates": [
                                toFloat(row["x"]),
                                toFloat(row["y"]),
                                toFloat(row["top"])
                                ]
                            }
                    else:
                        code = row["Descrizione"].upper()
                        geoparameters = self.reference_strata[code]
                        doc = {
                            "code":code,
                            "parameters":geoparameters,
                            "points":{
                                "top":{
                                    "type":"Point",
                                    "coordinates":[
                                        toFloat(row["x"]),
                                        toFloat(row["y"]),
                                        toFloat(row["top"])
                                        ]
                                    },
                                "base": {
                                    "type":"Point",
                                    "coordinates":[
                                        toFloat(row["x"]),
                                        toFloat(row["y"]),
                                        toFloat(row["base"])
                                        ]
                                    }
                                }
                            }
                        if hasattr(align, "strata"):
                            align.strata.append(doc)
                        else:
                            align.strata = [doc]
            if align:
                align.updated = datetime.datetime.utcnow()
                align.save()


    def import_falda(self, csv_file_path):
        '''importa le informazioni della falda da file CSV'''
        with open(csv_file_path, 'rb') as csvfile:
            falda_list = list(csv.DictReader(csvfile, delimiter=';'))
            pk = -1.0
            align = None
            self.logger.debug('import_falda - starting reading %d rows from %s',
                              len(falda_list), csv_file_path)
            for row in falda_list:
                pk = float(row["PK"])
                align = Alignment.collection.find_one({"pk":pk, "alignment_set_id":self._id})
                if align:
                    align.falda = {"type":"Point", "coordinates":[toFloat(row["x"]),
                                                                  toFloat(row["y"]),
                                                                  toFloat(row["z"])]}
                    align.save()
                    self.logger.debug('import_falda - FALDA saved for pk=%f and alignment_set %s',
                                      pk, self._id)
                else:
                    self.logger.debug('import_falda - nothing found for pk=%f and alignment_set %s',
                                      pk, self._id)


    def import_sezioni(self, csv_file_path):
        '''importa le informazioni sulle sezioni di scavo da file CSV'''
        with open(csv_file_path, 'rb') as csvfile:
            sezioni_list = list(csv.DictReader(csvfile, delimiter=';'))
            pk = -1.0
            align = None
            self.logger.debug('import_sezioni - starting reading %d rows from %s',
                              len(sezioni_list), csv_file_path)
            for row in sezioni_list:
                pk = float(row["PK"])
                align = Alignment.collection.find_one({"pk":pk, "alignment_set_id":self._id})
                if align:
                    align.sections = {
                        "excavation":{"radius": toFloat(row["Excavation Radius"])},
                        "lining":{"internal_radius": toFloat(row["Lining Internal Radius"]),
                                  "thickness": toFloat(row["Lining Thickness"]),
                                  "offset": toFloat(row["Lining Offset"])}
                        }
                    align.save()


    #tbm_progetto.csv
    def import_tbm(self, csv_file_path):
        '''importa i dati delle TBM da file CSV'''
        with open(csv_file_path, 'rb') as csvfile:
            tbm_list = list(csv.DictReader(csvfile, delimiter=';'))
            pk = -1.0
            align = None
            self.logger.debug('import_tbm - starting reading %d rows from %s',
                              len(tbm_list), csv_file_path)
            for row in tbm_list:
                pk = float(row["PK"])
                align = Alignment.collection.find_one({"pk":pk, "alignment_set_id":self._id})
                if align:
                    align.tbm = {
                        "excav_diameter": toFloat(row["excav_diameter"]),
                        "bead_thickness": toFloat(row["bead_thickness"]),
                        "taper": toFloat(row["taper"]),
                        "tail_skin_thickness": toFloat(row["tail_skin_thickness"]),
                        "delta": toFloat(row["delta"]),
                        "gamma_muck": toFloat(row["gamma_muck"]),
                        "shield_length": toFloat(row["shield_length"]),
                        "pressure_max": toFloat(row["pressure_max"])
                        }
                    align.save()


    def import_reference_strata(self, csv_file_path):
        '''importa i reference_strata da file CSV'''
        if not os.path.exists(csv_file_path):
            self.logger.warning('il file %s non esiste', csv_file_path)
            return
        with open(csv_file_path, 'rb') as csvfile:
            reference_strata_list = list(csv.DictReader(csvfile, delimiter=';'))
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
                        items[key.lower()] = toFloat(value)
                geocodes[code.upper()] = items
            self.reference_strata = geocodes
            self.save()


    def import_building_pks(self, csv_file_path):
        '''importa le informazioni sui pk degli edifici'''
        if not os.path.exists(csv_file_path):
            self.logger.warning('%s non trovato', csv_file_path)
            return
        with open(csv_file_path, 'rb') as csv_file:
            csv_reader = csv.DictReader(csv_file, delimiter=';')
            b_num = 0
            for row in csv_reader:
                building_code = row["code"]
                pk_min = toFloat(row["pk_min"])
                pk_max = toFloat(row["pk_max"])
                d_min = toFloat(row["d_min"])
                d_max = toFloat(row["d_max"])
                prop = {"alignment_set_id": self._id, "alignment_code": self.code,
                        "pk_min": pk_min, "pk_max": pk_max, "d_min": d_min, "d_max": d_max}
                bldgs = Building.collection.find({"bldg_code": building_code})
                if bldgs.count == 0:
                    self.logger.error("Building with bldg_code = %s not found!", building_code)
                for bldg in bldgs:
                    self.logger.debug("Buliding %s found", building_code)
                    # aghensi@20160406 tolto livello pk_array da PK_INFO e valori fuori da PK_INFO
                    if hasattr(bldg, "pk_info"):
                        # TODO: se nell'array c'è già informazione su quell'allignment set?
                        bldg.pkinfo.append(prop)
                    else:
                        bldg.pkinfo = [prop]
                    # aghensi@20160407 memorizzo geometria impronta edificio in formato WKT in db
                    # TODO: trasformo WKT in GeoJSON per indicizzazione? (shapely)
                    if "WKT" in row:
                        bldg.wkt = row["WKT"]
                    bldg.updated = datetime.datetime.utcnow()
                    bldg.save()
                    b_num = b_num + 1
            self.logger.info("%d Buildings found", b_num)


    def doit(self, parm):
        pass
