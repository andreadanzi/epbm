# -*- coding: utf-8 -*-
"""
Sezione tipo di galleria

"""
from minimongo import Index

from base import BaseSmtModel

class Section(BaseSmtModel):
    '''
    Sezione tipo galleria

    in questa collection/classe vengono memorizzati gli attributi contenuti nel file IFC
    la struttura di base è
        * 'code': nome del progetto IFC, da impostare come codice della sezione
        * 'project_id': id del progetto smt
        * 'elements': lista degli elementi

    ogni elemento in elements è un dizionario del tipo
        * 'code': codice dell'elemento (attributo Name)
        * 'guid': global ID dell'elemento (utile per l'aggiornamento delle geometrie)
        * più tutte le coppie nomeproprietà:valore che verranno trovate nel file.
    '''
    class Meta(object):
        '''specifica alcune impostazioni per la collection'''
        database = 'smt' #TODO: come lo configuro in modo globale?
        indices = (Index("code"), Index('guid'))

#if __name__ == "__main__":
#    minimongo.configure(host='localhost', database='smt')
#    prova = Section({'code':'aaa', 'elements':[{'code':'1', 'guid':'evflaukbvfiluh'}]}).save
#    print prova.elements[0].code
