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


years = list(series)
connection = create_db_connection("localhost", USER,PWD,DB_NAME)
csvpath = "/home/sanchit/Git/Python/IPLstats/IPLstats/data/matchdata"

def get_bowlers_of(team,display=True):
	bowlers_query = """SELECT DISTINCT(s.name), s.bowling_style
						FROM squad s JOIN bowling b ON s.name=b.name 
						WHERE b.team="{}" AND b.year={} AND s.role like "%bowler%";
						""".format(team,years[0])

	bowlers_list = execute_query(connection,bowlers_query,verbosity=0)
	if display:
		field_names = ["Name","Bowling Style"]
		print_table(field_names,bowlers_list)
	bowler_names = [i[0] for i in bowlers_list]
	return bowler_names

def get_team_bowlers_stats(names,all=True):
	names = tuple(names)
	if all:
		bowler_stats_query = """SELECT name, 
							COUNT(*) AS innings,SUM(wickets) AS wickets, 
							AVG(economy) AS economy, 
							(SUM(wickets)/COUNT(*)) AS average 
							FROM bowling
							WHERE name IN {}
							GROUP BY name;
							""".format(names)
	else:

		bowler_stats_query = """SELECT name, 
								COUNT(*) AS innings,SUM(wickets) AS wickets, 
								AVG(economy) AS economy, 
								(SUM(wickets)/COUNT(*)) AS average 
								FROM bowling
								WHERE year IN ({},{},{}) AND name IN {}
								GROUP BY name;
								""".format(years[0],years[1],years[2],names)

	bowler_stats = execute_query(connection,bowler_stats_query,verbosity=0)
	
	#export_to_csv(team+"_bowler_stats.csv",csvpath,bowler_stats)
	return bowler_stats


def get_bowling_at_venue(team,venue,display=True):
	names = tuple(get_bowlers_of(team,display=False))
	venue_query = "SELECT b.name, count(*), sum(b.wickets), avg(b.economy), avg(b.wickets) from bowling b join matches m on b.match_id = m.match_id  where m.venue = '{}' and b.name in {} group by b.name".format(venue,names)
	venue_stats = execute_query(connection,venue_query,verbosity=0)
	#export_to_csv(team+"_bowling_at_venue.csv",csvpath,venue_stats)

def get_recent_bowling_form(player,records=7,display=True):
	
	query = "SELECT b.opposition, b.overs,b.maidens, b.runs, b.wickets, m.match_date from bowling b join matches m on b.match_id = m.match_id where b.name = '{}' order by b.year desc, m.match_number desc limit {};".format(player,records)
	recent_form= execute_query(connection,query,verbosity=0)
	if display and len(recent_form)>0:
		field_names = ["Opposition","Overs","Maidens","Runs","Wickets","Date"]
		print_table(field_names,recent_form)
		'''
	query = "SELECT name,COUNT(*),sum(wickets), avg(economy),avg(wickets) FROM bowling WHERE name IN {} AND year = {} GROUP BY name LIMIT {}".format(names,years[0],records)
	result = execute_query(connection,query,verbosity=0)
	export_to_csv(team+"_bowlers_recent_form.csv",csvpath,result)'''

def get_bowling_record_against(player,opposition,records=7,display = True):
	
	query = "SELECT b.overs, b.maidens, b.runs, b.wickets, b.economy, m.match_date from bowling b join matches m on b.match_id = m.match_id where b.name = '{}' and b.opposition = '{}' order by m.year desc limit 10;".format(player,opposition)
	record_against = execute_query(connection,query,verbosity=0)
	if display and len(record_against)>0:
		field_names = ["Overs","Maidens","Runs","Wickets","Economy","Date"]
		print_table(field_names,record_against)
		'''
	query = "SELECT name, COUNT(*), SUM(wickets), AVG(economy),AVG(wickets) FROM bowling WHERE name in {} AND opposition = '{}' GROUP BY name LIMIT {}".format(names,opposition,records)
	result = execute_query(connection,query,verbosity=0)
	export_to_csv(team+"_bowlers_record_against.csv",csvpath,result)'''

def get_individual_bowler_stats(player,all=True):
	if all:
		query = """
		SELECT COUNT(*) AS innings, SUM(wickets) AS wicket, AVG(economy) as economy, (SUM(wickets)/COUNT(*)) AS average 
		FROM bowling WHERE name = '{}';
		""".format(player)
	else:
		query = """
		SELECT COUNT(*) AS innings, SUM(wickets) AS wicket, AVG(economy) as economy, (SUM(wickets)/COUNT(*)) AS average 
		FROM bowling WHERE name = '{}' AND year in ({},{},{});
		""".format(player,years[0],years[1],years[2])

	result = list(execute_query(connection,query,verbosity=0)[0])
	return result


def get_individual_venue_stats_of_bowler(player,venue):
	query = """
	SELECT COUNT(*), SUM(wickets),AVG(economy),AVG(wickets)
	FROM bowling b JOIN matches m ON b.match_id = m.match_id WHERE b.name = '{}' AND m.venue = '{}'
	""".format(player,venue)

	venue_stats = list(execute_query(connection,query,verbosity=0)[0])
	for i in range(len(venue_stats)):
		if venue_stats[i] == None:
			venue_stats[i] = 0.0

	return venue_stats
	


def get_bowler_profile(player,team,opposition,venue,all=True):
	fore,back = team_colors[team][0],team_colors[team][1]
	color = fg(fore) + bg(back)
	res = attr('reset')
	overall_stats = get_individual_bowler_stats(player,all)
	venue_stats = get_individual_venue_stats_of_bowler(player,venue)

	print(color + player.upper()+res,'\n')


	print(color + 'Overall Record'+res,"\t","\t","\t", color+"Record at {}".format(venue)+res,"\n")
	print("Innnings      : ",overall_stats[0],"\t","\t","Innnings      : ",venue_stats[0])
	print("Wickets       : ",overall_stats[1],"\t","\t","Wickets       : ",venue_stats[1])
	print("Economy       : ",round(overall_stats[2],1),"\t","\t","Economy       : ",round(venue_stats[2],1))
	print("Wicket/Game   : ",round(overall_stats[3],1),"\t","\t","Wicket/Game   : ",round(venue_stats[3],1),'\n')


	print(color + 'Recent Form' + res,"\n")
	get_recent_bowling_form(player)

	print(color + "Record Against {}".format(opposition) + res,"\n")
	get_bowling_record_against(player,opposition)


