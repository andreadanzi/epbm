# -*- coding: utf-8 -*-
import logging
import csv
import os
import datetime
from utils import toFloat
from minimongo import Model

# aghensi@20160613 passaggio a minimongo (load, save e delete sono a carico di minimongo)

#class BaseStruct(object):
#    def __init__(self, d):
#        for a, b in d.iteritems():
#            if isinstance(b, (list, tuple)):
#                setattr(self, a, [BaseStruct(x) if isinstance(x, dict) else x for x in b])
#            else:
#                setattr(self, a, BaseStruct(b) if isinstance(b, dict) else b)


class BaseSmtModel(Model):
    @classmethod
    def ImportFromCSVFile(cls, csvFilePath, db, delete_existing=True):
        if not os.path.exists(csvFilePath):
            cls.logger.warn('cannot find file %s', csvFilePath)
            return
        with open(csvFilePath, 'rb') as csvfile:
            csv_reader = csv.DictReader(csvfile, delimiter=';')
            if delete_existing:
                cls.collection.remove({})
            for row in csv_reader:
                for key, value in row.iteritems():
                    # HACK: bldg_code deve restare stringa - oppure uso sempre toFloat?
                    if key != "bldg_code":
                        row[key] = toFloat(value)
                row["created"] = datetime.datetime.utcnow()
                row["updated"] = datetime.datetime.utcnow()
                cls(row).save()


    def delete_all(self):
        self.collection.remove({})


    def __init__(self, **kwargs):
        super(BaseSmtModel, self).__init__(**kwargs)
        self.logger = logging.getLogger('smt_main.' + self.__class__.__name__)


    def _init_utils(self, **kwargs):
        #self.logger.debug('created an instance of %s' % self.__class__.__name__)
        pass


    def before_doit(self, parm):
        self.logger.debug("before_doit with parm = " + parm)
        return parm


    def after_doit(self, parm, out):
        self.logger.debug("after_doit with parm = %s and out = %s", parm, out)
        return out


    def perform_calc(self, parm):
        retVal = {}
        parm = self.before_doit(parm)
        retVal = self.doit(parm)
        retVal = self.after_doit(parm, retVal)
        return retVal


    def doit(self, parm):
        out = ""
        self.logger.debug("doit with parm = %s and out = %s", parm, out)
        return out
