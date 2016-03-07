# -*- coding: utf-8 -*-
import logging
from base import BaseSmtModel
        
class Alignment(BaseSmtModel):
        
    def doit (self,parm):
        dem = None
        ph = None
        # quota z == ph["coordinates"][2]
        z = self.item["z"]
        pk = self.item["PK"]
        self.logger.debug("doit on %f<->%s with parm = %s " % (pk, self._id, parm) )
        """ elemento DEM
        {
             "type": "Point",
             "coordinates": [
               1653573.8,
               8176671.77,
               98.87 
            ] 
        }
        """
        if "DEM" in self.item:
            dem = self.item["DEM"]
        else:
            self.logger.debug("Alignment %f without DEM" % pk)
        """ elemento PH
        {
             "type": "Point",
             "coordinates": [
               1653573.8,
               8176671.77,
               69.1 
            ] 
        }
        """
        if "PH" in self.item:
            ph = self.item["PH"]
            if z == ph["coordinates"][2]:
                self.logger.debug("on %f , z is ok %s" % (pk, parm))
        else:
            self.logger.debug("Alignment %f without PH" % pk)

    