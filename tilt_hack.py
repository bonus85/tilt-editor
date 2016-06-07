#!/usr/bin/env python
"""
@author: Sindre Tosse
"""
import struct
import pdb

END = '' # Struct format

class TiltEditor:

    DEFAULT_HEADER = \
        '\xcd\xa5v\xc5\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    def __init__(self, header=None, expected_brush_strokes=0):
        if header is None:
            self.header = TiltEditor.DEFAULT_HEADER
        else:
            self.header = header
        self.expected_brush_strokes = expected_brush_strokes
        self.strokes = []
    
    @classmethod
    def from_sketch_file(cls, file_name):
        with open(file_name, 'rb') as f:
            raw_file = f.read()
        
        header = raw_file[:16] # Unknown
        brush_strokes = struct.unpack(END+'i', raw_file[16:20])[0] # Likely
        
        instance = TiltEditor(header, brush_strokes)
        
        file_length = len(raw_file)
        pos = 20
        
        while pos < file_length:
            stroke_header = raw_file[pos:pos+40]
            pos += 40
            stroke = Stroke.from_header(stroke_header)
            
            for i in range(stroke.expected_stroke_points):
                point = raw_file[pos:pos+36]
                pos += 36
                stroke_point = StrokePoint.from_data(point)
                stroke.add(StrokePoint.from_data(point))
            instance.add_stroke(stroke)
        assert pos == file_length,\
            'Error: file did not match format specification (incorrect length)'
        return instance
    
    def add_stroke(self, stroke):
        self.strokes.append(stroke)
        
    def write(self, file_name):
        with open(file_name, 'w') as f:
            f.write(self.header)
            f.write(struct.pack(END+'i', len(self.strokes)))
            for stroke in self.strokes:
                f.write(stroke.pack())
    
    def info(self):
        print 'Brush strokes: %d expected, %d actual' %(
            self.expected_brush_strokes, len(self.strokes))

class Stroke:

    DEFAULT_UNKNOWN_STROKE_HEADER = \
        '\x01\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00' # Stroke style?
    
    def __init__(self, color, brush_size, unknown_stroke_header=None,
            expected_stroke_points=None):
        self.color = color
        self.brush_size = brush_size
        self.stroke_points = 0
        self.points = []
        self.expected_stroke_points = expected_stroke_points
        if unknown_stroke_header is None:
            self.unknown_stroke_header = Stroke.DEFAULT_UNKNOWN_STROKE_HEADER
        else:
            self.unknown_stroke_header = unknown_stroke_header

    @classmethod
    def from_header(cls, stroke_header):
        if stroke_header[:4] != '\x00\x00\x00\x00':
            print 'Warning: Expected four zero bytes in stroke header'
            print struct.unpack(END+'cccc', stroke_header[:4])
        color = struct.unpack(END+'ffff', stroke_header[4:20])
        brush_size = struct.unpack(END+'f', stroke_header[20:24])[0]
        unknown_stroke_header = stroke_header[24:36]
        stroke_points = struct.unpack(END+'i', stroke_header[36:])[0]
        
        return Stroke(color, brush_size, unknown_stroke_header, stroke_points)
    
    def pack(self):
        s = '\x00\x00\x00\x00'
        args = self.color + (self.brush_size, )
        s += struct.pack(END+'fffff', *args)
        s += self.unknown_stroke_header
        s += struct.pack(END+'i', len(self.points))
        for point in self.points:
            s += point.pack()
        return s
    
    def add(self, point):
        self.points.append(point)
    
    def info(self):
        print 'Stroke color: (%f, %f, %f, %f)' %self.color
        print 'Brush size: %f' %self.brush_size
        print 'Unknown header: %r' %self.unknown_stroke_header
        print 'Number of stroke points: %d expected, %d actual' %(
            self.stroke_points, len(self.points))
        print 'First point:'
        self.points[0].info()
        print 'Last point:'
        self.points[-1].info()
    

class StrokePoint:

    DEFAULT_UNKNOWN_DATA = '\x0f\x1d\x00\x00'
    
    def __init__(self, position, orientation=(0.,0.,0.,0.),
            trigger_pressure=1.0, unknown_point_data=None):
        self.position = position
        self.orientation = orientation
        self.trigger_pressure = trigger_pressure
        if unknown_point_data is None:
            self.unknown_point_data = StrokePoint.DEFAULT_UNKNOWN_DATA
        else:
            self.unknown_point_data = unknown_point_data

    @classmethod
    def from_data(cls, data):
        assert len(data) == 36, 'Expected 36 byte str, got %d' %len(data)
        # Looks like
        position = struct.unpack(END+'fff', data[0:12])
        # Looks like
        orientation = struct.unpack(END+'ffff', data[12:28])
        # Looks like
        trigger_pressure = struct.unpack(END+'f', data[28:32])[0]
        unknown_point_data = data[32:36]
        return StrokePoint(position, orientation,
            trigger_pressure, unknown_point_data)
    
    def pack(self):
        args = self.position + self.orientation + (self.trigger_pressure, )
        return struct.pack(END+'ffffffff', *args) + self.unknown_point_data
    
    def info(self):
        print 'Position: (%f, %f, %f)' %self.position
        print 'Orientation: (%f, %f, %f, %f)' %self.orientation
        print 'Trigger pressure: %f' %self.trigger_pressure
        print 'Unknown: %r' %self.unknown_point_data
        
                

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Analyze and edit .sketch files (internal in .tilt)')
    parser.add_argument("file_name", type=str, help="Name of file to open")
    opts = parser.parse_args() # Parses sys.argv by default
    t = TiltEditor.from_sketch_file(opts.file_name)
    t.info()
    for stroke in t.strokes:
        stroke.info()
    #t.write('test.sketch')

