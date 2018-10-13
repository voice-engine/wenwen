# -*- coding: utf-8 -*-

"""
Fixed beamforming for 4 mic linear array
"""

import numpy as np

from voice_engine.element import Element


class BF(Element):
    def __init__(self, channels=8, pick=0):
        super(BF, self).__init__()
        self.channels = channels
        self.pick = pick

    def put(self, data):
        data = np.fromstring(data, dtype='int16')
        bf = data[0::self.channels] / 4
        for ch in range(1, 4):
            bf += data[ch::self.channels] / 4 
        super(BF, self).put(bf.tostring())

