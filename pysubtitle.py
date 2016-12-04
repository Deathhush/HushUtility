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
def parse_srt_item(next_line):     
    line = next_line()    
    while line == "":        
        line = next_line()    
    srtItem = SrtItem()    
    srtItem.index = int(line)
    timeLines = next_line().split(" --> ")
    startTimeLine = timeLines[0]            
    endTimeLine = timeLines[1]
    srtItem.start_time = startTimeLine.split(",")[0]
    srtItem.start_millisecond = startTimeLine.split(",")[1]
    srtItem.end_time = endTimeLine.split(",")[0]
    srtItem.end_millisecond = endTimeLine.split(",")[1]
    line = next_line()
    while line != "":        
        srtItem.text.append(line[0:-1])        
        line = next_line()  
        return srtItem

def read_file_line(f, encoding="gbk"):
    if (encoding !=""):
        return f.readline().decode(encoding)[0:-1]
    return f.readline()[0:-1]

def parse_srt(path):    
    with open(path) as f:        
        for i in xrange(2):
            print parse_srt_item(lambda:read_file_line(f))