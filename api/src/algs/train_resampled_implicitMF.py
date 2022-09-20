import sys
import warnings
if not sys.warnoptions:
        warnings.simplefilter("ignore")
'''
    There will be NumbaDeprecationWarnings here, use the above code to hide the warnings
'''            
import numpy as np
import pandas as pd
import setpath
import time
import pickle
import os

# You can import different datasets here from Lenskit
from lenskit.datasets import MovieLens

# You can import different algorithms here from Lenskit
from lenskit.algorithms import user_knn as knn

data_path = setpath.set_data_path()
fullpath_trian = data_path + 'train.npz'
attri_name = ['user', 'item', 'rating', 'timestamp']

# This is the training data being loaded
ratings_train = MovieLens('data/ml-latest-small').ratings

## 1 - Discounting the input ratings by ranking
item_popularity = pd.read_csv(data_path + 'item_popularity.csv')   
    # ['item', 'count', 'rank']

previsous_count = 0
previsous_rank = 0
for index, row in item_popularity.iterrows():
    current_count = row['count']
    
    if row['count'] == previsous_count:
        row['rank'] = previsous_rank

    previsous_count = current_count
    previsous_rank = row['rank']
            
# 1.2 - Start to discounting the input ratings by ranking
b = 0.4
ratings_train_popularity = pd.merge(ratings_train, item_popularity, how = 'left', on = 'item')
ratings_train_popularity['discounted_rating'] = ratings_train_popularity['rating']*(1-b/(2*ratings_train_popularity['rank']))
ratings_train = ratings_train_popularity[['user', 'item', 'discounted_rating', 'timestamp']]
ratings_train = ratings_train.rename({'discounted_rating': 'rating'}, axis = 1)

## 2 - Train the *@resampled@* implicit MF model
numObservations = ratings_train.shape[0]
numRepetition = 20
alpha = 0.5
start = time.time()

# This is where you train your model using your algorithm of choice
resampled_algo = knn.UserUser(20, min_nbrs=5)

model_path = os.path.join(os.path.dirname(__file__), './model/')
for i in range(numRepetition):
    print ('Resampling 20 MF models: %d ' % (i + 1), end = '\r')
    sampled_ratings = ratings_train.sample(n = int(numObservations * alpha), replace = False)
    resampled_algo.fit(sampled_ratings)
    filename = model_path + 'resampled_implictMF' + str(i + 1) + '.pkl'
    f = open(filename, 'wb')
    pickle.dump(resampled_algo, f)
    f.close() 
    
print("\n\n%d resampled MF models trained." % numRepetition)
end = time.time() - start
print('\nDone!!! Time spent: %0.0fs' % end)
