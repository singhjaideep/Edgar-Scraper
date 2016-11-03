import urllib2, StringIO, re, sys, time
from lxml import etree

csvheaders = ['nameOfIssuer','titleOfClass','cusip','value','shrsOrPrnAmt/sshPrnamt','shrsOrPrnAmt/sshPrnamtType','investmentDiscretion',
	'votingAuthority/Sole','votingAuthority/Shared','votingAuthority/None']
genDate = time.strftime('%Y%m%d')

def findFile(tickerCIK,filingType):
	#Goto EDGAR ATOM feed and get text file links
	print 'Getting text link for ',filingType,' ...'
	url = 'http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=%s&type=%s&dateb=&owner=exclude&count=40&output=atom' % (tickerCIK,filingType)
	page = urllib2.urlopen(url).read()
	# Check if XML file exists
	if not '<?xml' in page[:15]: sys.exit("Invalid CIK/Ticker.")
	#lxml parsing
	parsed = etree.parse(StringIO.StringIO(page))
	findSubstring = '{http://www.w3.org/2005/Atom}entry/{http://www.w3.org/2005/Atom}link'
	textUrlLink = parsed.find(findSubstring)
	if textUrlLink is not None:
		textUrlLink = textUrlLink.get('href')
		textUrlLink = textUrlLink.replace('-index.htm','.txt')
		return textUrlLink
	else:
		print 'txt file not found for ',filingType
		return None

def parse13FHR(url,tickerCIK,filingType):
	#Parse and output text file according to schema
	print 'Parsing text file for ',filingType,' ...'
	page = urllib2.urlopen(url).read()
	#We only care about the <XML>...</XML> part
	fundHoldingsStart = list(re.finditer(r"<XML>", page))[1].start()
	fundHoldingsEnd = list(re.finditer(r"</XML>",page))[1].end()
	fundHoldings = page[fundHoldingsStart:fundHoldingsEnd]
	#lxml parsing
	dataparse = etree.parse(StringIO.StringIO(fundHoldings))
	#Xpaths we need
	path = "/XML/*[local-name()='informationTable']/*[%s]/*[local-name()='%s']"
	path2= "/XML/*[local-name()='informationTable']/*[%s]/*[local-name()='%s']/*[local-name()='%s']"
	#Count the number of holdings
	infoTableNodeCount = int(dataparse.xpath("count(/XML/*[local-name()='informationTable']/*[local-name()='infoTable'])"))
	#Output the text file
	docName = '13FHR'
	filename = docName+'_'+tickerCIK+'_'+genDate+'.txt'
	fileio = open(filename,'w')
	fileio.write(','.join(csvheaders))
	for infoTableNodeNum in xrange(0,infoTableNodeCount+1):
		for csvheader in csvheaders:
			if '/' not in csvheader:
				xpath = path % (str(infoTableNodeNum),csvheader)
			else:
				csvSplit = csvheader.split('/')
				xpath = path2 % (str(infoTableNodeNum),csvSplit[0],csvSplit[1])
			for elem in dataparse.xpath(xpath):
				fileio.write(elem.text+',')
		fileio.write('\n')
	fileio.close()

def parse13FHRA(url,tickerCIK,filingType):
	#Parse and output text file according to schema
	print 'Parsing text file for ',filingType,' ...'
	page = urllib2.urlopen(url).read()
	#We only care about the <S>...</Table> part
	fundHoldingsStart = list(re.finditer(r"<S>", page))[0].start()
	fundHoldingsEnd = list(re.finditer(r"</Table>",page))[0].end()
	#Parse the table
	fundHoldings = page[fundHoldingsStart:fundHoldingsEnd] 
	cs = list(re.finditer(r"<C>", fundHoldings))
	#List to hold the positions of various datapoints
	cspos = [c.start() for c in cs]
	cspos.insert(0,0)
	#Output the text file
	docName = '13F-HRA'
	filename = docName+'_'+tickerCIK+'_'+genDate+'.txt'
	fileio = open(filename,'w')
	fileio.write(','.join(csvheaders))
	fileio.write('\n')
	for fundline in fundHoldings.split('\n')[1:-1]:
		for i in xrange(0,len(cspos)-1):
			point = fundline[cspos[i]:cspos[i+1]-1].strip()
			if len(point):
				fileio.write(point.replace(',','')+',')
			else:
				fileio.write(',')
		fileio.write('\n')
	fileio.close()

def main():
	#Parsing Argument
	if not sys.argv[1]: sys.exit("Script needs CIK/Ticker.")
	tickerCIK = sys.argv[1]
	filingTypes = ['13F-HR','13F-HR/A']
	for filingType in filingTypes:
		url = findFile(tickerCIK,filingType)
		if url is not None and filingType == '13F-HR': parse13FHR(url,tickerCIK,filingType)
		if url is not None and filingType == '13F-HR/A': parse13FHRA(url,tickerCIK,filingType)
	print 'Done!'

if __name__ == '__main__':
	main()