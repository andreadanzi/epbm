# -*- coding: utf-8 -*-
import os
import csv
import datetime
import glob
from lxml import etree
from shapely.geometry import MultiPoint, mapping
from shapely.ops import transform
import ifcopenshell
from minimongo import Model, Index

from base import BaseSmtModel
from building import Building
from utils import toFloat
from helpers import transform_to_wgs
from section import Section

# danzi.tn@20160418 pulizia sui Buildings del progetto dei dati di analisi=>clear_building_analysis
class Project(BaseSmtModel):
    class Meta(object):
        '''specifica alcune impostazioni per la collection'''
        database = 'smt' #TODO: come lo configuro in modo globale?
        indices = (Index("code"))

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


    def import_ifc(self, ifcpath):
        '''Importa il file IFC speficficato nella collection 'section'

        Args:
            ifcpath (string): percorso del file IFC

        Returns:
            bool - True se il file esiste e sono stati estratti degli elementi con proprietà
        '''
        if not os.path.exists(ifcpath):
            self.logger.warning('cannot find file %s', ifcpath)
            return False
        ifcfile = ifcopenshell.open(ifcpath)
        project = ifcfile.by_type("IfcProject")[0]
        cur_section = Section({
            'code':project.Name,
            'project_id':self._id,
            'elements':[]
            })

        supported_types = ('IfcBuildingElementProxy', 'IfcCovering', 'IfcBeam',
                           'IfcColumn', 'IfcCurtainWall', 'IfcDoor', 'IfcMember', 'IfcRailing',
                           'IfcRamp', 'IfcRampFlight', 'IfcWall', 'IfcWallStandardCase', 'IfcSlab',
                           'IfcStairFlight', 'IfcWindow', 'IfcStair', 'IfcRoof', 'IfcPile',
                           'IfcFooting', 'IfcBuildingElementComponent', 'IfcPlate',
                           'IfcReinforcingBar', 'IfcReinforcingMesh', 'IfcTendon',
                           'IfcTendonAnchor', 'IfcBuildingElementPart')
        for cur_type in supported_types:
            for element in ifcfile.by_type(cur_type):
                cur_element = {}
                for relation in element.IsDefinedBy:
                    if relation.is_a('IfcRelDefinesByProperties'):
                        for cur_prop in relation.RelatingPropertyDefinition.HasProperties:
                            if cur_prop.is_a('IfcPropertySingleValue'):
                                cur_element[cur_prop.Name] = cur_prop.NominalValue.wrappedValue
                if cur_element:
                    cur_element['code'] = element.Name
                    cur_element['guid'] = element.GlobalId
                    cur_section.elements.append(cur_element)
                else:
                    self.logger.warn('import_ifc: element %s without properties', element.Name)
        if len(cur_section.elements) > 0:
            cur_section.created = datetime.datetime.utcnow()
            cur_section.updated = datetime.datetime.utcnow()
            cur_section.save()
            return True
        else:
            return False


    def import_ifcs(self, ifcfolder):
        '''Importa i file IFC presenti nella cartella speficficata

        Args:
            ifcfolder (string): percorso della cartella contenente i file IFC
        '''
        if not os.path.exists(ifcfolder):
            self.logger.warning('cannot find folder %s', ifcfolder)
            return
        imported_files = 0
        tot_files = 0
        for ifcfile in glob.glob("*.ifc"):
            tot_files += 1
            if self.import_ifc(ifcfile):
                imported_files += 1
        self.logger.info('%i over %i IFC files imported', imported_files, tot_files)


    def doit(self, parm):
        pass
