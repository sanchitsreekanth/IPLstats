import os
import sys
import mysql.connector
from mysql.connector import Error

def create_server_connection(host_name,user_name,user_password):
	connection = None
	try:
		connection = mysql.connector.connect(
			host=host_name,
			user=user_name,
			passwd=user_password)
		print("MySQL Database connection successful")
	except Error as err:
		print(f"Error: '{err}'")

	return connection

def create_db_connection(host_name,user_name,user_password,db_name,verbosity=1):
	connection = None
	try:
		connection = mysql.connector.connect(
			host=host_name,
			user=user_name,
			passwd=user_password,
			database = db_name)
		if verbosity ==0:
			print("MySQL Database connection successful")
	except Error as err:
		print(f"Error: '{err}'")

	return connection

def execute_query(connection, query,verbosity=1):
	cursor = connection.cursor()
	try:
		cursor.execute(query)
		if verbosity == 1:
			print("Query Successful")
		a = cursor.fetchall()
		cursor.close()
		connection.commit()
		return a
	except Error as err:
		print(f"Error: '{err}'")

def create_database(connection, query):
	cursor = connection.cursor()
	try:
		cursor.execute(query)
		print("Database created successfully")
	except Error as err:
		print(f"Error: '{err}'")