#!/usr/bin/env python
"""
@author: Sindre Tosse
"""

TILT_HEADER = 'tilT\x10\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00'

def main(opts):
    with open(opts.file_name) as f:
        raw_file = f.read()
    new_name = opts.file_name.replace('.zip', '.tilt')
    with open(new_name, 'w') as f:
        f.write(TILT_HEADER)
        f.write(raw_file)
    

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Convert .zip to .tilt (add header)')
    parser.add_argument("file_name", type=str, help="Name of file to open")
    opts = parser.parse_args() # Parses sys.argv by default
    main(opts)

