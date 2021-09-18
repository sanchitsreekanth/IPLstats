import os
import sys
import csv
import time
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from settings import USER, DB_NAME, PWD, series,teams
from tools.db_funcs import create_db_connection, execute_query
from tools.match_helpers import batting_scorecard, bowling_scorecard
from tools.utils import printProgressBar

def create_scorecard_data():
	create_batting_table_query = """
	CREATE TABLE batting (
		name VARCHAR(50) NOT NULL,
		team VARCHAR(10) NOT NULL,
		opposition VARCHAR(10) NOT NULL,
		position INT NOT NULL,
		status VARCHAR(100) NOT NULL,
		runs INT NOT NULL,
		balls INT NOT NULL,
		fours INT NOT NULL,
		sixes INT NOT NULL,
		strike_rate FLOAT(5,2) NOT NULL ,
		match_id VARCHAR(150) NOT NULL,
		year INT NOT NULL
		
		);
		"""


	create_bowling_table_query = """
	CREATE TABLE bowling (
		name VARCHAR(50) NOT NULL,
		team VARCHAR(10) NOT NULL,
		opposition VARCHAR(10) NOT NULL,
		overs FLOAT(2,1) NOT NULL,
		maidens INT NOT NULL,
		runs INT NOT NULL,
		wickets INT NOT NULL,
		economy FLOAT(4,2) NOT NULL,
		match_id VARCHAR(1500) NOT NULL,
		year INT NOT NULL
		);
		"""


	connection = create_db_connection("localhost", USER, PWD,DB_NAME)
	execute_query(connection,"DROP TABLE IF EXISTS batting")
	execute_query(connection,"DROP TABLE IF EXISTS bowling")
	execute_query(connection,create_batting_table_query)
	execute_query(connection,create_bowling_table_query)

	cwd = os.getcwd()

	with open(parentdir + os.path.sep + 'data' + os.path.sep + 'match_ids.csv','r') as f:
		reader = csv.reader(f)
		l = list(reader)
	matches = [[i for i in ele[1:] if i] for ele in l]
	years = [ele[0] for ele in l]

	for index,year in enumerate(years):
		series_id = series[int(year)]
		l = len(matches[index])
		print("Obtaining scorecards from {}".format(year))
		printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
		for j,match_id in enumerate(matches[index]):
			try:
				batting = batting_scorecard(series_id,match_id,int(year))
				bowling = bowling_scorecard(series_id,match_id,int(year))
				
				for ele in batting:
					for i in ele:
						query = """INSERT INTO batting VALUES {}""".format(tuple(i))
						execute_query(connection,query,verbosity=0)
			
				for ele in bowling:
					for i in ele:
						query = """INSERT INTO bowling VALUES {}""".format(tuple(i))
						execute_query(connection,query,verbosity=0)
			except:
				print(match_id,year)

			time.sleep(0.05)
			printProgressBar(j+1, l, prefix = 'Progress:', suffix = 'Complete', length = 50)