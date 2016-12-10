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
    
def parse_srt_item(next_line):    
    try:        
        line = parse_next_line(next_line)    
        while line == "":        
            line = parse_next_line(next_line)    
        srtItem = SrtItem()        
        srtItem.index = int(line)
        timeLines = parse_next_line(next_line).split(" --> ")
        startTimeLine = timeLines[0]            
        endTimeLine = timeLines[1]
        srtItem.start_time = startTimeLine.split(",")[0]
        srtItem.start_millisecond = startTimeLine.split(",")[1]
        srtItem.end_time = endTimeLine.split(",")[0]
        srtItem.end_millisecond = endTimeLine.split(",")[1]
        line = parse_next_line(next_line)        
        while len(line) != 0:
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
def parse_srt(path, encoding="gbk", skip_bytes=0): 
    next_line = lambda:read_file_line(f)
    with codecs.open(path, "r", encoding) as f:
        if skip_bytes != 0:
            f.read(skip_bytes)
        item = parse_srt_item(next_line)
        while item != None:
            yield item
            item = parse_srt_item(next_line)
        print "parse end reached"
        raise StopIteration