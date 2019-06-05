import re
import imp
import json
from  bs4 import BeautifulSoup
from urlparse import urlparse
import chardet
import urllib2

api = imp.load_source('api','/var/bot/dump_/scraper/api/flipapi.py')

#from analyze import analyze

FLIPKART_ID = ""
FLIPKART_TOKEN = ""

class flipkart():
	def __init__(self, content, url, header):
		self.dict= {}
		self.content = content
		self.header = header
		self.url = url

	def fetch(self):
	    if self.content:
	        self.soup = BeautifulSoup(self.content, 'lxml')

	    try:
	        self.get_item_info()
	    except Exception as e:
	    	print e

	    try:
	        self.get_links()
	    except Exception as e:
	        print e


	    return self.dict

	def get_flipkart_item_id(self):
	    itemid_search = re.search(r'pid=(\w{16})', self.url)
	    if itemid_search:
	        return itemid_search.group(1)
	    return None

	def re_encode(self,string):
	    try:
	        string = string.encode('ascii', 'ignore')
	    except Exception as e:
	        string = string.encode('UTF-8')
	        print e
	    return string

	def get_brdcrm(self):
		brdcrm_div = self.soup.find('div',{'class':'clp-breadcrumb'})
		if brdcrm_div:
			brdcrm_list = []
			if brdcrm_div:
				for li in brdcrm_div.findAll('li'):
					brdcrm_list.append(self.re_encode(li.text.strip()))			
			if len(brdcrm_list) > 0:
				self.dict['brdcrm'] = brdcrm_list
		return brdcrm_list

	def get_prod_spec(self):
		prod_spec = []
		prod_spec_div = self.soup.find('div', {'class':'productSpecs'})

		if prod_spec_div:
			prod_spec_tbl = prod_spec_div.findAll('table', {'class':'specTable'})
			for tbl in prod_spec_tbl:
				for tr in tbl.findAll('tr'):
					left = tr.find('td', {'class':'specsKey'})
					right = tr.find('td', {'class':'specsValue'})
					if left and right:
						prod_spec.append((self.re_encode(left.text.strip()),self.re_encode(right.text.strip())))

		return prod_spec

	def get_item_info(self):
	    itemid = self.get_flipkart_item_id()
	    
	    if itemid:
	    	fk = api.FlipkartAPI(FLIPKART_ID,FLIPKART_TOKEN)
	        try:
	        	product = fk.getProductByID(itemid)

	        	if product:
	        		self.dict['title'] = product.title
	        		self.dict['mrp_price'] = "%s %s" % (product.maximumRetailPrice['currency'],product.maximumRetailPrice['amount'])
	        		self.dict['selling_price'] = "%s %s" % (product.sellingPrice['currency'],product.sellingPrice['amount'])
	        		self.dict['img'] = product.imageUrls["400x400"]
	        		self.dict['brdcrm'] = self.get_brdcrm()

	        		non_specs = ['title','maximumRetailPrice','sellingPrice','imageUrls','categories']

		      		specs = list()

	        		for prop in dir(product):
	        			if not prop.startswith('__') and not prop in non_specs:
	        				specs.append( (prop,getattr(product,prop)) )

	        		self.dict['spec'] = self.get_prod_spec()
	        		
	        except Exception as e:
	        	print e

	def get_links(self):
	    links = []
	    host = urlparse( self.url ).hostname
	    scheme = urlparse( self.url ).scheme
	    domain_link = scheme+'://'+host

	    for a in self.soup.find_all(href=True):
	        
	        href = a['href']
	        if not href or len(href) <= 1:
	            continue
	        elif 'javascript' in href.lower() or 'review' in href.lower() or 'facets' in href.lower() or 'login' in href.lower() or 'android-app:' in href.lower() or 'brand' in href.lower():
	        	continue
	        else:
	            href = href.strip()
	        if href[0] == '/':
	            href = (domain_link + href).strip()
	        elif href[:4] == 'http':
	            href = href.strip()
	        elif href[0] != '/' and href[:4] != 'http':
	            href = ( domain_link + '/' + href ).strip()
	        if '#' in href:
	            indx = href.index('#')
	            href = href[:indx].strip()
	        if href in links:
	            continue

	        links.append(self.re_encode(href))

	    self.dict['a_href'] = links
