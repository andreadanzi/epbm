# -*- coding: utf-8 -*-
import os
import csv
import datetime
from lxml import etree
from shapely.geometry import MultiPoint, mapping
from shapely.ops import transform

from base import BaseSmtModel
from building import Building
from utils import toFloat
from helpers import transform_to_wgs

# danzi.tn@20160418 pulizia sui Buildings del progetto dei dati di analisi=>clear_building_analysis
class Project(BaseSmtModel):
    def _init_utils(self, **kwargs):
        self.logger.debug('created an instance of %s', self.__class__.__name__)


    def delete_referencing(self):
        # aghensi@20160406 aggiunta eliminazione di edifici e classi relativi al progetto
        d_collection = self.db["Domain"]
        as_collection = self.db["AlignmentSet"]
        a_collection = self.db["Alignment"]
        for d in d_collection.find({"project_id":self._id}):
            for als in as_collection.find({"domain_id":d["_id"]}):
                a_collection.remove({"alignment_set_id":als["_id"]})
            as_collection.remove({"domain_id":d["_id"]})
        d_collection.remove({"project_id":self._id})
        # danzi.tn@20160407 nuova collection ReferenceStrata
        for db_collection in ["Building", "BuildingClass", "UndergroundStructureClass",
                              "UndergroundUtilityClass", "OvergroundInfrastructureClass",
                              "VibrationClass", "ReferenceStrata", "StrataSurfacePoints"]:
            self.db[db_collection].remove({"project_id":self._id})


    def delete(self):
        self.delete_referencing()
        super(Project, self).delete()


    def clear_building_analysis(self, b_values_dtype_names):
        d_collection = self.db["Building"]
        bldgs = d_collection.find({"project_id": self._id})
        # b_values_dtype_names
        for bl_item in bldgs:
            b = Building(self.db, bl_item)
            b.load()
            b.clear_analysis(b_values_dtype_names)
            b.item["updated_by"] = "Project.clear_building_analysis"
            b.save()


    def import_objects(self, class_name, csv_file_path):
        if not os.path.exists(csv_file_path):
            self.logger.warning('il file %s non esiste', csv_file_path)
            return
        with open(csv_file_path, 'rb') as csvfile:
            rows = []
            csv_reader = csv.DictReader(csvfile, delimiter=';')
            for row in csv_reader:
                for key, value in row.iteritems():
                    # aghensi@20160503 HACK per mantenere bldg_code testo
                    if key != "bldg_code":
                        row[key] = toFloat(value)
                    # danzi.tn@20160408 i codici sono sempre UPPERCASE
                    if key == "code":
                        row[key] = value.upper()
                row["project_id"] = self._id
                row["created"] = datetime.datetime.utcnow()
                row["updated"] = datetime.datetime.utcnow()
                rows.append(row)
            d_collection = self.db[class_name]
            d_collection.insert(rows)


    def import_stratasurf(self, landxml_file_path, epsg):
        '''
        Importa le superfici da file LandXML e le salva in oggetto GeoJSON MultiPoint.
        La struttura del LandXML è la seguente:
        <LandXML>
            <Surfaces>
                <Surface id="id", desc="descrizione">
                    <Pnts>
                        <P>X Y Z</P>
                        ..
                    </Pnts>
                </Surface>
                ..
            </Surfaces>
        </LandXML>
        '''
        if not os.path.exists(landxml_file_path):
            self.logger.warning('il file %s non esiste', landxml_file_path)
            return
        doc = etree.parse(landxml_file_path)
        self.logger.debug('import_stratasurf_points - starting reading %d rows from %s',
                          len(doc), landxml_file_path)
        strata = doc.find('.//{http://www.landxml.org/schema/LandXML-1.2}Surfaces')
        surf_list = []
        for surface in strata.iter("Surface"):
            coords = []
            for point in surface.find("Pnts").iter("P"):
                coords.append([float(coord) for coord in point.text.split(' ')])
            #uso shapely e pyproj per ottenere latitudine e longitudine in WGS84
            wgs_surf = transform(transform_to_wgs(epsg), MultiPoint(coords))
            surf_list.append({
                "strata_id": surface.get("id"),
                "CODE": surface.get("desc"), #.upper()?
                "geometry": {"type": "MultiPoint", "coordinates": coords},
                "geom_wgs": mapping(wgs_surf), #trasforma oggetto shapely in geoJSON
                 # memorizzo il massimo delle z per avere strati ordinati
                "max_elev": max([point.z for point in wgs_surf]),
                "project_id": self._id,
                "created":   datetime.datetime.utcnow(),
                "updated": datetime.datetime.utcnow(),
                })
        if len(surf_list) > 0:
            p_collection = self.db["StrataSurface"]
            p_collection.insert(surf_list)
            # aggiungo indice spaziale 2d
            p_collection.create_index([("geom_wgs", "2dsphere")])


    def doit(self, parm):
        pass
