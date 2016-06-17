# -*- coding: utf-8 -*-
"""
Classe che riassume le classi di sensibilità/danno per i vari tipi di elementi
"""
from .base import BaseSmtModel

class ElementClass(BaseSmtModel):
    '''
    classe che descrive le classi sensibilità/danno elementi

    struttura di base:
        * typology (string): building, overground_infrastructure, underground_infrastructure,
            underground_utility
        * sc_lev (float): classe di sensibilità
        * dc_lev (float): classe di danno
        ...
    '''
    pass
