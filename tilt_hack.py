#!/usr/bin/env python
"""
Analyze and edit .sketch files (internal in .tilt)
Also supports generating .sketch files from json

@author: Sindre Tosse
"""
import struct
import json
import pdb
import math
import numpy as np

END = '' # Struct format

ORDERS_OF_TWO = [2**i for i in range(32)]
MAX_BYTE_VALUE = ORDERS_OF_TWO[-1] - 1        

def bits(byte, max_order=32):
    assert byte <= MAX_BYTE_VALUE
    return [min(byte&oot, 1) for oot in ORDERS_OF_TWO[:max_order]]
    
MAX_DV = 0.5 # Max length (x,y,z) between two points (from_json)

class SketchEditor:

    STROKE_EXTENSION_ENCODING = {
        0: 'I', #  uint32 flags
    }

    POINT_EXTENSION_ENCODING = {
        0: 'f', #  float stroke pressure
        1: 'I', #  uint32 timestamp (ms)
    }

    def __init__(self, sentinel=-982080051, version=5, expected_brush_strokes=None):
        self.sentinel = sentinel
        self.version = version
        self.expected_brush_strokes = expected_brush_strokes
        self.strokes = []
    
    @classmethod
    def from_sketch_file(cls, file_name):
        with open(file_name, 'rb') as f:
            header_bytes = f.read(16)
            sentinel, version, reserved, extra_size = \
                struct.unpack(END+'iiii', header_bytes)
            assert reserved == 0, \
                '.sketch header reserved bytes are not zero: %d' %reserved
            if extra_size > 0:
                additional_header_data = f.read(extra_size)
                print 'Warning: Additional header data present (skipping):'
                print '    %r' %additional_header_data
                
            num_strokes_bytes = f.read(4)
            num_strokes = struct.unpack(END+'i', num_strokes_bytes)[0]
        
            instance = SketchEditor(sentinel, version , num_strokes)
        
            for i in range(num_strokes):
                stroke_header = f.read(32)
                #print repr(stroke_header), len(stroke_header)
                idx, r, g, b, a, brush_size, stroke_extension, point_extension = \
                    struct.unpack(END+'ifffffII', stroke_header)
                    
                # int32/float32 for each set bit in stroke_extension & ffff
                stroke_extension_mask = bits(stroke_extension & 0xffff, 16)
                stroke_extension_data = {}
                for i, bit in enumerate(stroke_extension_mask):
                    if bit:
                        fmt = SketchEditor.STROKE_EXTENSION_ENCODING.get(i, 'cccc') 
                        stroke_extension_data[i] = struct.unpack(END+fmt, f.read(4))[0]
                
                # uint32 size + <size> for each set bit in stroke_extension & ~ffff
                stroke_extension_mask_extra = bits(stroke_extension & ~0xffff, 16)
                stroke_extension_data_extra = {}
                for i, bit in enumerate(stroke_extension_mask_extra):
                    if bit:
                        size = struct.unpack(END+'I', f.read(4))[0]
                        stroke_extension_data_extra[i] = f.read(size)
                        
                num_points = struct.unpack(END+'i', f.read(4))[0]
                point_extension_mask = bits(point_extension & 0xffff)
                stroke = Stroke(
                    (r, g, b, a),
                    brush_size,
                    brush_index=idx,
                    stroke_extension_mask=stroke_extension_mask,
                    stroke_extension_data=stroke_extension_data,
                    stroke_extension_mask_extra=stroke_extension_mask_extra,
                    stroke_extension_data_extra=stroke_extension_data_extra,
                    point_extension_mask=point_extension_mask,
                    expected_points=num_points
                )
                
                for j in range(num_points):
                    point_data = f.read(28)
                    x, y, z, or1, or2, or3, or4 = \
                        struct.unpack(END+'fffffff', point_data) # position and orientation
                    # int32/float32 for each set bit in point_extension
                    point_extension_data = {}
                    for i, bit in enumerate(point_extension_mask):
                        if bit:
                            fmt = SketchEditor.POINT_EXTENSION_ENCODING.get(i, 'cccc')
                            point_extension_data[i] = struct.unpack(END+fmt, f.read(4))[0]
                    point = StrokePoint(
                        stroke,
                        (x, y, z),
                        (or1, or2, or3, or4),
                        point_extension_data
                    )
                    stroke.add(point)
                instance.add_stroke(stroke)
            assert f.read() == '',\
                'Error: file did not match format specification (incorrect length)'
        return instance
    
    @classmethod
    def from_json(cls, file_name):
        with open(file_name) as f:
            json_sketch = json.load(f)
        instance = SketchEditor()
        for stroke_spec in json_sketch['strokes']:
            stroke = Stroke(tuple(stroke_spec['color']), stroke_spec['brush_size'])
            positions = np.array(stroke_spec['points'], dtype=float)
            prev_pos = np.roll(positions, 1, 0)
            prev_pos[0][0] = np.nan
            for prev, position in zip(prev_pos, positions):
                if not np.isnan(prev[0]):
                    dv = MAX_DV * (position-prev) / np.linalg.norm(position-prev)
                    print prev, position, dv
                    while np.linalg.norm(position-prev) > MAX_DV:
                        prev += dv
                        #print prev
                        stroke.add(StrokePoint(stroke, tuple(prev)))
                #print position
                stroke.add(StrokePoint(stroke, tuple(position)))
            instance.add_stroke(stroke)
        return instance
    
    def add_stroke(self, stroke):
        self.strokes.append(stroke)
        
    def write(self, file_name):
        with open(file_name, 'wb') as f:
            f.write(struct.pack(END+'iiiii',
                self.sentinel, self.version, 0, 0, len(self.strokes)))
            for stroke in self.strokes:
                f.write(stroke.pack())
    
    def info(self):
        print 'Sentinel: %d' %self.sentinel
        print 'Version: %d' %self.version
        print 'Brush strokes: %s expected, %d actual' %(
            self.expected_brush_strokes, len(self.strokes))

Z16 = [0 for i in range(16)]
Z32 = [0 for i in range(32)]

class Stroke:
    
    def __init__(
                self,
                (r, g, b, a),
                brush_size,
                brush_index=0,
                stroke_extension_mask=Z16,
                stroke_extension_data=None,
                stroke_extension_mask_extra=Z16,
                stroke_extension_data_extra=None,
                point_extension_mask=Z32,
                expected_points=None
            ):
        self.r = r
        self.g = g
        self.b = b
        self.a = a
        self.brush_size = brush_size
        self.brush_index = brush_index
        
        self.stroke_extension_mask = stroke_extension_mask
        self.stroke_extension_mask_extra = stroke_extension_mask_extra
        self.point_extension_mask = point_extension_mask
        
        self.stroke_extension_data = stroke_extension_data
        self.stroke_extension_data_extra = stroke_extension_data_extra
        
        self.expected_stroke_points = expected_points
        self.points = []
    
    def pack(self):
        stroke_extension = sum(b * oot for b, oot in 
            zip(self.stroke_extension_mask, ORDERS_OF_TWO[:16]))
        stroke_extension += sum(b * oot for b, oot in 
            zip(self.stroke_extension_mask_extra, ORDERS_OF_TWO[16:]))
        point_extension = sum(b * oot for b, oot in 
            zip(self.point_extension_mask, ORDERS_OF_TWO))
        s = struct.pack(END+'ifffffII',
            self.brush_index, self.r, self.g, self.b, self.a,
            self.brush_size, stroke_extension, point_extension)
        for i, bit in enumerate(self.stroke_extension_mask):
            if bit:
                fmt = SketchEditor.STROKE_EXTENSION_ENCODING.get(i, 'cccc') 
                s += struct.pack(END+fmt, self.stroke_extension_data[i])
        for i, bit in enumerate(self.stroke_extension_mask_extra):
            if bit:
                s += struct.pack(END+'I', len(self.stroke_extension_data_extra[i]))
                s += self.stroke_extension_data_extra[i]
        s += struct.pack(END+'i', len(self.points))
        for point in self.points:
            s += point.pack()
        return s
    
    def add(self, point):
        self.points.append(point)
    
    def info(self):
        print 'Stroke color: (%f, %f, %f, %f)' %(self.r, self.g, self.b, self.a)
        print 'Brush size: %f' %self.brush_size
        print 'Stroke extension:'
        for i, bit in enumerate(self.stroke_extension_mask):
            if bit:
                print '    %d: %r' %(i, self.stroke_extension_data[i])
        print 'Stroke extension (extra):'
        for i, bit in enumerate(self.stroke_extension_mask_extra):
            if bit:
                print '    %d: %r' %(i, self.stroke_extension_data_extra[i])
        print 'Number of stroke points: %s expected, %d actual' %(
            self.expected_stroke_points, len(self.points))
        print 'First point:'
        self.points[0].info()
        print 'Last point:'
        self.points[-1].info()
    

class StrokePoint:
    
    def __init__(
                self,
                parent_stroke,
                (x, y, z),
                (or1, or2, or3, or4)=(0.,0.,0.,0.),
                point_extension_data=None
            ):
        self.parent_stroke = parent_stroke
        self.x = x
        self.y = y
        self.z = z
        self.or1 = or1
        self.or2 = or2
        self.or3 = or3
        self.or4 = or4
        self.point_extension_data = point_extension_data
    
    def pack(self):
        s = struct.pack(END+'fffffff',
            self.x, self.y, self.z, self.or1, self.or2, self.or3, self.or4)
        for i, bit in enumerate(self.parent_stroke.point_extension_mask):
            if bit:
                fmt = SketchEditor.POINT_EXTENSION_ENCODING.get(i, 'cccc')
                s += struct.pack(END+fmt, self.point_extension_data[i])
        return s
    
    def info(self):
        print 'Position: (%f, %f, %f)' %(self.x, self.y, self.z)
        print 'Orientation: (%f, %f, %f, %f)' %(self.or1, self.or2, self.or3, self.or4)
        
        print 'Point extension:'
        for i, bit in enumerate(self.parent_stroke.point_extension_mask):
            if bit:
                print '    %d: %r' %(i, self.point_extension_data[i])

if __name__ == '__main__':
    import argparse
    import os
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file_name", type=str, help="Name of file to open")
    opts = parser.parse_args() # Parses sys.argv by default
    
    name, ext = os.path.splitext(opts.file_name)
    if ext == '.sketch':
        t = SketchEditor.from_sketch_file(opts.file_name)
        
        t.info()
        for stroke in t.strokes:
            stroke.info()
        print 'Removing stroke extension'
        t.strokes[0].stroke_extension_mask = [0 for i in range(16)]
        t.strokes[0].stroke_extension_mask_extra = [0 for i in range(16)]
        print 'Removing point extension'
        t.strokes[0].point_extension_mask = [0 for i in range(32)]
        
        print "Saving"
        t.write('data.sketch')
    elif ext == '.json':
        t = SketchEditor.from_json(opts.file_name)
        t.info()
        for stroke in t.strokes:
            stroke.info()
        t.write('data.sketch')
    else:
        print 'Unknown file type: %s' %ext

