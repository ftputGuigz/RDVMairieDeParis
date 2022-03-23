from concurrent.futures import thread
from genericpath import exists
from pickle import FALSE
from posixpath import split
from queue import Empty
from tkinter import W
from urllib import request
from webbrowser import BaseBrowser
from datetime import date
from sys import platform
import time
import sys
from signal import signal, SIGINT
from notifypy import Notify
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

""" Chrome_options set up chrome browser to NOT shut down after a slot is found
on the website, and give back control to the user for CAPTCHA INPUT  """
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

Blue= "\u001b[34;1m"
Reset= "\u001b[0m"
Red= "\u001b[31;1m"
Yellow= "\u001b[33;1m"
White= "\u001b[37;1m"

""" This is the starting point of any HTTP REQUEST """
calendar_url = "https://teleservices.paris.fr/rdvtitres/jsp/site/Portal.jsp?page=appointment&view=getViewAppointmentCalendar&id_form="

""" This dictionnary contains all the Mairies-Id as used by the teleservice.paris.fr"""
Mairies = {
	1 : "28",
	2 : "29",
	3 : "29",
	4 : "29",
	5 : "30",
	6 : "31",
	7 : "32",
	8 : "33",
	9 : "34",
	10 : "35",
	11 : "36",
	12 : "37",
	13 : "38",
	14 : "39",
	15 : "40",
	16 : "41",
	17 : "42",
	18 : "43",
	19 : "44",
	20 : "45",
}

def notifyMe():
	""" This is the function managing the notification on user system, 
	MacOS is managed for now """

	notification = Notify()
	notification.title = "RDVMairieDeParis.py"
	notification.message = "Form is waiting for your final input !"
	notification.audio = "./Glass.wav"

	notification.send()

def printparseError():
	""" This Parse error appears if error is detected in the program args """

	print("Mauvais nombre d'arguments.")
	print("La syntaxe est la suivante : python3 RDVMairieDeParis.py <Code Postal> <Date de RDV souhaitée> <Heure de RDV souhaitée>")
	print("Les codes postaux gérés sont ceux compris entre 75001 et 75020. Exemple: 75014")
	print("La Date de RDV est au format JJ/MM/YY. Exemple: 08/12/2022 ou 21/09/2022")
	print("L'heure du RDV est au format HH:MM. Exemple: 8:54 ou 17:30")


def parseArgs(argc, args):
	""" This parse the 1 or 3 (for now) args inputed by user """
	if argc is 0:
		return None
	
	new_list = []

	for elem in args:
		if not elem.strip():
			print("Un ou plusieurs arguments sont vides.\nEssayez encore.")
			return None;

		if elem is args[0]:
			if len(elem) != 5:
				print("Le code postal ne peut avoir que 5 chiffres\nEssayez encore.")
				return None
			if elem[:3] != "750":
				print("La syntaxe est du type : <750XX>, XX est votre numero d'arrondissement. Exemple : '75019' ou '75001'\nEssayez encore.")
				return None
			if int(elem[3:]) < 1 or int(elem[3:]) > 20:
				print("Le numéro d'arrondissement doit être compris entre 1 et 20.\nEssayez encore.")
				return None
			else:
				new_list.append(int(elem[3:]))
			if argc is 1:
				return new_list
			else:
				continue


		#improve PARSING OF DATE
		if elem is args[1]:
			today = date.today()
			d3 = today.strftime("%d/%m/%Y")
			if d3[2:] != elem[2:]:
				print("Choose an appointment in the current Month and Year Please")
				return None
			elif int(elem[:2]) > 31 or int(elem[:2]) < 1:
				print("Choose a day between 1 and 31 of this month, in the current Month and Year Please")	
				return None
			else:
				formated_elem = (elem[:2], elem[3:5], elem[6:])
				new_list.append(formated_elem)
			if argc is 2:
				return new_list
			else:
				continue

		if elem is args[2]:
			splited = elem.partition(":")
			if not splited[1] and not splited[2] or int(splited[0]) > 19 or int(splited[0]) < 8 \
			or int(splited[2]) < 0 or int(splited[2]) > 59 \
			or (int(splited[0]) == 19 and int(splited[2]) > 0) \
			or (int(splited[0]) == 8 and int(splited[2]) < 30):
				print("La syntaxe est du type <HH:MM>. Choisissez un créneau entre 8h30 et 19h00. Exemple : '08:45' ou '17:30'.")
				return None
			else:
				new_list.append((splited[0], splited[2]))
	return new_list

def getKey(nb):
	""" This function return a str needed to access field in dictionnary 
	created earlier on user input """

	if nb == 0:
		return ("nom")
	elif nb == 1:
		return ("prenom")
	elif nb == 2:
		return ("email")
	elif nb == 3:
		return ("email")
	elif nb == 4:
		return ("telephone")
	elif nb == 5:
		return ("code postal")

def fillForm(browser):
	""" This function fill the fields of a page using XPATH to navigate from 
	case to case, using what the user gave in stdin earlier """

	fields = browser.find_elements(By.CLASS_NAME, "form-control")
	counter = 0
	for elem in fields:
		elem.send_keys(inputs[getKey(counter)])
		counter += 1
	tmp = browser.find_element(By.XPATH, '//*[@id="form-validate"]/div/div[3]/div/div/button')
	tmp.click()


def bookAnySlot(arrond, refresh=True):
	""" This function books any slot for a given Mairie, 
	using detection of calendar class, which appears if at least ONE slot is available.
	So this function while loop as long as calendar elem is not detected, 
	then may proceed """

	request_url = calendar_url + Mairies[arrond]
	browser.get(request_url)
	timer = WebDriverWait(browser, 2)
	while True:
		try:
			timer.until(EC.presence_of_all_elements_located((By.ID, "calendar")))
		except Exception:
			if refresh is False:
				return 0
			browser.refresh()
		else:
			content = browser.find_element(by=By.CSS_SELECTOR, value="a[class='fc-day-grid-event fc-h-event fc-event fc-start fc-end ']")
			browser.get(content.get_attribute("href"))
			fillForm(browser)
			notifyMe()
			return 1

def scanMairies():
	while True:
		for i in range(len(Mairies)):
			if (i + 1) is 3 or (i + 1) is 4:
				continue
			if bookAnySlot(i + 1, refresh=False):
				return

def bookSlot(url,refresh=True):
	browser.get(url)
	timer = WebDriverWait(browser, 2)
	while True:
		try:
			timer.until(EC.presence_of_all_elements_located(By.CLASS_NAME, "form-control"))
		except Exception:
			if refresh is False:
				return 0
			browser.refresh()
		else:
			fillForm(browser)
			Notify()
	return

def quarterFix(minutes):
	if (minutes % 15 == 0):
		return minutes
	else:
		quarts = []
		idx = 0
		while idx != 60:
			quarts.append(idx)
			idx += 15
		shortest_span = 60
		for elem in quarts:
			dist = abs(minutes - elem)
			if dist < shortest_span:
				shortest_span = dist
		return shortest_span


def bookWantedHour(args):

	main_url = calendar_url + Mairies[args[0]]
	date_of_rdv = "&starting_date_time=" + args[1][2] + '-' + args[1][1] + '-' + args[1][0]
	main_url += date_of_rdv
	trailer_url = "&modif_date=false&anchor=step3"
	while True:
		startHour = int(args[2][0])
		startMins = quarterFix(int(args[2][1]))
		Hour = startHour
		Mins = startMins
		for i in range(4):
			hour_url = 'T' + (str(Hour)).rjust(2, '0') + ':' + str(Mins).rjust(2, '0')
			tmp_url = main_url + hour_url + trailer_url
			print(tmp_url)
			if bookSlot(tmp_url, False):
				return
			Mins += 15
			if Mins == 60:
				Hour += 1
				Mins = 0
			if Hour == 19 and Mins == 15:
				break
			elif Hour == startHour + 1 and Mins == startMins:
				break
	return
		


def	bookWantedDay(args):
	""" This function find a Mairie and a day and iter through all hour of the day until an open slot is found """
	
	## FORMAT == https://teleservices.paris.fr/rdvtitres/jsp/site/Portal.jsp?page=appointment&view=getViewAppointmentCalendar&id_form=35&starting_date_time=2022-03-22T09:00&modif_date=false&anchor=step3 ##
	main_url = calendar_url + Mairies[args[0]]
	date_of_rdv = "&starting_date_time=" + args[1][2] + '-' + args[1][1] + '-' + args[1][0]
	main_url += date_of_rdv
	trailer_url = "&modif_date=false&anchor=step3"
	while True:
		Hour = 8
		while Hour != 20:
			if Hour == 8:
				Mins = 30
			else:
				Mins = 0
			while Mins != 60:
				hour_url = 'T' + (str(Hour)).rjust(2, '0') + ':' + str(Mins).rjust(2, '0')
				tmp_url = main_url + hour_url + trailer_url
				if bookSlot(tmp_url, False):
					return
				Mins += 15
				if Hour == 19 and Mins == 15:
					break
			Hour += 1
	return

def getInput():
	""" This function request user input for form completion and store it in a 
	dictionnary. Parsing may be requested to avoid numerical input in first and 
	lastaname, then showing input to user, and asking him if ok or if redo 
	is necessary """

	are_you_happy = False
	new_dico = {}
	
	while not are_you_happy:
		new_dico["prenom"] = input("Entrez votre prénom: ").strip()
		new_dico["nom"] = input("Entrez votre nom de famille: ").strip()
		new_dico["email"] = input("Entrez votre e-mail: ").strip()
		new_dico["telephone"] = input("Entrez votre numéro de téléphone (10 chiffres): ").strip()
		new_dico["code postal"] = input("Entrez votre code postal (Tapez 99999 si vous résidez à l'étranger.) : ").strip()
		print()
		""" Imprimer input """
		for key, word in new_dico.items():
				print(key, word, sep=" : ")
		while True:
			resp = input("Êtes-vous satisfait par vos informations ? Tapez 'oui' ou 'non' : ")
			if resp.strip() == "oui":
				are_you_happy = True;
				break
			elif resp.strip() == "non":
				print("Essayons encore !")
				new_dico.clear()
				break
			else:
				print("Je n'ai pas compris votre réponse.")
	return new_dico

def sigint_handler(sig, frame):
	print("Fin du Programme. A bientot en Mairie !")
	exit(0)

if __name__ == "__main__":

	signal(SIGINT, sigint_handler)

	argc = len(sys.argv) - 1
	if argc > 3:
		printparseError()
	else:
		args = parseArgs(argc, sys.argv[1:])
	if not args and argc != 0:
		exit()
	inputs = getInput()
	""" ARGC == 0 ---> program look for first available slot in any Mairie 
		ARGC == 1 ---> program look for specified Mairie and refresh until it gets a slot
		ARGC == 2 ---> program look for specified Mairie at specified day, until it finds a slot looping through all hours
		ARGS == 3 ---> program look for specified Mairie at specified day, at specified time -+30 min, until it finds a slot
	"""
	browser = webdriver.Chrome(options=chrome_options)
	if argc is 0:
		scanMairies()
	elif argc is 1:	
		bookAnySlot(args[0])
	elif argc is 2:
		bookWantedDay(args)
	else:
		bookWantedHour(args)
	exit(0)
