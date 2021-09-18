import os
import sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from settings import USER, DB_NAME, PWD, series,teams
from tools.db_funcs import create_db_connection, execute_query
from tools.setup_helpers import get_player_info
from tools.match_helpers import get_match_details
from tools.utils import printProgressBar
from prettytable import PrettyTable
import csv
import time


def create_match_data():

	create_match_details_query = """
	CREATE TABLE matches (
		match_id VARCHAR(150) PRIMARY KEY,
		year VARCHAR(5) NOT NULL,
		match_number INT NOT NULL,
		match_date VARCHAR(30) NOT NULL,
		venue VARCHAR(100) NOT NULL,
		city VARCHAR(50) NOT NULL,
		first_batting VARCHAR(5),
		second_batting VARCHAR(5),
		first_innings_score VARCHAR(10) NOT NULL,
		second_innings_score VARCHAR(10) NOT NULL,
		winner VARCHAR(10),
		margin VARCHAR(50),
		man_of_the_match VARCHAR(50) NOT NULL,
		rpo1 VARCHAR(100),
		rpo2 VARCHAR(100),
		fow1 VARCHAR(100),
		over1 VARCHAR(100),
		fow2 VARCHAR(100),
		over2 VARCHAR(100)
		);
		"""

	with open(parentdir + os.path.sep + 'data' + os.path.sep + 'match_ids.csv','r') as f:
		reader = csv.reader(f)
		match_ids = list(reader)
	matches = [[i for i in ele[1:] if i] for ele in match_ids]
	years = [ele[0] for ele in match_ids]
	connection = create_db_connection("localhost", USER, PWD, DB_NAME)
	execute_query(connection,create_match_details_query)


	for index,year in enumerate(years):
		series_id = series[int(year)]
		l = len(matches[index])
		print("Obtaining match details from {}".format(year))
		printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
		for i,match_id in enumerate(matches[index]):
			try:
				match_id,year,match_number,date,venue,city,first,second,inn1,inn2,winner,margin,mom,rpo1,rpo2,fow1,ovr1,fow2,ovr2 = get_match_details(series_id,match_id,year,i)
				query = "INSERT INTO matches VALUES {};".format((match_id,year,match_number,date,venue,city,first,second,inn1,inn2,winner,margin,mom,rpo1,rpo2,fow1,ovr1,fow2,ovr2))
				execute_query(connection,query,verbosity=0)
			except TypeError as e:
				pass
			time.sleep(0.05)
			printProgressBar(i+1, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
	print("DONE!")