#!/usr/bin/env python
"""
@author: Sindre Tosse
"""

import numpy as np
from stl import mesh

def main(opts):
    m = mesh.Mesh.from_file(opts.file_name)
    
    if opts.verbose:
        for p0, p1, p2 in zip(m.v0, m.v1, m.v2):
            print p0, p1, p2

    volume, cog, inertia = m.get_mass_properties()
    print("Volume                                  = {0}".format(volume))
    print("Position of the center of gravity (COG) = {0}".format(cog))
    print("bounds: x: [{0}, {1}]".format(m.x.min(), m.x.max()))
    print("        y: [{0}, {1}]".format(m.y.min(), m.y.max()))
    print("        z: [{0}, {1}]".format(m.z.min(), m.z.max()))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Analyze .stl files')
    parser.add_argument("file_name", type=str, help="Name of file to open")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose")
    opts = parser.parse_args() # Parses sys.argv by default
    main(opts)

