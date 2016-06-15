#!/usr/bin/env python
"""
@author: Sindre Tosse
"""

import numpy as np
from stl import mesh

ORIGIN_COORDS = np.array([0.0,10.0,10.0])
TB_BOUNDS = np.array([
    [-10.0, 0.1, -10.0],
    [10.0, 20.0, 10.0]
])
TB_SIZE = TB_BOUNDS[1]-TB_BOUNDS[0]

def main(opts):
    m = mesh.Mesh.from_file(opts.file_name)
    
    if not opts.scale:
        size = np.array([
            m.x.max() - m.x.min(),
            m.y.max() - m.y.min(),
            m.z.max() - m.z.min(),
        ])
        scale = TB_SIZE/size
        print "Scaling by a factor of %f" %min(scale)
        m.points *= min(scale)
    

    volume, cog, inertia = m.get_mass_properties()
    
    if not opts.center:
        middle = np.array([
            .5*(m.x.max() + m.x.min()),
            .5*(m.y.max() + m.y.min()),
            .5*(m.z.max() + m.z.min()),
        ])
        d = ORIGIN_COORDS - middle
        print "Centering object"
        m.x += d[0]
        m.y += d[1]
        m.z += d[2]
            
    m.save(opts.file_name)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Analyze .stl files')
    parser.add_argument("file_name", type=str, help="Name of file to open")
    #parser.add_argument("-v", "--verbose", action="store_true", help="Verbose")
    parser.add_argument("-c", "--center", action="store_true", help="Skip centering")
    parser.add_argument("-s", "--scale", action="store_true", help="Skip scaling")
    opts = parser.parse_args() # Parses sys.argv by default
    main(opts)

