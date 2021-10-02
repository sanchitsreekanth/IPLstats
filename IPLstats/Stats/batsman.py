import os
import sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from tools.db_funcs import execute_query , create_db_connection
from tools.utils import print_table, export_to_csv, create_plot
from settings import DB_NAME,USER,PWD,series,teams, team_colors
from prettytable import PrettyTable
import requests
from bs4 import BeautifulSoup
from statistics import mean
from colored import fg,bg,attr
from operator import itemgetter


years = list(series)
connection = create_db_connection("localhost", USER,PWD,DB_NAME)
csvpath = "/home/sanchit/Git/Python/IPLstats/IPLstats/data/matchdata"



def get_batsmen_of(team,display=True):
	query = """
			SELECT DISTINCT name
			FROM batting 
			WHERE year = {} AND position < 8 AND team = '{}'
			group by name order by sum(runs) desc;
			""".format(years[0],team)
	result = execute_query(connection, query, verbosity=0)
	result = [i[0] for i in result]
	query = """SELECT name from squad where name in {} and (role like "%tter%" or role like "%keeper%");""".format(tuple(result))
	e = execute_query(connection,query,verbosity=0)
	e = [i[0] for i in e]
	return e

def player_positions(team):
	query = "SELECT match_id from matches where first_batting = '{0}' or second_batting = '{0}' order by year desc,match_number desc limit 2;".format(team)
	match_ids = execute_query(connection,query,verbosity=0)
	match_ids = [i[0] for i in match_ids] 
	positions = list()
	for match_id in match_ids:
		query = "SELECT name,position from batting where match_id = '{}' and position < 8 and team = '{}';".format(match_id,team)
		positions = positions + execute_query(connection,query,verbosity=0)
	positions = list(set(positions))
	positions = sorted(positions, key = lambda x:x[1])
	positions = [list(i) for i in positions]
	for index,ele in enumerate(positions):
		try:
			name = ele[0]
			query = "SELECT batting_style from squad where name = '{}'".format(name)
			role = execute_query(connection,query,verbosity=0)[0][0]
			positions[index].append(role)
		except:
			positions[index].append("")
			print(name)
	field_names = ["Player","Position","Role"]
	print_table(field_names,positions)

def get_batting_stats(team,names,all = True):
	names = tuple(names)
	if all:
		batting_stats_query = """
		SELECT name, COUNT(*), SUM(runs), (SUM(runs)/SUM(IF(status != "not out ",1,0))), AVG(strike_rate), MAX(runs)
		FROM batting WHERE name IN {}
		GROUP BY name
		""".format(names)
	else:
		batting_stats_query = """
		SELECT name, COUNT(*), SUM(runs), (SUM(runs)/SUM(IF(status != "not out ",1,0))), AVG(strike_rate), MAX(runs)
		FROM batting WHERE name IN {} AND year IN ({},{},{})
		GROUP BY name
		""".format(names,years[0],years[1],years[2])

	batting_stats = execute_query(connection,batting_stats_query,verbosity=0)
	names = [*map(itemgetter(0),batting_stats)]
	runs = [*map(itemgetter(2),batting_stats)]
	print(runs)
	create_plot(xlabel="Player",ylabel="runs",title="Runs of "+team+" batsmen",x_data=names, y_data=runs)
	averages = [*map(itemgetter(3),batting_stats)]
	create_plot(xlabel="Player",ylabel="averages",title="Average of "+team+" batsmen",x_data=names, y_data=averages)
	
	
	
def get_batting_at_venue(team,venue):
	names = tuple(get_batsmen_of(team,display=False))
	query = """
	SELECT b.name, COUNT(*), SUM(b.runs), (SUM(b.runs)/SUM(IF(b.status != "not out ",1,0))), AVG(strike_rate), MAX(b.runs)
	FROM batting b JOIN matches m ON b.match_id = m.match_id
	WHERE b.name IN {} AND m.venue = '{}'
	GROUP BY name
	""".format(names,venue)

	venue_stats = execute_query(connection,query,verbosity=0)
	export_to_csv(team+"_batting_at_venue.csv",csvpath,venue_stats)

def get_recent_batting_form(player,records=7,display=True):

	query = """
	SELECT b.opposition, b.position, b.status, b.runs, b.balls, m.match_date
	FROM batting b JOIN matches m ON b.match_id = m.match_id
	WHERE b.name = "{}" AND b.year={}
	ORDER BY m.year DESC, m.match_number DESC LIMIT {}
	""".format(player,years[0],records)
	recent_form= execute_query(connection,query,verbosity=0)
	if display and len(recent_form)>0:
		field_names = ["Opposition","Position", "Status","Runs","Balls","Date"]
		print_table(field_names,recent_form)
	'''query = """
	SELECT name, COUNT(*), SUM(runs), AVG(runs), AVG(strike_rate), MAX(runs)
	FROM batting
	WHERE name IN {} AND year = {}
	GROUP BY name LIMIT {}
	""".format(names,years[0],records)
	result = execute_query(connection,query,verbosity=0)
	export_to_csv(team+"_batsmen_recent_form.csv",csvpath,result)'''


def get_batting_record_against(player,opposition,records=7,display=True):
	
	query = """
	SELECT b.position, b.status, b.runs, b.balls, m.match_date
	FROM batting b JOIN matches m ON b.match_id = m.match_id
	WHERE b.name = '{}' AND b.opposition = '{}'
	ORDER BY b.year DESC, m.match_number DESC LIMIT {}
	""".format(player,opposition,records)
	recent_form= execute_query(connection,query,verbosity=0)
	if display and len(recent_form)>0:
		field_names = ["Position", "Status","Runs","Balls","Date"]
		print_table(field_names,recent_form)
	'''query = """
	SELECT name, COUNT(*), SUM(runs), AVG(runs), AVG(strike_rate), MAX(runs)
	FROM batting
	WHERE name IN {} AND opposition = '{}'
	GROUP BY name LIMIT {}
	""".format(names,opposition,records)
	result = execute_query(connection,query,verbosity=0)
	export_to_csv(team+"_batsmen_recent_form.csv",csvpath,result)'''



def get_individual_batsman_stats(player,all=True):
	if all:
		query = """
		SELECT COUNT(*), SUM(runs), (SUM(runs)/SUM(IF(status != "not out ",1,0))), AVG(strike_rate), MAX(runs) 
		FROM batting WHERE name = '{}';
		""".format(player)
	else:
		query = """
		SELECT COUNT(*), SUM(runs), (SUM(runs)/SUM(IF(status != "not out ",1,0))), AVG(strike_rate), MAX(runs) 
		FROM batting WHERE name = '{}' AND year in ({},{},{});
		""".format(player,years[0],years[1],years[2])

	result = list(execute_query(connection,query,verbosity=0)[0])
	return result

def get_individual_venue_stats_of_batsman(player,venue):
	query = """
	SELECT COUNT(*), SUM(b.runs), (SUM(b.runs)/SUM(IF(b.status != "not out ",1,0))), AVG(strike_rate), MAX(b.runs)
	FROM batting b JOIN matches m ON b.match_id = m.match_id WHERE b.name = '{}' AND m.venue = '{}'
	""".format(player,venue)

	venue_stats = list(execute_query(connection,query,verbosity=0)[0])
	for i in range(len(venue_stats)):
		if venue_stats[i] == None:
			venue_stats[i] = 0.0

	return venue_stats
	
def get_batsman_profile(player,team,opposition,venue,all=True):
	fore,back = team_colors[team][0],team_colors[team][1]
	color = fg(fore) + bg(back)
	res = attr('reset')
	overall_stats = get_individual_batsman_stats(player,all)
	venue_stats = get_individual_venue_stats_of_batsman(player,venue)

	print(color + player.upper()+res,'\n')

	print(color + 'Overall Record'+res,"\t","\t","\t", color+"Record at {}".format(venue)+res,"\n")
	print("Innnings      : ",overall_stats[0],"\t","\t","Innnings      : ",venue_stats[0])
	print("Runs Scored   : ",overall_stats[1],"\t","\t","Runs Scored   : ",venue_stats[1])
	print("Average Score : ",round(overall_stats[2],1),"\t","\t","Average Score : ",round(venue_stats[2],1))
	print("Strike Rate   : ",round(overall_stats[3],1),"\t","\t","Strike Rate   : ",round(venue_stats[3],1))
	print("Highest Score : ",overall_stats[4],"\t","\t","Highest Score : ",venue_stats[4],"\n")

	print(color + 'Recent Form' + res,"\n")
	get_recent_batting_form(player)

	print(color + "Record Against {}".format(opposition) + res,"\n")
	get_batting_record_against(player,opposition)

