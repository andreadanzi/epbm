# -*- coding: utf-8 -*-
'''classe di base per le collection del database'''
import logging
import csv
import os
import datetime
from .utils import toFloat

class BaseStruct(object):
    '''classe che trasforma un dizionario in oggetto con attributi'''
    def __init__(self, d):
        '''inizializza la classe'''
        for a, b in d.iteritems():
            if isinstance(b, (list, tuple)):
                setattr(self, a, [BaseStruct(x) if isinstance(x, dict) else x for x in b])
            else:
                setattr(self, a, BaseStruct(b) if isinstance(b, dict) else b)


class BaseSmtModel(object):
    '''classe di base per le collection del database'''
    @classmethod
    def find(cls, db, parms=None):
        '''cerca gli elmenti nella collection a cui appartiene l'elemento'''
        collection = db[cls.__name__]
        return collection.find(parms)


    def __init__(self, db, initial=None, **kwargs):
        self._id = None
        self.db = db
        self.item = {}
        self.logger = logging.getLogger('smt_main.' + self.__class__.__name__)
        if initial:
            self.item = initial
            if "_id" in initial:
                self._id = initial["_id"]
        self.collection = self.db[self.__class__.__name__]
        self.__dict__.update(kwargs)
        # after __dict__.update it could have a valid _id
        if self._id:
            self.item["_id"] = self._id
        self._init_utils(**kwargs)


    def _init_utils(self):
        '''ulteriori inizializzazioni

        metodo da modificare nelle subclassi per particolari inizializzazioni'''
        self.logger.debug('created an instance of %s', self.__class__.__name__)


    def load(self, **kwargs):
        '''carica il documento di mongodb nell'attributo item'''
        #self.logger.debug('load %s %s' % (fields,self.__class__.__name__))
        self.item = self.collection.find_one({'_id': self._id}, **kwargs)
        return self


    def save(self, *args, **kwargs):
        '''memorizza il documento nel database'''
        #self.logger.debug('save %s' % (self.__class__.__name__))
        self.item["updated"] = datetime.datetime.utcnow()
        self._id = self.collection.save(self.item, *args, **kwargs)


    def delete(self):
        '''elimina il documento dalla collection'''
        self.logger.debug('delete %s %s', self.__class__.__name__, self._id)
        self.collection.remove(self._id)


    @classmethod
    def delete_all(cls, db):
        '''rimuove tutti gli elementi della collection'''
        collection = db[cls.__name__]
        collection.remove({})


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
    def import_from_csv_file(cls, db, csv_file_path, delete_existing=False):
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
            rows = []
            csv_reader = csv.DictReader(csvfile, delimiter=';')
            for row in csv_reader:
                for key, value in row.iteritems():
                    # HACK: bldg_code deve restare stringa - oppure uso sempre toFloat?
                    if key != "bldg_code":
                        row[key] = toFloat(value)
                row["created"] = datetime.datetime.utcnow()
                row["updated"] = datetime.datetime.utcnow()
                rows.append(row)
            #db.Alignment.insert(rows)
            collection = db[cls.__name__]
            if delete_existing:
                collection.remove()
            collection.insert(rows)
