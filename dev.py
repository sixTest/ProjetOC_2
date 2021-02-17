import requests
from bs4 import BeautifulSoup

HEADERS = ["product_page_url",
		   "universal_ product_code (upc)",
		   "title","price_including_tax",
		   "price_excluding_tax",
		   "number_available",
		   "product_description",
		   "category",
		   "review_rating","image_url"]

URL_BASE ='http://books.toscrape.com/'

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