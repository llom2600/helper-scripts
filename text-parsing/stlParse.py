import numpy as np
from fileIO import *
from numpy.core.multiarray import dtype

import pyqtgraph as pg
import pyqtgraph.opengl as gl
from PyQt4 import QtCore
from PyQt4 import QtGui


def parseFacets(parsedFileArray):
	fileLength = len(parsedFileArray)
	facetIndices = []
	outerloopIndices = []
	endFacetIndices = []
	endLoopIndices = []
        
	for i in range(fileLength):
		if parsedFileArray[i][0] == 'f':
			facetIndices.append(i)
		elif parsedFileArray[i][0:4] == "endf":
			endFacetIndices.append(i)
    
	facetList = []
	vertexList = []
    
	for i in range(len(facetIndices)):
		facetRange = [facetIndices[i], endFacetIndices[i]]
		currentObject = parsedFileArray[facetRange[0]: facetRange[1]]
    
		currentFacet = currentObject[0]
		currentVertices = currentObject[2:-1]
		#facetList = np.array([])
  
		currentFacetCoordinates = np.char.strip(currentFacet, "facet normal")
		currentFacetCoordinates = np.char.split(currentFacetCoordinates, " ")
        
		currentVertices = np.char.strip(currentVertices,"vertex ")
		currentVertices = np.char.split(currentVertices, " ")
        
        
		print "\nFacet ", i, "\n"
		print currentFacetCoordinates
		print "------"
		print currentVertices
        
        
		facetList.append(currentFacetCoordinates.tolist())
		vertexList.append(currentVertices.tolist())
            
	facetList = np.asarray(facetList, dtype=np.float32)
	vertexList = np.asarray(vertexList, dtype=np.float32)
    
	return [facetList, vertexList]


def generateMesh(facetList, vertexList):
	app = QtGui.QApplication([])
	w = gl.GLViewWidget()
	w.opts['distance'] = 40
	w.show()
	w.setWindowTitle('pyqtgraph example: GLLinePlotItem')
	pts = np.vstack(facetList).transpose()
	plt = gl.GLLinePlotItem(pos=pts, antialias=True)
	w.addItem(plt)
    
	facetList = np.array([])
    
	#while(True):
	#    continue
	

def main():
	fileName = "sample.ast"
    
	fileArray = fileIO.importFile(fileName)
	
	parsedSTL = np.asarray(fileArray)
	parsedSTL = np.char.strip(parsedSTL)
	
	parsedSTL = parseFacets(parsedSTL)
	
	STLMesh = generateMesh(parsedSTL[0], parsedSTL[1])
    
    
if __name__ == "__main__":main()
