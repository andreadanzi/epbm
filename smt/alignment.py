# -*- coding: utf-8 -*-
import logging
from base import BaseSmtModel, BaseStruct
from utils import *
import datetime, math
import csv
"""
{
  "_id": ObjectId("56deab2e2a13da141c249612"),
  "updated": ISODate("2016-03-08T10:36:40.288Z"),
  "z": 69.1,
  "created": ISODate("2016-03-08T10:36:30.53Z"),
  "STRATA": [
    {
      "CODE": "R",
      "POINTS": {
        "top": {
          "type": "Point",
          "coordinates": [
            1653543.8,
            8176671.63,
            98.73
          ]
        },
        "base": {
          "type": "Point",
          "coordinates": [
            1653543.8,
            8176671.63,
            97.15
          ]
        }
      },
      "PARAMETERS": {
        "imin": 12,
        "c_dr": 5,
        "phi_dr": 30,
        "phi_un": 20,
        "c_tr": 5,
        "c_un": 15,
        "k0": 0.5,
        "etounnel": 20,
        "imax": 22,
        "inom": 18,
        "phi_tr": 30,
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
            1653543.8,
            8176671.63,
            97.15
          ]
        },
        "base": {
          "type": "Point",
          "coordinates": [
            1653543.8,
            8176671.63,
            95.82
          ]
        }
      },
      "PARAMETERS": {
        "imin": 19,
        "c_dr": 0,
        "phi_dr": 25,
        "phi_un": 15,
        "c_tr": 0,
        "c_un": 40,
        "k0": 0.5,
        "etounnel": 120,
        "imax": 19,
        "inom": 19,
        "phi_tr": 25,
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
            1653543.8,
            8176671.63,
            95.82
          ]
        },
        "base": {
          "type": "Point",
          "coordinates": [
            1653543.8,
            8176671.63,
            90.21
          ]
        }
      },
      "PARAMETERS": {
        "imin": 0,
        "c_dr": 0,
        "phi_dr": 0,
        "phi_un": 0,
        "c_tr": 0,
        "c_un": 0,
        "k0": 0,
        "etounnel": 0,
        "imax": 0,
        "inom": 0,
        "phi_tr": 0,
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
            1653543.8,
            8176671.63,
            90.21
          ]
        },
        "base": {
          "type": "Point",
          "coordinates": [
            1653543.8,
            8176671.63,
            82.35
          ]
        }
      },
      "PARAMETERS": {
        "imin": 17,
        "c_dr": 20,
        "phi_dr": 15,
        "phi_un": 0,
        "c_tr": 80,
        "c_un": 80,
        "k0": 0.8,
        "etounnel": 54,
        "imax": 20,
        "inom": 19,
        "phi_tr": 0,
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
            1653543.8,
            8176671.63,
            82.35
          ]
        },
        "base": {
          "type": "Point",
          "coordinates": [
            1653543.8,
            8176671.63,
            77.12
          ]
        }
      },
      "PARAMETERS": {
        "imin": 19,
        "c_dr": 30,
        "phi_dr": 25,
        "phi_un": 5,
        "c_tr": 110,
        "c_un": 190,
        "k0": 0.6,
        "etounnel": 150,
        "imax": 21,
        "inom": 20,
        "phi_tr": 15,
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
            1653543.8,
            8176671.63,
            77.12
          ]
        },
        "base": {
          "type": "Point",
          "coordinates": [
            1653543.8,
            8176671.63,
            67.91
          ]
        }
      },
      "PARAMETERS": {
        "imin": 19,
        "c_dr": 25,
        "phi_dr": 25,
        "phi_un": 25,
        "c_tr": 100,
        "c_un": 180,
        "k0": 0.6,
        "etounnel": 150,
        "imax": 21,
        "inom": 20,
        "phi_tr": 25,
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
            1653543.8,
            8176671.63,
            67.91
          ]
        },
        "base": {
          "type": "Point",
          "coordinates": [
            1653543.8,
            8176671.63,
            38.91
          ]
        }
      },
      "PARAMETERS": {
        "imin": 17,
        "c_dr": 40,
        "phi_dr": 30,
        "phi_un": 10,
        "c_tr": 80,
        "c_un": 150,
        "k0": 0.6,
        "etounnel": 840,
        "imax": 21,
        "inom": 19,
        "phi_tr": 15,
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
            1653543.8,
            8176671.63,
            38.91
          ]
        },
        "base": {
          "type": "Point",
          "coordinates": [
            1653543.8,
            8176671.63,
            37.65
          ]
        }
      },
      "PARAMETERS": {
        "imin": 16,
        "c_dr": 15,
        "phi_dr": 35,
        "phi_un": 25,
        "c_tr": 30,
        "c_un": 45,
        "k0": 0.6,
        "etounnel": 60,
        "imax": 19,
        "inom": 18,
        "phi_tr": 25,
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
            1653543.8,
            8176671.63,
            37.65
          ]
        },
        "base": {
          "type": "Point",
          "coordinates": [
            1653543.8,
            8176671.63,
            26.69
          ]
        }
      },
      "PARAMETERS": {
        "imin": 15,
        "c_dr": 30,
        "phi_dr": 30,
        "phi_un": 15,
        "c_tr": 75,
        "c_un": 150,
        "k0": 0.5,
        "etounnel": 1080,
        "imax": 22,
        "inom": 19,
        "phi_tr": 20,
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
            1653543.8,
            8176671.63,
            26.69
          ]
        },
        "base": {
          "type": "Point",
          "coordinates": [
            1653543.8,
            8176671.63,
            22.46
          ]
        }
      },
      "PARAMETERS": {
        "imin": 17,
        "c_dr": 25,
        "phi_dr": 35,
        "phi_un": 25,
        "c_tr": 40,
        "c_un": 80,
        "k0": 0.5,
        "etounnel": 128,
        "imax": 22,
        "inom": 21,
        "phi_tr": 30,
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
            1653543.8,
            8176671.63,
            22.46
          ]
        },
        "base": {
          "type": "Point",
          "coordinates": [
            1653543.8,
            8176671.63,
            9.54
          ]
        }
      },
      "PARAMETERS": {
        "imin": 14,
        "c_dr": 40,
        "phi_dr": 35,
        "phi_un": 30,
        "c_tr": 120,
        "c_un": 180,
        "k0": 0.5,
        "etounnel": 680,
        "imax": 24,
        "inom": 19,
        "phi_tr": 30,
        "n": 0.35,
        "esout": 1020,
        "elt": 340
      }
    },
    {
      "CODE": "CG",
      "POINTS": {
        "top": {
          "type": "Point",
          "coordinates": [
            1653543.8,
            8176671.63,
            9.54
          ]
        },
        "base": {
          "type": "Point",
          "coordinates": [
            1653543.8,
            8176671.63,
            -4.1
          ]
        }
      },
      "PARAMETERS": {
        "imin": 17,
        "c_dr": 100,
        "phi_dr": 40,
        "phi_un": 40,
        "c_tr": 100,
        "c_un": 100,
        "k0": 0.5,
        "etounnel": 1200,
        "imax": 27,
        "inom": 21,
        "phi_tr": 40,
        "n": 0.2,
        "esout": 1800,
        "elt": 600
      }
    }
  ],
  "Descrizione": "Profilo Progetto",
  "domain_id": ObjectId("56deab2e2a13da141c2492fc"),
  "DEM": {
    "type": "Point",
    "coordinates": [
      1653543.8,
      8176671.63,
      98.73
    ]
  },
  "x": 1653543.8,
  "y": 8176671.63,
  "PK": 2129968,
  "PH": {
    "type": "Point",
    "coordinates": [
      1653543.8,
      8176671.63,
      69.1
    ]
  },
  "SECTIONS": {
    "Excavation": {
      "Radius": 4.9
    },
    "Lining": {
      "Offset": 2.16,
      "Thickness": 0.4,
      "Internal_Radius": 4.35
    }
  },
  "ID": "Profilo Progetto"
}
"""        
class Alignment(BaseSmtModel):
    
    def _init_utils(self,**kwargs):
        self.project = None
        self.logger.debug('created an instance of %s' % self.__class__.__name__)
        
    def setProject(self, projectItem):
        self.project = BaseStruct(projectItem)    
    
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
                ### Verifica strato di riferimento per le PK
                indexes = [idx for idx, strato in enumerate(align.STRATA) if strato.POINTS.top.coordinates[2] > align.z >= strato.POINTS.base.coordinates[2]]
                for idx in indexes:
                    ref_stratus = align.STRATA[idx]
                    pointsDict = self.item["STRATA"][idx]["POINTS"]
                    self.item["REFERENCE_STRATA"] = {"CODE":ref_stratus.CODE,"PARAMETERS": ref_stratus.PARAMETERS.__dict__ , "POINTS": pointsDict}
                    retVal = ref_stratus.CODE
                    self.logger.debug(u"\tstrato di riferimento per %f è %s: %f > %f >= %f " % (align.PK, retVal,ref_stratus.POINTS.top.coordinates[2],align.z,strato.POINTS.base.coordinates[2]))
                ##### Verifica strato di riferimento per le sezioni di riferimento per pressione minima di stabilità
                z_top = align.PH.coordinates[2] + align.SECTIONS.Lining.Offset + align.TBM.excav_diameter/2.0
                z_base = z_top - align.TBM.excav_diameter
                z_tun = align.PH.coordinates[2] + align.SECTIONS.Lining.Offset
                z_wt = align.FALDA.coordinates[2]
                gamma_muck = align.TBM.gamma_muck
                self.logger.debug("on %f , TBM.excav_diameter = %f, Lining.Internal_Radius = %f e Lining.Offset = %f. z_top = %f e z_base = %f" % (align.PK,align.TBM.excav_diameter, align.SECTIONS.Lining.Internal_Radius, align.SECTIONS.Lining.Offset,z_top,z_base))
                # Seleziona solo gli strati che stanno sopra z_base
                ref_strata = [strato for strato in align.STRATA if strato.POINTS.top.coordinates[2] > z_base]
                self.logger.debug(u"\tstrati sopra z_base = %f sono:" % z_base)
                fCob = 0.0
                sigma_v = 0.0
                for ref_stratus in ref_strata:
                    fTempCOB = 0.0
                    retVal = ref_stratus.CODE
                    # se la base dello strato è sotto allora sono sulla base del tunnel
                    if ref_stratus.POINTS.base.coordinates[2] <= z_base:
                        sigma_v = cob_step_1(z_base,ref_stratus,sigma_v)
                        fTempCOB = cob_step_2(z_base,ref_stratus,sigma_v,z_wt, z_tun, gamma_muck, self.project.p_safe_cob_kpa)
                        self.logger.debug(u"\tstrato di riferimento per z_base %f è %s con base a %f. sigma_v = %f, fTempCOB = %f" % (z_base,ref_stratus.CODE, ref_stratus.POINTS.base.coordinates[2],sigma_v,fTempCOB))
                    # se la base dello strato è sotto il top del tunnell allora sono negli strati intermedi
                    elif ref_stratus.POINTS.base.coordinates[2] <= z_top:
                        sigma_v = cob_step_1(ref_stratus.POINTS.base.coordinates[2],ref_stratus,sigma_v)
                        fTempCOB = cob_step_2(ref_stratus.POINTS.base.coordinates[2],ref_stratus,sigma_v,z_wt, z_tun, gamma_muck, self.project.p_safe_cob_kpa)
                        self.logger.debug(u"\tstrato intermedio sotto z_top (%f>) è %s con base a %f. sigma_v = %f, fTempCOB = %f" % (z_top,ref_stratus.CODE, ref_stratus.POINTS.base.coordinates[2],sigma_v,fTempCOB))
                    # altrimenti sono sempre sopra
                    else:
                        sigma_v = cob_step_1(ref_stratus.POINTS.base.coordinates[2],ref_stratus,sigma_v)
                        self.logger.debug(u"\tstrato sopra z_top (%f<) è %s con base a %f. sigma_v = %f, fTempCOB = %f" % (z_top,ref_stratus.CODE, ref_stratus.POINTS.base.coordinates[2],sigma_v,fTempCOB))
                    # Verifica del massimo
                    if fTempCOB > fCob:
                        fCob = fTempCOB
                # Assegno il valore COB alla PK
                self.item["COB"] = fCob
                
                # 20160309@Gabriele Aggiunta valutazione blowup - inizio
                fBlowUp=0.0
                sigma_v = 0.0
                for ref_stratus in ref_strata:
                    # se la base dello strato e' sopra il top del tunnel aggiorno la sigma_v
                    if ref_stratus.POINTS.base.coordinates[2] >= z_top:
                        zRef = ref_stratus.POINTS.base.coordinates[2]
                        sigma_v = cob_step_1(zRef,ref_stratus,sigma_v)
                        self.logger.debug(u"\tstrato di riferimento per z_top %f è %s con base a %f. zRef = %f, sigma_v = %f" % (z_top,ref_stratus.CODE, ref_stratus.POINTS.base.coordinates[2],zRef,sigma_v))
                    # se la base dello strato e' sotto il top del tunnel e il top dello strato sta sopra il tunnel aggiorno la sigmav
                    elif ref_stratus.POINTS.top.coordinates[2] > z_top:
                        zRef = z_top
                        sigma_v = cob_step_1(zRef,ref_stratus,sigma_v)
                        self.logger.debug(u"\tstrato di riferimento per z_top %f è %s con base a %f. zRef = %f, sigma_v = %f" % (z_top,ref_stratus.CODE, ref_stratus.POINTS.base.coordinates[2],zRef,sigma_v))
                # calcolo il valore complessivo di BLOWUP
                fBlowUp = blowup(sigma_v, align.TBM.excav_diameter/2.0, gamma_muck, self.project.p_safe_blowup_kpa)
                # Assegno il valore BLOWUP alla PK
                self.item["BLOWUP"] = fBlowUp
                self.logger.debug("Valore di COB =%f, Valore di Blowup =%f" % (fCob, fBlowUp))
                # 20160309@Gabriele Aggiunta valutazione blowup - fine
                
                # calcolo parametri per volume perso
                # tensione totale come media pesata sullo spessore tra superficie e asse tunnel
                sigma_v=0.
                for ref_stratus in ref_strata:
                    if ref_stratus.POINTS.base.coordinates[2] >= z_tun:
                        zRef = ref_stratus.POINTS.base.coordinates[2]
                        sigma_v = cob_step_1(zRef,ref_stratus,sigma_v)
                    elif ref_stratus.POINTS.top.coordinates[2] > z_tun:
                        zRef = z_tun
                        sigma_v = cob_step_1(zRef,ref_stratus,sigma_v)
                # k0 e modulo di young come media sull'altezza del fronte
                k0_th = 0.
                young_th = 0.
                ci_th = 0.
                phi_th = 0.
                nu_th = 0.
                th = 0.
# inom	imin	imax	elt	esout	etounnel	phi_dr	c_dr	phi_tr	c_tr	phi_un	c_un	k0	n
                for ref_stratus in ref_strata:
                    if ref_stratus.POINTS.base.coordinates[2] < z_top:
                        z_max = min(z_top, ref_stratus.POINTS.top.coordinates[2])
                        z_min = max(z_base, ref_stratus.POINTS.base.coordinates[2] )
                        tmp_th = z_max - z_min
                        th += tmp_th
                        k0_th += tmp_th * ref_stratus.PARAMETERS.k0
                        young_th += tmp_th * ref_stratus.PARAMETERS.etounnel
                        ci_th += tmp_th * ref_stratus.PARAMETERS.c_tr
                        phi_th += tmp_th * ref_stratus.PARAMETERS.phi_tr
                        nu_th += tmp_th * ref_stratus.PARAMETERS.n
                k0_face = k0_th/th
                young_face = young_th/th
                ci_face = ci_th/th
                phi_face = phi_th/th
                nu_face = nu_th/th
                p_wt = max(0., (z_wt-z_tun)*9.81)
                s_v = sigma_v
                r_excav = align.TBM.excav_diameter/2.
                gf=gap_front(fCob, p_wt, s_v, k0_face, young_face, ci_face, phi_face, r_excav)
                shield_taper = align.TBM.taper
                cutter_bead_thickness = align.TBM.bead_thickness
                gs=gap_shield(fCob, p_wt, s_v, nu_face, young_face, r_excav, shield_taper, cutter_bead_thickness)
                tail_skin_thickness=align.TBM.tail_skin_thickness
                delta=align.TBM.delta
                gt=gap_tail(tail_skin_thickness, delta)
                gap=gf+gs+gt
                eps0=volume_loss(gap, r_excav)
                self.item["VOLUME_LOSS"] = eps0
                
                # calcolo parametri per cedimenti
                # nu, phi sono calcolati come media pesata sullo spessore e sulla distanza dello strato dall'asse della galleria
                # il peso e' dato dallo spessore * coeff_d
                # coeff_d = 3.*r_excav/(max(3.*r_excav, dist) [vale 1 fino a distanze di 3 raggi di scavo e poi va a diminuire
                # dist = distanza tra il baricentro dello strato considerato e l'asse del tunnel
                ###### CONTINUA QUI
                for ref_stratus in ref_strata:
                    if ref_stratus.POINTS.base.coordinates[2] >= z_tun:
                        zRef = ref_stratus.POINTS.base.coordinates[2]
                        sigma_v = cob_step_1(zRef,ref_stratus,sigma_v)
                    elif ref_stratus.POINTS.top.coordinates[2] > z_tun:
                        zRef = z_tun
                        sigma_v = cob_step_1(zRef,ref_stratus,sigma_v)
                
                
                
                ###### CONTINUA QUI
        except AttributeError as ae:
            self.logger.error("Alignment %f , missing attribute [%s]" % (align.PK, ae))
        if "REFERENCE_STRATA" in self.item:
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
        return collection.aggregate(pipeline=pipe)

        
    @classmethod
    def export_data_by_pk(cls, db, domain_id, csvPk, csvOut):
        bDone = False
        with open(csvPk, 'rb') as csvfile:
            rows = []
            csv_reader = csv.DictReader(csvfile, delimiter=';')
            csv_list = list(csv_reader)
            pkarray = []
            for row in csv_list:
                pkarray.append(toFloat(row["PK"]))
            if len(pkarray):
                pkOutArray = []
                # PK;Z_TUN;Z_DEM;Z_WT;DESCR_STRATUS;STRATUS TOP;STRATUS BASE;STRATUS_PARAMS....
                header = ["PK","Z_TUN","Z_DEM","Z_WT","DESCR_STRATUS","STRATUS_TOP","STRATUS_BASE"]
                alignments = db[cls.__name__]
                res = alignments.find({"PK":{"$in":pkarray}})
                for re in res:
                    bDone = True
                    align = BaseStruct(re)
                    z_top = align.PH.coordinates[2] + align.SECTIONS.Lining.Offset + align.TBM.excav_diameter/2.0
                    z_base = z_top - align.TBM.excav_diameter
                    z_tun = align.PH.coordinates[2] + align.SECTIONS.Lining.Offset
                    for strata in align.STRATA:
                        item = [align.PK,z_tun,align.DEM.coordinates[2],align.FALDA.coordinates[2],strata.CODE,strata.POINTS.top.coordinates[2],strata.POINTS.base.coordinates[2]]
                        dictParam = strata.PARAMETERS.__dict__
                        for key, value in dictParam.iteritems():
                            if key not in header:
                                header.append(key)
                            item.append(value)                    
                        pkOutArray.append(item)
                with open(csvOut, 'wb') as out_csvfile:
                    writer = csv.writer(out_csvfile,delimiter=";")
                    writer.writerow(header)
                    writer.writerows(pkOutArray)
        return bDone
