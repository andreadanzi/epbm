# -*- coding: utf-8 -*-
'''Classe del progetto'''
import os
import csv
import datetime
import glob
from math import atan2, degrees, cos, sin
from lxml import etree
from shapely.geometry import MultiPoint, mapping, asShape
from shapely.ops import transform
import ifcopenshell
from utils import toFloat
from helpers import transform_to_wgs, get_csv_dict_list
from base import BaseSmtModel
from building import Building
from schedule import WBS
from tbm import TBM
from reference_strata import ReferenceStrata
from domain import Domain
from element_class import ElementClass
from vibration_class import VibrationClass
from corridor import Corridor
from alignment_set import AlignmentSet

# danzi.tn@20160418 pulizia sui Buildings del progetto dei dati di analisi=>clear_building_analysis
class Project(BaseSmtModel):
    '''Classe del progetto'''
    REQUIRED_CSV_FIELDS = ('code', 'align_scan_length', 'epsg')


    def delete_referencing(self):
        '''cancella tutti gli oggetti che appartengono al progetto'''
        # aghensi@20160406 aggiunta eliminazione di edifici e classi relativi al progetto
        as_collection = self.db["AlignmentSet"]
        a_collection = self.db["Alignment"]
        for als in as_collection.find({"project_id":self._id}):
            a_collection.remove({"alignment_set_id":als["_id"]})
        as_collection.remove({"project_id":self._id})
        # danzi.tn@20160407 nuova collection ReferenceStrata
        # aghensi@20160620 unica collection ElementClass
        for db_collection in ["Building", "ElementClass", "Domain", "WBS",
                              "VibrationClass", "ReferenceStrata", "StrataSurfacePoints"]:
            self.db[db_collection].remove({"project_id":self._id})


    def delete(self):
        '''cancella il progetto e tutti gli oggetti ad esso appartenenti'''
        self.delete_referencing()
        super(Project, self).delete()


    def clear_building_analysis(self, b_values_dtype_names):
        '''elimina i dati delle analisi sugli edifici del progetto'''
        d_collection = self.db["Building"]
        bldgs = d_collection.find({"project_id": self._id})
        # b_values_dtype_names
        for bl_item in bldgs:
            bldg = Building(self.db, bl_item)
            bldg.load()
            bldg.clear_analysis(b_values_dtype_names)
            bldg.save("Project.clear_building_analysis")


    def import_objects(self, class_name, csv_file_path):
        '''importa gli oggetti nel database

        trasforma tutti gli attributi possibili in float e il valore di 'code' in uppercase'''
        try:
            req_fields = eval(class_name).REQUIRED_CSV_FIELDS
        except AttributeError:
            req_fields = None
        obj_list = get_csv_dict_list(csv_file_path, self.logger, req_fields)
        if obj_list:
            for obj_dict in obj_list:
                obj_dict["project_id"] = self._id
                obj_dict["created"] = datetime.datetime.utcnow()
                obj_dict["updated"] = datetime.datetime.utcnow()
            self.db[class_name].insert(obj_list)


    def import_schedule(self, csv_file_path):
        '''importa il cronoprogramma e assegna le WBS agli alignment relativi'''
        wbs_list = get_csv_dict_list(csv_file_path, self.logger, WBS.REQUIRED_CSV_FIELDS)
        if wbs_list:
            a_collection = self.db['AlignmentSet']
            for wbs_dict in wbs_list:
                wbs_dict["project_id"] = self._id
                cur_wbs = WBS(self.db, wbs_dict)
                # start_date e end_date devono essere datetime, uso update_schedule per parsing
                cur_wbs.update_schedule(wbs_dict['start_date'], wbs_dict['end_date'])
                aset = a_collection.find_one({'code':cur_wbs.item['alignment_set_code']})
                if aset:
                    cur_wbs.item['alignment_set_id'] = aset['_id']
                    cur_wbs.assign_to_alignment(self.item['align_scan_length'])
                    cur_wbs.save("import_schedule", True)
                else:
                    self.logger.warn('Cannot find alignment_set id of alignment set %s for WBS %s',
                                     cur_wbs.item['alignment_set_code'], cur_wbs.item['code'])


# aghensi@20160621 aggiunte multiple TBM su alignment
    def import_tbm(self, csv_file_path):
        '''importa le TBM e le assegna agli Alignment relativi'''
        tbm_list = get_csv_dict_list(csv_file_path, self.logger, TBM.REQUIRED_CSV_FIELDS)
        if tbm_list:
            a_collection = self.db['AlignmentSet']
            for tbm_dict in tbm_list:
                tbm_dict["project_id"] = self._id
                tbm_dict['totalContactThrust'] = tbm_dict['loadPerCutter']*tbm_dict['cutterCount']
                cur_tbm = TBM(self.db, tbm_dict)
                aset = a_collection.find_one({'code':cur_tbm.item['alignment_set_code']})
                if aset:
                    cur_tbm.item['alignment_set_id'] = aset['_id']
                    cur_tbm.assign_to_alignment()
                    cur_tbm.save("import_schedule", True)
                else:
                    self.logger.warn('Cannot find alignment_set id of alignment set %s for TBM %s',
                                     cur_tbm.item['alignment_set_code'], cur_tbm.item['code'])


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
                "code": surface.get("desc"), #.upper()?
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
        #TODO: controllo unità misura...
        if not os.path.exists(ifcpath):
            self.logger.warning('cannot find file %s', ifcpath)
            return False
        ifcfile = ifcopenshell.open(ifcpath)
        project = ifcfile.by_type("IfcProject")[0]
        cur_section = {'code':project.Name, 'project_id':self._id, 'elements':[]}

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
                try:
                    for relation in element.IsDefinedBy:
                    #if relation.is_a('IfcRelDefinesByProperties'):
                        for cur_prop in relation.RelatingPropertyDefinition.HasProperties:
                            #if cur_prop.is_a('IfcPropertySingleValue'):
                            cur_element[cur_prop.Name] = cur_prop.NominalValue.wrappedValue
                except AttributeError as atterr:
                    self.logger.warn('import ifc: cannot find attribute %s', atterr)
                if cur_element:
                    cur_element['code'] = element.Name
                    cur_element['guid'] = element.GlobalId
                    cur_section['elements'].append(cur_element)
                else:
                    self.logger.warn('import_ifc: element %s without properties', element.Name)
        if len(cur_section['elements']) > 0:
            cur_section['created'] = datetime.datetime.utcnow()
            cur_section['updated'] = datetime.datetime.utcnow()
            return cur_section
        else:
            return None


    def import_ifcs(self, ifcfolder):
        '''Importa i file IFC presenti nella cartella speficficata

        Args:
            ifcfolder (string): percorso della cartella contenente i file IFC
        '''
        if not os.path.exists(ifcfolder):
            self.logger.warning('cannot find folder %s', ifcfolder)
            return
        tot_files = 0
        for ifcfile in glob.glob("*.ifc"):
            tot_files += 1
            sections = []
            cur_section = self.import_ifc(ifcfile)
            if cur_section:
                sections.append(cur_section)
        if len(sections) > 0:
            self.db["Section"].insert(sections)
            self.logger.info('%i over %i IFC files imported', len(sections), tot_files)


    # aghensi@20160616 domini slegati da alignment sets
    def import_domains(self, csv_file_path):
        '''
        importa i domini da file CSV e memorizza le matrici di trasformazione da e per M3E
        i vertici del sottodominio sono salvati in "boundaries" e pronti per essere utilizzati
        con la query campo: {$geoWithin: {$polygon: boundaries}}
        '''
        domain_list = get_csv_dict_list(csv_file_path, self.logger, Domain.REQUIRED_CSV_FIELDS)
        if domain_list:
            domains = []
            transf = transform_to_wgs(self.item['epsg'])
            for row in domain_list:
                x_1 = row["x1"]
                y_1 = row["y1"]
                x_2 = row["x2"]
                y_2 = row["y2"]
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
                        [row["x3"], row["y3"]],
                        [row["x4"], row["y4"]],
                        [x_1, y_1]
                        ]
                    }
                row["boundaries"] = boundary,
                # uso shapely e proj per salvare coordinate WGS
                row["bound_wgs"] =mapping(transform(transf, asShape(boundary))),
                row["project_id"] = self._id,
                row["export_matrix"] = trasl_rot_matrix,
                row["import_matrix"] = rot_trasl_matrix
                # memorizzo gli altri valori
                domains.append(row) #Serve? basta usare domain_list?
            if len(domains) > 0:
                self.db['Domain'].insert(domains)
