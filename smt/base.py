# -*- coding: utf-8 -*-
'''
classe di base per le collection del database

utilizza minimongo per trasformare i documenti in classi con attributi (anche annidati)
'''
import logging
import csv
import os
import datetime
from utils import toFloat
from minimongo import Model

class BaseSmtModel(Model):
    '''
    classe di base per le collection del database

    utilizza minimongo per trasformare i documenti in classi con attributi (anche annidati)
    minimongo espone gli attributi "collection" e "database" per accedere agli oggetti di pymongo
    '''
    class Meta(object):
        '''metadati per minimongo'''
        database = 'smt'


    def __init__(self, *args, **kwargs):
        ''' inizializza la classe

        chiama il costruttore della superclasse
        quindi chiama _init_utils, eventualmente modificato dalle subclassi'''
        super(BaseSmtModel, self).__init__(*args, **kwargs)
        self._init_utils(**kwargs)


    @property
    def logger(self):
        '''ottiene il logger per la classe

        non salva l'istanza come attributo per evitare conflitti con minimongo'''
        name = '.'.join([__name__, self.__class__.__name__])
        return logging.getLogger(name)


    def delete_all(self):
        '''rimuove tutti gli elementi della collection'''
        self.collection.remove({})


    def delete(self):
        '''elimina il documento dalla collection

        funzione per mantenere compatibilità con vecchio codice'''
        self.remove()


    def _init_utils(self, **kwargs):
        '''ulteriori inizializzazioni

        metodo da modificare nelle subclassi per particolari inizializzazioni'''
        self.logger.debug('created an instance of %s', self.__class__.__name__)


# TODO: implementare logica plugin (categoria Calculation)

    def before_doit(self, parm):
        '''operazioni da svolgere prima dei calcoli

        metodo da modificare nelle subclassi'''
        self.logger.debug("before_doit with parm = " + parm)
        return parm


    def after_doit(self, parm, out):
        '''operazioni da svolgere dopo i calcoli

        metodo da modificare nelle subclassi'''
        self.logger.debug("after_doit with parm = %s and out = %s", parm, out)
        return out


    def doit(self, parm):
        '''esegue i calcoli

        metodo da modificare nelle subclassi'''
        out = ""
        self.logger.debug("doit with parm = %s and out = %s", parm, out)
        return out


    def perform_calc(self, parm):
        '''esegue tutte le operazioni per eseguire i calcoli

        metodo da modificare nelle subclassi'''
        parm = self.before_doit(parm)
        retval = self.doit(parm)
        retval = self.after_doit(parm, retval)
        return retval


    @classmethod
    def import_from_csv_file(cls, csv_file_path, delete_existing=False):
        '''Importa i documenti da file CSV

        trasforma tutti i nomi di campo in minuscolo
        trasforma tutti i valori possibili in float
        trasforma i valori del campo "code" in maiuscolo
        se il file CSV non esiste avvisa nel log ma non restituisce errori

        Args:
            * cls (object): classe che chiama il metodo
            * csv_file_path (string): percorso del file CSV
            * delete_existing (bool, default=False): cancella tutti gli elementi della collection
        '''
        if not os.path.exists(csv_file_path):
            cls.logger.warn('cannot find file %s', csv_file_path)
            return
        with open(csv_file_path, 'rb') as csvfile:
            csv_reader = csv.DictReader(csvfile, delimiter=';')
            if delete_existing:
                cls.collection.remove({})
            for row in csv_reader:
                doc = {}
                for key, value in row.iteritems():
                    doc[key] = toFloat(value)
                try:
                    doc['code'] = row['code'].upper()
                except KeyError:
                    # non esiste alcun campo chiamato code, che faccio?
                    pass
                doc["created"] = datetime.datetime.utcnow()
                doc["updated"] = datetime.datetime.utcnow()
                cls(doc).save()
