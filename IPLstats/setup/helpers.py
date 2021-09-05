import requests
from bs4 import BeautifulSoup
import csv
import os
import sys
import mysql.connector
from mysql.connector import Error
import pandas as pd
import re
import unicodedata
from prettytable import PrettyTable
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from settings import teams

def getPlayerIds(series_id, match_id,player_dict):
	url = 'https://www.espncricinfo.com/series/'+ str(series_id) + '/' + str(match_id) + '/full-scorecard'
	page = requests.get(url)
	bs = BeautifulSoup(page.content,'lxml')
	table_body = bs.find_all('a','title',class_ = 'small')
	for player in table_body:
		try:
			q = player['title'].split()
			player_name = ' '.join(q[4:])
			player_id = player['href'].split('-')[-1]
			if player_name not in player_dict:
				player_dict[player_name] = player_id
		except:
			pass


def getMatches(series_id):
	url = 'https://www.espncricinfo.com/series/{}/match-results'.format(series_id)
	page = requests.get(url)
	bs = BeautifulSoup(page.content,'lxml')
	matches = bs.find_all('a',class_ = 'match-info-link-FIXTURES')
	ids = [i['href'].split('/')[3] for i in matches]

	return ids[::-1]

def getPlayerInfo(player_id):
	batting_style = 'NULL'
	bowling_style = 'NULL'
	role = 'NULL'
	name = 'NULL'
	country = 'NULL'
	try:
		url = 'http://www.espncricinfo.com/ci/content/player/{}.html'.format(player_id)
		page = requests.get(url)
		bs = BeautifulSoup(page.content,'lxml')
		profile = bs.find(class_ = 'player-card__details')
		name = profile.h2.contents[0]
		if "'" in name:
			name = name.replace("'"," ")
		q = profile.find_all('span')
		country = q[0].contents[0]
		
		w = bs.find(class_ = 'player_overview-grid')
		try:
			role = q[2].contents[0]
		except:
			#print(name,'1')
			pass
		e = w.find_all('p')
		e = [ele.contents[0] for ele in e]
		
		try:	
			index = e.index('Batting Style')
			batting_style = w.find_all('h5')[index].contents[0]
		except:
			#print(name,'2')
			pass
		try:
			if role != 'Wicketkeeper batter':
				bowling_style = w.find_all('h5')[index+1].contents[0]
		except:
			#print(name,'3')
			pass
	except:
		pass
	return int(player_id),name,country,role,batting_style,bowling_style

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
	"""
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
	 
	percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
	filledLength = int(length * iteration // total)
	bar = fill * filledLength + '-' * (length - filledLength)
	print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = "\r")
	# Print New Line on Complete
	if iteration == total: 
		print()

def create_server_connection(host_name,user_name,user_password):
	connection = None
	try:
		connection = mysql.connector.connect(
			host=host_name,
			user=user_name,
			passwd=user_password)
		print("MySQL Database connection successful")
	except Error as err:
		print(f"Error: '{err}'")

	return connection

def create_db_connection(host_name,user_name,user_password,db_name,verbosity=1):
	connection = None
	try:
		connection = mysql.connector.connect(
			host=host_name,
			user=user_name,
			passwd=user_password,
			database = db_name)
		if verbosity ==0:
			print("MySQL Database connection successful")
	except Error as err:
		print(f"Error: '{err}'")

	return connection

def execute_query(connection, query,verbosity=1):
	cursor = connection.cursor()
	try:
		cursor.execute(query)
		if verbosity == 1:
			print("Query Successful")
		a = cursor.fetchall()
		cursor.close()
		connection.commit()
		return a
	except Error as err:
		print(f"Error: '{err}'")

def create_database(connection, query):
	cursor = connection.cursor()
	try:
		cursor.execute(query)
		print("Database created successfully")
	except Error as err:
		print(f"Error: '{err}'")

def battingScorecard(series_id,match_id):

	url = 'https://www.espncricinfo.com/series/{}/{}/full-scorecard'.format(series_id,match_id)
	page =  requests.get(url)
	soup = BeautifulSoup(page.content,'lxml')
	table_body=soup.find_all('tbody')
	q = soup.find_all(class_ = 'header-title label')[:2]
	q = [i.text.split('INNINGS')[0] for i in q]
	ret = list()
	for i,table in enumerate(table_body[0:4:2]):
		try:
			temp = list()
			team = [teams[j][1] for j in teams if j in q[i]][0]
			opp = [teams[j][1] for j in teams if j in q[::-1][i]][0]
			rows = table.find_all('tr')
			for position,row in enumerate(rows[:-1:2]):
				colvals = row.find_all('td')
				colvals = [k.text for k in colvals]
				name = colvals[0]
				name = name.split('(c)')[0]
				name = name.split('†')[0]
				if "'"  in name:
					name = name.replace("'"," ")
				status,runs,balls,fours,sixes,sr = colvals[1],colvals[2],colvals[3],colvals[5],colvals[6],colvals[7]
				if sr == '-': sr = '0.0'
				if position == 1:
					position = 0
				if runs == '-':
					continue
				temp.append([unicodedata.normalize("NFKD", name)[:-1],team,opp,position+1,status,int(runs),int(balls),int(fours),int(sixes),float(sr),match_id])
			ret.append(temp)
		except:
			pass
		

	return ret

def bowlingScorecard(series_id,match_id):

	url = 'https://www.espncricinfo.com/series/{}/{}/full-scorecard'.format(series_id,match_id)
	page =  requests.get(url)
	soup = BeautifulSoup(page.content,'lxml')
	table_body=soup.find_all('tbody')
	q = soup.find_all(class_ = 'header-title label')[:2]
	q = [i.text.split('INNINGS')[0] for i in q]
	q = q[::-1]
	ret = list()
	for i,table in enumerate(table_body[1:4:2]):
		try:
			temp = list()
			team = [teams[j][1] for j in teams if j in q[i]][0]
			opp = [teams[j][1] for j in teams if j in q[::-1][i]][0]
			rows = table.find_all('tr')
			for row in rows:
				colvals = row.find_all('td')
				colvals = [i.text for i in colvals]
				name = colvals[0].split('(c)')[0]
				if "'"  in name:
					name = name.replace("'"," ")
				overs,maidens,run,wickets,eco,dots,f,s,w,n = colvals[1],colvals[2],colvals[3],colvals[4],colvals[5],colvals[6],colvals[7],colvals[8],colvals[9],colvals[10]
				temp.append([name,team,opp,float(overs),int(maidens),int(run),int(wickets),float(eco),match_id]) 
			ret.append(temp)
		except:
			pass
		return ret
