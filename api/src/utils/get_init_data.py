import os
import shutil
import zipfile
import urllib.request

def init_dirs():
	print('Initializing directory structure.')

	if not os.path.exists('algs/model'):
		os.makedirs('algs/model')

	if not os.path.exists('algs/data'):
		os.makedirs('algs/data')
	
	if not os.path.exists('temp'):
		os.makedirs('temp')
		
	if not os.path.exists('db_connectors/db'):
	    os.makedirs('db_connectors/db')

def get_data():
	print("Getting data from RSSA server.")
	urllib.request.urlretrieve('https://rssa.recsys.dev/newrs/api/v1', "temp/rssa.zip")

	print("Unpacking data files.")
	with zipfile.ZipFile("temp/rssa.zip", 'r') as zip_ref:
		zip_ref.extractall('temp/')

	print("Organizing files.")
	try:
		shutil.move('temp/cache', 'db_connectors/')
	except shutil.Error:
		print('Cache already exists, skipping.')
	try:
		shutil.move('temp/ieRS_movieInfo_emotions_ranking.csv', 'algs/data/ieRS_movieInfo_emotions_ranking.csv')
	except shutil.Error:
		print('ieRS_movieInfo_emotions_ranking.csv already exists, skipping.')
	try:
		shutil.move('temp/rssa_movie_info.csv', 'algs/data/rssa_movie_info.csv')
	except shutil.Error:
		print('rssa_movie_info.csv already exists, skipping.')

	print("Checking for MovieLens dataset.")
	if not os.path.exists('algs/data/ml-latest-small'):
		print('Movie lens data does not exist. Downloading the latest small datset.')
		urllib.request.urlretrieve('https://files.grouplens.org/datasets/movielens/ml-latest-small.zip', 'temp/ml-latest-small.zip')
		with zipfile.ZipFile("temp/ml-latest-small.zip") as zip_ref:
			zip_ref.extractall('temp/')
		shutil.move('temp/ml-latest-small', 'algs/data/ml-latest-small')
	else:
		print('Movie lens dataset exists. Nothing to do.')

	print("Cleaning up.")
	shutil.rmtree('temp')
	# os.remove('temp.zip')
	# os.remove('ml-latest-small')
	# os.remove('ml-latest-small.zip')
