import sys
import warnings
if not sys.warnoptions:
        warnings.simplefilter("ignore")
        
import os
import numpy as np
import time
import pandas as pd
import pickle
from setpath import set_data_path

# You can import different datasets here from Lenskit
from lenskit.datasets import MovieLens

# You can import different algorithms here from Lenskit
from lenskit.algorithms import user_knn as knn

data_path = set_data_path()
attri_name = ['user', 'item', 'rating', 'timestamp']

# This is the training data being loaded
ratings_train = MovieLens('data/ml-latest-small').ratings


## 1 - Discounting the input ratings by ranking
# 1.1 - Calculating item rating counts and popularity rank,
# This will be used to discount the popular items from the input side
items, rating_counts = np.unique(ratings_train['item'], return_counts = True)
    # items is sorted by default

items_rating_count = pd.DataFrame({'item': items, 'count': rating_counts}, columns = ['item', 'count'])
items_rating_count_sorted = items_rating_count.sort_values(by = 'count', ascending = False)
item_popularity = items_rating_count_sorted
item_popularity['rank'] = range(1, len(item_popularity)+1)
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

## 2 - Train the implicit MF model
model_path = os.path.join(os.path.dirname(__file__), './model/')
f = open(model_path + 'implictMF.pkl', 'wb')
print("Training models ...")
start = time.time()

# This is where you train your model using your algorithm of choice
algo = knn.UserUser(20, min_nbrs=5)

algo.fit(ratings_train)
end = time.time() - start
print("\nMF models trained.\n")
print('\nTime spent: %0.0fs' % end)
print('\nExporting the trained model - an object - as a pkl file')
pickle.dump(algo, f)
f.close() 

print('\nSaving the item popularity as a csv file')
item_popularity.to_csv(data_path + 'item_popularity.csv', index = False)
    # ['item', 'count', 'rank']

print('\nDone\n')
