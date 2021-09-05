import csv
import os
import requests
from bs4 import BeautifulSoup
import time
import sys


player_dict = dict()
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from settings import series
from tools.setup_helpers import get_matches, get_player_ids, printProgressBar


def createMatchIds():
	ipl = list(series)
	print("Getting matches...")
	series_ids = [series[i] for i in series]
	ids = [get_matches(j) for j in series_ids]
	print('Obtained all match ids')

	for index,match_ids in enumerate(ids):
		series_id = series[ipl[index]]
		print("Obtaining player ids from {}".format(ipl[index]))
		l = len(match_ids)
		printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50)


		for i,match_id in enumerate(match_ids):
			get_player_ids(series_id, match_id,player_dict)
			time.sleep(0.1)
			printProgressBar(i + 1, l, prefix = 'Progress:', suffix = 'Complete', length = 50)

	print("Done!")
	with open(parentdir + os.path.sep + 'data'+ os.path.sep +'match_ids.csv','w') as f:
		writer = csv.writer(f)
		writer.writerows([ipl[i]] + ids[i] for i in range(len(ipl)))
	print("Finished writing match ids")


	fieldnames = ['player','id']
	with open(parentdir + os.path.sep + 'data'+ os.path.sep +'player_ids.csv','w') as f:
		writer = csv.writer(f)
		writer.writerow(fieldnames)
		writer.writerows([i] + [player_dict[i]] for i in player_dict)
	print("Finished writing player ids")
