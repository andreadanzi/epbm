'''alignment set - tracciato'''
import datetime
from shapely.geometry import asShape, mapping
from shapely.ops import transform

from base import BaseSmtModel
from alignment import Alignment
from utils import toFloat
from building import Building
from helpers import transform_to_wgs, get_csv_dict_list

class AlignmentSet(BaseSmtModel):
    '''classe dell'alignment set (tracciato)'''
    REQUIRED_CSV_FIELDS = ('code')
    def delete_referencing(self, alignments=False, buildings=False):
        '''
        cancella gli alignments appartenenti a questo alignment set
            e le informazioni relative nei buildings

        Args:
            * alignments (bool): cancella tutti gli alignments dell'alignment set
            * buildings (bool): cancella le info relative all'alignment set nei buildings
        '''
        if alignments:
            a_collection = self.db["Alignment"]
            a_collection.remove({"alignment_set_id":self._id})
        # aghensi@20160407 eliminazione della PK_INFO relativa a quell'allineamento
        if buildings:
            for bldg in self.db["Building"].find({"alignment_set_id":self._id}):
                building = Building(self.db, bldg)
                building.load()
                building.item["PK_INFO"][:] = [x for x
                                               in building.item["PK_INFO"]
                                               if x["alignment_set_id"] != self._id]
                building.save()


    def delete(self):
        '''cancella l'alignment set e tutti i riferimenti'''
        super(AlignmentSet, self).delete()
        self.delete_referencing(True, True)


    def import_alignment(self, csv_file_path, epsg):
        '''importa gli alignments da file CSV'''
        align_list = get_csv_dict_list(csv_file_path, self.logger, Alignment.REQUIRED_CSV_FIELDS)
        if align_list:
            transf = transform_to_wgs(epsg)
            for row in align_list:
                row["alignment_set_id"] = self._id
                row["alignment_set_code"] = self.item["code"]
                row["PH"] = {"type": "Point", "coordinates": [(row["x"]), (row["y"]), (row["z"])]}
                # aghensi@20160503 creato campo coordinate WGS84 per l'indice spaziale
                row["PH_wgs"] = mapping(transform(transf, asShape(row["PH"])))
                row["created"] = datetime.datetime.utcnow()
                row["updated"] = datetime.datetime.utcnow()
            self.delete_referencing(alignments=True)
            a_collection = self.db["Alignment"]
            a_collection.insert(align_list)
            a_collection.create_index([("PH_wgs", "2dsphere")])


    def import_strata(self, csv_file_path):
        '''importa la stratigrafia da file csv'''
        req_fields = ("PK", "x", "y", "top", "base", "code")
        strata_list = get_csv_dict_list(csv_file_path, self.logger, req_fields)
        if strata_list:
            pk = -1.0
            a_collection = self.db["Alignment"]
            ac = None
            for row in strata_list:
                cur_pk = float(row["PK"])
                if cur_pk == pk:
                    # still on the same pk
                    pass
                else:
                    # new pk
                    if ac:
                        ac["updated"] = datetime.datetime.utcnow()
                        align = Alignment(self.db, ac)
                        align.save()
                        ac = None
                    pk = cur_pk
                    ac = a_collection.find_one({"PK":pk, "alignment_set_id":self._id})
                if ac:
                    code = row["code"]
                    if code == "DEM":
                        ac["DEM"] = {
                            "type": "Point",
                            "coordinates": [
                                toFloat(row["x"]),
                                toFloat(row["y"]),
                                toFloat(row["top"])
                                ]
                            }
                    else:
                        geoparameters = self.item["REFERENCE_STRATA"][code]
                        doc = {
                            "CODE":code,
                            "PARAMETERS":geoparameters,
                            "POINTS":{
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
                        if "STRATA" in ac:
                            ac["STRATA"].append(doc)
                        else:
                            ac["STRATA"] = [doc]
            if ac:
                ac["updated"] = datetime.datetime.utcnow()
                align = Alignment(self.db, ac)
                align.save()


    def import_falda(self, csv_file_path):
        '''importa le informazioni della falda da file CSV'''
        req_fields = ("PK", "x", "y", "z")
        falda_list = get_csv_dict_list(csv_file_path, self.logger, req_fields)
        if falda_list:
            pk = -1.0
            a_collection = self.db["Alignment"]
            ac = None
            for row in falda_list:
                pk = float(row["PK"])
                ac = a_collection.find_one({"PK":pk, "alignment_set_id":self._id})
                if ac:
                    ac["FALDA"] = {"type":"Point", "coordinates":[toFloat(row["x"]),
                                                                  toFloat(row["y"]),
                                                                  toFloat(row["z"])]}
                    align = Alignment(self.db, ac)
                    align.save()
                    self.logger.debug('FALDA saved for pk=%f and alignment_set %s', pk, self._id)
                else:
                    self.logger.debug('nothing found for pk=%f and alignment_set %s', pk, self._id)


    def import_sections(self, csv_file_path):
        '''importa le informazioni sulle sezioni di scavo da file CSV'''
        req_fields = ("PK", "Excavation Radius", "Lining Internal Radius",
                      "Lining Thickness", "Lining Offset")
        sezioni_list = get_csv_dict_list(csv_file_path, self.logger, req_fields)
        if sezioni_list:
            pk = -1.0
            a_collection = self.db["Alignment"]
            ac = None
            for row in sezioni_list:
                pk = float(row["PK"])
                ac = a_collection.find_one({"PK":pk, "alignment_set_id":self._id})
                if ac:
                    ac["SECTIONS"] = {
                        "Excavation":{"Radius": toFloat(row["Excavation Radius"])},
                        "Lining":{"Internal_Radius": toFloat(row["Lining Internal Radius"]),
                                  "Thickness": toFloat(row["Lining Thickness"]),
                                  "Offset": toFloat(row["Lining Offset"])}
                        }
                    align = Alignment(self.db, ac)
                    align.save()


    #tbm_progetto.csv
    def import_tbm(self, csv_file_path):
        '''importa i dati delle TBM da file CSV'''
        req_fields = ("PK", "excav_diameter", "bead_thickness", "taper", "tail_skin_thickness",
                      "delta", "gamma_muck", "shield_length", "pressure_max")
        tbm_list = get_csv_dict_list(csv_file_path, self.logger, req_fields)
        if tbm_list:
            pk = -1.0
            a_collection = self.db["Alignment"]
            ac = None
            for row in tbm_list:
                pk = float(row["PK"])
                ac = a_collection.find_one({"PK":pk, "alignment_set_id":self._id})
                if ac:
                    ac["TBM"] = {
                        "excav_diameter": toFloat(row["excav_diameter"]),
                        "bead_thickness": toFloat(row["bead_thickness"]),
                        "taper": toFloat(row["taper"]),
                        "tail_skin_thickness": toFloat(row["tail_skin_thickness"]),
                        "delta": toFloat(row["delta"]),
                        "gamma_muck": toFloat(row["gamma_muck"]),
                        "shield_length": toFloat(row["shield_length"]),
                        "pressure_max": toFloat(row["pressure_max"])
                        }
                    align = Alignment(self.db, ac)
                    align.save()


    def import_reference_strata(self, csv_file_path):
        '''importa i reference_strata da file CSV'''
        req_fields = ("code") #TODO: aggiungo altri campi obbligatori
        reference_strata_list = get_csv_dict_list(csv_file_path, self.logger, req_fields)
        if reference_strata_list:
            self.item["REFERENCE_STRATA"] = {row['code']: row for row in reference_strata_list}
            self.save()


    def import_building_pks(self, csv_file_path):
        '''importa le informazioni sui pk degli edifici'''
        req_fields = ("code", "pk_min", "pk_max", "d_min", "d_max")
        bldg_list = get_csv_dict_list(csv_file_path, self.logger, req_fields)
        if bldg_list:
            b_num = 0
            building_coll = self.db["Building"]
            for row in bldg_list:
                building_code = row["code"]
                prop = {"alignment_set_id": self._id, "alignment_code": self.item["code"],
                        "pk_min": row["pk_min"], "pk_max": row["pk_max"],
                        "d_min": row["d_min"], "d_max": row["d_max"]}
                ccurr = building_coll.find({"code": building_code})
                if ccurr.count == 0:
                    self.logger.error("Building with code = %s not found!", building_code)
                for bitem in ccurr:
                    self.logger.debug("Buliding %s found", building_code)
                    building = Building(self.db, bitem)
                    building.load()
                    # aghensi@20160406 tolto livello pk_array da PK_INFO e valori fuori da PK_INFO
                    if "PK_INFO" in building.item:
                        building.item["PK_INFO"].append(prop)
                    else:
                        building.item["PK_INFO"] = [prop]
                    # aghensi@20160407 memorizzo geometria impronta edificio in formato WKT in db
                    # TODO: trasformo WKT in GeoJSON per indicizzazione? (shapely)
                    if "WKT" in row:
                        building.item["WKT"] = row["WKT"]
                    building.item["updated"] = datetime.datetime.utcnow()
                    building.save()
                    b_num = b_num + 1
            self.logger.info("%d Buildings found in %d CSV lines", b_num, len(bldg_list))
