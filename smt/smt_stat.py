# -*- coding: utf-8 -*-
import numpy as np
import logging
from scipy.stats import *
from base import BaseStruct

# funzione che restituisce media e sigma di una gaussiana sulla base di valori minimi e massimi al 99 percentile
def get_sigma(min,max,p=99):
    if min==-1 or max == -1:
        return -1, 0
    avg = np.average([max,min])
    if p==95:
        sigma = (max-avg)/2.0
    else:
        sigma = (max-avg)/3.0
    return avg, sigma


class CNorm:
    mean=0
    def __init__(self, mean):
        self.mean = mean
    
    def ppf(self, perc):
        return self.mean
    
    def rvs(self, size=1):
        if size > 1:
            return np.full(size,self.mean)
        return self.mean

#danzi.tn@20160407 norma troncata sulla base del 99% 
def get_truncnorm(vmin,vmax,name='',p=99.,nIter=1000):
    vmin = float(vmin)
    vmax = float(vmax)
    if vmin < 0 or vmax < 0:
        return CNorm(0.0)
    elif vmin == vmax:
        return CNorm(vmin)
    elif nIter<2:
        return CNorm((vmin+vmax)/2.0)
    elif nIter < 4:
        hixk = [vmin,(vmin+vmax)/2.0,vmax]
        #la distribuzione delle tre opzioni
        hipk = (0.2,0.6,0.2)
        #Custom made discrete distribution for Human Factor - da chiamare con hi[hcustm.rvs()] restituisce S N o F sulla base della distribuzione
        myNorm = rv_discrete(name='bbt_%s' % name, values=(hixk, hipk))
        return myNorm
    else:
        mean , std = get_sigma(vmin,vmax,p)
        if mean == -1: return mean
        lower = vmin
        upper = vmax
        if lower < 0:
            lower = mean - std
            upperupper = mean + std
        a, b = (lower - mean) / std, (upper - mean) / std
        myNorm = truncnorm(a, b, loc=mean, scale=std)
        return myNorm

def get_truncnorm_avg(your_avg, your_sigma, p=99):
    scale = 3.0
    if p == 95:
        scale = 2.0
    lower = your_avg - scale*your_sigma
    upper = your_avg + scale*your_sigma
    a, b = (lower - your_avg) / your_sigma, (upper - your_avg) / your_sigma
    myNorm = truncnorm(a, b, loc=your_avg, scale=your_sigma)
    return myNorm

#danzi.tn@20160407 distribuzione triangolare
def get_triang(minVal,avgVal,maxVal):
    minVal = float(minVal)
    avgVal = float(avgVal)
    maxVal = float(maxVal)
    c = (avgVal-minVal)/(maxVal-minVal)
    loc = minVal
    scale = maxVal-minVal
    return triang(c, loc=loc,scale=scale)

def assign_standard_strata_samples(rs_items,samples,nSamples):
    log = logging.getLogger('smt_main')
    log.debug('assign_standard_strata_samples started with %d samples' % nSamples)
    for rs_item in rs_items:
        rstrata = BaseStruct(rs_item)
        log.debug('assign_standard_strata_samples standard for %s', rstrata.code)
        log.debug('i (%f,%f)' % (rstrata.imin,rstrata.imax))
        i_func = get_truncnorm(rstrata.imin,rstrata.imax,name='i_func',p=99.,nIter=nSamples)
        log.debug('E (%f,%f)' % (rstrata.Emin,rstrata.Emax))
        e_func = get_truncnorm(rstrata.Emin,rstrata.Emax,name='e_func',p=99.,nIter=nSamples)
        log.debug('phi (%f,%f)' % (rstrata.phimin,rstrata.phimax))
        phi_func = get_truncnorm(rstrata.phimin,rstrata.phimax,name='phi_func',p=99.,nIter=nSamples)
        log.debug('c (%f,%f)' % (rstrata.cmin,rstrata.cmax))
        c_func = get_truncnorm(rstrata.cmin,rstrata.cmax,name='c_func',p=99.,nIter=nSamples)
        log.debug('k0 (%f,%f)' % (rstrata.k0min,rstrata.k0max))
        k0_func = get_truncnorm(rstrata.k0min,rstrata.k0max,name='k0_func',p=99.,nIter=nSamples)
        i_samples = i_func.rvs(size=nSamples)
        e_samples = e_func.rvs(size=nSamples)
        phi_samples = phi_func.rvs(size=nSamples)
        c_samples = c_func.rvs(size=nSamples)
        k0_samples = k0_func.rvs(size=nSamples)
        if nSamples > 1:
            for j, sample in enumerate(i_samples):
                samples["items"][j+1][rs_item["code"]]= BaseStruct({"inom":sample, "e": e_samples[j] , "phi_tr" : phi_samples[j], "c_tr" : c_samples[j], "k0" : k0_samples[j] } )
                if j < 10:
                    log.debug('\ti_sample=%f ' % sample)
                    log.debug('\te_sample=%f ' % e_samples[j])
                    log.debug('\tphi_sample=%f ' %  phi_samples[j])
                    log.debug('\tc_sample=%f ' % c_samples[j])
                    log.debug('\tk0_sample=%f ' % k0_samples[j] )
        else:
            samples["items"][1][rs_item["code"]]= BaseStruct({"inom":i_samples, "e": e_samples , "phi_tr" : phi_samples, "c_tr" : c_samples, "k0" : k0_samples })
    return samples

    
def assign_custom_strata_samples(rs_items,samples,custom_type_tuple):
    log = logging.getLogger('smt_main')
    log.debug('assign_custom_strata_samples started')
    for rs_item in rs_items:
        rstrata = BaseStruct(rs_item)
        log.debug('assign_custom_strata_samples custom for %s', rstrata.code)
        for j, a in enumerate(custom_type_tuple):
            i = j+1
            log.debug('\t%s' %str(a))
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
                i_func = get_truncnorm(rstrata.imin,rstrata.imax,name='i_func',p=99.,nIter=1)
                e_func = get_truncnorm(rstrata.Emin,rstrata.Emax,name='e_func',p=99.,nIter=1)
                phi_func = get_truncnorm(rstrata.phimin,rstrata.phimax,name='phi_func',p=99.,nIter=1)
                c_func = get_truncnorm(rstrata.cmin,rstrata.cmax,name='c_func',p=99.,nIter=1)
                k0_func = get_truncnorm(rstrata.k0min,rstrata.k0max,name='k0_func',p=99.,nIter=1)
                i_sample = i_func.ppf(float(a)/100.)
                e_sample =  e_func.ppf(float(a)/100.)
                phi_sample =  phi_func.ppf(float(a)/100.)
                c_sample =  c_func.ppf(float(a)/100.)
                k0_sample =  k0_func.ppf(float(a)/100.)
            samples["items"][i][rs_item["code"]]= BaseStruct({"inom":i_sample, "e": e_sample , "phi_tr" : phi_sample, "c_tr" : c_sample, "k0" : k0_sample })
            log.debug('\t\ti_sample=%f ' % i_sample)
            log.debug('\t\te_sample=%f ' % e_sample)
            log.debug('\t\tphi_sample=%f ' % phi_sample)
            log.debug('\t\tc_sample=%f ' % c_sample)
            log.debug('\t\tk0_sample=%f ' % k0_sample)
    return samples

def assign_base_strata_percentiles(t_norm,triVLoss, rs_items,samples,base_percentile):
    log = logging.getLogger('smt_main')
    std_norm_base_percentile = t_norm.ppf(base_percentile/100.)
    log.debug('gen_samples_strata std_norm_base_percentile(%f) = %f ' % (base_percentile, std_norm_base_percentile))
    vloss_tail_base_percentile = triVLoss.ppf(base_percentile/100.)
    log.debug('gen_samples_strata vloss_tail_base_percentile(%f) = %f ' % (base_percentile, vloss_tail_base_percentile))
    # aggiungo la prima riga in items con i valori calcolati sulla base del percentile di base
    samples["items"].append({"vloss_tail":vloss_tail_base_percentile, "p_tbm":std_norm_base_percentile, "type":None})
    # assegno i valori degli strati calcolati sulla base del percentile di base
    log.debug('assign_base_strata_percentiles started with %f' % base_percentile)
    for rs_item in rs_items:
        rstrata = BaseStruct(rs_item)
        log.debug('assign_base_strata_percentiles for %s', rstrata.code)
        i_func = get_truncnorm(rstrata.imin,rstrata.imax,name='i_func',p=99.,nIter=1)
        e_func = get_truncnorm(rstrata.Emin,rstrata.Emax,name='e_func',p=99.,nIter=1)
        phi_func = get_truncnorm(rstrata.phimin,rstrata.phimax,name='phi_func',p=99.,nIter=1)
        c_func = get_truncnorm(rstrata.cmin,rstrata.cmax,name='c_func',p=99.,nIter=1)
        k0_func = get_truncnorm(rstrata.k0min,rstrata.k0max,name='k0_func',p=99.,nIter=1)
        i_sample = i_func.ppf((1.-base_percentile)/100.)
        e_sample =  e_func.ppf(base_percentile/100.)
        phi_sample =  phi_func.ppf(base_percentile/100.)
        c_sample =  c_func.ppf(base_percentile/100.)
        k0_sample =  k0_func.ppf(base_percentile/100.)
        samples["items"][0][rs_item["code"]]= BaseStruct({"inom":i_sample, "e": e_sample , "phi_tr" : phi_sample, "c_tr" : c_sample, "k0" : k0_sample })
        log.debug('\t\tbase i_sample=%f ' % i_sample)
        log.debug('\t\tbase e_sample=%f ' % e_sample)
        log.debug('\t\tbase phi_sample=%f ' % phi_sample)
        log.debug('\t\tbase c_sample=%f ' % c_sample)
        log.debug('\t\tbase k0_sample=%f ' % k0_sample)
    return samples
    
    
if __name__ == '__main__':
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 1)
    # restituisce la truncnorm calcolata tra minimo e massimo, default è 99%
    rn95 = get_truncnorm(17., 19.,"95trunc",95.)
    rn99 = get_truncnorm(17., 19.,"99trunc")
    # restituisce la funzione di distribuzione triangolare calcolata tra minimo e massimo con moda
    tri = get_triang(12., 26.,28.)
    # genero un array con 1000 valori random calcolati sulla base della truncnorm al 95%
    nSize = 1000
    samples=rn95.rvs(size=nSize)
    min_samples = np.min(samples)
    max_samples = np.max(samples)
    print "%d campioni compreso tra %f e %f" % (nSize,min_samples,max_samples)
    custom_bins = (min_samples,17.4,17.8,18.2,18.6,max_samples)
    # histogram restituisce i bin
    print "############# histogram"
    res = np.histogram(samples, bins =5) # se bins è un intero => crea bin uguali per cui sum=numerosità
    print res[0]
    print "sum=%d" % np.sum(res[0])
    print "array contenente gli estremi dei bin = ", res[1]
    cum=0
    for i, b in enumerate(res[0]):
        cum += b
        print "\tnell'intervallo [%f,%f] ci sono %d elementi, pari al %f percento (cumulato %f)" % (res[1][i],res[1][i+1],b, 100.*b/float(nSize), cum)
    print "##### uso bin custom"
    res = np.histogram(samples, bins=custom_bins) # se bins è un array => crea bin con estremi predefiniti
    print res[0]
    print "sum=%d" % np.sum(res[0])
    print "array contenente gli estremi dei bin = ", res[1]
    cum=0
    for i, b in enumerate(res[0]):
        cum += b
        print "\tnell'intervallo [%f,%f] ci sono %d elementi, pari al %f percento (cumulato %f)" % (res[1][i],res[1][i+1],b, 100.*b/float(nSize), cum)
    # se voglio il valore della funzione nei bins
    res = np.histogram(samples, bins =5, density =True) # se density è True => crea bin contenenti il valore della funzione di densità
    print "### density = True"
    print "valori normalizzati della funzione: ", res[0]
    for i, b in enumerate(res[0]):
        print u"\tnell'intervallo [%f,%f] il valore di normalizzato è %f" % (res[1][i],res[1][i+1],b)
    # Percentile
    print "############# Percentiles"
    percentiles = [5.,10.,15.,20.,50.,95.,99.]
    vals = np.percentile(samples,percentiles)
    for i, val in enumerate(vals):
        print "%f percentile the value is %f" %(percentiles[i], val)
    # Percentili sotto soglia
    print "############# ercentili sotto soglia"
    soglie = [17.2,17.8,18.2,18.6]
    for s in  soglie:
        print u"Sotto %f c'è il %f percento del campione" % (s,percentileofscore(samples,s))
        
    # PLOT
    # valori per asse x
    x = np.linspace(0, 50, 100)
    # per fare un confronto creo la funzione distribuzione gaussiana al 99%
    loc,sigma = get_sigma(17.,19.)
    rv = norm(loc,sigma)
    ax.plot(x, rv.pdf(x), 'r-', lw=2, label='Norma')
    ax.plot(x, tri.pdf(x), 'b-', lw=2, label='Tri')
    # ax.plot(x, rn95.pdf(x), 'k-', lw=2, label='Trunc')
    ax.plot(x, rn99.pdf(x), 'y-', lw=2, label='Trunc')
    ax.hist(samples,5, normed=True, histtype='stepfilled', alpha=0.2)
    ax.legend(loc='best', frameon=False)
    plt.show()
    # 
    fig, ax = plt.subplots()
    func = get_triang(0.09, .095, .1)
    print func.ppf(0.5)
    std_norm_samples = func.rvs(size=1000)
    print min(std_norm_samples)
    print max(std_norm_samples)
    ax.hist(std_norm_samples,nSize/10, normed=True, histtype='stepfilled', alpha=0.2)
    plt.show()