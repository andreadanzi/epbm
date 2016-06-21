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
from smt_stat import get_truncnorm, get_triang, get_truncnorm_avg, assign_standard_strata_samples,assign_custom_strata_samples, assign_base_strata_percentiles
# danzi.tn@20160407 sampling degli strati di riferimento
# danzi.tn@20160408 gestione unica iterazione nSamples = 1
class ReferenceStrata(BaseSmtModel):
    def gen_samples(self,nSamples):
        self.samples = []
        self.logger.debug('%s.gen_samples starts', self.__class__.__name__)
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
            self.logger.debug('%s.gen_samples terminated with %d samples', self.__class__.__name__,
                              len(self.samples))
        else:
            self.logger.error('%s.gen_samples has an empty item', self.__class__.__name__)
        return self.samples


    @classmethod
    def gen_samples_strata(cls, mongodb, nSamples, project_code, type_of_analysis, base_percentile,
                           custom_type_tuple):
        log = logging.getLogger('smt_main')
        log.debug('starting with %s and %s', type_of_analysis, str(custom_type_tuple))
        samples = {"len":nSamples, "type":type_of_analysis, "base_percentile":base_percentile,
                   "custom_type_tuple":custom_type_tuple, "items":[]}
        std_norm_samples = []
        vloss_tail_samples = []
        pd = mongodb.Project.find_one({"project_code":project_code})
        if pd:
            rs_items = mongodb.ReferenceStrata.find({"project_id": pd["_id"]})
            rs_items_list = list(rs_items)
            t_norm = get_truncnorm_avg(0, 10.)
            triVLoss = get_triang(pd["vloss_tail_min"], pd["vloss_tail_mode"], pd["vloss_tail_max"])
            assign_base_strata_percentiles(t_norm, triVLoss, rs_items_list, samples, base_percentile)
            log.debug('gen_samples_strata, assign_base_strata_percentiles terminated')
            if type_of_analysis == 's' and nSamples > 0:
                # restituisce campioni tra vmin = - 30 kPa e vmax = + 30 kPa e con il 99 precentile pari a vmax.
                std_norm_samples = t_norm.rvs(size=nSamples)
                vloss_tail_samples = triVLoss.rvs(size=nSamples)
                for i, vloss_tail_sample in enumerate(vloss_tail_samples):
                    samples["items"].append({"vloss_tail":vloss_tail_sample,
                                             "p_tbm":std_norm_samples[i], "type":None})
                log.debug("before assign_standard_strata_samples - len samples %d",
                          len(samples["items"]))
                assign_standard_strata_samples(rs_items_list, samples, nSamples)
                log.debug('assign_standard_strata_samples terminated')
            elif type_of_analysis == 'c' and len(custom_type_tuple) >= 0:
                vloss_tail_samples = np.full(len(custom_type_tuple), pd["vloss_tail_max"])
                std_norm_samples = np.zeros(len(custom_type_tuple))
                for i, vloss_tail_sample in enumerate(vloss_tail_samples):
                    samples["items"].append({"vloss_tail":vloss_tail_sample,
                                             "p_tbm":std_norm_samples[i],
                                             "type":str(custom_type_tuple[i])})
                assign_custom_strata_samples(rs_items_list, samples, custom_type_tuple)
                log.debug('assign_custom_strata_samples terminated')
        log.debug('terminated with %d samples', len(samples["items"]))
        log.debug(samples["items"])
        return samples
