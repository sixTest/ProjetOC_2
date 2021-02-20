import requests
from bs4 import BeautifulSoup
import csv
import os
import threading

HEADERS = ["product_page_url",
		   "universal_ product_code (upc)",
		   "title",
		   "price_including_tax",
		   "price_excluding_tax",
		   "number_available",
		   "product_description",
		   "category",
		   "review_rating",
		   "image_url"]

MAXIMUM_RESULT_PER_PAGE = 20
URL_BASE ='http://books.toscrape.com/'


class ResponseError(Exception):
	def __init__(self, resp_status):
		self.resp_status = resp_status

	def __str__(self):
		return f"Une erreur est survenu lors de la requete 'get' code status : ({self.resp_status})"


def getInformationsOneBook(resp):

	soup = BeautifulSoup(resp.content, 'html.parser')
	title = soup.find('h1').text
	description = soup.find('meta', attrs={'name':'description'})['content']
	category = soup.find('ul').findAll('li')[2].text
	image_url = URL_BASE + soup.find('img')['src']

	product_information_tableaux = soup.find('table', attrs={'class':'table table-striped'}).findAll('tr')
	product_information_dictionnaire = {tr.th.text: tr.td.text for tr in product_information_tableaux}
	universal_product_code = product_information_dictionnaire['UPC']
	price_including_tax = product_information_dictionnaire['Price (incl. tax)']
	price_excluding_tax = product_information_dictionnaire['Price (excl. tax)']
	number_available = product_information_dictionnaire['Availability']
	review_rating = product_information_dictionnaire['Number of reviews']

	return title,description,category,image_url,universal_product_code,price_excluding_tax,price_including_tax,number_available,review_rating


def getNumberPageForCategory(resp):
	soup = BeautifulSoup(resp.text, 'html.parser')
	npage = int(soup.find('form', attrs={'method': 'get', 'class': 'form-horizontal'}).strong.text)
	return int(npage/MAXIMUM_RESULT_PER_PAGE) + 1


def getAllUrlsBooksOnePageCategory(resp):
	soup = BeautifulSoup(resp.text, 'html.parser')
	l_li = soup.findAll('li', attrs={'class': 'col-xs-6 col-sm-4 col-md-3 col-lg-3'})
	return [li.a['href'] for li in l_li]


def getUrlsBooksInCategory(url_category, npage):

	urls = []
	for i in range(1,npage+1):

		if i == 1:
			resp = requests.get(url_category)
			if resp.ok:
				urls.extend(getAllUrlsBooksOnePageCategory(resp))
		else:
			url_page = url_category.replace(os.path.basename(url_category), f'page-{i}.html')
			resp = requests.get(url_page)
			if resp.ok:
				urls.extend(getAllUrlsBooksOnePageCategory(resp))

	return [url.replace('../../../', 'http://books.toscrape.com/catalogue/' ) for url in urls]

def getInformationsAllBooksInCategory(url_category):

	informations = []
	resp = requests.get(url_category)
	if resp.ok:
		npage = getNumberPageForCategory(resp)
		urls = getUrlsBooksInCategory(url_category, npage)

		for url in urls:
			resp = requests.get(url)
			if resp.ok:
				informations.append((url, *getInformationsOneBook(resp)))
	else:
		raise ResponseError(resp.status_code)

	return informations

def getUrlsAllCategory():

	resp = requests.get(URL_BASE)
	if resp.ok:
		soup = BeautifulSoup(resp.text, 'html.parser')
		l_a = soup.find('ul', attrs={'class': 'nav nav-list'}).ul.findAll('a')
	else:
		raise ResponseError(resp.status_code)

	return [ URL_BASE+a['href'] for a in l_a ]

def downloadingImgBooks(urls, path):
	nimg = 0
	for url in urls:
		with open(path+'/'+os.path.basename(url), 'wb') as f:

			resp = requests.get(url)
			if resp.ok:
				f.write(resp.content)
				nimg+=1
	return nimg

def writeCSV(headers, values, path, name_file):

	with open(f'{path}/{name_file}.csv', 'w', newline='', encoding='utf-8') as f:

		writer = csv.writer(f)
		writer.writerow(headers)
		writer.writerows(values)

class MyThread(threading.Thread):
	def __init__(self, url_category, path_csv, path_img):
		threading.Thread.__init__(self)
		self.informations = []
		self.url_category = url_category
		self.path_csv = path_csv
		self.path_img = path_img
		self.nbooks = 0
		self.nimg = 0

	def run(self):

		try:

			name_category = self.url_category.split('/')[-2]
			print(f'Chargement des livres de la catégorie {name_category}.')
			self.informations = getInformationsAllBooksInCategory(self.url_category)
			writeCSV(HEADERS, self.informations, self.path_csv, name_category)
			url_img = [ inf[4] for inf in self.informations ]
			self.nimg = downloadingImgBooks(url_img, self.path_img)
			self.nbooks = len(self.informations)

		except ResponseError as e:
			print(e)

os.mkdir('./images')
os.mkdir('./csv')

threads = []
for url_category in getUrlsAllCategory():

	name_category = url_category.split('/')[-2]
	th = MyThread(url_category, './csv', './images')
	th.start()
	threads.append(th)

for th in threads:
	th.join()

ncategory = sum([1 for th in threads if th.informations])
nbooks = sum([th.nbooks for th in threads])
nimg = sum([th.nimg for th in threads])

print(f'Total de catégorie récuperé {ncategory}.\nTotal de livres récupéré {nbooks}.\nTotal images récuperé {nimg}')
