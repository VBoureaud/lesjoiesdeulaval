from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from datetime import datetime, timedelta
import json
import unidecode
import random
import time
import re

# TODO 
#  Facultés des sciences de l'éducation -> Trouble Accents
##

#####
### REQUESTING
#####
def httpGet(url):
	try:
		with closing(get(url, stream=True)) as resp:
			if is_valid(resp):
				return resp.content
			else:
				return None

	except RequestException as e:
		log_error('Error during requests to {0] : {1]'.format(url, str(e)))
		return None

def is_valid(resp):
	content_type = resp.headers['Content-type'].lower()
	return (resp.status_code == 200
			and content_type is not None
			and content_type.find('html') > -1)

def log_error(e):
	print(e)

def get_datas(url):
	response = httpGet(url)

	if response is not None:
		html = BeautifulSoup(response.decode('utf-8','ignore'), 'html.parser')
		return html

	raise Exception('Error retriveing contents at {}'.format(url))

def launchChrome(url):
	chrome_options = webdriver.ChromeOptions()
	prefs = {"profile.default_content_setting_values.notifications": 2}
	chrome_options.add_experimental_option("prefs", prefs)

	# A randomizer for the delay
	seconds = 5 + (random.random() * 5)
	# create a new Chrome session
	driver = webdriver.Chrome('./chromedriver', chrome_options=chrome_options)
	driver.implicitly_wait(30)
	# driver.maximize_window()

	# navigate to the application home page
	driver.get(url)
	time.sleep(seconds)
	html = driver.page_source

	page_soup = BeautifulSoup(html, "html.parser")	
	return page_soup

#####
### SORTING
#####
format = '%Y-%m-%dT%H:%M:%S'
def pushByDate(date, item, fac, arr):
	if len(arr) == 0:
		arr.append({
			"title": item['title'],
			"faculte": fac,
			"link": item['link'],
			"date": item['date'],
			"description": item['description'] if 'description' in item else '',
			"lieu": item['lieu'] if 'lieu' in item else '',
		})
		return arr

	count = 0
	for elt in arr:
		if datetime.strptime(elt['date'], format) > date:
			arr.insert(count, {
					"title": item['title'],
					"faculte": fac,
					"link": item['link'],
					"date": item['date'],
					"description": item['description'] if 'description' in item else '',
					"lieu": item['lieu'] if 'lieu' in item else '',
			})
			return arr
		count = count + 1

	arr.append({
			"title": item['title'],
			"faculte": fac,
			"link": item['link'],
			"date": item['date'],
			"description": item['description'] if 'description' in item else '',
			"lieu": item['lieu'] if 'lieu' in item else '',
	})
	return arr

def sortByDateWFac(data):
	yesterday = datetime.now() - timedelta(days=1)
	dataSorted = []
	for key in data:
		for item in data[key]:
			if (datetime.strptime(item['date'], format) > yesterday):
				dataSorted = pushByDate(datetime.strptime(item['date'], format), item, key, dataSorted)
	return dataSorted

def sortByDate(data):
	yesterday = datetime.now() - timedelta(days=1)
	dataSorted = []
	for item in data:
		if (datetime.strptime(item['date'], format) > yesterday):
			dataSorted = pushByDate(datetime.strptime(item['date'], format), item, item['faculte'], dataSorted)
	return dataSorted

####
### UTILS
####
def eventBuilder(
		title,
		link,
		date,
		lieu=None,
		heure=None,
		faculte=None,
	):
	event = {}
	event["title"] = title
	event["link"] = link
	event["date"] = date
	if (lieu is not None):
		event["lieu"] = lieu
	if (heure is not None):
		event["heure"] = heure
	if (faculte is not None):
		event["faculte"] = faculte
	return event

#####
### MANAGORS
#####
def fdManagor(url):
	HTMLcode = launchChrome(url)
	
	year = datetime.now().year
	months = {'janv': 1, 'fev': 2, 'mars': 3, 'avr': 4, 'mai': 5, 'juin': 6, 'juil': 7, 'aout': 8, 'sept': 9, 'oct': 10, 'nov': 11, 'dec': 12}
	events=[]
	eventsHTML= HTMLcode.find("div", {"id": "events"})
	containers = eventsHTML.findAll("a", {"class":"notice"})

	for container in containers:
		try:
			href = "https://www.fd.ulaval.ca" + container['href']
			dateEvent = unidecode.unidecode(container.time.text)
			title = container.div.text

			#Month Gestion
			monthNum = 0
			monthEvent = re.findall(r'[A-Za-z]+', dateEvent)
			if (monthEvent[0] in months):
				monthNum = months[monthEvent[0]]
			else:
				return False

			#Day Gestion
			daysEvent = re.findall(r'\d+', dateEvent)
			if (len(daysEvent) > 1 and int(daysEvent[-1]) - 1 > int(daysEvent[0])):
				start = int(daysEvent[0])
				end = start + len(daysEvent)
				daysEvent= []
				for i in range(start, end):
					daysEvent.append(i)
			
			for day in daysEvent:
				events.append(
					eventBuilder(
						title,
						href,
						datetime(year, int(monthNum), int(day)).isoformat()))

		except AttributeError:
			continue

	return events

def ffggManagor(url):
	months = {'janvier': 1, 'fevrier': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6, 'juillet': 7, 'aout': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'decembre': 12}
	year = datetime.now().year
	events=[]

	HTMLcode = get_datas(url)
	containers = HTMLcode.findAll("article", {"class":"post"})
	for contain in containers:
		try:
			description = contain.find("div", {"class":"description"})
			title = description.find('h2', {"class": "post--title"}).text
			href = url + "" + description.find('h2', {"class": "post--title"}).find('a')['href']
			date = unidecode.unidecode(description.find('p', {"class": "date"}).text)
			month = re.findall(r'[A-Za-z]+', date)[0]
			day = re.findall(r'[0-9]+', date)[0]
			lieu = contain.find("p", {"class": "lieu"}).text.split('Lieu :')[1].strip()

			events.append(
				eventBuilder(
					title,
					href,
					datetime(year, int(months[month]), int(day)).isoformat(),
					lieu))

		except AttributeError:
			continue

	return events

def flshManagor (url):
	months = {'janv': 1, 'fevr': 2, 'mars': 3, 'avr': 4, 'mai': 5, 'juin': 6, 'juil': 7, 'aout': 8, 'sept': 9, 'oct': 10, 'nov': 11, 'dec': 12}
	year = datetime.now().year
	events=[]

	HTMLcode = get_datas(url)
	containers = HTMLcode.findAll("div", {"class": "article-item"})
	for contain in containers:
		try:
			title = contain.find('div', {"class": "card-item-info"}).h2.text
			href = url.replace("/evenements", "") + contain.find('a')['href']
			date = unidecode.unidecode(contain.find('a').text)
			month = re.findall(r'[A-Za-z]+', date)[0]
			day = re.findall(r'[0-9]+', date)[0]
			lieu = contain.find('div', {"class": "article-detail"}).text.strip().replace('\t', '').replace('\n', '')
			horaire = lieu.split('Horaire : ')[1].split('Lieu')[0].strip() if len(lieu.split('Horaire : ')) > 1 else ''
			lieu = lieu.split('Lieu')[len(lieu.split('Lieu')) - 1].strip().replace(':', '').strip() if len(lieu.split('Lieu')) > 1 else ''
			lieu = horaire + " - " + lieu if horaire else lieu

			events.append(
				eventBuilder(
					title,
					href,
					datetime(year, int(months[month]), int(day)).isoformat(),
					lieu))

		except AttributeError:
			continue

	return events

def musManagor(url):
	months = {'janv': 1, 'fevr': 2, 'mars': 3, 'avr': 4, 'mai': 5, 'juin': 6, 'juil': 7, 'aout': 8, 'sept': 9, 'oct': 10, 'nov': 11, 'dec': 12}
	year = datetime.now().year
	events=[]

	HTMLcode = get_datas(url)
	containers = HTMLcode.find("div", {"class": "feature"}).findAll("table")

	for contain in containers:
		try:
			day = contain.find('span', {"class": "iCal_date_date"}).text
			date = unidecode.unidecode(contain.find('span', {"class": "iCal_date_mois"}).text.lower())
			month = re.findall(r'[A-Za-z]+', date)[0]
			title = contain.find('span', {"class": "calendrier_titre"}).text.strip()
			href = contain.find('span', {"class": "calendrier_titre"}).find('a')['href'] if contain.find('span', {"class": "calendrier_titre"}).find('a') else ""
			if href and href.find('javascript:popUp') != -1:
				href = url.replace('calendrier.php', '') + href.replace("javascript:popUp('", "")[:-2]
			lieu = contain.find('span', {"class": "calendrier_lieu"}).text

			events.append(
				eventBuilder(
					title,
					href,
					datetime(year, int(months[month]), int(day)).isoformat(),
					lieu))

		except AttributeError:
			continue

	return events

# Date Month Name to do verif - AND Checked with only one event
def phaManagor(url):
	year = datetime.now().year
	months = {'jan': 1, 'fev': 2, 'mar': 3, 'avr': 4, 'mai': 5, 'jui': 6, 'jui': 7, 'aou': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12}
	events=[]

	HTMLcode = get_datas(url)
	eventsHTML= HTMLcode.findAll("div", {"class": "container"})[1]
	containers = eventsHTML.findAll("article", {"class":"columns"})

	for contain in containers:
		try:
			title = contain.find("div", {"class": "header"}).text.strip()
			href = "https://www.pha.ulaval.ca/" + contain.find("div", {"class": "header"}).find('a')['href']
			lieu = contain.find("div", {"class": "evenement_date_lieu"}).text.strip()
			date = contain.find("time", {"class", "actualite-date"})
			day = date.find("span", {"class", "jour"}).text.strip()
			month = unidecode.unidecode(date.find("span", {"class", "mois"}).text.lower())

			events.append(
				eventBuilder(
					title,
					href,
					datetime(year, int(months[month]), int(day)).isoformat(),
					lieu))

		except AttributeError:
			continue

	return events

# /!\ the site has a bad SSL implementation
# Temporary disable
def fpManagor(url):
	return []

	months = {'janvier': 1, 'fevrier': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6, 'juillet': 7, 'aout': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'decembre': 12}
	year = datetime.now().year
	events=[]

	HTMLcode = get_datas(url)
	containers = HTMLcode.findAll("div", {"class": "evenement"})

	
	for contain in containers:
		try:
			date = unidecode.unidecode(contain.find('div', {"class": "date"}).text.lower())
			month = re.findall(r'[A-Za-z]+', date)[0]
			day = re.findall(r'[0-9]+', date)[0]

			title = contain.find('div', {"class": "content"}).find('a').text
			href = contain.find('div', {"class": "content"}).find('a')['href']
			if href.find('http://www.fp.ulaval.ca/') == -1:
				href = "http://www.fp.ulaval.ca/" + href

			#lieu = contain.find('div', {"class": "contenu"}).findAll('p')[0].text
			lieu = contain.find('div', {"class": "contenu"}).text

			events.append(
				eventBuilder(
					title,
					href,
					datetime(year, int(months[month]), int(day)).isoformat(),
					lieu))

		except AttributeError:
			continue

	return events

#Only if event of one day, multiple day doesnt work yet
def fsaManagor(url):
	months = {'janvier': 1, 'fevrier': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6, 'juillet': 7, 'aout': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'decembre': 12}
	events=[]

	HTMLcode = get_datas(url)
	containers = HTMLcode.findAll("article")

	for contain in containers:
		try:
			date = unidecode.unidecode(contain.find('p', {"class": "date"}).text.lower())
			if len(date.split(' ')) == 4:
				day = re.findall(r'[0-9]+', date.split(' ')[1])[0]
				month = date.split(' ')[2]
				year = date.split(' ')[3]

				title = contain.find('h1').text
				href = unidecode.unidecode(contain.find('h1').find('a')['href'])

				heure = contain.findAll('p')[1].text.replace('Heure', '')
				lieu = contain.findAll('p')[2].text.replace('Lieu', '')

				events.append(
					eventBuilder(
						title,
						href,
						datetime(int(year), int(months[month]), int(day)).isoformat(),
						lieu,
						heure))


		except AttributeError:
			continue
	
	return events


def fmedManagor(url):
	months = {'janv': 1, 'fevr': 2, 'mars': 3, 'avr': 4, 'mai': 5, 'juin': 6, 'juil': 7, 'aout': 8, 'sept': 9, 'oct': 10, 'nov': 11, 'dec': 12}
	year = datetime.now().year
	events=[]

	HTMLcode = get_datas(url)
	containers = HTMLcode.find("ul", {"id": "bxslider_evn"}).findAll('li')

	for contain in containers:
		try:
			date = unidecode.unidecode(contain.find('div', {"class": "carousel-evn-prochain-date"}).text.strip())
			day = re.findall(r'[0-9]+', date)[0]
			month = re.findall(r'[A-Za-z]+', date)[1]

			title = contain.find('div', {"class": "carousel-evn-prochain-texte"}).text.strip()

			href = contain.find('div', {"class": "carousel-evn-hover-bouton"}).find('a')['href']
			lieu = contain.find('span', {"class": "carousel-text-location"}).text.strip()

			events.append(
				eventBuilder(
					title,
					href,
					datetime(year, int(months[month]), int(day)).isoformat(),
					lieu))

		except AttributeError:
			continue

	return events

#Only if event of one day, multiple day doesnt work yet
def ftsrManagor(url):
	months = {'janvier': 1, 'fevrier': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6, 'juillet': 7, 'aout': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'decembre': 12}
	year = datetime.now().year
	events=[]

	HTMLcode = get_datas(url)
	containers = HTMLcode.findAll("div", {"class": "nouvelle"})

	for contain in containers:
		try:
			date = contain.find('p', {"class": "date"}).text
			if len(date.split(' ')) == 3:
				day = date.split(' ')[0]
				month = unidecode.unidecode(date.split(' ')[1])

				title = contain.find('h2').text.strip()
				href = contain.find('h2').find('a')['href']
				lieu = contain.find('div', {"class": "content"}).find('p').text.strip()

				events.append(
					eventBuilder(
						title,
						href,
						datetime(year, int(months[month]), int(day)).isoformat(),
						lieu))

		except AttributeError:
			continue

	return events

def fssManagor(url):
	months = {'janv': 1, 'fevr': 2, 'mars': 3, 'avr': 4, 'mai': 5, 'juin': 6, 'juil': 7, 'aout': 8, 'sept': 9, 'oct': 10, 'nov': 11, 'dec': 12}
	year = datetime.now().year
	events=[]

	HTMLcode = get_datas(url)
	eventsHTML = HTMLcode.find("div", {"class": "grid article-list"})
	containers = eventsHTML.findAll("article", {"class": "article-item-wrapper"})

	for contain in containers:
		try:
			title = contain.find("h2", {"class": "title"}).text
			href = "https://www.fss.ulaval.ca" + contain.find("a", {"class": "article-item"})['href']

			date = contain.find("time", {"class": "date-item"}).text.replace('\n', ' ').strip()
			day = date.split(' ')[0]
			month = unidecode.unidecode(date.split(' ')[1])
			month = re.findall(r'[A-Za-z]+', month)[0]

			events.append(
					eventBuilder(
						title,
						href,
						datetime(year, int(months[month]), int(day)).isoformat()))

		except AttributeError:
			continue

	return events

def fsiManagor(url):
	months = {'janvier': 1, 'fevrier': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6, 'juillet': 7, 'aout': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'decembre': 12}
	year = datetime.now().year
	events=[]

	HTMLcode = get_datas(url)
	containers = HTMLcode.findAll("div", {"class": "evenement"})

	for contain in containers:
		try:
			title= contain.find('h2', {"class": "post--title"}).text
			date= contain.find('p', {"class": "date"}).text.strip()
			day = date.split(' ')[0]
			month = unidecode.unidecode(date.split(' ')[1]).lower()

			href = "https://www.fsi.ulaval.ca/" + contain.findAll('div', {"class": "grid--item"})[0].find('a')['href']
			info = contain.find('div', {"class": "evenement-details"}).text.strip()
			heure = info.split('Heure:')[1].split('Lieu:')[0].strip() if len(info.split('Heure:')) > 1 else ''
			lieu = info.split('Lieu:')[1].split('\n')[0].strip() if len(info.split('Lieu:')) > 1 else ''

			events.append(
					eventBuilder(
						title,
						href,
						datetime(year, int(months[month]), int(day)).isoformat(),
						lieu,
						heure))


		except AttributeError:
			continue
	return events

# TODO REINTEGRATE
def fsgManagor(url):
	return []

	months = {'janvier': 1, 'fevrier': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6, 'juillet': 7, 'aout': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'decembre': 12}
	year = datetime.now().year
	month = datetime.now().month
	events=[]

	HTMLcode = get_datas(url)
	eventsHTML = HTMLcode.find("ul", {"id": "evenements_list"})
	containers = eventsHTML.findAll("li")
	for contain in containers:
		try:			
			day= contain.find('div', {"class": "jour"}).text.strip()

			allEventsForDay = contain.find('ul').findAll('li')
			for containTitle in allEventsForDay:
				title = containTitle.find('h2').text.strip()
				href = "https://www.fsg.ulaval.ca" + containTitle.find('a')['href']
				description = containTitle.find('p', {"class": "bodytext"}).text.strip()

			events.append(
					eventBuilder(
						title,
						href,
						datetime(year, month, int(day)).isoformat(),
						description))

		except AttributeError:
			continue
	return events

# only try with mars avr mai
def fseManagor(url):
	months = {'janv': 1, 'fevr': 2, 'mars': 3, 'avr': 4, 'mai': 5, 'juin': 6, 'juil': 7, 'aout': 8, 'sept': 9, 'oct': 10, 'nov': 11, 'dec': 12}
	year = datetime.now().year
	events=[]

	HTMLcode = get_datas(url)
	eventsHTML = HTMLcode.find("div", {"id": "agenda-accueil"})
	containers = eventsHTML.findAll("div", {"class": "agenda-item"})
	for contain in containers:
		try:			
			date=contain.find('div', {"class": "boite-date"})
			day=date.find('div', {"class": "jour"}).text.strip()
			month= unidecode.unidecode(date.find('div', {"class": "mois"}).text).strip()

			href = contain.find('div', {"class": "boiteg-acc-titre"}).find('a')['href']
			if 'http' not in href:
				href = "https://www.fse.ulaval.ca" + href

			title = contain.find('div', {"class": "boiteg-acc-titre"}).find('a').text.strip()

			events.append(
					eventBuilder(
						title,
						href,
						datetime(year, int(months[month]), int(day)).isoformat()))

		except AttributeError:
			continue
	return events

def fsaaManagor(url):
	months = {'janvier': 1, 'fevrier': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6, 'juillet': 7, 'aout': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'decembre': 12}
	year = datetime.now().year
	events=[]

	HTMLcode = get_datas(url)
	eventsHTML = HTMLcode.find("div", {"id": "tx_fsaaevents_listevent_AjaxContent"})
	containers = eventsHTML.findAll("article")
	for contain in containers:
		try:			
			date=contain.find('div', {"class": "time"}).text.strip()

			day = re.findall(r'[0-9]+', date)[0].strip()
			month = re.findall(r'[A-Za-z]+', date)[1]
			title = contain.find('h3').text.strip()

			href = "https://www.fsaa.ulaval.ca" + contain.find('h3').find('a')['href']

			events.append(
				eventBuilder(
					title,
					href,
					datetime(year, int(months[month]), int(day)).isoformat()))

		except AttributeError:
			continue
	return events


def generalManagor():
	allEvents = {}
	allEvents['fd'] = fdManagor("https://www.fd.ulaval.ca/evenements")
	allEvents['ffgg'] = ffggManagor("https://www.ffgg.ulaval.ca/evenements")
	allEvents['flsh'] = flshManagor ("https://www.flsh.ulaval.ca/evenements")
	allEvents['mus'] = musManagor("https://www.mus.ulaval.ca/calendrier.php")
	allEvents['pha'] = phaManagor("https://www.pha.ulaval.ca/evenements/")
	allEvents['fp'] = fpManagor("https://www.fp.ulaval.ca/notre-faculte/vie-facultaire/evenements/a-venir/tous-les-evenements/")
	allEvents['fsa'] = fsaManagor("https://www4.fsa.ulaval.ca/evenements/")
	allEvents['fmed'] = fmedManagor("http://www.fmed.ulaval.ca/faculte-et-reseau/a-surveiller/calendrier-facultaire/")
	allEvents['ftsr'] = ftsrManagor("https://www.ftsr.ulaval.ca/notre-faculte/toutes-les-actualites/toutes-les-actualites/")
	allEvents['fss'] = fssManagor("https://www.fss.ulaval.ca/evenements")
	allEvents['fsi'] = fsiManagor(
		"https://www.fsi.ulaval.ca/evenements?annee="+ str(datetime.now().year)+"&mois=0"+str(datetime.now().month)
 		if len(str(datetime.now().month)) == 1 else
 		"https://www.fsi.ulaval.ca/evenements?annee="+ str(datetime.now().year) +"&mois="+ str(datetime.now().month))
	allEvents['fsg'] = fsgManagor("https://www.fsg.ulaval.ca/accueil/calendrier-complet/")
	allEvents['fse'] = fseManagor("https://www.fse.ulaval.ca/actualites/")
	allEvents['fsaa'] = fsaaManagor("https://www.fsaa.ulaval.ca/faculte/actualites-et-evenements/evenements/lister_evenements/")

	return allEvents

HTMLcode = get_datas('https://drive.google.com/drive/folders/1yo-2l4VCmNisIgb7kHyJcRjsTJQ3QI_T')

regex = 'https://lh3.google.com/u/0/d/+'
#regex=https://lh3.google.com/u/0/d/1_Ej-9UFRWVHPXJ0u2F1K20l6R0kjIsEn=w200-h190-p-k-nu-iv1
find = re.findall(regex, HTMLcode)
print(find)


# Normal use
# dataSorted = sortByDateWFac(generalManagor())
# print(json.dumps(dataSorted))

# Exemple 
#print(fpManagor("https://www.fp.ulaval.ca/notre-faculte/vie-facultaire/evenements/a-venir/tous-les-evenements/"))

# Add some news events in your database
# with open('tmp', 'r') as fd:
#   data = fd.read()
# data = json.loads(data)

# data.append(eventBuilder('Journée d\'étude sur le vieillissement', 'http://www.fp.ulaval.ca/notre-faculte/vie-facultaire/evenements/a-venir/tous-les-evenements/evenement-single-view/article/journee-detudes-sur-le-vieillissement/', '2019-04-29T00:00:00', 'Lundi 29 avril, 9 h à 15 h, (Pavillon Gene-H.-Kruger, salles 2320-2330)\r\nLa professeure Marie-Andrée Ricard prononcera une conférence intitulée « La beauté sans apprêt » à l\'occasion d\'une journée d\'étude sur le...', None, 'fp'))
# data.append(eventBuilder('Réfléchir sur l\'eau (colloque étudiant)', 'https://www.fp.ulaval.ca/notre-faculte/vie-facultaire/evenements/a-venir/tous-les-evenements/evenement-single-view/article/reflechir-sur-leau-colloque-etudiant/', '2019-04-29T00:00:00', 'Lundi 29 avril,  11 h 15 à 17 h, (Pavillon Félix-Antoine-Savard, salle 413)', None, 'fp'))
# data.append(eventBuilder('Marie-Anne Casselot prononcera une conférence dans le cadre de l\'Université féministe d\'été', 'http://www.fp.ulaval.ca/notre-faculte/vie-facultaire/evenements/a-venir/tous-les-evenements/evenement-single-view/article/marie-anne-casselot-prononcera-une-conference-dans-le-cadre-de-luniversite-feministe-dete-1/', '2019-05-21T00:00:00', 'Mardi 21 mai 13 h 30', None, 'fp'))

# print(json.dumps(sortByDate(data)))