# -*- coding: utf-8 -*-
'''Classe del progetto'''
import os
import csv
import datetime
import glob
from lxml import etree
from shapely.geometry import MultiPoint, mapping, asShape
from shapely.ops import transform
import ifcopenshell
from minimongo import Index
from math import atan2, degrees, cos, sin

from utils import toFloat
from helpers import transform_to_wgs
from base import BaseSmtModel
from building import Building
from section import Section
from alingnment_set import AlignmentSet
from alignment import Alignment
from element_classes import ElementClasses
from vibration_class import VibrationClass
from reference_strata import ReferenceStrata
from strata_surface import StrataSurface
from domain import Domain

# danzi.tn@20160418 pulizia sui Buildings del progetto dei dati di analisi=>clear_building_analysis
# aghensi@20160615 refactoring per usare minimongo e domains trattato come il vecchio sottodominio
class Project(BaseSmtModel):
    '''Classe del progetto'''
    class Meta(object):
        '''specifica alcune impostazioni per la collection'''
        database = 'smt' #TODO: come lo configuro in modo globale?
        indices = (Index("code"))

#    def _init_utils(self, **kwargs):
#        self.logger.debug('created an instance of %s', self.__class__.__name__)


    def delete_referencing(self):
        '''cancella tutti gli oggetti che appartengono al progetto'''
        # aghensi@20160406 aggiunta eliminazione di edifici e classi relativi al progetto
        for als in AlignmentSet.collection.find({"project_id":self._id}):
            # TODO: creo un delete_referencing anche in alignment_set?
            Alignment.collection.remove({"alignment_set_id":als._id})
        AlignmentSet.collection.remove({"project_id":self._id})
        # danzi.tn@20160407 nuova collection ReferenceStrata
        for db_collection in [Building, ElementClasses, VibrationClass, ReferenceStrata,
                              StrataSurface, Domain]:
            self.database[db_collection].remove({"project_id":self._id})


    def delete(self):
        '''cancella il progetto e tutti gli oggetti ad esso appartenenti'''
        self.delete_referencing()
        super(Project, self).delete() #o sempicemente self.remove()?


    def clear_building_analysis(self, b_values_dtype_names):
        '''elimina i dati delle analisi sugli edifici del progetto'''
        # b_values_dtype_names
        for bldg in Building.collection.find({"project_id": self._id}):
            bldg.clear_analysis(b_values_dtype_names)
            bldg.updated_by = "Project.clear_building_analysis"
            bldg.save()


    def import_objects(self, cls, csv_file_path):
        '''importa gli oggetti dal database

        trasforma tutti gli attributi possibili in float e il valore di 'code' in uppercase'''
        if not os.path.exists(csv_file_path):
            self.logger.warning('il file %s non esiste', csv_file_path)
            return
        with open(csv_file_path, 'rb') as csvfile:
            csv_reader = csv.DictReader(csvfile, delimiter=';')
            rows = []
            for row in csv_reader:
                doc = {}
                for key, value in row.iteritems():
                    doc[key] = toFloat(value)
                try:
                    doc['code'] = row['code'].upper()
                    doc["created"] = datetime.datetime.utcnow()
                    doc["updated"] = datetime.datetime.utcnow()
                    rows.append(doc)
                except KeyError:
                    # TODO: non esiste alcun campo chiamato code, warning e tralascio elemento
                    self.logger.warning('non trovo il campo "code" per la collection %s', cls.__name__)
            cls.collection.insert(rows)


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
        for surface in strata.iter("Surface"):
            coords = []
            for point in surface.find("Pnts").iter("P"):
                coords.append([float(coord) for coord in point.text.split(' ')])
            #uso shapely e pyproj per ottenere latitudine e longitudine in WGS84
            wgs_surf = transform(transform_to_wgs(epsg), MultiPoint(coords))
            surf = StrataSurface({
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
            surf.save()


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


    # aghensi@20160616 domini slegati da alignment sets
    def import_domains(self, csv_file_path):
        '''
        importa i domini da file CSV e memorizza le matrici di trasformazione da e per M3E
        i vertici del sottodominio sono salvati in "boundaries" e pronti per essere utilizzati
        con la query campo: {$geoWithin: {$polygon: boundaries}}
        '''
        if not os.path.exists(csv_file_path):
            self.logger.warning('il file %s non esiste', csv_file_path)
            return
        with open(csv_file_path, 'rb') as csvfile:
            domain_reader = csv.DictReader(csvfile, delimiter=';')
            domains = []
            self.logger.debug('import_domains - starting reading %d rows from %s',
                              len(domain_reader), csv_file_path)
            transf = transform_to_wgs(self.epsg)
            for row in domain_reader:
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
                domain = {
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
                        domain[key] = toFloat(value)
                domains.append(domain)
            if len(domains) > 0:
                Domain.collection.insert(domains)


    def doit(self, parm):
        pass
