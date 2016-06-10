#!/usr/bin/env python
"""
@author: Sindre Tosse
"""

import numpy as np
from stl import mesh

m = mesh.Mesh.from_file('cube.stl')

for p0, p1, p2 in zip(m.v0, m.v1, m.v2):
    print p0, p1, p2



if __name__ == '__main__':
    pass

