# -*- coding: utf-8 -*-
"""
classe che memorizza la nuvola di punti delle superfici stratigrafiche
"""
from minimongo import Index
from base import BaseSmtModel

class StrataSurface(BaseSmtModel):
    '''classe della nuvola di punti della superficie stratigrafica'''
    class Meta(object):
        '''impostazioni per minimongo'''
        database = 'smt'
        indexes = (Index("geom_wgs", "2dsphere"))

#    def _init_utils(self,**kwargs):
#        self.logger.debug('created an instance of %s' % self.__class__.__name__)
#
#    def doit(self, parm):
#        pass
