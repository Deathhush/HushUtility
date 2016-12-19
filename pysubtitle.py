class SrtItem(object):
    def __init__(self):
        self.index = -1        
        self.start_time = ""
        self.start_millisecond = ""
        self.end_time = ""
        self.end_millisecond = ""
        self.text = []
    def __str__(self):
        return "{0},{1},{2},{3},{4},{5}".format(self.index, self.start_time, self.start_millisecond, self.end_time, self.end_millisecond, self.text)
    
def parse_next_line(next_line):
    line = next_line()    
    return line
    
def parse_srt_item(next_line, index):    
    try:
        srtItem = SrtItem() 
        srtItem.index = index
        next_index_string = str(index+1)
        timeLines = parse_next_line(next_line).split(" --> ")
        startTimeLine = timeLines[0]            
        endTimeLine = timeLines[1]
        srtItem.start_time = startTimeLine.split(",")[0]
        srtItem.start_millisecond = startTimeLine.split(",")[1]
        srtItem.end_time = endTimeLine.split(",")[0]
        srtItem.end_millisecond = endTimeLine.split(",")[1]
        line = parse_next_line(next_line)
        last_line_empty = False
        while True:
            if (len(line) == 0):
                last_line_empty = True                
            elif(len(line) > 0 and last_line_empty and line == next_index_string):                
                break                
            else:
                last_line_empty = False
                srtItem.text.append(line)                
            line = parse_next_line(next_line)        
        return srtItem        
    except StopIteration:
        print "file end reached."
        return None

def read_file_line(f):
    line = f.readline()
    if line == "":
        raise StopIteration
    return line[0:-2]    

import codecs
import chardet
import os

def detect_encoding(file_name):
    bytes = min(256, os.path.getsize(file_name))
    with open(file_name, 'rb') as f:
        header = f.read(bytes)
        if header.startswith(codecs.BOM_UTF8):
            return ('utf8', 1)
        elif header.startswith(codecs.BOM_UTF16):
            return ('utf16', 0)
        else:
            result = chardet.detect(header)    
            encoding = result['encoding']
            if encoding == "GB2312":
                encoding = "GB18030"
            return (encoding, 0)
        
def parse_srt(path): 
    result = detect_encoding(path)
    encoding = result[0]
    skip_bytes = result[1]
    next_line = lambda:read_file_line(f)
    with codecs.open(path, "r", encoding) as f:
        if skip_bytes != 0:
            f.read(skip_bytes)
        while len(next_line()) == 0:
            continue
        item = parse_srt_item(next_line, 1)        
        while item != None:
            yield item
            next_index = item.index+1
            item = parse_srt_item(next_line, next_index)            
        print "parse end reached"
        raise StopIteration