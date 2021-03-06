import urllib2
import re
from bs4 import BeautifulSoup
from time import time

# Get the start time
t0 = time()

base_p7_url = 'http://www-01.ibm.com/support/knowledgecenter/api/content/POWER7/p7hdx/'
p7_models = ['9117_mmb','9117_mmc','9117_mmd']
keywords = ['troubleshooting']

Out_file = './Data/POWER7_data.txt';
Links_file = './Data/Processed_links.txt';
f1 = open(Out_file,'wb')
f2 = open(Links_file,'wb')

count_links = 0
processed_urls = []
processed_topics = []
# Function to process each link
def process_link(link, parent_url):
	global count_links 
	count_links = count_links + 1;
	# Get the title and relative url
	url = str(link['href'])
	title = str((link.contents[-1]).encode('utf-8'))

	# If this is a relative URL, then find the absolut URL
	if (url.find("http") < 0):
		# Create the full URL
		full_url = parent_url+url
	else:
		return;

	# If this link is a strong 
	# Get the current base url (without the html filename)
	url_parts = full_url.split('/')
	base_url = '/'.join(url_parts[0:-1])+'/'

	# Add the url to the list of processed ones if not already processed
	if (processed_urls.count(full_url) > 0):
		return
	else:
		processed_urls.append(full_url)
		if processed_topics.count(title) > 0:
			print "DUPLICATE SKIPPED:"+title
			return
		else:
			processed_topics.append(title)
		f2.write(str(processed_topics[-1]+' : '+processed_urls[-1]))
		# If not a parentlink or a Subscribe, feedback or Rate link
		#if (not(link.parent is None) and (str(link.parent['class'][0]) == 'parentlink')):
		#	return
		link_text = link.text.encode('utf-8')
		if ((str(link_text).find('Subscribe') < 0) and (full_url.find('#') < 0) and
			(str(link_text).find('Rate') < 0) and (str(link_text).find('feedback') < 0) and
			(str(link_text).find('PDF file for') < 0) and (full_url.find('.pdf') < 0)):
			print 'Title =' + title  
			print 'URL = '+full_url   
			#print 'Parent URL = '+parent_url
			print '\n'		
			# Open the url to get all the Sublinks
			try:
				html = urllib2.urlopen(full_url).read()
			except:
				try:
					sleep(0.5)
					html = urllib2.urlopen(full_url).read()
				except:
					return
			soup = BeautifulSoup(html)
			[s.extract() for s in soup(['style', 'script', '[document]', 'head', 'title', 'span','a'])]
			visible_text = soup.getText()
			# Remove multiple new lines
			visible_text = str((re.sub( '\n+', ' ', visible_text)).encode('utf-8'))
			#print visible_text
			# Save text to the output file
			#f1.write(title+'\n');
			f1.write(visible_text+'\n');
			soup = BeautifulSoup(html)
			# Get all the links in the page
			links = soup.find_all('a',href=True)
			for link in links:
				process_link(link, base_url)

# Main code: Loop over all the models of IBM POWER 7 
for p7_model in p7_models: 
	#connect to the URL of a model
	model_page = urllib2.urlopen(base_p7_url+p7_model+'_landing.htm?locale=en')

	#read html code of main page of model
	html = model_page.read()
	soup = BeautifulSoup(html)
 
	#get all the links on the page
	#links = re.findall('"((http|ftp)s?://.*?)"', html)
	#links = re.findall('href="(.*?).(htm|html)s?', html)
	links = soup.find_all('a',href=True)

	# search all the links for those whose title contains a specific keyword, e.g. troubleshooting
	for l in links:
		link_url = str(l['href'])
		link_title = str(l.contents[0]).lower()
		for k in keywords:
			if (link_title.find(k) > -1): 
				trouble_url = base_p7_url+link_url
				print "\nFound the Troubleshooting Page..\n"
				break;

	#test
	#trouble_url = 'http://www-01.ibm.com/support/knowledgecenter/api/content/POWER7/p7hcg/iphcg_device_commands.htm'
	#base_p7_url = 'http://www-01.ibm.com/support/knowledgecenter/api/content/POWER7/p7hcg/'

	#read the html code of the troubleshooting page
	html = urllib2.urlopen(trouble_url).read()
	soup = BeautifulSoup(html)
	#get all the links in a troubleshooting page 
	links = soup.find_all('a',href=True)

	## search all the links for sub-links and save them
	for link in links:
		process_link(link, base_p7_url) 

f1.close()
f2.close()
# Get the end time
t1 = time()
	
print('\n\n')
print "\n\nProcessed a total of:"
print str(count_links)+" Links"		
print str(len(processed_urls))+" Unique Pages" 
print "In "+str(t1-t0)+' seconds..\n'