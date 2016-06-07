#!/bin/bash

python tilt_hack.py cube.json
cp template.zip cube.zip
zip -0 cube.zip data.sketch
python add_tilt_header.py cube.zip
echo "cube.tilt created"

