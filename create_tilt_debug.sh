#!/bin/bash

cp template.zip test.zip

python tilt_hack.py -m move_point 1/data.sketch
zip -0 test.zip data.sketch
python add_tilt_header.py test.zip
mv test.tilt "tilt_files/move_point.tilt"

python tilt_hack.py -m two_points 1/data.sketch
zip -0 test.zip data.sketch
python add_tilt_header.py test.zip
mv test.tilt "tilt_files/two_points.tilt"

python tilt_hack.py -m move_point data.sketch
zip -0 test.zip data.sketch
python add_tilt_header.py test.zip
mv test.tilt "tilt_files/two_points_moved.tilt"

python tilt_hack.py -m three_points 1/data.sketch
zip -0 test.zip data.sketch
python add_tilt_header.py test.zip
mv test.tilt "tilt_files/three_points.tilt"

python tilt_hack.py -m move_point data.sketch
zip -0 test.zip data.sketch
python add_tilt_header.py test.zip
mv test.tilt "tilt_files/three_points_moved.tilt"

python tilt_hack.py -m move_all 1/data.sketch
zip -0 test.zip data.sketch
python add_tilt_header.py test.zip
mv test.tilt "tilt_files/move_all.tilt"

rm test.zip

