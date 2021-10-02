import Stats
import sys
from params import team1, team2, venue

team_1_bowlers = Stats.get_bowlers_of(team1)
team_2_bowlers = Stats.get_bowlers_of(team2)



for player in team_1_bowlers:
	print('||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||','\n')
	Stats.get_bowler_profile(player,team1,team2,venue,all=False)
    


for player in team_2_bowlers:
	print('||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||','\n')
	Stats.get_bowler_profile(player,team2,team1,venue,all=False)
