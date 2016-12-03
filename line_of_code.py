import os

def analyze_file(fileName, root=''):    
    filePath=os.path.join(root, fileName)
    with open(filePath) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def need_exclude(fileName, filesToExclude):
    return any(exclude.lower() in fileName.lower() for exclude in filesToExclude)

def count_line(folderPath, searchExt = ['.cpp', '.h'], filesToExclude = ['designer.cs'], verbose=False):
    lineOfCode = 0
    fileCount = 0
    for root, dirs, files in os.walk(folderPath):    
        for fileName in files:            
            if (os.path.splitext(fileName)[1] in searchExt) and not need_exclude(fileName, filesToExclude):
                fileCount=fileCount+1
                currentLine = analyze_file(os.path.join(root, fileName))
                if verbose:
                    print os.path.join(root, fileName + ' , ' + str(currentLine))
                lineOfCode = lineOfCode+currentLine
    print str(fileCount) + " source code files found."
    print str(lineOfCode) + " lines in total."