# luke lombardi - 2016
#orphan file - really only useful for the setup code, will update later 
# serial wrapper v0.2

import serial
import subprocess
import datetime
import copy
import numpy as np
import struct
import time

from multiprocessing import *


# Return codes & Constants
FAILURE_CODE = {
                "baud_rate":-1,
                "device_not_found":-2,
                "open_error":-3,
                "no_connection":-4
                }

SUCCESS_CODE = 0

## default configuration parameters ##
default_baudRate = 9600

#### parameter filtering ####
acceptedBaudRates = [300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 28800, 38400, 57600, 115200]


class serialIO(object):
    deviceList = {}
    
    def newConnection(self, params):
        returnCode = self.verifyConnectionParameters(params)
        if returnCode == SUCCESS_CODE:
            print "<OK> Device", params["port"], "exists."
            currentTime = datetime.datetime.now().time()
            self.form.outputMessage(currentTime.isoformat() + self.spacer + "Device" + params["port"] + " exists.")
            self.form.outputMessage(currentTime.isoformat() + self.spacer + "Attempting connection to:  " + params["port"])
            
            if params["port"] not in self.deviceList:
                self.form.outputMessage(currentTime.isoformat() + self.spacer + "No existing connection, creating new instance...")
                print "No existing connection, creating new instance..."
                self.openConnection(params)
        else:
            print "Exiting with error code: ", returnCode    
        
        
    def openConnection(self, params):
        currentTime = datetime.datetime.now().time()
        try:
            self.interface = serial.Serial(params["port"])
        except Exception as e:
            print "Exception: ", e
            return FAILURE_CODE["open_error"]
        
        if self.interface.isOpen():
            self.interface.close()
            
        #creating fresh connection to serial device
        try:
            self.interface.open()
            self.connectionState = 1
        except:
            self.connectionState = 0
        
        if self.connectionState:
            #modify connect button dynamically
            self.form.outputMessage(currentTime.isoformat() + self.spacer + "Connected successfully.")
            self.form.btnConnect.setText("Disconnect")
            self.form.btnConnect.clicked.disconnect(self.form.connectSerial)
            self.form.btnConnect.clicked.connect(self.form.disconnectSerial)
            self.form.btnSendSerial.setEnabled(True)     
                 
            #### multiprocessing stuff
    
            self.dataPool = Queue()     #create queue to store shared data
            self.plotData = Queue()     #create queue to store shared data
            self.messagePool = Queue()  #create queue for process message sharing
            
            
            self.startDataAcquisition()
            
        else:
            return FAILURE_CODE["open_error"]
            
    
    def closeConnection(self):
        currentTime = datetime.datetime.now().time()
        if self.connectionState:
            self.interface.close()
            
            self.form.outputMessage(currentTime.isoformat() + self.spacer + "Disconnected.")
            self.form.btnConnect.setText("Connect")
            self.form.btnConnect.clicked.disconnect(self.form.disconnectSerial)
            self.form.btnConnect.clicked.connect(self.form.connectSerial)
            self.form.btnSendSerial.setEnabled(False)
            
            self.connectionState = 0
            
            #terminate worker processes forcefully
            for i in range(len(self.tList)):
                self.tList[i].terminate()
    
    
    def verifyConnectionParameters(self, params):
        currentTime = datetime.datetime.now().time()
        #check baud rate
        if params["baud_rate"] not in acceptedBaudRates:
            self.validateParams(False)
            return FAILURE_CODE["baud_rate"]
        
        #check if serial port file exists
              
        if(params["port"] not in self.portList):
            #print params["port"], " is not available."
            if params["port"] != "":
                self.form.outputMessage(params["port"] + " is not available.")
                if (len(self.portList) > 0):
                    self.form.outputMessage("Possible alternative device(s):")
                    for i in range(len(self.portList)):
                        self.form.outputMessage(str(i) + "-" + str(self.portList[i]))
            
            self.validateParams(False)
            return FAILURE_CODE["device_not_found"]
        
        
        elif self.portList[0] == "No serial devices available.":
            self.validateParams(False)
            return FAILURE_CODE["device_not_found"]        
        else:
            self.validateParams(True)
            return SUCCESS_CODE
    
    
    def validateParams(self, status):
        self.form.setValidity(status)
    

    def updatePortList(self):
        deviceList = subprocess.check_output(["ls","/dev/"])
        deviceList = deviceList.split("\n")
        
        portList = []
        
        for i in range(len(deviceList)):
            if ("ttyACM" in deviceList[i]) or ("ttyUSB" in deviceList[i]):
                portList.append("/dev/" + deviceList[i])
        
        if portList == []:
            portList.append("No serial devices available.")
        
        self.portList = portList
        
    
        
    def writeCommand(self, command):
        self.dataStreaming = False
        self.messagePool.put("join")
        
        for i in range(len(self.tList)):
            self.tList[i].join()
        
        self.tList = []
        
        currentTime = datetime.datetime.now().time()
        if not self.connectionState:
            return FAILURE_CODE["no_connection"]
        
        #cmd = self.parse_command(command)
        
        command = list(command)
        self.form.outputMessage(currentTime.isoformat() + self.spacer + "Sending:   " + "".join(command))

        command += ">"
        
        for i in range(len(command)):
            self.interface.write(struct.pack('>c', command[i]))  
        self.startDataAcquisition()
        
    
    def startDataAcquisition(self):
        pRead = Process(target=self.readData, args=(self.dataPool,self.messagePool))                       #data acquisition process
        pParse = Process(target=self.parseData, args=(self.dataPool,self.plotData ))     #data parsing -> processing 
        
        #create process list
        self.tList.append(pRead)
        self.tList.append(pParse)
        
        pRead.start()
        pParse.start()
        
        self.dataStreaming = True
        self.form.refreshPlot()


    
    def readData(self, dataPool, messagePool):
        currentTime = datetime.datetime.now()

        if not self.connectionState:
            return FAILURE_CODE["no_connection"]
        
        dataWindow = []
        timeVector = []
        
        while self.connectionState:
            data = None
            partialPacket = ""
            
            if not messagePool.empty():
                try:
                    processMessages = messagePool.get()
                    dataPool.put("join")
                    break
                except:
                    print "Error retrieving message."
            
            previousTime = currentTime
            previousWindowLength = len(dataWindow)
            
            currentTime = datetime.datetime.now()
            
            currentSecond = currentTime.second
            currentMinute = currentTime.minute

            currentMs = float(currentTime.microsecond/1000000.0)
            
            currentSecond = (currentSecond+currentMs)/60.0
            
            try:
                data = self.interface.read(8)            
            except:
                print "Problem getting data from serial interface."
             
            if (data[0] == ":" and data[len(data)-1] == ":"):
                if data[1:-1] != "------":
                    data = data[1:]
                    data = data.replace(" ","")
                    dataWindow += data
                    timeVector.append(currentMinute+currentSecond)
              
            else:
                partialPacket += data
                #add something here to piece together partial packets
                
            #sampleRate = (((currentTime.microsecond - previousTime.microsecond) / 1000000.0) / 60.0)
            #print "Sample rate:", sampleRate
            
            if len(dataWindow) >= self.windowSize:
                dataPool.put([dataWindow,timeVector])
                dataWindow = []
                timeVector = []
            
    
    def parse_command(self, dataPool):
        currentTime = datetime.datetime.now().time()
        
    
    def parseData(self, dataPool, plotData):
        delim = ":"
        
        while self.connectionState:            
            if not dataPool.empty():
                try:
                    dataWindow = dataPool.get()
                except:
                    continue
                    
                if dataWindow == "join":
                    break
            
                timeVector = copy.deepcopy(dataWindow[1])            
                dataWindow = ''.join(dataWindow[0])
                dataWindow = dataWindow.split(delim)
                dataWindow = dataWindow[:-1]
                dataWindow = [float(i) for i in dataWindow]
                        
                print dataWindow
                #print timeVector
                x = np.asarray(timeVector)
                y = np.asarray(dataWindow)
                
                if self.form.plotVisible:
                    plotData.put([x,y])


    def __init__(self, form):
        currentTime = datetime.datetime.now().time()
        self.spacer = ":   "
        self.windowSize = 100
        self.dataStreaming = False
        
        self.form = form
    
        self.tList = []             #process list
        self.updatePortList()
        self.connectionState = 0
        
        
    def __call__(self, form):
        currentTime = datetime.datetime.now().time()
        self.__init__()
       