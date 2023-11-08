import requests
import sqlite3
from selectolax.parser import HTMLParser

def get_html(url, pages):
	offers = []
	kv = 0

	for page in range(1, pages+1):
		if page > 1:
			sub_url = url + "&pN=" + str(page)
		else:
			sub_url = url

		response = requests.get(url=sub_url)
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
			offer['total_square'] = float(list_ttx[i+4].text())
			offer['living_square'] = float(list_ttx[i+5].text())
			offer['kitchen_square'] = float(list_ttx[i+6].text())
			offer['price'] = int(list_ttx[i+8].text())

			for key, value in offer.items():
				print(key, value)
			print('-------------------------')
			print()
			offers.append(offer)
	
	return offers


def db(url):
	offers = get_html(url, 5)
	connection = sqlite3.connect('db/magnitogorsk.db')
	cursor = connection.cursor()
	
	for offer in offers:
		cursor.execute("""
			INSERT INTO offers 
			VALUES (NULL, :type, :district, :adress, :floor, :total_square, :living_square, :kitchen_square, :price)
			""",
			offer
			)
		connection.commit()
		print(f"offer {offer['id']} added to database")

	connection.close()


def main():
	url = "http://citystar.ru/detal.htm?d=43&nm=%CE%E1%FA%FF%E2%EB%E5%ED%E8%FF%20-%20%CF%F0%EE%E4%E0%EC%20%EA%E2%E0%F0%F2%E8%F0%F3%20%E2%20%E3.%20%CC%E0%E3%ED%E8%F2%EE%E3%EE%F0%F1%EA%E5"
	# get_html(url, 5)
	db(url)

if __name__ == '__main__':
	main()


