# -*- coding: utf-8 -*-
import logging
import csv
from base import BaseSmtModel
from base import BaseStruct
from alignment import Alignment
from collections import defaultdict
from utils import toFloat
import datetime
import numpy as np
from smt_stat import get_truncnorm, get_triang, get_truncnorm_avg
# danzi.tn@20160407 sampling degli strati di riferimento
# danzi.tn@20160408 gestione unica iterazione nSamples = 1
class ReferenceStrata(BaseSmtModel):
    def _init_utils(self,**kwargs):
        self.logger.debug('created an instance of %s' % self.__class__.__name__)
    
    def gen_samples(self,nSamples):
        self.samples = []
        self.logger.debug('%s.gen_samples starts' % self.__class__.__name__)
        if self.item:
            rstrata = BaseStruct(self.item)
            i_func = get_truncnorm(rstrata.imin,rstrata.imax,name='i_func',p=99.,nIter=nSamples)
            e_func = get_truncnorm(rstrata.Emin,rstrata.Emax,name='e_func',p=99.,nIter=nSamples)
            phi_func = get_truncnorm(rstrata.phimin,rstrata.phimax,name='phi_func',p=99.,nIter=nSamples)
            c_func = get_truncnorm(rstrata.cmin,rstrata.cmax,name='c_func',p=99.,nIter=nSamples)
            k0_func = get_truncnorm(rstrata.k0min,rstrata.k0max,name='k0_func',p=99.,nIter=nSamples)
            i_samples = i_func.rvs(size=nSamples)
            e_samples = e_func.rvs(size=nSamples)
            phi_samples = phi_func.rvs(size=nSamples)
            c_samples = c_func.rvs(size=nSamples)
            k0_samples = k0_func.rvs(size=nSamples)
            if nSamples > 1:
                for i, sample in enumerate(i_samples):                
                    self.samples.append(BaseStruct({"inom":sample,
                                        "e":e_samples[i],
                                        "phi_tr":phi_samples[i],
                                        "c_tr":c_samples[i],
                                        "k0":k0_samples[i],
                                         }))
            else:
                self.samples.append(BaseStruct({"inom":i_samples,
                                        "e":e_samples,
                                        "phi_tr":phi_samples,
                                        "c_tr":c_samples,
                                        "k0":k0_samples,
                                         }))
            self.logger.debug('%s.gen_samples terminated with %d samples' % (self.__class__.__name__ , len(self.samples)))
        else:        
            self.logger.error('%s.gen_samples has an empty item' % self.__class__.__name__)
        return self.samples
    def doit (self,parm):
        pass
    
    @classmethod
    def gen_samples_strata(cls,mongodb,nSamples, project_code, type_of_analysis, custom_type_tuple):
        samples = {"len":nSamples, "type":type_of_analysis, "custom_type_tuple":custom_type_tuple, "items":[]}
        std_norm_samples = []
        vloss_tail_samples = []
        pd = mongodb.Project.find_one({"project_code":project_code})
        if pd:
            t_norm = get_truncnorm_avg(0, 10.)
            triVLoss = get_triang(pd["vloss_tail_min"],pd["vloss_tail_mode"],pd["vloss_tail_max"])
            rs_items = mongodb.ReferenceStrata.find({"project_id": pd["_id"]}) 
            if type_of_analysis == 's' and nSamples > 0:
                # restituisce campioni tra vmin = - 30 kPa e vmax = + 30 kPa e con il 99 precentile pari a vmax.
                std_norm_samples = t_norm.rvs(size=nSamples)
                vloss_tail_samples = triVLoss.rvs(size=nSamples)
                for i, vloss_tail_sample in enumerate(vloss_tail_samples):
                    samples["items"].append({"vloss_tail":vloss_tail_sample, "p_tbm":std_norm_samples[i]})
                for rs_item in rs_items:
                    rstrata = BaseStruct(rs_item)
                    i_func = get_truncnorm(rstrata.imin,rstrata.imax,name='i_func',p=99.,nIter=nSamples)
                    e_func = get_truncnorm(rstrata.Emin,rstrata.Emax,name='e_func',p=99.,nIter=nSamples)
                    phi_func = get_truncnorm(rstrata.phimin,rstrata.phimax,name='phi_func',p=99.,nIter=nSamples)
                    c_func = get_truncnorm(rstrata.cmin,rstrata.cmax,name='c_func',p=99.,nIter=nSamples)
                    k0_func = get_truncnorm(rstrata.k0min,rstrata.k0max,name='k0_func',p=99.,nIter=nSamples)
                    i_samples = i_func.rvs(size=nSamples)
                    e_samples = e_func.rvs(size=nSamples)
                    phi_samples = phi_func.rvs(size=nSamples)
                    c_samples = c_func.rvs(size=nSamples)
                    k0_samples = k0_func.rvs(size=nSamples)
                    if nSamples > 1:
                        for i, sample in enumerate(i_samples):
                            samples["items"][i][rs_item["code"]]= BaseStruct({"inom":sample, "e": e_samples[i] , "phi_tr" : phi_samples[i], "c_tr" : c_samples[i], "k0" : k0_samples[i] } )
                    else:
                        samples["items"][0][rs_item["code"]]= BaseStruct({"inom":i_samples, "e": e_samples , "phi_tr" : phi_samples, "c_tr" : c_samples, "k0" : k0_samples })
            elif type_of_analysis == 'c' and len(custom_type_tuple) >= 0:
                vloss_tail_samples = np.full(len(custom_type_tuple),pd["vloss_tail_max"])
                std_norm_samples = np.zeros(len(custom_type_tuple))
                for i, vloss_tail_sample in enumerate(vloss_tail_samples):
                    samples["items"].append({"vloss_tail":vloss_tail_sample, "p_tbm":std_norm_samples[i], "type":str(custom_type_tuple[i])})
                for rs_item in rs_items:
                    rstrata = BaseStruct(rs_item)
                    for i, a in enumerate(custom_type_tuple):
                        if a =='avg':
                            i_sample = np.mean((rstrata.imin,rstrata.imax))
                            e_sample = np.mean((rstrata.Emin,rstrata.Emax))
                            phi_sample = np.mean((rstrata.phimin,rstrata.phimax))
                            c_sample = np.mean((rstrata.cmin,rstrata.cmax))
                            k0_sample = np.mean((rstrata.k0min,rstrata.k0max))
                        elif a == 'max':
                            i_sample = np.max((rstrata.imin,rstrata.imax))
                            e_sample = np.max((rstrata.Emin,rstrata.Emax))
                            phi_sample = np.max((rstrata.phimin,rstrata.phimax))
                            c_sample = np.max((rstrata.cmin,rstrata.cmax))
                            k0_sample = np.max((rstrata.k0min,rstrata.k0max))
                        elif a == 'min':
                            i_sample = np.min((rstrata.imin,rstrata.imax))
                            e_sample = np.min((rstrata.Emin,rstrata.Emax))
                            phi_sample = np.min((rstrata.phimin,rstrata.phimax))
                            c_sample = np.min((rstrata.cmin,rstrata.cmax))
                            k0_sample = np.min((rstrata.k0min,rstrata.k0max))
                        else:
                            rstrata = BaseStruct(rs_item)
                            i_func = get_truncnorm(rstrata.imin,rstrata.imax,name='i_func')
                            e_func = get_truncnorm(rstrata.Emin,rstrata.Emax,name='e_func')
                            phi_func = get_truncnorm(rstrata.phimin,rstrata.phimax,name='phi_func')
                            c_func = get_truncnorm(rstrata.cmin,rstrata.cmax,name='c_func')
                            k0_func = get_truncnorm(rstrata.k0min,rstrata.k0max,name='k0_func')
                            i_sample = i_func.ppf(float(a))
                            e_sample =  e_func.ppf(float(a))
                            phi_sample =  phi_func.ppf(float(a))
                            c_sample =  c_func.ppf(float(a))
                            k0_sample =  k0_func.ppf(float(a))
                        samples["items"][i][rs_item["code"]]= BaseStruct({"inom":i_sample, "e": e_sample , "phi_tr" : phi_sample, "c_tr" : c_sample, "k0" : k0_sample })
        return samples
        
    def doit (self,parm):
        pass

