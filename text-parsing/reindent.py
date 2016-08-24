from itertools import islice
from fileIO import *
import re
import sys

def  cleanFile(fileArray):
	for i in range(len(fileArray)):
			fileArray[i] = fileArray[i].replace("\t", "    ")

	spaceIndent = re.compile(r'^([\t]*(\040\040\040\040)+[\t]*[^\t ])')
	for i in range(len(fileArray)):
		m = re.search(spaceIndent, fileArray[i])
		if m:
			#print m.group(0)
			indentation_groups = ((m.end() - m.start()) / 4 )
			#print indentation_groups
			fileArray[i] = ("\t" * indentation_groups) + fileArray[i][m.end()-1:]
			#print fileArray[i]
	
	return fileArray

	
####### script:entry ######
argCount = len(sys.argv) 

if argCount == 1:
	print "No input files specified.\n\nUsage: python reindent.py filename.py ... filenameX.py\n"

else:
	for i in range(1, argCount):
		print sys.argv[i]
		fileName = sys.argv[i]
		fileArray = fileIO.importFile(fileName)
		fileArray = cleanFile(fileArray)
		
		split_fileName = fileName.split(".")
		new_fileName = split_fileName[0] + "_modified." + split_fileName[1]
		
		fileIO.writeFile(fileArray, new_fileName)

		