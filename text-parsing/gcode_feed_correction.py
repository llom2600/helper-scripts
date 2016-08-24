'''
luke lombardi - 8/16

purpose: separates GCODE files by command and can also threshold values to be under certain firmware constants

input: GCODE files from slic3r/cura
output: cleaned GCODE files ready for printer

------------------------------------------------
basic usage:

1. open and import the file: 
	fname = "test.gcode"
	unparsedFile = importGCode(fname)

2. pick out lines that contain the commands you want to modify:
	cmdArray = ["G1", "G28", "G92", "G1 Z[0-9.]+ "]
 	cmdIndices = getCommands(unparsedFile, cmdArray)

3. then, set command constraints. so if you wanted to constrain only the z specific movement to a set maximum feedrate:

	maxFeedrate = 2000.000
	constraintObject = [re.compile(r"F[0-9\.]+"), maxFeedrate]   
	parsedFile = thresholdCommand("G1 Z[0-9.]+ ", cmdIndices["G1 Z[0-9.]+ "], unparsedFile, constraintObject)

4. rewrite modified file to new location

'''

#script:begin

import re
from fileIO import *

def getCommands(unparsedFileArray, cmdArray):
	searchObject = []
	cmdIndices = {}
	for i in range(len(cmdArray)):
		searchObject.append(re.compile(cmdArray[i] + r".+"))  
		cmdIndices[cmdArray[i]] = []
    
	#print unparsedFileArray
	for i in range(len(unparsedFileArray)):
	#print unparsedFileArray[i]
		for j in range(len(searchObject)):
			result = re.search(searchObject[j], unparsedFileArray[i])
			if result:
				cmdIndices[cmdArray[j]].append(i)
    
	return cmdIndices


def thresholdCommand(cmd, cmdIndices, unparsedFile, constraintObject):
   for i in range(len(cmdIndices)):
       current = unparsedFile[cmdIndices[i]]
       match = re.search(constraintObject[0], current)

       if match:
           constrainedCmd = str.replace(unparsedFile[cmdIndices[i]],unparsedFile[cmdIndices[i]][match.start()+1:match.end()], str(constraintObject[1]))
           unparsedFile[cmdIndices[i]] = constrainedCmd
			
   return unparsedFile
   
	

#script:entry-point

fileName = "test.gcode"
fileArray = fileIO.importFile(fileName)

#pick out lines that contain the following commands:
cmdArray = ["G1", "G28", "G92", "G1 Z[0-9.]+ "]
cmdIndices = getCommands(fileArray, cmdArray)

#for example, if you wanted to constrain only the z movements to specific feedrate

maxFeedrate = 2000.000
constraintObject = [re.compile(r"F[0-9\.]+"), maxFeedrate]   

modifiedFileArray = thresholdCommand("G1 Z[0-9.]+ ", cmdIndices["G1 Z[0-9.]+ "], fileArray, constraintObject)

#write modified file to disk with a new file name

split_fileName = fileName.split(".")
new_fileName = split_fileName[0] + "_modified." + split_fileName[1]

fileIO.writeFile(modifiedFileArray, new_fileName)


#script:end