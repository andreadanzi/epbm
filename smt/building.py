# -*- coding: utf-8 -*-
'''
Classe Edificio e altro elemento strutturale/infrastrutturale

'''
# danzi.tn@20160312 import delle PK di riferimento sui building
# danzi.tn@20160418 pulizia sul Building dei dati di analisi => clear_analysis
# aghensi@201605XX spostamento import PK in alignment_set
from .base import BaseSmtModel

class Building(BaseSmtModel):
    '''
    classe edificio
    '''
    def _init_utils(self, **kwargs):
        #self.logger.debug('created an instance of %s' % self.__class__.__name__)
        pass

# assign_building_class
    def assign_class(self):
        '''assegna la classe all'elemento in base alla tipologia e al livello di sensibilità'''
        ccurr = list(self.db.ElementClass.find({"project_id":self.item["project_id"],
                                                "typology":self.item["typology"],
                                                "sc_lev":self.item["sc_lev"]}).sort("dc_lev"))
        # TODO: controllo che ccurr sia una lista di dict
        self.item["DAMAGE_LIMITS"] = ccurr
        #Gabriele@20160330 Vibration analysis
        # per il momento uso la sensibilita' generale dell'edificio
#        ccurr = list(self.db.VibrationClass.find({"sc_lev":self.item["sc_vbr_lev"]}).sort("dc_lev"))
#        self.item["VIBRATION_LIMITS"] = ccurr
        self.save()
        return len(ccurr)


    def clear_analysis(self, b_values_dtype_names):
        '''cancella i dati degli edifici relativi alle analisi'''
        self.item["samples_size"] = .0
        for key in b_values_dtype_names:
            if key in self.item:
                self.item[key] = {}
                self.logger.debug("_clear_buildings_data on %s->%s", self.item["bldg_code"], key)


    def doit(self, parm):
        pass
