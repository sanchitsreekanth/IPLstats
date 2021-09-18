import requests
from bs4 import BeautifulSoup
import csv
import os
import sys
import mysql.connector
from mysql.connector import Error
import pandas as pd
import re
import unicodedata
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from settings import teams

def batting_scorecard(series_id,match_id,year):

	url = 'https://www.espncricinfo.com/series/{}/{}/full-scorecard'.format(series_id,match_id)
	page =  requests.get(url)
	soup = BeautifulSoup(page.content,'lxml')
	table_body=soup.find_all('tbody')
	q = soup.find_all(class_ = 'header-title label')[:2]
	q = [i.text.split('INNINGS')[0] for i in q]
	ret = list()
	for i,table in enumerate(table_body[0:4:2]):
		try:
			temp = list()
			team = [teams[j][1] for j in teams if j in q[i]][0]
			opp = [teams[j][1] for j in teams if j in q[::-1][i]][0]
			rows = table.find_all('tr')
			for position,row in enumerate(rows[:-1:2]):
				colvals = row.find_all('td')
				colvals = [k.text for k in colvals]
				name = colvals[0]
				name = name.split('(c)')[0]
				name = name.split('†')[0]
				if "'"  in name:
					name = name.replace("'"," ")
				status,runs,balls,fours,sixes,sr = colvals[1],colvals[2],colvals[3],colvals[5],colvals[6],colvals[7]
				if sr == '-': sr = '0.0'
				if position == 1:
					position = 0
				if runs == '-':
					continue
				temp.append([unicodedata.normalize("NFKD", name)[:-1],team,opp,position+1,status.strip(),int(runs),int(balls),int(fours),int(sixes),float(sr),match_id,year])
			ret.append(temp)
		except:
			pass
		

	return ret

def bowling_scorecard(series_id,match_id,year):

	url = 'https://www.espncricinfo.com/series/{}/{}/full-scorecard'.format(series_id,match_id)
	page =  requests.get(url)
	soup = BeautifulSoup(page.content,'lxml')
	table_body=soup.find_all('tbody')

	q = soup.find_all(class_ = 'header-title label')[:2]
	q = [i.text.split('INNINGS')[0] for i in q]
	q = q[::-1]
	ret = list()
	for i,table in enumerate(table_body[1:4:2]):
		try:
			temp = list()
			team = [teams[j][1] for j in teams if j in q[i].strip()][0]
			opp = [teams[j][1] for j in teams if j in q[::-1][i].strip()][0]
			rows = table.find_all('tr')		
			for row in rows:
				colvals = row.find_all('td')
				colvals = [i.text for i in colvals]
				if len(colvals) > 1:
					name = colvals[0].split('(c)')[0]
					if "'"  in name:
						name = name.replace("'"," ")
					overs,maidens,run,wickets,eco,dots,f,s,w,n = colvals[1],colvals[2],colvals[3],colvals[4],colvals[5],colvals[6],colvals[7],colvals[8],colvals[9],colvals[10]
					temp.append([name,team,opp,float(overs),int(maidens),int(run),int(wickets),float(eco),match_id,year]) 
			ret.append(temp)
		
		except:
			pass
	return ret

def get_rpo(series_id,match_id):
	try:
		url = 'https://www.espncricinfo.com/series/{}/{}/match-statistics'.format(series_id,match_id)
		page = requests.get(url)
		bs = BeautifulSoup(page.content, 'lxml')
		q = bs.find_all(class_ = 'rv-xy-plot__series rv-xy-plot__series--bar')
		w=q[0].find_all('rect')
		a = bs.find_all(class_ = 'rv-xy-plot__axis rv-xy-plot__axis--vertical')
		divisions=a[0].find_all(class_ = 'rv-xy-plot__axis__tick')[-1].text
		a = bs.find_all(class_ = 'rv-xy-plot__grid-lines undefined')
		b = a[0].find_all('line')
		higher = float(b[0]['y1'])
		lower = float(b[-1]['y1'])
		unit = (higher-lower)/float(divisions)
		runs_per_over_1 = [str(int(float(i['height'])/unit)) for i in w[1:]]
		runs_per_over_1 = ' '.join(runs_per_over_1)
		w=q[1].find_all('rect')
		runs_per_over_2 = [str(int(float(i['height'])/unit)) for i in w[1:]]
		runs_per_over_2 = ' '.join(runs_per_over_2)
		
	except:
		runs_per_over_2=runs_per_over_1='None'

	return runs_per_over_1,runs_per_over_2


def get_fow(series_id,match_id):
	ret = list()
	url = 'https://www.espncricinfo.com/series/{}/{}/full-scorecard'.format(series_id,match_id)
	page = requests.get(url)
	bs = BeautifulSoup(page.content,'lxml')
	q = bs.find_all('tfoot')
	for ele in q:
		w=ele.find_all('tr')[-1]
		e=w.text.split(':')[1]
		fow = list()
		ovr = list()
		for i in e.split():
			if '-' in i and len(i)<7:
				fow.append(i)
			elif '.' in i:
				ovr.append(i)
		fow = ' '.join(fow)
		ovr = ' '.join(ovr)
		ret = ret + [fow]+[ovr]
	if len(ret) == 2:
		return ret[0],ret[1],'',''
	elif len(ret) == 4:
		return ret[0],ret[1],ret[2],ret[3]
	else:
		return '','','',''

def get_match_details(series_id,match_id,year,match_number):
	url = 'https://www.espncricinfo.com/series/{}/{}/full-scorecard'.format(series_id,match_id)
	page =  requests.get(url)
	soup = BeautifulSoup(page.content,'lxml')
	bs4_object=soup.find(class_ = 'font-weight-bold match-venue').text
	c = bs4_object.split(',')
	if len(c) == 1:
		city = c[0].split()[0]
		venue = c[0]
	else:
		city = c[1]
		venue = c[0]

	venue = venue.replace("'","")
	q=soup.find(class_ = 'match-info match-info-MATCH match-info-MATCH-half-width')
	first=second=inn1=inn2=mom=date="None"
	winner = margin='No Result'
	rpo1,rpo2 = get_rpo(series_id,match_id)
	fow1,ovr1,fow2,ovr2 = get_fow(series_id,match_id)
	if q == None:
		q=soup.find(class_ = 'match-info match-info-MATCH match-info-MATCH-full-width')
	if 'without a ball bowled' not in q.text:
			
		first,second = [i.text for i in q.find_all(class_ = 'name')]
		for x in teams:
			if x == first:
				first = teams[x][1]
			if x == second:
				second = teams[x][1]

		if 'won by' in q.text:
			try:
				mom = soup.find(class_ = 'playerofthematch-name').text
			except:
				mom = ''
			date = soup.find_all(class_ = 'description')[0].text.split(',')[2].strip()
			inn1,inn2 = [i.text for i in q.find_all(class_ = 'score')]
			margin = q.text.split('won by')[1]
			if inn1.split('/')[0] > inn2.split('/')[0]:
				winner = first
			else:
				winner = second

		elif 'won' in q.text:
			date = soup.find_all(class_ = 'description')[0].text.split(',')[2].strip()
			mom = soup.find(class_ = 'playerofthematch-name').text
			inn1,inn2 = [i.text for i in q.find_all(class_ = 'score')]
			w = re.search('tied (.*)won', q.text).group(1)[1:]
			t = w.split()[-1]
			for key,value in teams.items():
				if t in key:
					winner = value[1]
			margin = "Win by Super Over" 
		else:
			date = soup.find_all(class_ = 'description')[0].text.split(',')[2].strip()
			mom = 'None'
			winner = 'No Result'
			margin = 'No Result'
			s = q.find_all(class_ = 'score')
			if len(s)>1:
				inn1,inn2 = [i.text for i in s]
			elif len(s) == 1:
				inn1 = s[0].text
				inn2 = "None"
			else:
				inn1 = inn2 = "None"
	else:
		return None
	return match_id,year,match_number+1,date,venue,city,first,second,inn1,inn2,winner,margin,mom,rpo1,rpo2,fow1,ovr1,fow2,ovr2
