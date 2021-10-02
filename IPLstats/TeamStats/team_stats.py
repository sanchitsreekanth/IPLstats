import os
import sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from settings import DB_NAME,USER,PWD, series, teams
from tools.db_funcs import execute_query, create_db_connection
from tools.utils import print_table
from prettytable import PrettyTable
import requests
from bs4 import BeautifulSoup
from Stats import get_batsmen_of, get_bowlers_of

year = list(series)[1]
years = list(series)[:3]
connection = create_db_connection("localhost", "sanchit", PWD, DB_NAME)


def show_teams():
	team_names = list(teams)
	symbol = [teams[i][1] for i in team_names]
	x = PrettyTable()
	x.add_column("Team",team_names)
	x.add_column("Symbol",symbol)
	print(x)


def show_venues():
	query = "SELECT distinct venue from matches;"
	result = execute_query(connection,query,verbosity=0)
	result = [[i[0]] for i in result]
	print_table(["Venues"],result)


def previous_results(team,year=0):
	
	if year == 0:
		query = """SELECT match_id,year,venue,winner,margin,man_of_the_match 
		FROM matches 
		WHERE (first_batting= '{0}' OR second_batting = '{0}') AND winner != 'No Result'
		ORDER BY year DESC
		""".format(team)
	else:
		query = """SELECT match_id,year,venue,winner,margin,man_of_the_match 
		FROM matches 
		WHERE (first_batting= '{0}' OR second_batting = '{0}') AND year = {1} AND winner != 'No Result'
		""".format(team,year) 

	previous_year_results = execute_query(connection,query,verbosity=0)
	previous_year_results = [list(i) for i in previous_year_results]
	for i in previous_year_results:
		if i[3] == team:
			i[3] = 'Won'
		else:
			i[3] ='Lost'
	previous_results_fieldnames = ["match_id","year","venue","result","margin","man_of_the_match"]
	print_table(previous_results_fieldnames,previous_year_results)


def team_performance(team):
	query1 = "SELECT rpo1,rpo2,over2,over1 FROM matches WHERE first_batting = '{}' AND first_innings_score != 'None' AND year IN ('{}','{}','{}') AND rpo2 != 'None';".format(team,str(years[0]),str(years[1]),str(years[2]))
	first_innings_results = execute_query(connection, query1,verbosity=0)
	query2 = "SELECT rpo2,rpo1,over1,over2 FROM matches WHERE second_batting = '{}' AND second_innings_score != 'None' AND year IN ('{}','{}','{}');".format(team,str(years[0]),str(years[1]),str(years[2]))
	second_innings_results = execute_query(connection,query2,verbosity=0)
	result = first_innings_results+second_innings_results	
	result = [list(i) for i in result]
	c = len(first_innings_results)
	powerplay_wickets = list()
	middle_wickets = list()
	death_wickets = list()
	pp_wickets = list()
	m_wickets = list()
	d_wickets = list()
	for index,i in enumerate(result):
		i[0] = [int(x) for x in i[0].split()]
		i[1] = [int(x) for x in i[1].split()]
		i[2] = [float(x) for x in i[2].split()]
		i[3] = [float(x) for x in i[3].split()]
	
	powerplay = [i[0][:6] for i in result if len(i[0])>10]
	middle = [i[0][6:15] for i in result if len(i[0])>15]
	death = [i[0][15:] for i in result[:len(r)] if len(i[0])>17]
	powerplay_bowl = [i[1][:6] for i in result if len(i[1])>10]
	middle_bowl = [i[1][6:15] for i in result if len(i[1])>15]
	death_bowl = [i[1][15:] for i in result[:len(r)] if len(i[1])>17]
	for index,i in enumerate(result):
		if len(i[1])> 10:
			powerplay_wickets.append([j for j in i[2] if j < 6.1])
			if len(i[1])>15:
				middle_wickets.append([j for j in i[2] if (j > 6.0) and (j<15.1)]) 
				if len(i[1])>17 and index < c:
					death_wickets.append([j for j in i[2] if (j > 15.0)])
	for index,i in enumerate(result):
		if len(i[0])> 10:
			pp_wickets.append([j for j in i[3] if j < 6.1])
			if len(i[0])>15:
				m_wickets.append([j for j in i[3] if (j > 6.0) and (j<15.1)]) 
				if len(i[0])>17 and index < c:
					d_wickets.append([j for j in i[3] if (j > 15.0)])
	

	powerplay_wickets = int(mean([len(i) for i in powerplay_wickets]))
	middle_wickets = int(mean([len(i) for i in middle_wickets]))
	death_wickets = int(mean([len(i) for i in death_wickets]))
	pp_wickets = int(mean([len(i) for i in pp_wickets]))
	m_wickets = int(mean([len(i) for i in m_wickets]))
	d_wickets = int(mean([len(i) for i in d_wickets]))
	powerplay = mean([sum(i) for i in powerplay])
	middle = mean([sum(i) for i in middle])
	death =mean([sum(i)/(len(i)/5) for i in death])
	powerplay_bowl = mean([sum(i) for i in powerplay_bowl])
	middle_bowl = mean([sum(i) for i in middle_bowl])
	death_bowl =mean([sum(i)/(len(i)/5) for i in death_bowl])


	print("BATTING STATS:",'\n')
	print("Average powerplay runrate: ", round(powerplay/6.0 , 2))
	print("Average middle overs runrate: ", round(middle/9.0 ,2))
	print("Average death overs runrate: ", round(death/5.0 , 2),'\n')
	#print("Wickets fallen in powerplay: ",pp_wickets)
	#print("Wickets fallen in middle overs: ",m_wickets)
	#print("Wickets fallen in death overs: ",d_wickets,'\n')
	print("BOWLING STATS:",'\n')
	print("Bowling powerplay runrate: ", round(powerplay_bowl/6.0 , 2))
	print("Bowling middle overs runrate: ", round(middle_bowl/9.0 ,2))
	print("Bowling death overs runrate: ", round(death_bowl/5.0 , 2))
	#print("Wickets in powerplay: ",powerplay_wickets)
	#print("Wickets in middle overs: ",middle_wickets)
	#print("Wickets in death overs: ",death_wickets)
	

def head_to_head(team1,team2):
	query = """	SELECT match_id, year, venue, first_batting , second_batting, winner, margin, man_of_the_match 
	from matches 
	where first_batting IN ('{0}','{1}') AND second_batting IN ('{0}','{1}') AND winner != 'No result'
	ORDER BY year DESC;
	""".format(team1,team2)
	results = execute_query(connection,query,verbosity=0)
	results = [list(i) for i in results]

	w = [0 if i[5] == team2 else 1 for i in results]
	w_3 = [0 if i[5] == team2 else 1 for i in results if int(i[1]) in years ] 
	total_games = len(w)
	team1_wins = sum(w)
	team2_wins = total_games - team1_wins
	total_games_3 = len(w_3)
	team1_wins_3 = sum(w_3)
	team2_wins_3 = total_games_3 - team1_wins_3
	defending = [i[3] for i in results if i[3] == i[5]]
	chasing = [i[4] for i in results if i[4] == i[5]]
	team1_defending = defending.count(team1)
	team2_defending = len(defending) - team1_defending
	team1_chasing = chasing.count(team1)
	team2_chasing = len(chasing) - team1_chasing
	x = PrettyTable()
	print("{} vs {}".format(str.upper(team1),str.upper(team2)),'\n')
	x.field_names = ['',team1,team2]
	x.add_row(['Overall',team1_wins,team2_wins])
	x.add_row(['Last 3 years',team1_wins_3,team2_wins_3])
	x.add_row(['Defending',team1_defending,team2_defending])
	x.add_row(['Chasing',team1_chasing,team2_chasing])
	print('Head to Head')
	print(x,'\n')
	print('Previous Encounters')
	x = PrettyTable()
	x.field_names = ['match_id', 'year', 'venue', 'first_batting' , 'second_batting', 'winner', 'margin', 'man_of_the_match']
	for i in results:
		x.add_row(i)
	print(x)

def ground_stats(venue):
	query = """SELECT year,first_innings_score,second_innings_score,margin, rpo1, rpo2
	FROM matches
	WHERE venue = '{}' AND margin !='No result'
	ORDER BY year DESC;""".format(venue)
	result = execute_query(connection,query,verbosity=0)
	result = [list(i) for i in result]
	w = [0 if 'run' in i[3] else 1 for i in result]
	w_prev = [0 if 'run' in i[3] else 1 for i in result if i[0] == str(year)]
	total_games = len(w)
	won_batting_second = sum(w)
	won_batting_first = total_games - won_batting_second
	total_games_prev= len(w_prev)
	won_batting_second_prev = sum(w_prev)
	won_batting_first_prev = total_games_prev - won_batting_second_prev
	first_innings_scores = [int(i[1].split('/')[0]) for i in result]
	second_innings_scores = [int(i[2].split('/')[0]) for i in result]
	avg = (sum(first_innings_scores)+sum(second_innings_scores))/(2*total_games)
	avg_first_innings = sum(first_innings_scores)/len(first_innings_scores)
	avg_second_innings = sum(second_innings_scores)/len(second_innings_scores)
	avg_first_innings_prev = sum(first_innings_scores[:total_games_prev])/total_games_prev
	avg_second_innings_prev = sum(second_innings_scores[:total_games_prev])/total_games_prev
	'''
	for index,i in enumerate(result):
		i[5] = [int(x) for x in i[5].split()]
		i[4] = [int(x) for x in i[4].split()]
	powerplay = [i[4][:6] for i in result if len(i[4])>10] + [i[5][:6] for i in result if len(i[5])>10]
	middle = [i[4][6:15] for i in result if len(i[4])>15] + [i[5][:6] for i in result if len(i[5])>10]
	death = [i[4][15:] for i in result if len(i[4])>17] + [i[5][15:] for i in result if len(i[5])>17]
	powerplay = mean([sum(i) for i in powerplay])
	middle = mean([sum(i) for i in middle])
	death =mean([sum(i)/(len(i)/5) for i in death])'''
	print("Overall stats")
	print("Total games played: ",total_games)
	print("Games won defending: ",won_batting_first)
	print("Games won chasing: ",won_batting_second)
	print("Average score: ", avg)
	print("Average score batting first: ",avg_first_innings)
	print("Average score batting second: ",avg_second_innings,"\n")
	print("Previous year stats")
	print("Total games played: ",total_games_prev)
	print("Games won defending: ",won_batting_first_prev)
	print("Games won chasing: ",won_batting_second_prev)
	print("Average score batting first: ",avg_first_innings_prev)
	print("Average score batting second: ",avg_second_innings_prev,"\n")
	#print("Average powerplay runrate: ", round(powerplay/6.0 , 2))
	#print("Average middle overs runrate: ", round(middle/9.0 ,2))
	#print("Average death overs runrate: ", round(death/5.0 , 2),'\n')


def player_battle(team1,team2):
	team_1_batsmen = get_batsmen_of(team1)
	team_2_bowlers = get_bowlers_of(team2)
	print(team_1_batsmen)
	print(team_2_bowlers)
	
	query = "SELECT name,match_id,opposition,status from batting where name in {} and status like '% b %'".format(tuple(team_1_batsmen))
	result = execute_query(connection,query,verbosity=0)
	player_battle_dict = dict()
	for batsman,match_id,opposition,status in result:
		query = """SELECT name FROM bowling WHERE match_id = '{}' and team = '{}'""".format(match_id,opposition)
		result = execute_query(connection,query,verbosity=0)
		result = [j[0] for j in result]
		wickettaker = status.split("b ")[1].strip()
		results = [i for i in result if wickettaker in i]
		if len(results) == 1:
			pass
		else:
			s = wickettaker.split()
			if len(s) == 2:
				first,second = s[0],s[1]
				result = [i for i in result if second in i and i[0] == first]
				
			

		#player_battle_dict.setdefault(batsman,[]).append([match_id,opp,status])
	



	

