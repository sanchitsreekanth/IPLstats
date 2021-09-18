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


def get_player_ids(series_id, match_id,player_dict):
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


def get_matches(series_id):
	url = 'https://www.espncricinfo.com/series/{}/match-results'.format(series_id)
	page = requests.get(url)
	bs = BeautifulSoup(page.content,'lxml')
	matches = bs.find_all('a',class_ = 'match-info-link-FIXTURES')
	ids = [i['href'].split('/')[3] for i in matches]

	return ids[::-1]

def get_player_info(player_id):
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

