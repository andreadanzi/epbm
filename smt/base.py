# -*- coding: utf-8 -*-
import logging, csv
import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
from utils import toFloat

class BaseStruct(object):
    def __init__(self, d):
        for a, b in d.iteritems():
            if isinstance(b, (list, tuple)):
               setattr(self, a, [BaseStruct(x) if isinstance(x, dict) else x for x in b])
            else:
               setattr(self, a, BaseStruct(b) if isinstance(b, dict) else b)


class BaseSmtModel:
    @classmethod
    def ImportFromCSVFile(cls,csvFilePath, db, delete_existing=True):
        with open(csvFilePath, 'rb') as csvfile:
            rows = []
            csv_reader = csv.DictReader(csvfile, delimiter=';')
            for row in csv_reader:
                for key, value in row.iteritems():
                    row[key] = toFloat(value)
                row["created"] = datetime.datetime.utcnow()
                row["updated"] = datetime.datetime.utcnow()
                rows.append(row)
            #db.Alignment.insert(rows)
            collection = db[cls.__name__]
            if delete_existing:
                collection.remove()
            collection.insert(rows)
    
    @classmethod
    def find(cls, db, parms=None):
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
        self.__dict__.update( kwargs )
        # after __dict__.update it could have a valid _id 
        if self._id:
            self.item["_id"] = self._id
        self._init_utils(**kwargs)
    
    def _init_utils(self,**kwargs):
        #self.logger.debug('created an instance of %s' % self.__class__.__name__)
        pass
        
    
    def load(self, fields=None, **kwargs):
        #self.logger.debug('load %s %s' % (fields,self.__class__.__name__))
        self.item = self.collection.find_one({'_id': self._id}, **kwargs)
        return self
   
    def save(self, *args, **kwargs):
        #self.logger.debug('save %s' % (self.__class__.__name__))
        self.item["updated"] = datetime.datetime.utcnow()
        self._id = self.collection.save(self.item,*args, **kwargs)
    
    def delete(self):
        self.logger.debug('delete %s %s' % (self.__class__.__name__, self._id))
        self.collection.remove(self._id)
    
    @classmethod
    def delete_all(cls,db):
        collection = db[cls.__name__]
        collection.remove({})
    
    def before_doit(self, parm):
        self.logger.debug("before_doit with parm = " + parm )
        return parm
    
    def after_doit(self, parm, out):
        self.logger.debug("after_doit with parm = %s and out = %s" % (parm,out) )
        return out
    
    def perform_calc(self, parm):
        retVal = {}
        parm = self.before_doit(parm)
        retVal = self.doit(parm)
        retVal = self.after_doit(parm, retVal)
        return retVal
    
    def doit(self, parm):
        out = ""
        self.logger.debug("doit with parm = %s and out = %s" % (parm,out) )
        return out


        
