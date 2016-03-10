# -*- coding: utf-8 -*-
import logging
from base import BaseSmtModel, BaseStruct
from utils import *
import datetime, math
import csv
# danzi.tn@20160310 refactoring per separare calc da setup
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
    
    
    def assign_reference_strata(self):
        retVal = "XXX"
        # BaseStruct converte un dizionario in un oggetto la cui classe ha come attributi gli elementi del dizionario
        # per cui se ho d={"a":2,"c":3} con o=BaseStruct(d) => d.a == 2 e d.c == 3
        # a volte ci sono elementi che durante import non hanno recuperato DEM e Stratigrafia, per questo bisogna mettere try
        align = BaseStruct(self.item)
        self.logger.debug("Analisi alla PK %f" % (align.PK) )
        try:
            if align.z == align.PH.coordinates[2]:
                ### Verifica strato di riferimento per le PK
                indexes = [idx for idx, strato in enumerate(align.STRATA) if strato.POINTS.top.coordinates[2] > align.z >= strato.POINTS.base.coordinates[2]]
                for idx in indexes:
                    ref_stratus = align.STRATA[idx]
                    pointsDict = self.item["STRATA"][idx]["POINTS"]
                    self.item["REFERENCE_STRATA"] = {"CODE":ref_stratus.CODE,"PARAMETERS": ref_stratus.PARAMETERS.__dict__ , "POINTS": pointsDict}
                    retVal = ref_stratus.CODE
                    self.logger.debug(u"\tstrato di riferimento per %f è %s: %f > %f >= %f " % (align.PK, retVal,ref_stratus.POINTS.top.coordinates[2],align.z,strato.POINTS.base.coordinates[2]))
                ###### CONTINUA QUI
        except AttributeError as ae:
            self.logger.error("Alignment %f , missing attribute [%s]" % (align.PK, ae))
        if "REFERENCE_STRATA" in self.item:
            self.save()
        return retVal
    
    def doit (self,parm):
        retVal = "XXX"
        # BaseStruct converte un dizionario in un oggetto la cui classe ha come attributi gli elementi del dizionario
        # per cui se ho d={"a":2,"c":3} con o=BaseStruct(d) => d.a == 2 e d.c == 3
        # a volte ci sono elementi che durante import non hanno recuperato DEM e Stratigrafia, per questo bisogna mettere try
        align = BaseStruct(self.item)
        self.logger.debug("Analisi alla PK %f" % (align.PK) )
        try:
            if align.z == align.PH.coordinates[2]:
                ##### Verifica strato di riferimento per le sezioni di riferimento per pressione minima di stabilità
                z_top = align.PH.coordinates[2] + align.SECTIONS.Lining.Offset + align.TBM.excav_diameter/2.0
                z_base = z_top - align.TBM.excav_diameter
                z_tun = align.PH.coordinates[2] + align.SECTIONS.Lining.Offset
                z_wt = align.FALDA.coordinates[2]
                copertura = align.DEM.coordinates[2] - z_top
                r_excav = align.TBM.excav_diameter/2.
                self.logger.debug("\tcopertuta = %f, tra pc = %f e asse tunnel = %f, con falda a %f m" % (copertura, align.DEM.coordinates[2], z_tun, z_wt))
                gamma_muck = align.TBM.gamma_muck
                self.logger.debug("\tdiametro di scavo = %f, Raggio interno concio = %f e spessore concio = %f" % (align.TBM.excav_diameter, align.SECTIONS.Lining.Internal_Radius, align.SECTIONS.Lining.Thickness))
                # Seleziona solo gli strati che stanno sopra z_base
                ref_strata = [strato for strato in align.STRATA if strato.POINTS.top.coordinates[2] > z_tun - align.TBM.excav_diameter]
                self.logger.debug("\tgli strati di riferimento sono:")
                fCob = 0.0
                sigma_v = 0.0
                for ref_stratus in ref_strata:
                    fTempCOB = 0.0
                    retVal = ref_stratus.CODE
                    # se la base dello strato è sotto allora sono sulla base del tunnel
                    if ref_stratus.POINTS.base.coordinates[2] <= z_base:
                        sigma_v = cob_step_1(z_base,ref_stratus,sigma_v)
                        fTempCOB = cob_step_2(z_base,ref_stratus,sigma_v,z_wt, z_tun, gamma_muck, self.project.p_safe_cob_kpa)
                        self.logger.debug(u"\t\tstrato di base %s con top a %f, base a %f e spessore = %f" % (ref_stratus.CODE, ref_stratus.POINTS.top.coordinates[2], ref_stratus.POINTS.base.coordinates[2], ref_stratus.POINTS.top.coordinates[2]-ref_stratus.POINTS.base.coordinates[2]))
                    # se la base dello strato è sotto il top del tunnell allora sono negli strati intermedi
                    elif ref_stratus.POINTS.base.coordinates[2] <= z_top:
                        sigma_v = cob_step_1(ref_stratus.POINTS.base.coordinates[2],ref_stratus,sigma_v)
                        fTempCOB = cob_step_2(ref_stratus.POINTS.base.coordinates[2],ref_stratus,sigma_v,z_wt, z_tun, gamma_muck, self.project.p_safe_cob_kpa)
                        self.logger.debug(u"\t\tstrato intermedio %s con top a %f, base a %f e spessore = %f" % (ref_stratus.CODE, ref_stratus.POINTS.top.coordinates[2], ref_stratus.POINTS.base.coordinates[2], ref_stratus.POINTS.top.coordinates[2]-ref_stratus.POINTS.base.coordinates[2]))
                    # altrimenti sono sempre sopra
                    else:
                        sigma_v = cob_step_1(ref_stratus.POINTS.base.coordinates[2],ref_stratus,sigma_v)
                        self.logger.debug(u"\t\tstrato superiore %s con top a %f, base a %f e spessore = %f" % (ref_stratus.CODE, ref_stratus.POINTS.top.coordinates[2], ref_stratus.POINTS.base.coordinates[2], ref_stratus.POINTS.top.coordinates[2]-ref_stratus.POINTS.base.coordinates[2]))
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
                    # se la base dello strato e' sotto il top del tunnel e il top dello strato sta sopra il tunnel aggiorno la sigmav
                    elif ref_stratus.POINTS.top.coordinates[2] > z_top:
                        zRef = z_top
                        sigma_v = cob_step_1(zRef,ref_stratus,sigma_v)
                # calcolo il valore complessivo di BLOWUP
                fBlowUp = blowup(sigma_v, align.TBM.excav_diameter/2.0, gamma_muck, self.project.p_safe_blowup_kpa)
                # Assegno il valore BLOWUP alla PK
                self.item["BLOWUP"] = fBlowUp
                self.logger.debug("\tValore di COB (riferito all'asse) =%f e valore di Blowup (riferito all'asse) =%f" % (fCob, fBlowUp))
                # 20160309@Gabriele Aggiunta valutazione blowup - fine
                
                # CALCOLO VOLUME PERSO
                # configurazione TBM
                cutter_bead_thickness = align.TBM.bead_thickness
                shield_taper = align.TBM.taper
                tail_skin_thickness=align.TBM.tail_skin_thickness
                delta=align.TBM.delta
                
                # tensione totale come valore a fondo scavo (sigma_v) riportato in asse tunnel (s_v)
                sigma_v=0.
                for ref_stratus in ref_strata:
                    if ref_stratus.POINTS.base.coordinates[2] >= z_base:
                        zRef = ref_stratus.POINTS.base.coordinates[2]
                        sigma_v = cob_step_1(zRef,ref_stratus,sigma_v)
                    elif ref_stratus.POINTS.top.coordinates[2] > z_base:
                        zRef = z_base
                        sigma_v = cob_step_1(zRef,ref_stratus,sigma_v)
                depth_tun = align.DEM.coordinates[2] - z_tun
                depth_base = align.DEM.coordinates[2] - z_base
                s_v = sigma_v / depth_base * depth_tun
                
                # pressione falda in asse tunnel
                p_wt = max(0., (z_wt-z_tun)*9.81)
                
                # pressione al fronte
                if align.PK == 2128748:
                    p_tbm=400.
                elif align.PK == 2123208:
                    p_tbm=300.
                elif align.PK == 2127608:
                    p_tbm=300.
                elif align.PK == 2124508:
                    p_tbm=400.
                elif align.PK == 2123868:
                    p_tbm=400.
                else:
                    p_tbm=fCob
                
                # parametri relativi all'estrusione del fronte (k0, modulo di young, coesione e attrito)
                # come media sull'altezza del fronte piu' mezzo raggio sopra e sotto
                k0_th = 0.
                young_th = 0.
                phi_th = 0.
                ci_th = 0.
                th = 0.
                for ref_stratus in ref_strata:
                    if ref_stratus.POINTS.base.coordinates[2] < z_top + r_excav/2.:
                        z_max = min(z_top + r_excav/2., ref_stratus.POINTS.top.coordinates[2])
                        z_min = max(z_base - r_excav/2., ref_stratus.POINTS.base.coordinates[2] )
                        tmp_th = z_max - z_min
                        th += tmp_th
                        k0_th += tmp_th * ref_stratus.PARAMETERS.k0
                        young_th += tmp_th * ref_stratus.PARAMETERS.etounnel
                        ci_th += tmp_th * ref_stratus.PARAMETERS.c_tr
                        phi_th += tmp_th * ref_stratus.PARAMETERS.phi_tr
                k0_face = k0_th/th
                young_face = 1000.*young_th/th
                ci_face = ci_th/th
                phi_face = phi_th/th
                
                # parametri geomeccanici relativi al cavo, utilizzati sia per il calcolo volume perso lungo lo scudo, 
                # che per il calcolo della curva dei cedimenti. I parametri sono:
                # young_tun, nu_tun, phi_tun
                # sono calcolati come media pesata sullo spessore e sulla distanza dello strato dall'asse della galleria
                # il peso e' dato dallo spessore * coeff_d
                # coeff_d = 3.*r_excav/(max(3.*r_excav, dist) [vale 1 fino a distanze di 3 raggi di scavo e poi va a diminuire
                # dist = distanza tra il baricentro dello strato considerato e l'asse del tunnel
                # prendo in considerazione tutti gli strati con top superiore a z_tun meno un diametro

                young_wg = 0.
                nu_wg = 0.
                phi_wg = 0.
                wg_tot = 0.
                for ref_stratus in ref_strata:
                    if ref_stratus.POINTS.top.coordinates[2] > z_base - r_excav:
                        z_max = ref_stratus.POINTS.top.coordinates[2]
                        z_min = max(z_base - r_excav, ref_stratus.POINTS.base.coordinates[2] )
                        z_avg = (z_max+z_min)/2.
                        dist = abs(z_avg-z_tun)
                        th = z_max-z_min
                        wg = th * 3.*r_excav/max(3.*r_excav, dist)
                        young_wg += wg * ref_stratus.PARAMETERS.etounnel
                        nu_wg += wg * ref_stratus.PARAMETERS.n
                        phi_wg += wg * ref_stratus.PARAMETERS.phi_tr
                        wg_tot += wg
                young_tun = 1000.*young_wg/wg_tot
                nu_tun = nu_wg/wg_tot
                phi_tun = phi_wg/wg_tot
                # calcolo gap
                # todo modificare il valore della pressione al fronte entro i limiti per soddisfare la classe di danno degli edifici
                gf=gap_front(p_tbm, p_wt, s_v, k0_face, young_face, ci_face, phi_face, r_excav)
                gs=gap_shield(p_tbm, p_wt, s_v, nu_tun, young_tun, r_excav, shield_taper, cutter_bead_thickness)
                #gap_tail(p_tbm, nu, young, r_excav, tail_skin_thickness, delta)
                gt=gap_tail(p_tbm,nu_tun, young_tun, r_excav, tail_skin_thickness, delta)
                gap=gf+gs+gt
                gap_inst=gf+gs
                # calcolo del volume perso
                eps0=volume_loss(gap, r_excav)
                eps0_inst=volume_loss(gap_inst, r_excav)
                self.item["VOLUME_LOSS"] = eps0
                self.logger.debug("\tAnalisi di volume perso")
                self.logger.debug("\tParametri geomeccanici mediati:")
                self.logger.debug("\t\tTensione totale verticale =%f kPa e pressione falda =%f kPa" % (s_v, p_wt))
                self.logger.debug("\t\tal fronte: k0 =%f, E =%f MPa, phi' = %f °, c' = %f kPa" % (k0_face, young_face/1000., phi_face, ci_face))
                self.logger.debug("\t\tsul cavo: E =%f MPa, nu = %f, phi' = %f °" % (young_tun/1000., nu_tun, phi_tun))
                self.logger.debug("\tValore di gap totale, gap = %f cm" % (gap*100))
                self.logger.debug("\t\t gap al fronte, gf =%f cm; gap sullo scudo, gs= %f cm; gap in coda,gt = %f cm" % (gf*100, gs*100, gt*100))
                self.logger.debug("\tValore di volume perso, VL = %f percent" % (eps0*100))
                
                # calcolo cedimento massimo in asse
                beta = math.radians(45.+phi_tun/2.)
                s_max = uz_laganathan(eps0, r_excav, depth_tun, nu_tun, beta, 0., 0.)
                s_inst = uz_laganathan(eps0_inst, r_excav, depth_tun, nu_tun, beta, 0., 0.)
                self.item["SETTLEMENT_MAX"] = s_max
                self.logger.debug("\tAnalisi cedimenti")
                self.logger.debug("\t\tCedimento massimo in asse, s_max =%f mm" % (s_max*1000))
                self.logger.debug("\t\tCedimento istantaneo in asse, s_inst =%f mm" % (s_inst*1000))
                
                
                
                ###### CONTINUA QUI
                s_calc = 0.
                sett_list=[]
                # qui inizializzo con il SETTLEMENT_MAX
                sett_list.append({"code":0., "value":s_max})
                for fstep in [20., 40., 60.]:
                    # qui il calcolo del SETTLEMENT per lo step corrente
                    s_calc = s_calc
                    sett_list.append({"code":fstep,"value": s_calc  })
                self.item["SETTLEMENTS"] = sett_list
        except AttributeError as ae:
            self.logger.error("Alignment %f , missing attribute [%s]" % (align.PK, ae))
        if "SETTLEMENTS" in self.item:
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
