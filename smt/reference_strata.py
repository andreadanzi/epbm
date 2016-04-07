# -*- coding: utf-8 -*-
import logging
import csv
from base import BaseSmtModel
from base import BaseStruct
from alignment import Alignment
from collections import defaultdict
from utils import toFloat
import datetime

from smt_stat import get_truncnorm, get_triang
# danzi.tn@20160407 sampling degli strati di riferimento
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
            for i, sample in enumerate(i_samples):                
                self.samples.append(BaseStruct({"i":sample,
                                    "e":e_samples[i],
                                    "phi":phi_samples[i],
                                    "c":c_samples[i],
                                    "k0":k0_samples[i],
                                     }))
            self.logger.debug('%s.gen_samples terminated with %d samples' % (self.__class__.__name__ , len(self.samples)))
        else:        
            self.logger.error('%s.gen_samples has an empty item' % self.__class__.__name__)
        return self.samples
    def doit (self,parm):
        pass



