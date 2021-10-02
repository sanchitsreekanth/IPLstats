import Stats
import sys
from params import team1, team2, venue

team1_batsmen = Stats.get_batsmen_of(team1)
Stats.player_positions(team1)

team2_batsmen = Stats.get_batsmen_of(team2)
Stats.player_positions(team2)


for player in team1_batsmen:
    print('||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||','\n')
    Stats.get_batsman_profile(player,team1,team2,venue,all=False)
   


for player in team2_batsmen:
    print('||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||','\n')
    Stats.get_batsman_profile(player,team2,team1,venue,all=False)
    

