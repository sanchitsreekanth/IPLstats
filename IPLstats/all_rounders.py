import Stats
import sys
from params import team1, team2, venue


team_1_allrounders = Stats.get_allrounders_of(team1)
team_2_allrounders = Stats.get_allrounders_of(team2)

for player in team_1_allrounders:
	print('||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||','\n')
	Stats.get_allrounder_profile(player,team1,team2,venue,all=False)
    


for player in team_2_allrounders:
	print('||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||','\n')
	Stats.get_allrounder_profile(player,team2,team1,venue,all=False)
