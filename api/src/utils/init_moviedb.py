from sqlite3 import Error
import pandas as pd
import math
import json
from pathlib import Path

from dataclasses import dataclass
from flask import Flask, jsonify
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

from flask.json import JSONEncoder
import decimal
import datetime


db = SQLAlchemy()

class RssaJsonEncoder(JSONEncoder):
	def default(self, obj):
		if isinstance(obj, decimal.Decimal):
			return float(obj)
		if isinstance(obj, datetime.timedelta):
			return str(obj)
		if isinstance(obj, datetime.datetime):
			return obj.isoformat

		return JSONEncoder.default(self, obj)


@dataclass
class RankGroup(db.Model):
	__tablename__ = 'rank_group'

	id:int = db.Column(db.Integer, primary_key=True, autoincrement=True)
	group_label:str = db.Column(db.String(144), nullable=False)


@dataclass
class Movie(db.Model):
	__tablename__ = 'movie'

	id:int = db.Column(db.Integer, primary_key=True, autoincrement=True)

	movie_id:int = db.Column(db.Integer, nullable=False, unique=True)
	imdb_id:str = db.Column(db.String(144), nullable=False)
	title_year:str = db.Column(db.String(234), nullable=False)
	title:str = db.Column(db.String(234), nullable=False)
	year:int = db.Column(db.Integer, nullable=False)
	runtime:int = db.Column(db.Integer, nullable=False)
	genre:str = db.Column(db.String(144), nullable=False)
	ave_rating:float = db.Column(db.Numeric, nullable=True)
	director:str = db.Column(db.Text, nullable=True)
	writer:str = db.Column(db.Text, nullable=True)
	description:str = db.Column(db.Text, nullable=True)
	cast:str = db.Column(db.Text, nullable=True)
	poster:str = db.Column(db.String(234), nullable=False)
	count:int = db.Column(db.Integer, nullable=False)
	rank:int = db.Column(db.Integer, nullable=False)

	rank_group:RankGroup = db.Column('rank_group', db.ForeignKey('rank_group.id'))
	rank_group_idx = db.Index(rank_group, postgresql_using='hash')

	year_bucket:int = db.Column(db.Integer, nullable=False)
	year_bucket_idx = db.Index(year_bucket, postgresql_using='hash')

	movie_id_idx = db.Index(movie_id, postgresql_using='tree')

	emotions = db.relationship('MovieEmotions', back_populates='movie', \
		uselist=False)

	def __hash__(self):
		return hash(self.movie_id)

@dataclass
class MovieEmotions(db.Model):
	__tablename__ = 'movie_emotions'

	id:int = db.Column(db.Integer, primary_key=True, autoincrement=True)

	movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), \
		nullable=False, unique=True)

	anger:float = db.Column(db.Numeric, nullable=False)
	anticipation:float = db.Column(db.Numeric, nullable=False)
	disgust:float = db.Column(db.Numeric, nullable=False)
	fear:float = db.Column(db.Numeric, nullable=False)
	joy:float = db.Column(db.Numeric, nullable=False)
	surprise:float = db.Column(db.Numeric, nullable=False)
	sadness:float = db.Column(db.Numeric, nullable=False)
	trust:float = db.Column(db.Numeric, nullable=False)
	iers_count:int = db.Column(db.Integer, nullable=False)
	iers_rank:int = db.Column(db.Integer, nullable=False)

	iers_rank_group:RankGroup = db.Column('rank_group', db.ForeignKey('rank_group.id'))
	iers_rank_group_idx = db.Index(iers_rank_group, postgresql_using='hash')

	movie = db.relationship('Movie', back_populates='emotions')


def get_year_bucket(year):
	yeardiff = 2022 - year
	if yeardiff <= 5:
		return 1
	if yeardiff <= 10:
		return 2
	if yeardiff <= 20:
		return 3
	if yeardiff <= 30:
		return 4
	if yeardiff <= 50:
		return 5
	else:
		return 6


def get_rank_group(rank):
	if rank <= 200:
		return 1
	if rank <= 1000:
		return 2
	if rank <= 2000:
		return 3
	if rank <= 5000:
		return 4
	if rank <= 10000:
		return 5
	else:
		return 6


def init_movie_db():

	app = Flask(__name__)

	config_path = Path(__file__).parent / '../config.json'

	print('Loading database path from {}'.format(config_path))
	with open(config_path) as f:
		settings = json.load(f)

	MOVIE_DB = settings['movidb']

	app.config['SQLALCHEMY_DATABASE_URI'] = MOVIE_DB
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
	db.init_app(app)
	app.json_encoder = RssaJsonEncoder

	print('Creating Movie database')
	with app.app_context():
		print('Dropping Existing tables.')
		db.drop_all()

		print('Creating tables.')
		db.create_all()

		rank_labels = ['Top 200', '200-1k', '1k-2k', '2k-5k', '5k-10k', '10k+']
		rank_groups = [RankGroup(group_label=label) for label in rank_labels]

		db.session.add_all(rank_groups)
		db.session.flush()
		db.session.commit()

	print('Generating ranking bucket for fast queries.')
	movie_dat = pd.read_csv('algs/data/rssa_movie_info.csv')
	movie_dat['rank_group'] = movie_dat.apply(
			lambda row: get_rank_group(row['rank']), axis=1)
	movie_dat['year_bucket'] = movie_dat.apply(
			lambda row: get_year_bucket(row['year']), axis=1)

	movie_ers = pd.read_csv('algs/data/ieRS_movieInfo_emotions_ranking.csv')
	movie_ers['iers_rank_group'] = movie_ers.apply(
			lambda row: get_rank_group(row['ieRS_rank']), axis=1)
	movie_ers['year_bucket'] = movie_ers.apply(
			lambda row: get_year_bucket(row['year']), axis=1)


	movies = {}
	for rowidx, rowitems in movie_dat.iterrows():
		try:
			movieidx = rowitems['movie_id']
			titleyear = rowitems['title(year)']
			year = rowitems['year']
			if math.isnan(year):
				if '(' in titleyear:
					idx = titleyear.index('(')
					year = int(titleyear[idx+1:-1])
			else:
				year = int(year)
			rowitems['year'] = year
			movies[movieidx] = dict(rowitems)

		except ValueError as e:
			print(e)
			print(rowitems)

	for rowidx, rowitems in movie_ers.iterrows():
			movieidx = rowitems['movie_id']
			movies[movieidx] = {**movies[movieidx], **rowitems}

	print('Updating movie emotions')
	movietab = {}
	for k, v in movies.items():
		movie = Movie(movie_id=k, imdb_id=v['imdb_id'], \
				title_year=v['title(year)'], title=v['title'], \
				year=v['year'], runtime=v['runtime'], \
				genre=v['genre'], ave_rating=v['aveRating'], \
				director=v['director'], writer=v['writer'], \
				description=v['description'], cast=v['cast'], \
				poster=v['poster'], count=v['count'], rank=v['rank'], \
				rank_group=v['rank_group'], year_bucket=v['year_bucket'])

		movietab[k] = movie

	print('Adding {} movies to database'.format(len(movietab)))
	with app.app_context():
		db.session.add_all(list(movietab.values()))
		db.session.flush()

		ierstab = []
		for k, v in movies.items():
			if 'anger' in v:
				iers_movie = MovieEmotions(movie_id=movietab[k].id, \
						anger=v['anger'], anticipation=v['anticipation'], \
						disgust=v['disgust'], fear=v['fear'], joy=v['joy'], \
						sadness=v['sadness'], trust=v['trust'], \
						surprise=v['surprise'],
						iers_count=v['ieRS_count'], iers_rank=v['ieRS_rank'], \
						iers_rank_group=v['iers_rank_group']) 
				ierstab.append(iers_movie)

		db.session.add_all(ierstab)
		db.session.flush()
		db.session.commit()
