# -*- coding: utf-8 -*-
#import logging, sys
import math
import csv, datetime
import numpy as np
from base import BaseSmtModel, BaseStruct
from utils import *
from smt_stat import get_truncnorm_avg
from building import Building
# danzi.tn@20160310 refactoring per separare calc da setup
# danzi.tn@20160322 clacolati dati _base insieme a 
# danzi.tn@20160407 set samples degli strati ed esempio per l'utilizzo
# danzi.tn@20160410 Merge delle modifiche eseguite da Gabriele su Master Gabriele@2016040 esp critico Burland and Wroth 1974
class Alignment(BaseSmtModel):

    def _init_utils(self, **kwargs):
        self.project = None
        self.strata_samples = None
        self.logger.debug('created an instance of %s' % self.__class__.__name__)

    def setProject(self, projectItem):
        self.project = BaseStruct(projectItem)
    
    # danzi.tn@20160407 set samples degli strati
    def setSamples(self, samples):
        self.strata_samples = samples
        
    def assign_reference_strata(self):
        retVal = "XXX"
        # BaseStruct converte un dizionario in un oggetto la cui classe ha come attributi gli elementi del dizionario
        # per cui se ho d={"a":2,"c":3} con o=BaseStruct(d) => d.a == 2 e d.c == 3
        # a volte ci sono elementi che durante import non hanno recuperato DEM e Stratigrafia, per questo bisogna mettere try
        align = BaseStruct(self.item)
        self.logger.debug("Analisi alla PK %f" % (align.PK))
        try:
            if align.z == align.PH.coordinates[2]:
                ### Verifica strato di riferimento per le PK
                indexes = [idx for idx, strato in enumerate(align.STRATA) if strato.POINTS.top.coordinates[2] > align.z >= strato.POINTS.base.coordinates[2]]
                for idx in indexes:
                    ref_stratus = align.STRATA[idx]
                    pointsDict = self.item["STRATA"][idx]["POINTS"]
                    self.item["REFERENCE_STRATA"] = {"CODE":ref_stratus.CODE,
                                                     "PARAMETERS": ref_stratus.PARAMETERS.__dict__,
                                                     "POINTS": pointsDict}
                    retVal = ref_stratus.CODE
                    self.logger.debug(u"\tstrato di riferimento per %f è %s: %f > %f >= %f ",
                                      align.PK, retVal, ref_stratus.POINTS.top.coordinates[2],
                                      align.z, strato.POINTS.base.coordinates[2])
                ###### CONTINUA QUI
        except AttributeError as ae:
            self.logger.error("Alignment %f , missing attribute [%s]" % (align.PK, ae))
        if "REFERENCE_STRATA" in self.item:
            self.save()
        return retVal

    def assign_buildings(self, buff):
        retVal = "XXX"
        pk = self.item["PK"]
        # danzi.tn@20160315 nuovo criterio di ricerca: ci possono essere più PK per ogni building (tun02, tun04, sim)
        # {"PK_INFO":{"$elemMatch": {"$and":[{"pk_min":{"$lte":2150690}},{"pk_max":{"$gt":2150690}}]}}}
        # aghensi#20160406: rimosso livello pk_array, aggiunto filtro per alignment set per gestire più tracciati
        bcurr = self.db.Building.find({"PK_INFO":{"$elemMatch": {"$and":[{"alignment_set_id":self.item["alignment_set_id"]}, {"pk_min":{"$lte":pk+buff}}, {"pk_max":{"$gt":pk-buff}}]}}})
        building_array = []
        for b in bcurr:
            building_array.append(b)
        if len(building_array) > 0:
            self.item["BUILDINGS"] = building_array
            self.save()
        return retVal

    def assign_parameter(self, bcode, param, val): #vulnerability, damage_class, s_max_ab, beta_max_ab, esp_h_max_ab):
        retVal = 0
        #2129458 94076BC0006_01
        # { "$and":[{"bldg_code":94076BC0006_01},{"vulnerability":{"$lt":vulnerability}} ]}
        bcurr = self.db.Building.find({"$and":[{"bldg_code":bcode}, {param:{"$lte":val}}]})
        for b in bcurr:
            bldg = Building(self.db, b)
            bldg.load()
            bldg.item[param] = val
            bldg.save()
            retVal = retVal + 1

        # { "$and":[{"bldg_code":94076BC0006_01},{"vulnerability":{"$exists":False}} ]}
        bcurr = self.db.Building.find({"$and":[{"bldg_code":bcode}, {param:{"$exists":False}}]})
        for b in bcurr:
            bldg = Building(self.db, b)
            bldg.load()
            bldg.item[param] = val
            bldg.save()
            retVal = retVal + 1
#
#        bcurr = self.db.Building.find({ "$and":[{"bldg_code":bcode},{"damage_class":{"$lt":damage_class}} ]})
#        for b in bcurr:
#            bldg = Building(self.db, b)
#            bldg.load()
#            bldg.item["damage_class"]=damage_class
#            bldg.save()
#            retVal =  retVal + 1
#
#        # { "$and":[{"bldg_code":94076BC0006_01},{"vulnerability":{"$exists":False}} ]}
#        bcurr = self.db.Building.find({ "$and":[{"bldg_code":bcode},{"damage_class":{"$exists":False}} ]})
#        for b in bcurr:
#            bldg = Building(self.db, b)
#            bldg.load()
#            bldg.item["damage_class"]=damage_class
#            bldg.save()
#            retVal =  retVal + 1

        return retVal

    # parametri geomeccanici relativi al cavo, utilizzati sia per il calcolo volume perso lungo
    # lo scudo, che per il calcolo della curva dei cedimenti. I parametri sono:
    # young_tun, nu_tun, phi_tun
    # sono calcolati come media pesata sullo spessore e sulla distanza dello strato dall'asse della
    # galleria; il peso e' dato dallo spessore * coeff_d
    # coeff_d = 2.*r_excav/(max(2.*r_excav, dist) [vale 1 fino a distanze di 2 raggi di scavo e poi
    # va a diminuire]
    # dist = distanza tra il baricentro dello strato considerato e l'asse del tunnel
    # prendo in considerazione tutti gli strati con top superiore a z_tun meno un diametro
    def define_tun_param(self):
        retVal = "XXX"
        align = BaseStruct(self.item)
        r_excav = align.TBM.excav_diameter/2.0
        z_top = align.PH.coordinates[2] + align.SECTIONS.Lining.Offset + r_excav
        z_base = z_top - align.TBM.excav_diameter
        z_tun = align.PH.coordinates[2] + align.SECTIONS.Lining.Offset
        ref_strata = [strato for strato in align.STRATA if strato.POINTS.top.coordinates[2] > z_tun - align.TBM.excav_diameter]
        gamma_wg = 0.
        young_wg = 0.
        nu_wg = 0.
        phi_wg = 0.
        ci_wg = 0.
        wg_tot = 0.
        th_tot = 0.            
        for ref_stratus in ref_strata:
            if ref_stratus.POINTS.top.coordinates[2] > z_base - r_excav:
                z_max = ref_stratus.POINTS.top.coordinates[2]
                z_min = max(z_base - r_excav, ref_stratus.POINTS.base.coordinates[2])
                z_avg = (z_max+z_min)/2.
                dist = abs(z_avg-z_tun)
                th = max(0., z_max-z_min)
                th_tot += th
                wg = th * 2.*r_excav/max(2.*r_excav, dist)
# TODO: ricavare valori nominali/di progetto partendo da minimi e massimi? ripetere i calcoli con minimi, massimi e medi?
                gamma_wg += th * ref_stratus.PARAMETERS.inom
                young_wg += wg * ref_stratus.PARAMETERS.etounnel
                nu_wg += wg * ref_stratus.PARAMETERS.n
                phi_wg += wg * ref_stratus.PARAMETERS.phi_tr
                ci_wg += wg * ref_stratus.PARAMETERS.c_tr
                wg_tot += wg
        gamma_tun = gamma_wg/ th_tot
        young_tun = 1000.*young_wg/wg_tot
        nu_tun = nu_wg/wg_tot
        phi_tun = phi_wg/wg_tot
        ci_tun = ci_wg/wg_tot
        beta_tun = 45.+phi_tun/2.
        self.item["gamma_tun"] = gamma_tun
        self.item["young_tun"] = young_tun
        self.item["nu_tun"] = nu_tun
        self.item["phi_tun"] = phi_tun
        self.item["ci_tun"] = ci_tun
        self.item["beta_tun"] = beta_tun
        self.save()
        return retVal

    def define_face_param(self):
        retVal = "XXX"
        align = BaseStruct(self.item)
        r_excav = align.TBM.excav_diameter/2.0
        z_top = align.PH.coordinates[2] + align.SECTIONS.Lining.Offset + r_excav
        z_base = z_top - align.TBM.excav_diameter
        z_tun = align.PH.coordinates[2] + align.SECTIONS.Lining.Offset
        ref_strata = [strato for strato in align.STRATA if strato.POINTS.top.coordinates[2] > z_tun - align.TBM.excav_diameter]
        # parametri relativi all'estrusione del fronte (k0, modulo di young, coesione e attrito)
        # come media sull'altezza del fronte piu' mezzo raggio sopra e sotto
        gamma_th = 0.
        k0_th = 0.
        young_th = 0.
        phi_th = 0.
        ci_th = 0.
        th = 0.
        for ref_stratus in ref_strata:
            if ref_stratus.POINTS.base.coordinates[2] < z_top + r_excav/2.:
                z_max = min(z_top + r_excav/2., ref_stratus.POINTS.top.coordinates[2])
                z_min = max(z_base - r_excav/2., ref_stratus.POINTS.base.coordinates[2])
                tmp_th = max(0., z_max - z_min)
                th += tmp_th
                gamma_th += tmp_th * ref_stratus.PARAMETERS.inom
                k0_th += tmp_th * ref_stratus.PARAMETERS.k0
                young_th += tmp_th * ref_stratus.PARAMETERS.etounnel
                ci_th += tmp_th * ref_stratus.PARAMETERS.c_tr
                phi_th += tmp_th * ref_stratus.PARAMETERS.phi_tr
        gamma_face = gamma_th /th
        k0_face = k0_th/th
        young_face = 1000.*young_th/th
        ci_face = ci_th/th
        phi_face = phi_th/th
        self.item["gamma_face"] = gamma_face
        self.item["k0_face"] = k0_face
        self.item["young_face"] = young_face
        self.item["phi_face"] = phi_face
        self.item["ci_face"] = ci_face
        self.save()
        return retVal

    def define_buffer(self, buffer_size=1.0):
        buff = 0.
        align = BaseStruct(self.item)
        r_excav = align.TBM.excav_diameter/2.0
        z_tun = align.PH.coordinates[2] + align.SECTIONS.Lining.Offset
        depth_tun = align.DEM.coordinates[2] - z_tun
        beta_tun = align.beta_tun
        k_peck = k_eq(r_excav, depth_tun, beta_tun)
        buff = buffer_size*k_peck*depth_tun
        return buff, k_peck

    def init_dtype_array(self,retVal):
        b_dtype = None
        a_dtype = None
        s_dtype = None
        b_len = 0
        s_len = 0
        a_names = []
        a_formats = []
        b_names = []
        b_formats = []
        s_names = []
        s_formats = []
        for key, val in retVal.iteritems():
            if key not in ["BUILDINGS","SETTLEMENTS"]:
                if isinstance(val, float):
                    a_formats.append('f4')
                    a_names.append(key)
                if isinstance(val, int):
                    a_formats.append('i4')
                    a_names.append(key)
        for idx, b in enumerate(retVal["BUILDINGS"]):
            for key, val in b.iteritems():
                if key not in ["bldg_code"]:
                    if isinstance(val, float):
                        b_formats.append('f4')
                        b_names.append(key)
                    if isinstance(val, int):
                        b_formats.append('i4')
                        b_names.append(key)
            b_dtype = {'names':b_names, 'formats':b_formats}
            b_len = len(retVal["BUILDINGS"])
            break
        for s in retVal["SETTLEMENTS"]:
            s_names.append("%d"% s["code"])
            s_formats.append("f4")
        s_dtype = {'names':s_names, 'formats':s_formats}
        a_dtype = {'names':a_names, 'formats':a_formats}
        return a_dtype, b_dtype, b_len, s_dtype
        
    # danzi.tn@20160409 samples degli strati e di progetto
    def doit(self, parm):
        retVal = {}
        b_len = 0
        s_dtype = s_values = b_dtype = a_dtype = a_values = b_values = None
        updated = datetime.datetime.utcnow()
        retValList = []
        b_list = []
        for i, sample in enumerate(self.strata_samples["items"]):
            retVal = self.doit_sample(parm, sample)
            # per il primo giro definisco la struttura degli array
            if i==0:
                a_dtype, b_dtype, b_len, s_dtype = self.init_dtype_array(retVal)
                # dichiaro le matrici a_values, s_values con tutti i samples degli alignment e relativi settlements
                a_values = np.zeros(len(self.strata_samples["items"]),dtype=a_dtype)
                s_values = np.zeros(len(self.strata_samples["items"]),dtype=s_dtype)
                if b_len > 0:
                    # dichiaro la matrice b_values con tutti i samples dei building
                    b_values = np.zeros((len(self.strata_samples["items"]),b_len,),dtype=b_dtype)
            # assegno ad a_values i valori del campione i-esimo (corrente)
            for key in a_values.dtype.names:
                a_values[i][key] = retVal[key]            
            # per ogni settlement
            for s in retVal["SETTLEMENTS"]:
                s_values[i]["%d" % s["code"]] = s["value"]            
            # se ci sono buildings (non è detto)
            if b_len > 0:
                # per ogni building
                for idx, b in enumerate(retVal["BUILDINGS"]):
                    # assegno a b_values i valori del campione i-esimo (corrente)b
                    for key in b_values.dtype.names:
                        b_values[i][idx][key] = b[key]
        self.item["updated_by"] = "doit"
        # danzi.tn@20160409-end
        # TODO qui sotto bisogna decidere cosa salvare dei samples che stanno in a_values, b_values e s_values
        # per ora con un campione salva il valore nel DB
        if len(self.strata_samples["items"]) == 1:
            self._map_aitems(0,a_values)
            if b_len > 0:
                self._map_bitems(0,b_values, b_len)
            self._map_sitems(0,s_values)
        self.save()

    def _map_aitems(self,i,a_values):
        for key in a_values.dtype.names:
            self.item[key]= float(a_values[i][key])
    
    def _map_bitems(self,i,b_values,b_len):
        for idx in range(b_len):
            for key in b_values.dtype.names:
                self.item["BUILDINGS"][idx][key] = float(b_values[i][idx][key])
    
    def _map_sitems(self,i,s_values):
        sett_list = []
        for key in s_values.dtype.names:
            sett_list.append({"code":int(key),"value":float(s_values[i][key])})
        self.item["SETTLEMENTS"] = sett_list
        
    def doit_sample(self, parm, strata_sample):
        retVal = {"BUILDINGS":[]}
        # BaseStruct converte un dizionario in un oggetto la cui classe ha come attributi gli elementi del dizionario
        # per cui se ho d={"a":2,"c":3} con o=BaseStruct(d) => d.a == 2 e d.c == 3
        # a volte ci sono elementi che durante import non hanno recuperato DEM e Stratigrafia, per questo bisogna mettere try
        align = BaseStruct(self.item)
        r_excav = align.TBM.excav_diameter/2.
        z_tun = align.PH.coordinates[2] + align.SECTIONS.Lining.Offset
        z_top = z_tun + r_excav
        z_base = z_tun - r_excav
        z_dem = align.DEM.coordinates[2]
        self.logger.debug("Analisi alla PK %f" % (align.PK))       
        #try:
        if align.z == align.PH.coordinates[2] and z_dem > z_top:
            ##### Verifica strato di riferimento per le sezioni di riferimento per pressione minima di stabilità
            z_wt = align.FALDA.coordinates[2]
            copertura = align.DEM.coordinates[2] - z_top
            self.logger.debug("\tcopertura = %f, tra pc = %f e asse tunnel = %f, con falda a %f m" % (copertura, align.DEM.coordinates[2], z_tun, z_wt))
            gamma_muck = align.TBM.gamma_muck
            self.logger.debug("\tdiametro di scavo = %f, Raggio interno concio = %f e spessore concio = %f" % (align.TBM.excav_diameter, align.SECTIONS.Lining.Internal_Radius, align.SECTIONS.Lining.Thickness))
            # Seleziona solo gli strati che stanno sopra z_base
            ref_strata = [strato for strato in align.STRATA if strato.POINTS.top.coordinates[2] > z_tun - align.TBM.excav_diameter]
            self.logger.debug("\tgli strati di riferimento sono:")
            fCob = 0.0
            sigma_v = 0.0
            for ref_stratus in ref_strata:
                fCob, sigma_v = self._calc_cob( ref_stratus.CODE,
                                                ref_stratus.POINTS.base.coordinates[2],
                                                ref_stratus.POINTS.top.coordinates[2], 
                                                strata_sample[ref_stratus.CODE].inom, 
                                                strata_sample[ref_stratus.CODE].c_tr, 
                                                strata_sample[ref_stratus.CODE].phi_tr,
                                                z_wt, 
                                                z_tun, 
                                                gamma_muck,
                                                z_base,
                                                z_top,
                                                sigma_v, 
                                                fCob)
            # 20160309@Gabriele Aggiunta valutazione blowup - inizio
            fBlowUp = 0.0
            sigma_v = 0.0
            for ref_stratus in ref_strata:
                if ref_stratus.POINTS.top.coordinates[2] > z_top:
                    z_max = ref_stratus.POINTS.top.coordinates[2]
                    z_min = max(z_top, ref_stratus.POINTS.base.coordinates[2])
                    sigma_v += (z_max-z_min)*strata_sample[ref_stratus.CODE].inom
#
#                for ref_stratus in ref_strata:
#                    # se la base dello strato e' sopra il top del tunnel aggiorno la sigma_v
#                    if ref_stratus.POINTS.base.coordinates[2] >= z_top:
#                        zRef = ref_stratus.POINTS.base.coordinates[2]
#                        sigma_v = cob_step_1(zRef,ref_stratus,sigma_v)
#                    # se la base dello strato e' sotto il top del tunnel e il top dello strato sta sopra il tunnel aggiorno la sigmav
#                    elif ref_stratus.POINTS.top.coordinates[2] > z_top:
#                        zRef = z_top
#                        sigma_v = cob_step_1(zRef,ref_stratus,sigma_v)
            # calcolo il valore complessivo di BLOWUP
            delta_wt = max(0., (z_wt-z_dem)*9.81)
            fBlowUp = blowup(sigma_v, delta_wt, r_excav, gamma_muck, self.project.p_safe_blowup_kpa)
#                self.logger.debug("\tValore di COB (riferito all'asse) =%f e valore di Blowup (riferito all'asse) =%f" % (fCob, fBlowUp))
            # 20160309@Gabriele Aggiunta valutazione blowup - fine

            # CALCOLO VOLUME PERSO
            # configurazione TBM
            cutter_bead_thickness = align.TBM.bead_thickness
            shield_taper = align.TBM.taper
            tail_skin_thickness = align.TBM.tail_skin_thickness
            delta = align.TBM.delta

            # tensione totale come valore a fondo scavo (sigma_v) riportato in asse tunnel (s_v)
            sigma_v = 0.
            for ref_stratus in ref_strata:
                if ref_stratus.POINTS.base.coordinates[2] >= z_base:
                    zRef = ref_stratus.POINTS.base.coordinates[2]
                    sigma_v = cob_step_1(zRef, ref_stratus.POINTS.top.coordinates[2] , strata_sample[ref_stratus.CODE].inom, sigma_v)
                elif ref_stratus.POINTS.top.coordinates[2] > z_base:
                    zRef = z_base
                    sigma_v = cob_step_1(zRef, ref_stratus.POINTS.top.coordinates[2] , strata_sample[ref_stratus.CODE].inom, sigma_v)
            depth_tun = align.DEM.coordinates[2] - z_tun
            depth_base = align.DEM.coordinates[2] - z_base
            s_v = sigma_v / depth_base * depth_tun

            # nel caso di falda sopra dem aggiungo sovraccarico alla s_v
            if z_wt > z_dem:
                s_v += (z_wt-z_dem)*9.81

            # pressione falda in asse tunnel
            p_wt = max(0., (z_wt-z_tun)*9.81)

            gamma_face = align.gamma_face
            k0_face = align.k0_face
            young_face = align.young_face
            ci_face = align.ci_face
            phi_face = align.phi_face
            gamma_tun = align.gamma_tun
            young_tun = align.young_tun
            nu_tun = align.nu_tun
            phi_tun = align.phi_tun
            ci_tun = align.ci_tun
            beta_tun = align.beta_tun

            # calcolo pressione minima secondo tamez
            # p_min_tamez(H, z_wt, gamma_tun, ci_tun, phi_tun_deg, gamma_face, ci_face, phi_face_deg, D, a, req_safety_factor, additional_pressure)
            W = z_dem-align.FALDA.coordinates[2]
            a = align.TBM.shield_length
            tamez_safety_factor = 1.3
            p_tamez = p_min_tamez(copertura, W, gamma_tun, ci_tun, phi_tun, gamma_face, ci_face, phi_face, k0_face, 2*r_excav, a, tamez_safety_factor, self.project.p_safe_cob_kpa, gamma_muck)

            # pressione al fronte,  danzi.tn@20160408 strata_sample["p_tbm"] varia da -30 a +30
            p_max = min(round(align.TBM.pressure_max/10.)*10., round(fBlowUp/10.)*10. -30.+ strata_sample["p_tbm"])
            # forzo la pressione della macchina di massimo 0.5 bar oltre il limite
#                if p_tamez+30. > p_max:
#                    consolidation="front"
#                    consolidation_value = 1.
#                    p_max = min(p_tamez+30., align.TBM.pressure_max+50.)
            consolidation = "none"
            consolidation_value = 0.

            self.logger.debug("\tValore di TAMEZ (riferito all'asse) =%f e valore di Blowup (riferito all'asse) =%f" % (p_tamez, fBlowUp))

            # p_tbm=min(p_max, round(p_tamez/10.)*10., round(fCob/10.)*10., round(fBlowUp/10.)*10.)
#                p_tbm = min(p_max, round(p_tamez/10.)*10.+30.)
            # danzi.tn@20160408 strata_sample["p_tbm"] varia da -30 a +30
            p_tbm = min(p_max, round(fCob/10.)*10.+strata_sample["p_tbm"])
            p_tbm = max(p_tbm, 170.)

            # p_tbm = round(p_wt/10.)*10. + 50.

            p_tbm_base = p_tbm
            p_tbm_shield = max(p_tbm-50., p_wt)
            p_tbm_shield_base = p_tbm_shield
            # calcolo iniziale per greenfield
            gf = gap_front(p_tbm_base, p_wt, s_v, k0_face, young_face, ci_face, phi_face, r_excav)
            # ur_max(sigma_v, p_wt, p_tbm, phi, phi_res, ci, ci_res, psi, young, nu, r_excav)
            ui_shield = .5*2.*ur_max(s_v, p_wt, p_tbm_shield_base, phi_tun, phi_tun, ci_tun, ci_tun, 0., young_tun, nu_tun, r_excav)-gf
            #ui_shield = u_tun(p_tbm_shield_base, p_wt, s_v, nu_tun, young_tun, r_excav)
            # gap_shield(ui, shield_taper, cutter_bead_thickness)
            gs = gap_shield(ui_shield, shield_taper, cutter_bead_thickness)
            ui_tail = max(0., .5*2.*ur_max(s_v, p_wt, p_wt, phi_tun, phi_tun, ci_tun, ci_tun, 0., young_tun, nu_tun, r_excav) - gf - gs)
            #ui_tail = u_tun(0., p_wt, s_v, nu_tun, young_tun, r_excav)
            # gap_tail(ui, tail_skin_thickness, delta)
            gt = gap_tail(ui_tail, tail_skin_thickness, delta, strata_sample["vloss_tail"])
            gap = gf + gs + gt
            eps0_base = volume_loss(gap, r_excav)
            # TODO buffer_size deve essere un parametro di progetto
            buff, k_peck = self.define_buffer( 0.5)

            sensibility_pk = 0.
            damage_class_pk = 0.
            damage_class_pk_base = 0.
            vulnerability_pk = 0.
            vulnerability_pk_base = 0.
            sensibility_vbr_pk = 0.
            vibration_speed_mm_s_pk = 0.
            damage_class_vbr_pk = 0.
            vulnerability_vbr_pk = 0.

#                """
            if "BUILDINGS" in self.item:                    
                for idx, b in enumerate(align.BUILDINGS):
                    building_item = {"bldg_code":b.bldg_code}
                    self.logger.debug("\tAnalisi edificio %s con classe di sensibilita' %s" % (b.bldg_code, b.sc_lev))
                    # leggo l'impronta dell'edificio alla pk analizzata
                    x_min = None
                    x_max = None
                    pk_min = None
                    pk_max = None
                    for pk_item in b.PK_INFO:
                        if pk_item.pk_min <= align.PK +buff and pk_item.pk_max > align.PK-buff:
                            x_min = pk_item.d_min
                            x_max = pk_item.d_max
                            pk_min = pk_item.pk_min
                            pk_max = pk_item.pk_max
                    h_bldg = b.height_overground + b.depth_fondation
                    try:
                        self.logger.debug("\t\timpronta da %fm a %fm e a una profondita' di %fm dal piano di campagna e con un altezza totale di %fm" % (x_min, x_max, b.depth_fondation, h_bldg))
                    except TypeError:
                        self.logger.debug("Dati errati per l'edificio %s" % (b.bldg_code))
                        break
                    # calcolo delta_pk la distanza dell'edificio dalla pk corrente per correggere la distanza
                    # tengo conto anche del passo delle pk per contare fino a meta' di ogni step
                    delta_pk = min(max(0., pk_min-(align.PK+self.project.align_scan_length/2.)), max(0., align.PK-self.project.align_scan_length/2.-pk_max))
                    if delta_pk > 0.:
                        x_min = math.sqrt(x_min**2+delta_pk**2)
                        x_max = math.sqrt(x_max**2+delta_pk**2)
                    #if pk_min <= align.PK + self.project.align_scan_length/2. and pk_max>align.PK-self.project.align_scan_length/2.:


                    # valuto l'incremento di carico dovuto all'edificio come h_bldg * 5.4 kN/m3 + 7.5 kN/m2 (per solaio finale)
                    # a cui tolgo il peso del terreno rimosso per l'approfondimento della fondazione
                    p_soil = 0.
                    for ref_stratus in ref_strata:
                        if ref_stratus.POINTS.top.coordinates[2] > z_dem-b.depth_fondation:
                            z_max = min(z_dem, ref_stratus.POINTS.top.coordinates[2])
                            z_min = max(z_dem-b.depth_fondation, ref_stratus.POINTS.base.coordinates[2])
                            p_soil = (z_max-z_min)*strata_sample[ref_stratus.CODE].inom
                    p_bldg = 5.*h_bldg #+7.5
                    #Gabriele@20160407 Carico boussinesq - inizio
                    qs = max(0., p_bldg-p_soil)
                    Bqs = x_max - x_min
                    x_bou = abs((x_min+x_max)/2.)
                    z_bou = z_dem-b.depth_fondation-z_top
                    extra_load = boussinesq(qs, Bqs, x_bou, z_bou)
                    #Gabriele@20160407 Carico boussinesq - fine
                    s_v_bldg = s_v+extra_load
                    self.logger.debug("\t\textra carico in galleria %f kN/m2" % (extra_load))

                    
                    # primo calcolo di base con p_min
                    # calcolo gap e volume perso
                    VL_base = VolumeLoss(p_tbm_base, p_tbm_shield_base, p_wt, s_v_bldg, \
                                    k0_face, young_face, ci_face, phi_face, \
                                    phi_tun, phi_tun, ci_tun, ci_tun, 0., young_tun, nu_tun, \
                                    r_excav, shield_taper, cutter_bead_thickness, tail_skin_thickness, delta, strata_sample["vloss_tail"])
                    #TODO ripulire le variabili scalari e usare direttamente la classe dove serve
                    gf=VL_base.gf
                    ui_shield = VL_base.ui_shield
                    gs=VL_base.gs
                    ui_tail = VL_base.ui_tail
                    gt=VL_base.gt
                    gap=VL_base.gap
                    eps0_b=VL_base.eps0
                    
                    # ricerca massimi french-way
                    damage_base = DamageParametersFrench(eps0_b, r_excav, depth_tun, nu_tun, beta_tun, x_min, x_max, b.depth_fondation)
                    #TODO ripulive variabili scalari e usare quelle di classe
                    s_max_ab_b = damage_base.s_max
                    beta_max_ab_b = damage_base.beta_max
                    esp_h_max_ab_b = damage_base.esp_h_max
                    vulnerability_class_b = 0.
                    damage_class_b = 0.
                    for dl in b.DAMAGE_LIMITS:
                        if s_max_ab_b <= dl.uz and beta_max_ab_b <= dl.d_uz_dx and esp_h_max_ab_b <= dl.d_ux_dx:
                            vulnerability_class_b = dl.vc_lev
                            damage_class_b = dl.dc_lev
                            break

                    ###Gabriele@20160409 esp critico Burland and Wroth 1974 - inizio , sere file building_damage_class_Burland_Mair.csv?
                    
                    str_type = "M" # TODO leggerlo da info sul building
                    bldg_curr = DamageParametersBurlandWroth(x_min, x_max, str_type, h_bldg, b.depth_fondation)
                    bldg_curr.update_geo(r_excav, depth_tun, beta_tun, nu_tun)
                    bldg_curr.update_stress(eps0_b)
                    building_item["vulnerability_base"] = bldg_curr.eps_crit
                    
                    ###Gabriele@20160409 esp critico Burland and Wroth 1974 - fine
                    
                    building_item["vulnerability_base"] = vulnerability_class_b
                    building_item["damage_class_base"] = damage_class_b
                    building_item["settlement_max_base"] = s_max_ab_b
                    building_item["tilt_max_base"] = beta_max_ab_b
                    building_item["esp_h_max_base"] = esp_h_max_ab_b
                    building_item["k_peck"] = k_peck

                    
                    # assign_vulnerability(self, bcode, param, value):
                    """
                    n_found = self.assign_parameter(b.bldg_code, "vulnerability_base", vulnerability_class_b)
                    n_found = self.assign_parameter(b.bldg_code, "damage_class_base", damage_class_b)
                    n_found = self.assign_parameter(b.bldg_code, "settlement_max_base", s_max_ab_b)
                    n_found = self.assign_parameter(b.bldg_code, "tilt_max_base", beta_max_ab_b)
                    n_found = self.assign_parameter(b.bldg_code, "esp_h_max_base", esp_h_max_ab_b)
                    n_found = self.assign_parameter(b.bldg_code, "k_peck", k_peck)
                    """
                    self.logger.debug("\t\tp_tbm_base = %f, s_max_ab_base = %f, beta_max_ab_base = %f, esp_h_max_ab_base = %f, vul_base = %f" % (p_tbm_base, s_max_ab_b, beta_max_ab_b, esp_h_max_ab_b, vulnerability_class_b))

                    # aggiorno i parametri di base della pk
                    sensibility_pk = max(sensibility_pk, b.sc_lev)
                    damage_class_pk_base = max(damage_class_pk_base, damage_class_b)
                    vulnerability_pk_base = max(vulnerability_pk_base, vulnerability_class_b)
                    # da qui refactor on parameter min vs actual
                    while True:
                        # calcolo gap e volume perso
                        VL = VolumeLoss(p_tbm, p_tbm_shield, p_wt, s_v_bldg, \
                                                k0_face, young_face, ci_face, phi_face, \
                                                phi_tun, phi_tun, ci_tun, ci_tun, 0., young_tun, nu_tun, \
                                                r_excav, shield_taper, cutter_bead_thickness, tail_skin_thickness, delta, strata_sample["vloss_tail"])
                        #TODO ripulire le variabili scalari e usare direttamente la classe dove serve
                        gf=VL.gf
                        ui_shield = VL.ui_shield
                        gs=VL.gs
                        ui_tail = VL.ui_tail
                        gt=VL.gt
                        gap=VL.gap
                        eps0=VL.eps0

                        # ricerca massimi french-way
                        damage = DamageParametersFrench(eps0, r_excav, depth_tun, nu_tun, beta_tun, x_min, x_max, b.depth_fondation)
                        #TODO ripulive variabili scalari e usare quelle di classe
                        s_max_ab = damage.s_max
                        beta_max_ab = damage.beta_max
                        esp_h_max_ab = damage.esp_h_max

                        ###Gabriele@20160409 esp critico Burland and Wroth 1974 - inizio
                        
                        bldg_curr.update_stress(eps0)
                        
                        ###Gabriele@20160409 esp critico Burland and Wroth 1974 - fine
                        
                        vulnerability_class = 0.
                        damage_class = 0.
                        for dl in b.DAMAGE_LIMITS:
                            if s_max_ab <= dl.uz and beta_max_ab <= dl.d_uz_dx and esp_h_max_ab <= dl.d_ux_dx:
                                vulnerability_class = dl.vc_lev
                                damage_class = dl.dc_lev
                                break
                        if vulnerability_class == dl.vc_lev_target:
                            break
                        if p_tbm >= p_max:
                            break
                        else:
                            p_tbm += 10.
                            p_tbm_shield = max(p_tbm-50., p_wt)
                    if vulnerability_class > 2:
                        if consolidation == "none":
                            consolidation = b.bldg_code
                            consolidation_value = 1.
                        else:
                            consolidation += ";" + b.bldg_code

                    building_item["vulnerability"] = vulnerability_class
                    building_item["damage_class"] = damage_class
                    building_item["settlement_max"] = s_max_ab
                    building_item["tilt_max"] = beta_max_ab
                    building_item["esp_h_max"] = esp_h_max_ab
                    
                    ###Gabriele@20160409 esp critico Burland and Wroth 1974 - inizio

                    building_item["eps_crit"] = bldg_curr.eps_crit
                    
                    ###Gabriele@20160409 esp critico Burland and Wroth 1974 - fine
                    """
                    n_found = self.assign_parameter(b.bldg_code, "vulnerability", vulnerability_class)
                    n_found = self.assign_parameter(b.bldg_code, "damage_class", damage_class)
                    n_found = self.assign_parameter(b.bldg_code, "settlement_max", s_max_ab)
                    n_found = self.assign_parameter(b.bldg_code, "tilt_max", beta_max_ab)
                    n_found = self.assign_parameter(b.bldg_code, "esp_h_max", esp_h_max_ab)
                    """

                    # aghensi@20160404 - aggiunto attributi al database ma non so se è giusto
                    
                    building_item["eps_0"] = eps0
                    building_item["p_tbm"] = p_tbm
                    building_item["blowup"] = fBlowUp
                    building_item["tamez"] = p_tamez

                    """
                    n_found = self.assign_parameter(b.bldg_code, "eps_0", eps0)
                    n_found = self.assign_parameter(b.bldg_code, "p_tbm", p_tbm)
                    n_found = self.assign_parameter(b.bldg_code, "blowup", fBlowUp)
                    n_found = self.assign_parameter(b.bldg_code, "tamez", p_tamez)
                    """
                    #Gabriele@20160330 Vibration analysis
                    # danzi.tn@20160408 checks if VIBRATION_LIMITS is available
                    if "VIBRATION_LIMITS" in b.__dict__:
                        if x_min*x_max < 0:
                            distance = copertura-b.depth_fondation
                            if distance < 1.:
                                distance = 1.
                                self.logger.error("Struttura %s in collisione con tunnel alla pk %f" % (b.bldg_code, align.PK))
                        else:
                            ddd = min(abs(x_min), abs(x_max))
                            distance = math.sqrt(ddd**2+(copertura-b.depth_fondation)**2)
                        vibration_speed_mm_s = vibration_speed_Boucliers(distance)
                        vulnerability_class_vibration = 0.
                        damage_class_vibration = 0.
                        for dl in b.VIBRATION_LIMITS:
                            if vibration_speed_mm_s <= dl.mm_s:
                                vulnerability_class_vibration = dl.vc_lev
                                damage_class_vibration = dl.dc_lev
                                break
                        building_item["vulnerability_class_vibration"] = vulnerability_class_vibration
                        building_item["damage_class_vibration"] = damage_class_vibration
                        building_item["vibration_speed_mm_s"] = vibration_speed_mm_s
                        """
                        n_found = self.assign_parameter(b.bldg_code, "vulnerability_class_vibration", vulnerability_class_vibration)
                        n_found = self.assign_parameter(b.bldg_code, "damage_class_vibration", damage_class_vibration)
                        n_found = self.assign_parameter(b.bldg_code, "vibration_speed_mm_s", vibration_speed_mm_s)
                        """
                    retVal["BUILDINGS"].append( building_item )
                    # danzi.tn@20160408 end
                    # fin qui refactor on parameter min vs actual
                    # aggiorno i valori massimi della pk
                    damage_class_pk = max(damage_class_pk, damage_class)
                    vulnerability_pk = max(vulnerability_pk, vulnerability_class)
                    # TODO refactor sc_vbr_lev based on input levels
                    if "sc_vbr_lev" in b.__dict__:
                        sensibility_vbr_pk = max(b.sc_vbr_lev, sensibility_vbr_pk)
                        vibration_speed_mm_s_pk = max(vibration_speed_mm_s, vibration_speed_mm_s_pk)
                        damage_class_vbr_pk = max(damage_class_vibration, damage_class_vbr_pk)
                        vulnerability_vbr_pk = max(vulnerability_class_vibration, vulnerability_vbr_pk)
                    #, damage_class, s_max_ab, beta_max_ab, esp_h_max_ab)
                    # print "%d %d %s" %(n_found, align.PK, b.bldg_code )
                    self.logger.debug("\t\tp_tbm = %f, s_max_ab = %f, beta_max_ab = %f, esp_h_max_ab = %f, vul = %f, eps_0 = %f" % (p_tbm, s_max_ab, beta_max_ab, esp_h_max_ab, vulnerability_class,eps0))

            # calcolo finale per greenfield
            VL_pk = VolumeLoss(p_tbm, p_tbm_shield, p_wt, s_v, \
                            k0_face, young_face, ci_face, phi_face, \
                            phi_tun, phi_tun, ci_tun, ci_tun, 0., young_tun, nu_tun, \
                            r_excav, shield_taper, cutter_bead_thickness, tail_skin_thickness, delta,strata_sample["vloss_tail"])
            #TODO ripulire le variabili scalari e usare direttamente la classe dove serve
            gf=VL_pk.gf
            ui_shield = VL_pk.ui_shield
            gs=VL_pk.gs
            ui_tail = VL_pk.ui_tail
            gt=VL_pk.gt
            gap=VL_pk.gap
            eps0=VL_pk.eps0
            
            # ricerca massimi french-way
            x_min = -2.5*depth_tun
            x_max = - x_min
            # Sulla PK il DamageParametersFrench calcolato a piano campagna/green field =>  z=0.0
            damage_pk = DamageParametersFrench(eps0, r_excav, depth_tun, nu_tun, beta_tun, x_min, x_max, 0.0)                
            
            s_calc = 0.
            sett_list = []
            # qui inizializzo con il SETTLEMENT_MAX
            sett_list.append({"code":0., "value":damage_pk.s_max})
            for fstep in [2., 4., 6., 8., 10., 12., 15., 20., 25., 30., 35., 40., 45., 50., 75.]:
                # qui il calcolo del SETTLEMENT per lo step corrente
                # uz_laganathan(eps0, R, H, nu, beta, x, z)
                s_calc = uz_laganathan(eps0, r_excav, depth_tun, nu_tun, beta_tun, fstep, 0.)
                sett_list.append({"code":fstep, "value": s_calc})

            # Assegno il valore COB alla PK
            # {'col1':('i1',0,'title 1'), 'col2':('f4',1,'title 2')}
            retVal["COB"] = fCob
            retVal["P_TAMEZ"] = p_tamez
            retVal["P_WT"] = p_wt
            # Assegno il valore BLOWUP alla PK
            retVal["BLOWUP"] = fBlowUp
            retVal["P_EPB"] = p_tbm
            retVal["P_EPB_BASE"] = p_tbm_base
            retVal["VOLUME_LOSS"] = eps0
            retVal["VOLUME_LOSS_BASE"] = eps0_base
            retVal["K_PECK"] = k_peck
            retVal["SETTLEMENT_MAX"] = damage_pk.s_max
            retVal["TILT_MAX"] = damage_pk.beta_max
            retVal["EPS_H_MAX"] = damage_pk.esp_h_max
            retVal["SETTLEMENTS"] = sett_list
            if consolidation != "none":
                retVal["CONSOLIDATION"] = consolidation
            retVal["CONSOLIDATION_VALUE"] = consolidation_value
            retVal["SENSIBILITY"] = sensibility_pk
            retVal["DAMAGE_CLASS"] = damage_class_pk
            retVal["VULNERABILITY"] = vulnerability_pk
            retVal["DAMAGE_CLASS_BASE"] = damage_class_pk_base
            retVal["VULNERABILITY_BASE"] = vulnerability_pk_base
            
            retVal["sensibility_vbr_pk"] = sensibility_vbr_pk
            retVal["vibration_speed_mm_s_pk"] = vibration_speed_mm_s_pk
            retVal["damage_class_vbr_pk"] = damage_class_vbr_pk
            retVal["vulnerability_vbr_pk"] = vulnerability_vbr_pk
            
            self.logger.debug("\tAnalisi di volume perso")
            self.logger.debug("\tParametri geomeccanici mediati:")
            self.logger.debug("\t\tTensione totale verticale =%f kPa e pressione falda =%f kPa" % (s_v, p_wt))
            self.logger.debug("\t\tal fronte: k0 =%f, E =%f MPa, phi' = %f °, c' = %f kPa" % (k0_face, young_face/1000., phi_face, ci_face))
            self.logger.debug("\t\tsul cavo: E =%f MPa, nu = %f, phi' = %f °" % (young_tun/1000., nu_tun, phi_tun))
            self.logger.debug("\tValore di gap totale, gap = %f cm" % (gap*100))
            self.logger.debug("\t\t gap al fronte, gf =%f cm; gap sullo scudo, gs= %f cm; gap in coda,gt = %f cm" % (gf*100, gs*100, gt*100))
            self.logger.debug("\tValore di volume perso, VL = %f percent con k di peck = %f" % (eps0*100, k_peck))
            self.logger.debug("\tAnalisi cedimenti")
            self.logger.debug("\t\tCedimento massimo in asse, damage_pk.s_max =%f mm con una pressione al fronte di %fKPa" % (damage_pk.s_max*1000, p_tbm))
            #self.project.p_safe_cob_kpa
            self.logger.debug("\tExtra pressione minima, = %f kPa margine blowup = %f kPa" % (self.project.p_safe_cob_kpa, self.project.p_safe_blowup_kpa))
            self.logger.debug("\tPressiona acqua, = %f kPa, pressione tamex = %f kPa" % (p_wt, p_tamez))

        #except AttributeError as ae:
        #    self.logger.error("Alignment %f , missing attribute [%s]" % (align.PK, ae))
        return retVal

    def _calc_cob(self,code,z_base_ref_stratus,z_top_ref_stratus, inom, c_tr, phi_tr,z_wt, z_tun, gamma_muck,z_base,z_top,sigma_v, fCob):
        fTempCOB = 0
        # se la base dello strato è sotto allora sono sulla base del tunnel
        if z_base_ref_stratus <= z_base:
            sigma_v = cob_step_1(z_base, z_top_ref_stratus , inom, sigma_v)
            fTempCOB = cob_step_2(z_base, phi_tr, c_tr, sigma_v, z_wt, z_tun, gamma_muck, self.project.p_safe_cob_kpa)
            self.logger.debug(u"\t\tstrato di base %s con gamma = %f, c'= %f, phi'= %f e spessore = %f" % (code, inom, c_tr, phi_tr, z_top_ref_stratus-z_base_ref_stratus))
        # se la base dello strato è sotto il top del tunnell allora sono negli strati intermedi
        elif z_base_ref_stratus <= z_top:
            sigma_v = cob_step_1(z_base_ref_stratus, z_top_ref_stratus , inom, sigma_v)
            fTempCOB = cob_step_2(z_base_ref_stratus, phi_tr, c_tr, sigma_v, z_wt, z_tun, gamma_muck, self.project.p_safe_cob_kpa)
            self.logger.debug(u"\t\tstrato intermedio %s con gamma = %f, c'= %f, phi'= %f e spessore = %f" % (code, inom, c_tr, phi_tr, z_top_ref_stratus-z_base_ref_stratus))
        # altrimenti sono sempre sopra
        else:
            sigma_v = cob_step_1(z_base_ref_stratus, z_top_ref_stratus , inom, sigma_v)
            self.logger.debug(u"\t\tstrato superiore %s con gamma = %f, c'= %f, phi'= %f e spessore = %f" % (code, inom, c_tr, phi_tr, z_top_ref_stratus-z_base_ref_stratus))
        # Verifica del massimo
        if fTempCOB > fCob:
            fCob = fTempCOB
        return fCob, sigma_v


    @classmethod
    def aggregate_by_strata(cls, db, domain_id):
        collection = db[cls.__name__]
        pipe = [{"$project" : {"domain_id" : 1,
                               "REFERENCE_STRATA.CODE" : 1,
                               "REFERENCE_STRATA.PARAMETERS.inom" : 1,
                               "REFERENCE_STRATA.PARAMETERS.k0" : 1}},
                {"$match": {"domain_id": domain_id}},
                {"$group": {"_id":"$REFERENCE_STRATA.CODE",
                            "domain_id": {"$addToSet":"$domain_id"},
                            "inom": {"$addToSet":"$REFERENCE_STRATA.PARAMETERS.inom"},
                            "k0": {"$addToSet":"$REFERENCE_STRATA.PARAMETERS.k0"},
                            "total": {"$sum": {"$multiply": ["$REFERENCE_STRATA.PARAMETERS.inom", 10]}},
                            "count": {"$sum": 1}}},
                {"$sort": {"total" : 1, "count": 1}}]
        return collection.aggregate(pipeline=pipe)


    @classmethod
    def export_data_by_pk(cls, db, domain_id, csvPk, csvOut):
        bDone = False
        with open(csvPk, 'rb') as csvfile:
            csv_reader = csv.DictReader(csvfile, delimiter=';')
            csv_list = list(csv_reader)
            pkarray = []
            for row in csv_list:
                pkarray.append(toFloat(row["PK"]))
            if len(pkarray):
                pkOutArray = []
                # PK;Z_TUN;Z_DEM;Z_WT;DESCR_STRATUS;STRATUS TOP;STRATUS BASE;STRATUS_PARAMS....
                header = ["PK", "Z_TUN", "Z_DEM", "Z_WT", "DESCR_STRATUS", "STRATUS_TOP", "STRATUS_BASE"]
                alignments = db[cls.__name__]
                res = alignments.find({"PK":{"$in":pkarray}})
                for re in res:
                    bDone = True
                    align = BaseStruct(re)
                    z_top = align.PH.coordinates[2] + align.SECTIONS.Lining.Offset + align.TBM.excav_diameter/2.0
                    # TODO/FIXME: questa variabile non viene mai usata!
                    z_base = z_top - align.TBM.excav_diameter
                    z_tun = align.PH.coordinates[2] + align.SECTIONS.Lining.Offset
                    for strata in align.STRATA:
                        item = [align.PK, z_tun, align.DEM.coordinates[2], align.FALDA.coordinates[2],
                                strata.CODE, strata.POINTS.top.coordinates[2], strata.POINTS.base.coordinates[2]]
                        dictParam = strata.PARAMETERS.__dict__
                        for key, value in dictParam.iteritems():
                            if key not in header:
                                header.append(key)
                            item.append(value)
                        pkOutArray.append(item)
                with open(csvOut, 'wb') as out_csvfile:
                    writer = csv.writer(out_csvfile, delimiter=";")
                    writer.writerow(header)
                    writer.writerows(pkOutArray)
        return bDone
