import re
import sys
sys.path.append('../text-parsing')

import subprocess
from fileIO import *


rootURL = r"thepiratebay.org"
categoryURL = r"/browse/501/2/3"
rootURLfilename = "root.raw"
port = 443


linesPerRead = 2500


def getTorrentLinks(raw_rootFile):
	torrentURLgrabber = re.compile(r"/torrent/[0-9]+/[A-Za-z\_\(\)0-9\-\[\]\.]+", flags = re.DOTALL | re.MULTILINE)
	unparsedFile = fileIO.importFile(raw_rootFile)
	URL_list = []
	for i in range(len(unparsedFile)):
		URLs = re.search(torrentURLgrabber, unparsedFile[i])
		if URLs:
			URL_list.append(URLs.group(0))

	return URL_list



def getDescriptionLinks(torrentURLs):
	re_description = re.compile(r'(<div[^>]class="nfo">((?!</div>).)*)', flags=re.DOTALL | re.MULTILINE)
	re_link_A = re.compile(r'<a[^>]href="[^"]?http[s]*://[^"]*[^>]*rel=', flags = re.DOTALL | re.MULTILINE)
	re_protocol = re.compile(r'<a[^>]href="[^"]?http[s]*://')
	re_html = re.compile(r'[^>] rel=')

   
	for i in range(len(torrentURLs)):
		print rootURL + torrentURLs[i]
		cmd_wgetDesc = "wget -O temp.raw" + " \"" + rootURL + torrentURLs[i] + "\""
		downloadRoot = subprocess.check_output(cmd_wgetDesc, shell=True)
		tempFile = fileIO.importFile("temp.raw")
		tempFile = ''.join(tempFile)

		description = re.search(re_description, tempFile)
		print description.group(0)

		if description:
			innerLinks = re.findall(re_link_A, description.group(0)) 
			if innerLinks:
					print "####################### INNER Links #################"
					for i in range(len(innerLinks)):
						protocol = re.search(re_protocol, innerLinks[i])
						html = re.search(re_html, innerLinks[i])
						innerLinks[i] = innerLinks[i][protocol.end():html.start()]
						print innerLinks[i]
					print "#######################             #################"


#print rootURL
cmd_wgetRoot= "wget -O " + rootURLfilename + " " + (rootURL + categoryURL)
downloadRoot = subprocess.check_output(cmd_wgetRoot, shell=True)

links = getTorrentLinks(rootURLfilename)

for i in range(len(links)):
	print i,":", links[i]

if len(links) > 0:
	screenshot_links = getDescriptionLinks(links)


