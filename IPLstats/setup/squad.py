import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import requests
from bs4 import BeautifulSoup
import csv
from prettytable import PrettyTable
import pandas as pd
import time
from settings import series, DB_NAME, PWD, USER
from .helpers import create_server_connection, create_database, create_db_connection, execute_query, getPlayerInfo, printProgressBar


def create_squads():
	df = pd.read_csv(parentdir + os.path.sep + "data"+ os.path.sep+'player_ids.csv')
	players = df['id'].values
	connection = create_db_connection("localhost", USER,PWD,DB_NAME)

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
	print("Getting squads...")
	execute_query(connection,create_table_query,verbosity=0)

	l = len(players)
	printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
	for i,player_id in enumerate(players):
		details = getPlayerInfo(player_id)
		query = " INSERT INTO squad VALUES {};".format(details)
		execute_query(connection,query,0)
		time.sleep(0.05)
		printProgressBar(i + 1, l, prefix = 'Progress:', suffix = 'Complete', length = 50)