import os
import sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from tools.db_funcs import execute_query , create_db_connection
from tools.utils import print_table, export_to_csv
from settings import DB_NAME,USER,PWD,series,teams, team_colors
from prettytable import PrettyTable
import requests
from bs4 import BeautifulSoup
from statistics import mean
from colored import fg,bg,attr
from .bowler import *
from .batsman import *

years = list(series)
connection = create_db_connection("localhost", USER,PWD,DB_NAME)

def get_allrounders_of(team,display=True):
	query = """
	SELECT DISTINCT(b1.name) FROM batting b1 JOIN bowling b2 ON b1.name=b2.name
	WHERE b1.year={} AND b1.team='{}'
	""".format(years[0],team)
	result = [i[0] for i in execute_query(connection,query,verbosity=0)]

	all_rounders_query = """SELECT name, role, batting_style, bowling_style FROM squad WHERE name in {} AND role LIKE "%llrounder%" """.format(tuple(result))
	all_rounders =  execute_query(connection,all_rounders_query,verbosity=0)
	if display:
		field_names = ["Name","Role","Batting Style","Bowling Style"]
		print_table(field_names,all_rounders)

	return [i[0] for i in all_rounders]





def get_allrounder_profile(player,team,opposition,venue,all=True):
	fore,back = team_colors[team][0],team_colors[team][1]
	color = fg(fore) + bg(back)
	res = attr('reset')
	print(color + player.upper()+res,'\n')
	overall_batting_stats = get_individual_batsman_stats(player,all)
	overall_bowling_stats = get_individual_bowler_stats(player,all)
	venue_batting_stats = get_individual_venue_stats_of_batsman(player,venue)
	venue_bowling_stats = get_individual_venue_stats_of_bowler(player,venue)

	print(color + 'Overall Record'+res,"\t","\t","\t", color+"Record at {}".format(venue)+res,"\n")
	print("Innnings      : ",overall_batting_stats[0],"\t","\t","Innnings      : ",venue_batting_stats[0])
	print("Runs Scored   : ",overall_batting_stats[1],"\t","\t","Runs Scored   : ",venue_batting_stats[1])
	print("Average Score : ",round(overall_batting_stats[2],1),"\t","\t","Average Score : ",round(venue_batting_stats[2],1))
	print("Strike Rate   : ",round(overall_batting_stats[3],1),"\t","\t","Strike Rate   : ",round(venue_batting_stats[3],1))
	print("Highest Score : ",overall_batting_stats[4],"\t","\t","Highest Score : ",venue_batting_stats[4],"\n")


	print("Innnings      : ",overall_bowling_stats[0],"\t","\t","Innnings      : ",venue_bowling_stats[0])
	print("Wickets       : ",overall_bowling_stats[1],"\t","\t","Wickets       : ",venue_bowling_stats[1])
	print("Economy       : ",round(overall_bowling_stats[2],1),"\t","\t","Economy       : ",round(venue_bowling_stats[2],1))
	print("Wicket/Game   : ",round(overall_bowling_stats[3],1),"\t","\t","Wicket/Game   : ",round(venue_bowling_stats[3],1),'\n')

	print(color + 'Recent Batting Form' + res,"\n")
	get_recent_batting_form(player)


	print(color + "Record Batting Against {}".format(opposition) + res,"\n")
	get_batting_record_against(player,opposition)
	print("\n")

	print(color + 'Recent Bowling Form' + res,"\n")
	get_recent_bowling_form(player)

	print(color + "Record Bowling Against {}".format(opposition) + res,"\n")
	get_bowling_record_against(player,opposition)

