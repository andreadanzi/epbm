# -*- coding: utf-8 -*-
import os
import csv
import datetime
from base import BaseSmtModel
from utils import toFloat

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
        for db_collection in ["Building", "BuildingClass", "UndergroundStructureClass",
                              "UndergroundUtilityClass", "OvergroundInfrastructureClass",
                              "VibrationClass"]:
            self.db[db_collection].remove({"project_id":self._id})

    def delete(self):
        super(Project, self).delete()
        self.delete_referencing()

    def import_buildings(self, csv_file_path):
        if not os.path.exists(csv_file_path):
            self.logger.warning('il file %s non esiste', csv_file_path)
            return
        with open(csv_file_path, 'rb') as csvfile:
            rows = []
            csv_reader = csv.DictReader(csvfile, delimiter=';')
            for row in csv_reader:
                for key, value in row.iteritems():
                    # HACK: bldg_code deve restare stringa - oppure uso sempre toFloat?
                    if key != "bldg_code":
                        row[key] = toFloat(value)
                row["project_id"] = self._id
                row["created"] = datetime.datetime.utcnow()
                row["updated"] = datetime.datetime.utcnow()
                rows.append(row)
            d_collection = self.db["Building"]
            d_collection.insert(rows)

    def import_objects(self, class_name, csv_file_path):
        if not os.path.exists(csv_file_path):
            self.logger.warning('il file %s non esiste', csv_file_path)
            return
        with open(csv_file_path, 'rb') as csvfile:
            rows = []
            csv_reader = csv.DictReader(csvfile, delimiter=';')
            for row in csv_reader:
                for key, value in row.iteritems():
                    row[key] = toFloat(value)
                row["project_id"] = self._id
                row["created"] = datetime.datetime.utcnow()
                row["updated"] = datetime.datetime.utcnow()
                rows.append(row)
            d_collection = self.db[class_name]
            d_collection.insert(rows)

    def doit(self, parm):
        pass
