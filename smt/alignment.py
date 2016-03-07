# -*- coding: utf-8 -*-
import logging
from base import BaseSmtModel, BaseStruct
import datetime
"""
{
  "_id": ObjectId("56dd5fab2a13da17ac12da86"),
  "updated": ISODate("2016-03-07T11:02:05.766Z"),
  "z": 69.1,
  "created": ISODate("2016-03-07T11:02:03.466Z"),
  "STRATA": [
    {
      "CODE": "R",
      "POINTS": {
        "top": {
          "type": "Point",
          "coordinates": [
            1653523.8,
            8176671.53,
            98.65
          ]
        },
        "base": {
          "type": "Point",
          "coordinates": [
            1653523.8,
            8176671.53,
            97.2
          ]
        }
      },
      "PARAMETERS": {
        "imin": 12,
        "c_dr": 5,
        "etounnel": 20,
        "phi_un": 20,
        "c_un": 15,
        "phi_tr": 30,
        "k0": 0.5,
        "c_tr": 5,
        "imax": 22,
        "inom": 18,
        "phi_dr": 30,
        "n": 0.33,
        "esout": 30,
        "elt": 10
      }
    },
    {
      "CODE": "LP",
      "POINTS": {
        "top": {
          "type": "Point",
          "coordinates": [
            1653523.8,
            8176671.53,
            97.2
          ]
        },
        "base": {
          "type": "Point",
          "coordinates": [
            1653523.8,
            8176671.53,
            95.67
          ]
        }
      },
      "PARAMETERS": {
        "imin": 19,
        "c_dr": 0,
        "etounnel": 120,
        "phi_un": 15,
        "c_un": 40,
        "phi_tr": 25,
        "k0": 0.5,
        "c_tr": 0,
        "imax": 19,
        "inom": 19,
        "phi_dr": 25,
        "n": 0.33,
        "esout": 180,
        "elt": 60
      }
    },
    {
      "CODE": "TB",
      "POINTS": {
        "top": {
          "type": "Point",
          "coordinates": [
            1653523.8,
            8176671.53,
            95.67
          ]
        },
        "base": {
          "type": "Point",
          "coordinates": [
            1653523.8,
            8176671.53,
            90.47
          ]
        }
      },
      "PARAMETERS": {
        "imin": 0,
        "c_dr": 0,
        "etounnel": 0,
        "phi_un": 0,
        "c_un": 0,
        "phi_tr": 0,
        "k0": 0,
        "c_tr": 0,
        "imax": 0,
        "inom": 0,
        "phi_dr": 0,
        "n": 0,
        "esout": 0,
        "elt": 0
      }
    },
    {
      "CODE": "GV",
      "POINTS": {
        "top": {
          "type": "Point",
          "coordinates": [
            1653523.8,
            8176671.53,
            90.47
          ]
        },
        "base": {
          "type": "Point",
          "coordinates": [
            1653523.8,
            8176671.53,
            82.51
          ]
        }
      },
      "PARAMETERS": {
        "imin": 17,
        "c_dr": 20,
        "etounnel": 54,
        "phi_un": 0,
        "c_un": 80,
        "phi_tr": 0,
        "k0": 0.8,
        "c_tr": 80,
        "imax": 20,
        "inom": 19,
        "phi_dr": 15,
        "n": 0.35,
        "esout": 81,
        "elt": 27
      }
    },
    {
      "CODE": "MP",
      "POINTS": {
        "top": {
          "type": "Point",
          "coordinates": [
            1653523.8,
            8176671.53,
            82.51
          ]
        },
        "base": {
          "type": "Point",
          "coordinates": [
            1653523.8,
            8176671.53,
            77.19
          ]
        }
      },
      "PARAMETERS": {
        "imin": 19,
        "c_dr": 30,
        "etounnel": 150,
        "phi_un": 5,
        "c_un": 190,
        "phi_tr": 15,
        "k0": 0.6,
        "c_tr": 110,
        "imax": 21,
        "inom": 20,
        "phi_dr": 25,
        "n": 0.35,
        "esout": 225,
        "elt": 75
      }
    },
    {
      "CODE": "MA",
      "POINTS": {
        "top": {
          "type": "Point",
          "coordinates": [
            1653523.8,
            8176671.53,
            77.19
          ]
        },
        "base": {
          "type": "Point",
          "coordinates": [
            1653523.8,
            8176671.53,
            68.01
          ]
        }
      },
      "PARAMETERS": {
        "imin": 19,
        "c_dr": 25,
        "etounnel": 150,
        "phi_un": 25,
        "c_un": 180,
        "phi_tr": 25,
        "k0": 0.6,
        "c_tr": 100,
        "imax": 21,
        "inom": 20,
        "phi_dr": 25,
        "n": 0.35,
        "esout": 225,
        "elt": 75
      }
    },
    {
      "CODE": "MFL5",
      "POINTS": {
        "top": {
          "type": "Point",
          "coordinates": [
            1653523.8,
            8176671.53,
            68.01
          ]
        },
        "base": {
          "type": "Point",
          "coordinates": [
            1653523.8,
            8176671.53,
            39.01
          ]
        }
      },
      "PARAMETERS": {
        "imin": 17,
        "c_dr": 40,
        "etounnel": 840,
        "phi_un": 10,
        "c_un": 150,
        "phi_tr": 15,
        "k0": 0.6,
        "c_tr": 80,
        "imax": 21,
        "inom": 19,
        "phi_dr": 30,
        "n": 0.3,
        "esout": 1260,
        "elt": 420
      }
    },
    {
      "CODE": "MIG",
      "POINTS": {
        "top": {
          "type": "Point",
          "coordinates": [
            1653523.8,
            8176671.53,
            39.01
          ]
        },
        "base": {
          "type": "Point",
          "coordinates": [
            1653523.8,
            8176671.53,
            37.72
          ]
        }
      },
      "PARAMETERS": {
        "imin": 16,
        "c_dr": 15,
        "etounnel": 60,
        "phi_un": 25,
        "c_un": 45,
        "phi_tr": 25,
        "k0": 0.6,
        "c_tr": 30,
        "imax": 19,
        "inom": 18,
        "phi_dr": 35,
        "n": 0.33,
        "esout": 90,
        "elt": 30
      }
    },
    {
      "CODE": "SO1",
      "POINTS": {
        "top": {
          "type": "Point",
          "coordinates": [
            1653523.8,
            8176671.53,
            37.72
          ]
        },
        "base": {
          "type": "Point",
          "coordinates": [
            1653523.8,
            8176671.53,
            26.79
          ]
        }
      },
      "PARAMETERS": {
        "imin": 15,
        "c_dr": 30,
        "etounnel": 1080,
        "phi_un": 15,
        "c_un": 150,
        "phi_tr": 20,
        "k0": 0.5,
        "c_tr": 75,
        "imax": 22,
        "inom": 19,
        "phi_dr": 30,
        "n": 0.35,
        "esout": 1620,
        "elt": 540
      }
    },
    {
      "CODE": "SB",
      "POINTS": {
        "top": {
          "type": "Point",
          "coordinates": [
            1653523.8,
            8176671.53,
            26.79
          ]
        },
        "base": {
          "type": "Point",
          "coordinates": [
            1653523.8,
            8176671.53,
            22.56
          ]
        }
      },
      "PARAMETERS": {
        "imin": 17,
        "c_dr": 25,
        "etounnel": 128,
        "phi_un": 25,
        "c_un": 80,
        "phi_tr": 30,
        "k0": 0.5,
        "c_tr": 40,
        "imax": 22,
        "inom": 21,
        "phi_dr": 35,
        "n": 0.3,
        "esout": 192,
        "elt": 64
      }
    },
    {
      "CODE": "MC",
      "POINTS": {
        "top": {
          "type": "Point",
          "coordinates": [
            1653523.8,
            8176671.53,
            22.56
          ]
        },
        "base": {
          "type": "Point",
          "coordinates": [
            1653523.8,
            8176671.53,
            9.64
          ]
        }
      },
      "PARAMETERS": {
        "imin": 0,
        "c_dr": 0,
        "etounnel": 0,
        "phi_un": 0,
        "c_un": 0,
        "phi_tr": 0,
        "k0": 0,
        "c_tr": 0,
        "imax": 0,
        "inom": 0,
        "phi_dr": 0,
        "n": 0,
        "esout": 0,
        "elt": 0
      }
    },
    {
      "CODE": "CG",
      "POINTS": {
        "top": {
          "type": "Point",
          "coordinates": [
            1653523.8,
            8176671.53,
            9.64
          ]
        },
        "base": {
          "type": "Point",
          "coordinates": [
            1653523.8,
            8176671.53,
            -4.02
          ]
        }
      },
      "PARAMETERS": {
        "imin": 17,
        "c_dr": 100,
        "etounnel": 1200,
        "phi_un": 40,
        "c_un": 100,
        "phi_tr": 40,
        "k0": 0.5,
        "c_tr": 100,
        "imax": 27,
        "inom": 21,
        "phi_dr": 40,
        "n": 0.2,
        "esout": 1800,
        "elt": 600
      }
    }
  ],
  "Descrizione": "Profilo Progetto",
  "ID": "Profilo Progetto",
  "DEM": {
    "type": "Point",
    "coordinates": [
      1653523.8,
      8176671.53,
      98.65
    ]
  },
  "PK": 2129988,
  "y": 8176671.53,
  "x": 1653523.8,
  "PH": {
    "type": "Point",
    "coordinates": [
      1653523.8,
      8176671.53,
      69.1
    ]
  },
  "domain_id": ObjectId("56dd5fab2a13da17ac12d650")
}
"""        
class Alignment(BaseSmtModel):
        
    def doit (self,parm):
        retVal = "XXX"
        # BaseStruct converte un dizionario in un oggetto la cui classe ha come attributi gli elementi del dizionario
        # per cui se ho d={"a":2,"c":3} con o=BaseStruct(d) => d.a == 2 e d.c == 3
        # a volte ci sono elementi che durante import non hanno recuperato DEM e Stratigrafia, per questo bisogna mettere try
        align = BaseStruct(self.item)
        self.logger.debug("doit on %f<->%s with parm = %s " % (align.PK, self._id, parm) )
        try:
            if align.z == align.PH.coordinates[2]:
                copertura = align.DEM.coordinates[2] - align.PH.coordinates[2]
                self.logger.debug("on %f , copertuta = %f, tra zp = %f e z_dem = %f" % (align.PK, copertura, align.z, align.DEM.coordinates[2]))
                ref_strata = [strato for strato in align.STRATA if strato.POINTS.top.coordinates[2] > align.z >= strato.POINTS.base.coordinates[2]]
                for ref_stratus in ref_strata:
                    self.item["REFERENCE_STRATA"] = {"CODE":ref_stratus.CODE,"PARAMETERS": ref_stratus.PARAMETERS.__dict__ }
                    retVal = ref_stratus.CODE
                    self.logger.debug(u"\tstrato di riferimento è %s " % retVal)    
        except AttributeError as ae:
            self.logger.debug("Alignment %f , missing attribute [%s]" % (align.PK, ae))
        if "REFERENCE_STRATA" in self.item:
            self.item["updated"] = datetime.datetime.utcnow()
            self.save()
        return retVal
    
    @classmethod
    def aggregate_by_strata(cls, db, domain_id):
        collection = db[cls.__name__]
        pipe = [
                    {   
                        "$project" : { 
                                        "domain_id" : 1 ,
                                        "REFERENCE_STRATA.CODE" : 1 , 
                                        "REFERENCE_STRATA.PARAMETERS.inom" : 1 , 
                                        "REFERENCE_STRATA.PARAMETERS.k0" : 1 
                                    } 
                    },
                    {   
                        "$match": { 
                                        "domain_id": domain_id
                                    } 
                    },
                    {
                        "$group" : { 
                                        "_id":"$REFERENCE_STRATA.CODE",
                                        "domain_id":{"$addToSet":"$domain_id"}, 
                                        "inom":{"$addToSet":"$REFERENCE_STRATA.PARAMETERS.inom"}, 
                                        "k0":{"$addToSet":"$REFERENCE_STRATA.PARAMETERS.k0"}, 
                                        "total":{"$sum" :{ "$multiply": ["$REFERENCE_STRATA.PARAMETERS.inom",10]} }, 
                                        "count": { "$sum": 1 } 
                                    } 
                    }, 
                    { 
                        "$sort" : {     
                                        "total" : 1, 
                                        "count": 1 
                                    } 
                    }
                ]
        ret_aggr = collection.aggregate(pipeline=pipe)
        return ret_aggr['result']