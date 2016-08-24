from itertools import islice

class fileIO(object):
	
	def __init__(self):
		pass
	
	@staticmethod
	def importFile(fileName):
		linesPerRead = 2000
		#global linesPerRead
		#global fileLength

		unparsedFile = []
		try:
			fHandle = open(fileName)
		except Exception as e:
			print "Could not open file:", e
			return -1

		with fHandle as f:
			n = 0
			print "Importing file: ", fileName
			while True:
				n += 1
				next_n_lines = list(islice(f, linesPerRead))
				unparsedFile += next_n_lines            
				if not next_n_lines:
					break
					
		fileLength = len(unparsedFile)
		
		for i in range(fileLength):
			unparsedFile[i] = unparsedFile[i].replace("\n", "")
		
		return unparsedFile
	
	
	@staticmethod
	def writeFile(fileArray, fileName):
		print "Writing file array to: ", fileName
		
		try:
			fHandle = open(fileName,"w")
		except Exception as e:
			print "Could not write file:", e
			return -1

		for i in range(len(fileArray)):
			fHandle.write(fileArray[i] + "\n")

		fHandle.close()
		return 0

