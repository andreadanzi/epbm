# -*- coding: utf-8 -*-
'''
Classe TBM
'''
from base import BaseSmtModel
from alignment import Alignment

class TBM(BaseSmtModel):
    '''descrive tutte le TBM ipotizzate per il progetto'''
    REQUIRED_CSV_FIELDS = (
        # TODO: piuttosto che metterle obbligatorie abilito o disabilito calcoli relativi?
        # queste sono da smart_tunneling
        'code', 'manifacturer', 'alignment_set_code', 'pk_start', 'pk_end', 'type', 'dstype',
        'shield_length', 'frontShieldLength', 'frontShieldDiameter', 'tailShieldDiameter',
        'excav_diameter', 'overcut', 'loadPerCutter', 'cutterCount', 'cutterSize', 'cutterSpacing',
        'cutterThickness', 'referenceRpm', 'nominalTorque', 'breakawayTorque', 'backupDragForce',
        'nominalThrustForce', 'auxiliaryThrustForce', 'openingRatio', 'cutterheadThickness',
        # queste sono da smt
        'bead_thickness', 'taper', 'tail_skin_thickness', 'delta', 'gamma_muck', 'pressure_max')


    def assign_to_alignment(self):
        '''associa la TBM agli alignment relativi (tra pk_start e pk_end)

        è possibile che siano associate più di una TBM, viene quindi utilizzata una lista'''
        min_pk, max_pk = sorted((self.item['pk_start'], self.item['pk_end']))
        calign = self.db['Alignment'].find({'alignment_set_id':self.item['alignment_set_id'],
                                            'PK': {'$gte': min_pk, '$lte':max_pk}})
        if len(calign) > 0:
            tbm = self.item
            for curalign in calign:
                align = Alignment(self.db, curalign)
                align.load()
                try:
                    align.item['TBM'] = [x for x in align.item['TBM']
                                         if x['code'] != self.item['code']]
                    align.item['TBM'].append(tbm)
                except TypeError: #anche AttributeError?
                    align.item['TBM'] = [tbm]
                align.save("TBM.assign_to_alignment")
