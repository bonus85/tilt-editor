#!/usr/bin/env python
"""
@author: Sindre Tosse
"""

from tilt_hack import SketchEditor

if __name__ == '__main__':
    import argparse
    import os
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file_name", type=str, help="Name of file to open")
    parser.add_argument("point_file_name", type=str, help="Name of file to save")
    opts = parser.parse_args() # Parses sys.argv by default
    
    name, ext = os.path.splitext(opts.file_name)
    
    t = SketchEditor.from_sketch_file(opts.file_name)
    
    print "Saving points"
    t.write_points(opts.point_file_name)

