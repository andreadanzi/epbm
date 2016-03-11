# -*- coding: utf-8 -*-
import logging
import csv
from base import BaseSmtModel
        
class BuildingClass(BaseSmtModel):
    def _init_utils(self,**kwargs):
        self.logger.debug('created an instance of %s' % self.__class__.__name__)
    
    def doit (self,parm):
        pass


    
