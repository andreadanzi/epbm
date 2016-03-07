# -*- coding: utf-8 -*-
import logging
import csv
import datetime
from base import BaseSmtModel
from domain import Domain
        
class Project(BaseSmtModel):
    def _init_utils(self,**kwargs):
        self.logger.debug('created an instance of %s' % self.__class__.__name__)
    
    def delete_referencing(self):
        d_collection = self.db["Domain"] 
        a_collection = self.db["Alignment"]
        for d in d_collection.find({"project_id":self._id}):
            a_collection.remove({"domain_id":d["_id"]})
        d_collection.remove({"project_id":self._id})
    
    def delete(self):        
        super(Project,self).delete()
        self.delete_referencing()
    
    def import_domains(self, csvFilePath):
        with open(csvFilePath, 'rb') as csvfile:
            rows = []
            align_reader = csv.DictReader(csvfile, delimiter=';')
            for row in align_reader:
                row["project_id"] = self._id 
                row["created"] = datetime.datetime.utcnow()
                row["updated"] = datetime.datetime.utcnow()
                rows.append(row)
            self.delete_referencing()
            d_collection = self.db["Domain"] 
            d_collection.insert(rows)
    
    def doit (self,parm):
        pass


    