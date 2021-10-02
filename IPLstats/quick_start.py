from settings import DB_NAME, USER, PWD
import os
import csv
from tools.db_funcs import create_db_connection, execute_query, create_server_connection, create_database

def load_csv_to_db(filepath,table_name):
	file = open(filepath)
	csv_data = csv.reader(file)
	next(csv_data)
	if table_name == 'batting':
		print("Getting batting stats")
		for row in csv_data:
			values = [row[0],row[1],row[2],int(row[3]),row[4],int(row[5]),int(row[6]),int(row[7]),int(row[8]),float(row[9]),row[10],int(row[11])]
			query = """INSERT INTO {} VALUES {}""".format(table_name,tuple(values))
			execute_query(connection,query,verbosity=0)

	elif table_name == 'bowling':
		print("Getting bowling stats")
		for row in csv_data:
			values = [row[0],row[1],row[2], float(row[3]), int(row[4]), int(row[5]), int(row[6]), float(row[7]), row[8], int(row[9])]
			query = """INSERT INTO {} VALUES {}""".format(table_name,tuple(values))
			execute_query(connection,query,verbosity=0)


	elif table_name == 'matches':
		print("Getting matches")
		for row in csv_data:
			values = [row[0],row[1],int(row[2]),row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16],row[17],row[18]]
			query = """INSERT INTO {} VALUES {}""".format(table_name,tuple(values))
			execute_query(connection,query,verbosity=0)

	else:
		print("Getting squad")
		for row in csv_data:
			values = [int(row[0]), row[1], row[2], row[3], row[4], row[5]]
			query = """INSERT INTO {} VALUES {}""".format(table_name,tuple(values))
			execute_query(connection,query,verbosity=0)



connection = create_server_connection('localhost',USER,PWD)
create_database(connection,"CREATE DATABASE {}".format(DB_NAME))
cwd = os.getcwd()
	

connection = create_db_connection("localhost", USER, PWD,DB_NAME)

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
execute_query(connection,"DROP TABLE IF EXISTS matches",verbosity=0)
execute_query(connection,create_match_details_query)
create_table_query = """
	CREATE TABLE squad (
		player_id INT PRIMARY KEY,
		name VARCHAR(50) NOT NULL,
		country VARCHAR(50) NOT NULL,
		role VARCHAR(50),
		batting_style VARCHAR(50),
		bowling_style VARCHAR(50) 
		);
		"""
execute_query(connection,"DROP TABLE IF EXISTS squad",verbosity=0)
execute_query(connection,create_table_query,verbosity=0)

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
execute_query(connection,"DROP TABLE IF EXISTS batting",verbosity=0)
execute_query(connection,"DROP TABLE IF EXISTS bowling",verbosity=0)
execute_query(connection,create_batting_table_query,verbosity=0)
execute_query(connection,create_bowling_table_query,verbosity=0)


files = ['squad.csv','matches.csv','batting.csv','bowling.csv']
for file in files:
	filepath = cwd + os.path.sep + 'data' + os.path.sep + file
	table_name = file.split('.')[0]
	load_csv_to_db(filepath,table_name)
print("Done!")