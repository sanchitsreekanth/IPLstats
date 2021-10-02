import os
import csv
from settings import teams
from prettytable import PrettyTable
import matplotlib.pyplot as plt


def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
	"""
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
	 
	percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
	filledLength = int(length * iteration // total)
	bar = fill * filledLength + '-' * (length - filledLength)
	print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = "\r")
	# Print New Line on Complete
	if iteration == total: 
		print()


def print_table(fieldnames, data_array):
	x = PrettyTable()
	x.field_names = fieldnames
	for data in data_array:
		x.add_row(data)
	print(x)


def export_to_csv(filename,location,row_array):
	with open(location+os.path.sep + filename, "w") as f:
		writer = csv.writer(f)
		writer.writerows(row_array)


def create_plot(xlabel,ylabel,title,x_data,y_data):
	plt.subplot(2,1,1)
	plt.bar(x_data,y_data,color='maroon',width=0.4)
	plt.xlabel(xlabel)
	plt.xticks(fontsize=7,rotation=45)
	plt.ylabel(ylabel)
	plt.title(title)
	for index,value in enumerate(y_data):
		plt.text(value,index,str(value))
	plt.subplot(2,1,2)
	plt.bar(x_data,y_data,color='maroon',width=0.4)
	plt.xlabel(xlabel)
	plt.xticks(fontsize=7,rotation=45)
	plt.ylabel(ylabel)
	plt.title(title)
	for index,value in enumerate(y_data):
		plt.text(value,index,str(value))
	plt.show()

	'''
	fig = plt.figure(figsize = (10,5))
	plt.bar(x_data,y_data,color='maroon',width=0.4)
	plt.xlabel(xlabel)
	plt.xticks(fontsize=7,rotation=45)
	plt.ylabel(ylabel)
	plt.title(title)
	for index,value in enumerate(y_data):
		plt.text(value,index,str(value))
	plt.show()
	'''

