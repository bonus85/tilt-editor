#!/bin/bash

python tilt_hack.py $1
cp template.zip test.zip
zip -0 test.zip data.sketch
python add_tilt_header.py test.zip
mv test.tilt "tilt_files/$2"
rm test.zip
echo "tilt_files/$2 created"

