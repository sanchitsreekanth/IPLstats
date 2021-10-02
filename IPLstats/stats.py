from TeamStats import *
from settings import DB_NAME,USER, PWD
from tools.db_funcs import create_db_connection


team = 'CSK'
connection = create_db_connection("localhost", "sanchit", PWD, DB_NAME)
show_venues()
show_teams()

previous_results(team)
head_to_head('CSK','MI')
ground_stats('Sharjah Cricket Stadium')