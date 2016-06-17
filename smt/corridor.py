# -*- coding: utf-8 -*-
"""
Classe di definizione del tunnel come modellata in Civil3D"""
from base import BaseSmtModel

class Corridor(BaseSmtModel):
    """
    Classe di definizione del tunnel come modellata in Civil3D

    memorizza le informazioni del CSV che esce dal comando
    CORRIDORTOCSV del plugin SWS per Civil3D:
    code;alignment;profile;region;start_station;end_station;cross_section"""
    # TODO: questa classe potrebbe non esistere se collego alignment
    #   tra start_station e end_station con le coss_section ifc in base al CSV
    pass
