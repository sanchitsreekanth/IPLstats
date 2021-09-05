from setup import match_ids, squad, scorecard_data
from tools import db_funcs
from settings import DB_NAME, USER, PWD
import pandas as pd 


"""create MYSQL connection and create the ipl database"""
connection = db_funcs.create_server_connection('localhost',USER,PWD)
db_funcs.create_database(connection,"CREATE DATABASE {}".format(DB_NAME))

match_ids.create_match_ids()
squad.create_squads()
scorecard_data.create_scorecard_data()