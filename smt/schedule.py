# -*- coding: utf-8 -*-
"""
classe cronoprogramma
"""
import dateutil.parser
from base import BaseSmtModel

class WBS(BaseSmtModel):
    '''Classe WBS

    struttura base:
    * WBS (string): codice della WBS
    * alignment_set_id (string): id dell'alignment set
    * pk_start (float): pk di inizio della WBS
    * pk_end (float): pk di fine della WBS
    * schedule: dict con 'start' e 'end'
    '''
    pass


# TODO: non ancora chiaro come riconoscere quando devo fare un update o un add...
    def update_schedule(self, start, end):
        '''sostituisce le tempistiche alla WBS'''
        self.item['schedule']=[create_schedule_doc(start, end)]

    def add_schedule(self, start, end):
        '''aggiunge le tempistiche alla WBS'''
        if 'schedule' in self.item:
            self.item['schedule'].append(create_schedule_doc(start, end))
        else:
            self.update_schedule(start, end)

def create_schedule_doc(start, end):
    return {
        'start': dateutil.parser.parse(start, dayfirst=True),
        'end': dateutil.parser.parse(end, dayfirst=True)
        }