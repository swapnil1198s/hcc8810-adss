import sys
from pathlib import Path
import json
from flask import Flask
from db_connectors.db import db
from db_connectors.models.survey import *


def init_survey_user_db():
	app = Flask(__name__)

	config_path = Path(__file__).parent / '../config.json'

	print('Loading database path from {}'.format(config_path))
	with open(config_path) as f:
		settings = json.load(f)

	SURVEY_DB = settings['userdb']

	app.config['SQLALCHEMY_DATABASE_URI'] = SURVEY_DB
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

	print('Initializing Database at {}'.format(SURVEY_DB))
	db.init_app(app)
	with app.app_context():
		print('Dropping all existing tables in the user database.')
		db.drop_all()

		print('Creating tables.')
		db.create_all()

		print('Adding new Survey(title=\'rssa\')')
		survey = Survey(title='rssa')
		db.session.add(survey)
		db.session.flush()
		user = User(survey_id=survey.id, condition=1, user_type=1)
		db.session.add(user)
		pages = ['Welcome', 'Consent', 'Pre Survey Page 1', 'Pre Survey Page 2', 'Pre Survey Page 3', 
			'Pre Survey Page 4', 'Instruction Summary', 'Movie Rating', 'Recommendation Rating 1', \
			'Recommendation Rating 2', 'Recommendation Pick', 'Closing RecSys', 'Post Survey Page 1', \
			'Post Survey Page 2', 'Post Survey Page 3', 'Post Survey Page 4', 'Post Survey Page 5', \
			'Post Survey Page 6', 'Post Survey Page 7', 'Demographic Info', 'Ending']
		page_type = ['welcome', 'consent_form', 'likert_form', 'likert_form', 'likert_form', 'likert_form', \
			'info', 'rating', 'rating', 'rating', 'rating', 'feedback', 'likert_form', 'likert_form', 'likert_form', \
				'rating_familiarity', 'likert_form', 'likert_form', 'likert_form', 'demo_form', 'ending']

		survey_pages = []
		for pnum, (ptitle, ptype) in enumerate(zip(pages, page_type), 1):
			print('Adding new SurveyPage(page_num={}, page_title=\'{}\', page_type=\'{}\')'.format(pnum, ptitle, ptype))
			survey_page = SurveyPage(survey_id=survey.id, page_num=pnum, page_title=ptitle, page_type=ptype)
			survey_pages.append(survey_page)

		db.session.add_all(survey_pages)
		db.session.flush()

		conditions = ['Top N', 'Controversial', 'Hate', 'Hip', 'No Clue']
		cond_acts = ['More movies you may like', 'Movies that are controversial', 
					'Movies you may hate', 'Movies you will be among the first to try',
					'Movies we have no idea about']
		cond_exps = [
			'Beyond the top 7 movies on the left, there are the next 7 movies we \
				think you will like best.',
			'Thes movies received mixed reviews from people who are similar to you: \
				some likes them and some didin\'t.',
			'We predict that you particularly dislike these 7 movies... but we \
				we might be wrong.',
			'These movies received very few ratings, so you would be among the \
				first to try them.',
			'These are movies you may either like or dislike; we simply weren\'t \
				able to make an accurate prediction.'
			]
		survey_conds = []
		for tag, act, exp in zip(conditions, cond_acts, cond_exps):
			print('Adding experimental condition', tag)
			condition = Condition(cond_tag=tag, cond_act=act, cond_exp=exp, survey_id=survey.id)
			survey_conds.append(condition)

		db.session.add_all(survey_conds)
		db.session.flush()


		questions = [(1, 'Likert', 'I fear others may find more entertaining movies than me.', 3, 'FOMO1'),
		(1, 'Likert', 'I get worried when I find out others are finding better movies than me.', 3, 'FOMO2'),
		(1, 'Likert', 'I get anxious when I think about all the possible movies that are out there.', 3, 'FOMO3'),
		(1, 'Likert', 'Sometimes, I wonder if I spend too much time trying to make sure I have checked out every interesting movie.', 3, 'FOMO4'),
		(1, 'Likert', 'It bothers me when I miss an opportunity to learn about new available movies.', 3, 'FOMO5'),
		(1, 'Likert', 'When I miss out on an opportunity to watch a good movie, it bothers me.', 3, 'FOMO6'),
		(1, 'Likert', 'Once I decide to go watch a certain movie, I still check on other movies that are playing to see if there is anything better available.', 3, 'FOMO7'),
		(1, 'Likert', 'When I see a new or different brand on the shelf, I often pick it up just to see what it is like.', 4, 'NOV1'),
		(1, 'Likert', 'I like introducing new brands and products to my friends.', 4, 'NOV2'),
		(1, 'Likert', 'I enjoy taking chances in buying unfamiliar brands just to get some variety in my purchase.', 4, 'NOV3'),
		(1, 'Likert', 'I often read the information on the packages of products just out of curiosity.', 4, 'NOV4'),
		(1, 'Likert', 'I get bored with buying the same brands even if they are good.', 4, 'NOV5'),
		(1, 'Likert', 'I shop around a lot for my clothes just to find out more about the latest styles.', 4, 'NOV6'),
		(1, 'Likert', 'I am a movie lover.', 5, 'MOVE1'),
		(1, 'Likert', 'Compared to my peers I watch a lot of movies.', 5, 'MOVE2'),
		(1, 'Likert', 'Compared to my peers I am an expert on movie.', 5, 'MOVE3'),
		(1, 'Likert', 'I only know a few movies.', 5, 'MOVE4'),
		(1, 'Likert', 'No matter what I do, I have the highest standards for myself.', 6, 'MAXT1'),
		(1, 'Likert', 'I never settle for second best.', 6, 'MAXT2'),
		(1, 'Likert', 'No matter what it takes, I always try to choose the best thing.', 6, 'MAXT3'),
		(1, 'Likert', 'I dont like having to settle for “good enough.”', 6, 'MAXT4'),
		(1, 'Likert', 'I am a maximizer.', 6, 'MAXT5'),
		(1, 'Likert', 'I will wait for the best option, no matter how long it takes.', 6, 'MAXT6'),
		(1, 'Likert', 'I never settle.', 6, 'MAXT7'),
		(1, 'Likert', 'All the recommended movies in the final list were similar to each other.', 13, 'diversity1'),
		(1, 'Likert', 'None of the movies in the final list of recommendations were alike.', 13, 'diversity2'),
		(1, 'Likert', 'Most movies in the final list of recommendations were from the same genre.', 13, 'diversity3'),
		(1, 'Likert', 'The final list of recommended movies suits a broad set of tastes.', 13, 'diversity4'),
		(1, 'Likert', 'The recommended movies were from many different genres.', 13, 'diversity5'),
		(1, 'Likert', 'The recommendations contained a lot of variety.', 13, 'diversity6'),
		(1, 'Likert', 'I liked the movies in the final list of recommendations.', 14, 'recQual1'),
		(1, 'Likert', 'I found the movies in the final list of recommendations appealing.', 14, 'recQual2'),
		(1, 'Likert', 'The recommended movies fit my preference.', 14, 'recQual3'),
		(1, 'Likert', 'The recommended movies were relevant.', 14, 'recQual4'),
		(1, 'Likert', 'The system recommended too many bad movies.', 14, 'recQual5'),
		(1, 'Likert', 'I did <u><strong>not</strong></u> like any of the recommended movies.', 14, 'recQual6'),
		(1, 'Likert', 'I feel like I was recommended the same movies as everyone else.', 15, 'recConformity1'),
		(1, 'Likert', 'I think the recommendations are unique to me.', 15, 'recConformity2'),
		(1, 'Likert', 'I believe that the system is giving me a one of a kind experience.', 15, 'recConformity3'),
		(1, 'Likert', 'I believe that the movies recommended to me are rather different from the movies recommended to others.', 15, 'recConformity4'),
		(1, 'Likert', 'I would <u><strong>not</strong></u> be surprised if the system recommended the same movies to many other users.', 15, 'recConformity5'),
		(1, 'Binary', 'Did you watch this movie before?', 16, 'recFamiliarity1'),
		(1, 'Likert', 'How would you rate this movie?', 16, 'recFamiliarity2'),
		(1, 'Likert', 'I like the movie I’ve chosen from the final recommendation list.', 17, 'choiceSat1'),
		(1, 'Likert', 'The chosen movie fits my preference.', 17, 'choiceSat2'),
		(1, 'Likert', 'I would recommend my chosen movie to others/friends.', 17, 'choiceSat3'),
		(1, 'Likert', 'I was excited about my chosen movie.', 17, 'choiceSat4'),
		(1, 'Likert', 'I think I chose the best movie from the options.', 17, 'choiceSat5'),
		(1, 'Likert', 'I know several items that are better than the one I selected.', 17, 'choiceSat6'),
		(1, 'Likert', 'I would rather watch a different movie from the one I selected.', 17, 'choiceSat7'),
		(1, 'Likert', 'The movie recommender catered to all of my potential interests.', 18, 'tasteCov1'),
		(1, 'Likert', 'The movies that were recommended did <u><strong>not</strong></u> reflect my diverse taste in movies.', 18, 'tasteCov2'),
		(1, 'Likert', 'The movie recommender treated me as a one-dimensional person.', 18, 'tasteCov3'),
		(1, 'Likert', 'The lists of recommendations matched a diversity of my preferences.', 18, 'tasteCov4'),
		(1, 'Likert', 'The movie recommender seemed to target only a small subset of my interests.', 18, 'tasteCov5'),
		(1, 'Likert', 'The recommended movies were a perfect fit for me on many different levels.', 18, 'tasteCov6'),
		(1, 'Likert', 'The movie recommender seemed to stereotype me in a particular category of viewers.', 18, 'tasteCov7'),
		(1, 'Likert', 'I like using the system.', 19, 'sysSat1'),
		(1, 'Likert', 'Using the system is a pleasant experience.', 19, 'sysSat2'),
		(1, 'Likert', 'I would recommend the system to others.', 19, 'sysSat3'),
		(1, 'Likert', 'I can find better movies using the system.', 19, 'sysSat4'),
		(1, 'Likert', 'I would quickly abandon using the system.', 19, 'sysSat5'),
		(1, 'Likert', 'I would use the system more often if possible.', 19, 'sysSat6'),
		(1, 'Text', 'Did anything go wrong while using the system?', 12, 'meta1'),
		(1, 'Text', 'Self identifying race.', 20, 'meta2'),
		(1, 'Text', 'Self identifying gender.', 20, 'meta3'),
		(1, 'Text', 'Survey Completion Placeholder.', 21, 'meta4')]

		surveyquestions = []
		for q in questions:
			print('Adding Survey Question', q)
			survey_question = SurveyQuestion(survey_id=q[0], question_type=q[1], \
				question_text=q[2], survey_page=q[3], question_tag=q[4])
			surveyquestions.append(survey_question)
		
		db.session.add_all(surveyquestions)
		db.session.flush()

		db.session.commit()