# -*- coding: utf-8 -*-
import numpy as np
from scipy.stats import *

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
    for p in percentiles:
        val = np.percentile(samples,p)
        print "%f percentile the value is %f" %(p, val)
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
    lower = 0.0
    upper = 2.0
    mean = 1.0
    std = 1./3.
    a, b = (lower - mean) / std, (upper - mean) / std
    print a
    print b
    rn99 = truncnorm(a, b, loc=mean, scale=std) 
    rn99 = truncnorm(-3, 3, loc=1,scale=1./3.) 
    fig, ax = plt.subplots()
    samples = rn99.rvs(size=nSize)
    ax.hist(samples,nSize/10, normed=True, histtype='stepfilled', alpha=0.2)
    plt.show()