from utils.init_suserdb import init_survey_user_db
from utils.init_moviedb import init_movie_db
from utils.get_init_data import init_dirs, get_data


if __name__ == '__main__':
	init_dirs()
	get_data()
	init_survey_user_db()
	init_movie_db()
