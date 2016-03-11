# -*- coding: utf-8 -*-
import logging
import csv
from base import BaseSmtModel
        
class Building(BaseSmtModel):
    def _init_utils(self,**kwargs):
        self.logger.debug('created an instance of %s' % self.__class__.__name__)

# assign_building_class
    def assign_class(self):
        retVal="XXX"
        sensibility = self.item["sc_lev"]
        ccurr = self.db.BuildingClass.find({"sc_lev":sensibility}).sort("dc_lev")
        class_array = []
        for c in ccurr:
            class_array.append(c)
        self.item["DAMAGE_LIMITS"] = class_array
        self.save()
        return retVal

    
    def doit (self,parm):
        pass


    
