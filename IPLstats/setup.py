from setup import match_ids, squad, scorecard_data, helpers
from settings import DB_NAME, USER, PWD
import pandas as pd 


connection = helpers.create_server_connection('localhost',USER,PWD)
helpers.create_database(connection,"CREATE DATABASE {}".format(DB_NAME))

#match_ids.create_match_ids()
#squad.create_squads()
scorecard_data.create_scorecard_data()