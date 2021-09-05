import requests
from bs4 import BeautifulSoup
import csv
import os, sys

from settings import DB_NAME,USER,PWD, series
from tools.db_funcs import execute_query, create_db_connection
from tools.setup_helpers import get_matches,get_player_ids, get_player_info
from tools.match_helpers import get_match_details,batting_scorecard, bowling_scorecard
cwd = os.getcwd()

def updates_available(year,y):
	series_id = series[year]
	if year > int(y):
		flag = True
		matches_in_year = get_matches(series_id)
	else:
		series_id = series[year]
		matches_in_year = get_matches(series_id)
		if len(matches) != len(matches_in_year):
			flag = True
		else:
			flag = False
	return flag,matches_in_year

def update(matches_in_year):
	connection = create_db_connection("localhost", "sanchit", PWD, DB_NAME)
	year = list(series)[0]
	series_id = series[year]
	row = [[str(year)] + m]
	if year > int(y):
		matches_to_add = len(matches_in_year)
		for i in range(len(match_ids)):
			row.append([years[i]] + match_ids[i])
		with open(cwd + os.path.sep + 'data' + os.path.sep +'match_ids.csv','w') as f:
			writer = csv.writer(f)
			for ele in row:
				writer.writerow(ele)
	
	else:
		matches_to_add = len(matches_in_year) - len(matches)
		with open(cwd+ os.path.sep + 'datasets' + os.path.sep +'match_ids.csv','r') as f:
			reader = csv.reader(f.readlines())
		with open(cwd + os.path.sep + 'datasets' + os.path.sep +'match_ids.csv','w') as f:
			writer = csv.writer(f)
			for line in reader:
				if line[0] == str(year):
					writer.writerow(row[0])
				else:
					writer.writerow(line)

	p = matches_in_year[-matches_to_add:]
	r = len(matches_in_year)-matches_to_add
	player_dict = dict()
	for i,match_id in enumerate(p):
		get_player_ids_from(series_id, match_id, player_dict)
		try:
			match_id,year,match_number,date,venue,city,first,second,inn1,inn2,winner,margin,mom,rpo1,rpo2,fow1,ovr1,fow2,ovr2 = get_match_details(series_id,match_id,str(year),i+r)
			if first != 'None':
				query = "INSERT INTO matches VALUES {};".format((match_id,year,match_number,date,venue,city,first,second,inn1,inn2,winner,margin,mom,rpo1,rpo2,fow1,ovr1,fow2,ovr2))
				execute_query(connection,query)
		except Exception as e:
			print(e)
			print(match_id)

		batting = batting_scorecard(series_id,match_id)
		bowling = bowling_scorecard(series_id,match_id)
		for ele in batting:
			for i in ele:
				query = """INSERT INTO batting VALUES {}""".format(tuple(i))
				execute_query(connection,query)
		for ele in bowling:
			for i in ele:
				query = """INSERT INTO bowling VALUES {}""".format(tuple(i))
				execute_query(connection,query)

	for player in [key for key in player_dict if key in current_players]: del player_dict[player]
	if player_dict:
		with open(cwd + os.path.sep + 'datasets' + os.path.sep+'player_ids.csv','a') as f:
			writer = csv.writer(f)
			writer.writerows([i] + [player_dict[i]] for i in player_dict)


	connection = create_db_connection("localhost", "sanchit", pw, db_name)
	for player in player_dict:
		query = "INSERT INTO squad VALUES {};".format(get_player_info(player_dict[player]))
		execute_query(connection,query,verbosity=0)
	print("Updates Complete")


with open(cwd + os.path.sep + "data" + os.path.sep + "player_ids.csv", "r") as csv_file:
	csv_reader = csv.DictReader(csv_file, delimiter=',')
	current_players = [line['player'] for line in csv_reader]

with open(cwd + os.path.sep + 'data' + os.path.sep + 'match_ids.csv','r') as f:
	reader = csv.reader(f)
	l = list(reader)
match_ids = [[i for i in ele[1:] if i] for ele in l]
years = [ele[0] for ele in l]

year = list(series)[0]
series_id = series[year]
y = years[0]
matches = match_ids[0]
check,matches_in_year = updates_available(year,y)


if check:
	update(matches_in_year)
else:
	print("All matches are upto date")

