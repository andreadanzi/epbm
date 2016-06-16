# -*- coding: utf-8 -*-
"""
Classe che riassume le classi di sensibilità/danno per i vari tipi di elementi
"""
#from minimongo import Index

from base import BaseSmtModel

class ElementClasses(BaseSmtModel):
    '''
    classe che descrive le classi sensibilità/danno elementi

    struttura di base:
        * typology (string): building, overground_infrastructure, underground_infrastructure,
            underground_utility
        * sc_lev (float):
        ...
    '''
    class Meta(object):
        '''definizione Model minimongo'''
        database = 'smt'
        #indexes = (Index('code'))
