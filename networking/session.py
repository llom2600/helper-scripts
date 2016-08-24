### luke lombardi - Jan/16 ###

import socket, ssl
import pprint
from parser import *
import time
import copy
import chardet
import zlib


### constants ###
CRLF = "\r\n"
BUFFER_SIZE = 4906
TIMEOUT = 2
#################


error = [
"Undefined error.",
"You aren't connected to anything!",
"Timeout",

		]


class session(object):

	threadCount = 1
	request = None
	C_FLAG = False


	def open(self):

		if(self.SSL): 
			return self.openSSL()

		# if not using SSL, set up standard socket
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.setblocking(0)
		self.s.settimeout(TIMEOUT)
		
		try:
			self.s.connect((self.host, self.port))
		except socket.timeout as e:
			self.err(2)
			return (-1)

		self.C_FLAG = True 			#set connected flag



	def openSSL(self):
		context = ssl.create_default_context()

		self.s = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=self.host)
		self.s.setblocking(0)
		self.s.settimeout(TIMEOUT)

		self.s.connect((self.host, self.port))

		try:
			self.s.connect
		except socket.timeout as e:
			self.err(2)
			return (-1)

		self.C_FLAG = True

		self.cert = self.s.getpeercert()
		
		#pprint.pprint(self.cert)



	#extract necessary form
	def getFormData(self, form_id):
		formResults = extract_form(form_id, self.body)

		self.formData = formResults[0]
		self.formMethod = formResults[1]
		
		absolute_path_pattern = r'(https?\:/{2})?([w]{3})?(' + self.host +  r')/'

		self.formAction = "/" + re.sub(absolute_path_pattern, "", formResults[2])
		self.formAction = self.formAction[:-1]


	def err(self, err_code):
		print "Error: ", error[err_code]



	def login(self, path, form_id, params):

		self.s.close()

		#save this in case we need to login in again after a failed connection
		self.loginPath = path
		self.form_id = form_id
		self.params = params

		# open login path and get the form data required for post request content
		self.open()
		self.get(self.loginPath)

		
		self.getFormData(self.form_id)	#find the form data, including hidden fields, in the login form

		print "Acquired the following form data:"
		print self.formData
		
		#set parameters such as username and password for login

		for key,value in self.params.iteritems():
			self.setParam(key, value)

		# if form method was found to be post, send request
		if self.formMethod == "post":
			self.post(self.formAction)
		else:
			print "Needs more work here..."
		
	def get(self, path):
		#print "get running"
		self.currentPath = path

		if self.C_FLAG is not True: 
			self.err(1)
			return (-1)

		header = [ ("GET " + self.currentPath + " HTTP/1.1"),
						("host: " + self.host),
						("Connection: Keep-alive"),
						("user-agent: " + self.browser)
					  ]

		if  (self.__cookie != "" and self.cookiesEnabled):
			header.append("Cookie: " + cookieString(self.__cookie))


		### need these two gaps for a properly formatted request ###
		header.append("")
		header.append("")
		########################################################

		header = CRLF.join(header)		#concatenate request header components


		#print "Sending: "
		#print self.header
		
		self.s.send(header)					#send request

		response = ''

		data = None

		reformat = 0
		while True:
			if "</html>" in response:
				break
			if "MProfileController\"}}" in response:
				break

			try:
				data = self.s.recv(4906)
				#print data
			except:
				print "Attempting to reformat response..."
				if response[0] == "0":
					offset = 0
					while(response[offset] != "H"):
						offset += 1
					response = response[offset:]
					print "OFFSET:", offset, ":", response[offset]
					print "** ----SUCCESS -----**"
					reformat = 1
					break
				else:
					reformat = 1
					print "something else!!!!!"
					#print response[0:10]
					print response
					break

			if data:
				response += data
			else:
				break

		header_data, _, body = response.partition(CRLF*2)

		if reformat:
			body = joinChunks(body)

		self.__response = header_data
		self.__body = body

		self.__cookie = parse_cookies(self.response, self.__cookie)

		#print self.__cookie

		self.C_FLAG = True

		#print body

		return 1



### post method --- work in progress!!! ###

	def post(self, path):

		if self.C_FLAG is not True: 
			self.err(1)
			return (-1)

		self.content = urlEncode(self.formData)
		self.contentLength = len(self.content)

		
		header = [ ("POST " + path + " HTTP/1.1"),
						("Connection: " + "keep-alive"),
						("host: " + self.host),
						("user-agent: " + self.browser),
						("scheme: " + "https"),
						("version: " + " HTTP/1.1"),
						("accept: " + "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"),
						("accept: " + "accept-encoding:gzip, deflate"),
						("accept-language: " + "en-US,en;q=0.8"),
						("cache-control: " + "max-age=0"),
						("content-type: " + "application/x-www-form-urlencoded"),
						("content-length: " + str(self.contentLength))
					  ]
		

		'''
		header = ["POST /banner/twbkwbis.P_ValLogin HTTP/1.1",
				  "Host: ssb.cc.binghamton.edu",
				  "Connection: keep-alive",
				  "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
				  "Accept-Encoding: gzip, deflate",
				  "Accept-Language: en-US,en;q=0.8",
				  "Origin: https://ssb.cc.binghamton.edu",
				  "Referer: https://ssb.cc.binghamton.edu/banner/twbkwbis.P_ValLogin",
				  "Upgrade-Insecure-Requests: 1",
				  "User-Agent: Mozilla/5.0",
				  "Content-Type: application/x-www-form-urlencoded",
				  "Content-Length: 26"]
		
		'''
		if  (self.__cookie != "" and self.cookiesEnabled):
			header.append("Cookie: " + cookieString(self.__cookie))


		### need these two gaps for a properly formatted request ###
		header.append("")
		header.append("")
		########################################################

		

		self.request = header 

		self.request.append(self.content)
		#self.request.append("sid=llombar1&PIN=Av0nlife1")

		self.request = CRLF.join(header)		#concatenate request header components

		#print "-------------------------------------------------------------------"
		#print self.request
		#print "-------------------------------------------------------------------\n"


		self.s.send(self.request)					#send request

		print "Sending login request: "
		print self.request

		response = ''

		
		while True:
			if ("Content-Length") in response:
				print "broke too soon? broke on content length"
				break
			if ("Transfer-Encoding") in response:
				print "broke too soon? broke on chunked"
				break

			try:
				data = self.s.recv(4906)
				#print data
			except:
				print "exit loop"
				break

			if data:
				response += data
			else:
				break

		print "end: ", response

		response = extract_header(response)
		header_data, _, body = response.partition(CRLF*2)
		'''
		
		test = body.split("\r\n")
		print body.split("\r\n")

		for i in range(0,len(test)):
			currentSet =  chardet.detect(test[i])
			if currentSet["encoding"] != "ascii":
				#print i, "-------------------------", currentSet
				#print chardet.detect(test[6]),":", chardet.detect(test[6])
				pass
			else:
				pass
				#print "--------------------------"
				#print "COUNT:", test[i]
		#print test[1]
		for i in range(len(test[1])):
			#print i, ":",chardet.detect(test[1][i]), ":", test[1][i]
			print "WHWHWHW"
			d = zlib.decompressobj(16+zlib.MAX_WBITS) #this magic number can be inferred from the structure of a gzip file
			hm = d.decompress(test[3] + test[4])
 			print hm
		
 		'''

		'''
		print "-------------------------------------------------------------------"
		print "Response:", header_data
		print "body:", body.decode("ascii")
		print "-------------------------------------------------------------------"
		'''

		self.__response = header_data
		self.__body = body
		#print "Cookies before set:\n\n", self.__cookie
		self.__cookie = parse_cookies(self.response, self.__cookie)
		#print "Cookies after set:\n\n", self.__cookie
		self.C_FLAG = False

		



	
	def setParam(self, key, value):
		self.formData[key] = value


	### attribute handlers ###

	def get_cookies(self): return self.__cookie
	def set_cookies(self, value): self.__cookie = value
	def del_cookies(self): del self.__cookie

	def get_socket(self): return self.__socket
	def set_socket(self, value): self.__socket = value
	def del_socket(self): del self.__socket

	def get_host(self): return self.__host
	def set_host(self, value): self.__host = value
	def del_host(self): del self.__host

	def get_port(self): return self.__port
	def set_port(self, value): self.__port = value
	def del_port(self): del self.__port

	def get_browser(self): return self.__browser
	def set_browser(self, value): self.__browser = value
	def del_browser(self): del self.__browser


	def get_ssl(self): return self.__ssl
	def set_ssl(self, value): self.__ssl = value

	def get_cookiesEnabled(self): return self.__cookiesEnabled
	def set_cookiesEnabled(self, value): self.__cookiesEnabled = value


	def get_body(self): return self.__body
	def get_response(self): return self.__response

	### property definitions ###


	browser = property(get_browser, set_browser, del_browser)
	host = property(get_host, set_host, del_host)
	port = property(get_port, set_port, del_port)

	cookie = property(get_cookies, set_cookies, del_cookies)
	body = property(get_body)
	response = property(get_response)



	#configuration attributes
	SSL = property(get_ssl, set_ssl)
	cookiesEnabled = property(get_cookiesEnabled, set_cookiesEnabled)



  	def __call__(self):
		__init__(self)

	def __init__(self):
		self.__cookiesEnabled = False
		self.s = None

		self.__host = None
		self.__port = None
		self.__SSL = False

		self.__cookie = {}
		self.__body = None
		self.__response = None


		self.__browser = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537."