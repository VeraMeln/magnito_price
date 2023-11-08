import requests
from selectolax.parser import HTMLParser

def get_html(url):
	offers = []
	kv = 0

	response = requests.get(url=url)
	response.encoding = 'windows-1251'
	html = response.text

	tree = HTMLParser(html, detect_encoding=False)
	items = tree.css(".tbrd")
	# print('len(items):', len(items))
	stop = len(items[4].css('.ttx'))
	
	list_ttx = items[4].css('.ttx')

	
	for i in range(2, stop, 14):
		offer = {}
		kv += 1
		print('объявление №', kv)
		offer['id'] = kv
		offer['type'] = list_ttx[i].text()
		offer['district'] = list_ttx[i+1].text()
		offer['adress'] = list_ttx[i+2].text()
		offer['floor'] = list_ttx[i+3].text()
		offer['total_square'] = list_ttx[i+4].text()
		offer['living_square'] = list_ttx[i+5].text()
		offer['kitchen_square'] = list_ttx[i+6].text()
		offer['price'] = list_ttx[i+8].text()

		for key, value in offer.items():
			print(key, value)
		print('-------------------------')
		print()
		offers.append(offer)




def main():
	url = "http://citystar.ru/detal.htm?d=43&nm=%CE%E1%FA%FF%E2%EB%E5%ED%E8%FF%20-%20%CF%F0%EE%E4%E0%EC%20%EA%E2%E0%F0%F2%E8%F0%F3%20%E2%20%E3.%20%CC%E0%E3%ED%E8%F2%EE%E3%EE%F0%F1%EA%E5"
	url_1 = "http://citystar.ru/detal.htm?d=43&nm=%CE%E1%FA%FF%E2%EB%E5%ED%E8%FF+%2D+%CF%F0%EE%E4%E0%EC+%EA%E2%E0%F0%F2%E8%F0%F3+%E2+%E3%2E+%CC%E0%E3%ED%E8%F2%EE%E3%EE%F0%F1%EA%E5&pN=5"
	get_html(url)

if __name__ == '__main__':
	main()