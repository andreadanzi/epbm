# -*- coding: utf-8 -*-
'''Classe dominio'''
from .base import BaseSmtModel

class Domain(BaseSmtModel):
    '''Classe dominio

    rappresenta un'area rettangolare che contiene tutto o parte del progetto
    struttura di base:
        * code (upprecase string): codice del dominio
        * boundaries (GeoJSON Polygon): definizione dell'area rettangolare
        * bound_wgs (GeoJSON Polygon): boundaries in coordinate WGS per indicizzazione
        * project_id: ID del progetto
        * export_matrix (float list): matrice di trasformazione per l'export M3E
        * import_matrix (float list): matrice di trasformazione per l'import dei risultati M3E
    '''
    pass
