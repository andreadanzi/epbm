# -*- coding: utf-8 -*-
'''
Classe Edificio e altro elemento strutturale/infrastrutturale

'''
# danzi.tn@20160312 import delle PK di riferimento sui building
# danzi.tn@20160418 pulizia sul Building dei dati di analisi => clear_analysis
# aghensi@201605XX spostamento import PK in alignment_set
# aghensi@20160615 refactor per utilizzare minimongo
from minimongo import Index

from base import BaseSmtModel
#from element_classes import ElementClasses

class Building(BaseSmtModel):
    '''
    classe edificio

    struttura di base:
        * code (uppercase string): codice dell'edificio
        * ...
    '''
    class Meta(object):
        '''definizione Model minimongo'''
        database = 'smt'
        indexes = (Index('code'))


    def assign_class(self):
        '''assegna i valori delle classi per il tipo di elemento'''
        retval = "XXX"
        typology = self.typology
        sensibility = self.sc_lev
        # TODO: riassumo le "_classes" collection in un'unica collection "element_classes"
        # con attributo tipology - funziona ElementClasses.collection.find?
        ccurr = self.database['element_classes'].find({"sc_lev":sensibility,
                                                       "typology": typology}).sort("dc_lev")
        self.damage_limits = list(ccurr)
        #Gabriele@20160330 Vibration analysis
        # per il momento uso la sensibilita' generale dell'edificio
#        sensibility = self.item["sc_vbr_lev"]
#        ccurr = self.database['vibration_class'].find({"sc_lev":sensibility}).sort("dc_lev")
#        self.item["VIBRATION_LIMITS"] = list(ccurr)
        self.save()
        return retval

    def clear_analysis(self, b_values_dtype_names):
        self.samples_size = .0
        for key in b_values_dtype_names:
            if key in self:
                setattr(self, key, {})
                self.logger.debug("_clear_buildings_data on %s->%s" % (self.code, key))
