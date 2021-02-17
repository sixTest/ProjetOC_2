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