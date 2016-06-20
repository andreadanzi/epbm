# -*- coding: utf-8 -*-
"""
classe cronoprogramma
"""
import dateutil.parser
from base import BaseSmtModel
from alignment import Alignment

class WBS(BaseSmtModel):
    '''Classe WBS

    struttura base:
    * code (string): codice della WBS
    * project_id (id): Id del progetto
    * alignment_set_id (objectid): id dell'alignment set (in CSV ho il code!)
    * alignment_set_code (string): codice dell'alignment set
    * pk_start (float): pk di inizio della WBS
    * pk_end (float): pk di fine della WBS
    * start_date (datetime): data di inzio della lavorazione
    * end_date (datetime): data di fine della lavorazione
    * duration (datetime): timedelta delle due date
    * after (lista di string): eventuale lista dei codici WBS
    '''
    REQUIRED_CSV_FIELDS = ('code', 'alignment_set_code', 'pk_start', 'pk_end', 'start_date', 'end_date')


    def update_schedule(self, start, end):
        '''aggiunge o modifice le tempistiche della WBS

        utilizza dateutil per trasformare i dati di input in datetime

        Args:
            * start (string): data di inizio della WBS
            * end (string): data di fine della WBS'''
        try:
            self.item['start_date'] = dateutil.parser.parse(start, dayfirst=True)
            self.item['end_date'] = dateutil.parser.parse(end, dayfirst=True)
            self.item['duration'] = self.item['end_date'] - self.item['start_date']
            if self.item['duration'] < 0:
                self.logger.warn('update_schedule: start date greater than end date for WBS %s',
                                 self.item['code'])
        except ValueError as valerr:
            self.logger.error('update_schedule: cannot parse date : %s', valerr)


    def assign_to_alignment(self):
        '''associa la WBS agli alignment relativi

        cerca gli alignment dell'alignment set di quella WBS contenuti tra pk_start e pk_end
        calcola la percentuale di lavorazione per ogni punto (1/numero totale di punti)
        e la durata per ogni punto (percentuale*duration), oltre alla data di esecuzione del punto
        (start_date + durata puntuale* numero in sequenza del punto)
        l'esecuzione può avvenire nel senso inverso alle pk

        NB: questo metodo ipotizza un andamento lineare dell'attività
        '''
        if self.item['pk_start'] <= self.item['pk_end']:
            min_pk = self.item['pk_start']
            max_pk = self.item['pk_end']
            sortdir = 1
        else:
            max_pk = self.item['pk_start']
            min_pk = self.item['pk_end']
            sortdir = -1
        calign = self.db['Alignment'].find({
            'alignment_set_id':self.item['alignment_set_id'],
            'PK': {'$gte': min_pk, '$lt':max_pk}
            }).sort('PK', sortdir)
        tot_aligns = len(calign)
        if tot_aligns > 0:
            percent = 1./tot_aligns
            point_duration = self.item['duration']//tot_aligns
            wbs = {'wbs_code':self.item['code'], 'duration': point_duration, 'percent': percent}
            last_date = self.item['start_date']
            for curalign in calign:
                wbs['start_date'] = last_date
                last_date += point_duration
                # TODO: controllo che non si sia andati oltre all'end_date della WBS?
                wbs['end_date'] = last_date
                align = Alignment(self.db, curalign)
                align.load()
                align.item['wbs'] = wbs
                align.save()
