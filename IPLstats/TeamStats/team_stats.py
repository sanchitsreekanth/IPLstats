from settings import DB_NAME,USER,PWD, series
from tools.db_funcs import execute_query, create_db_connection
from tools.utils import print_table
from prettytable import PrettyTable

year = list(series)[1]
years = list(series)[:3]



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
	display(result,["Venues"])


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
	previous_year_results = [list(i) for i in result]
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
	