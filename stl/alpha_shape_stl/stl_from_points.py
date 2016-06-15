#!/usr/bin/env python
"""
@author: Sindre Tosse
"""
import numpy as np
from stl import mesh

def main(opts):

    vertices = np.genfromtxt('points.dat', delimiter=' ', skip_header=1)
    
    npoints, dim = vertices.shape
    
    assert dim == 3

    faces = np.genfromtxt('indices.dat', delimiter=' ') # Generated from alpha_shape

    # Create the mesh
    cube = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            cube.vectors[i][j] = vertices[f[j],:]
            
    # Write the mesh to file
    cube.save(opts.new_file_name)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Generate an stl file from a list of points')
    #parser.add_argument("point_file_name", type=str, help="Name of file to open")
    #parser.add_argument("indices_file_name", type=str, help="Name of file to open")
    parser.add_argument("new_file_name", type=str, help="Name of file to write")
    opts = parser.parse_args() # Parses sys.argv by default
    main(opts)

