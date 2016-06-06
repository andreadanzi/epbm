# -*- coding: utf-8 -*-
"""
aghensi@20160502 - importazione LandXML delle stratigrafie in mongodb con indice spaziale
"""
from base import BaseSmtModel

class StrataSurface(BaseSmtModel):
    def _init_utils(self,**kwargs):
        self.logger.debug('created an instance of %s' % self.__class__.__name__)

    def doit(self, parm):
        pass
