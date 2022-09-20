import sys
import warnings
if not sys.warnoptions:
        warnings.simplefilter("ignore")
'''
    There will be NumbaDeprecationWarnings here, use the above code to hide the warnings
'''            
import numpy as np
import pandas as pd
from setpath import set_data_path
import time
import pickle


# You can import different datasets here from Lenskit
from lenskit.datasets import MovieLens


def averaged_item_score(algo, transet, item_popularity, a = 0.2):  
    '''
        algo: trained implicitMF model
        transet: ['user', 'item', 'rating', 'timestamp']
        new_ratings: Series
        N: # of recommendations
        item_popularity: ['item', 'count', 'rank']
    '''

    items = transet.item.unique()
        # items is NOT sorted by default
    users = transet.user.unique()
    num_users = len(users)
        # users is NOT sorted by default
    
    ## discounting popular items
    highest_count = item_popularity['count'].max()
    digit = 1
    while highest_count/(10 ** digit) > 1:
        digit = digit + 1
    denominator = 10 ** digit
    
    ## items: ndarray -> df
    ave_scores_df = pd.DataFrame(items, columns = ['item'])
    ave_scores_df['ave_score'] = 0
    ave_scores_df['ave_discounted_score'] = 0
    calculated_users = -1
    start = time.time()
    for user in users:
        calculated_users += 1;
        print(num_users - (calculated_users + 1), end = '\r') 
            # flushing does not work
        
        user_implicit_preds = algo.predict_for_user(user, items)
            # the ratings of the user is already in the trainset used to train the algo
            # return a series with 'items' as the index, order is the same
        user_implicit_preds_df = user_implicit_preds.to_frame().reset_index()
        user_implicit_preds_df.columns = ['item', 'score']
        user_implicit_preds_df = pd.merge(user_implicit_preds_df, item_popularity, how = 'left', on = 'item')
            # ['item', 'score', 'count', 'rank']
        user_implicit_preds_df['discounted_score'] = user_implicit_preds_df['score'] - a*(user_implicit_preds_df['count']/denominator)
            # ['item', 'score', 'count', 'rank', 'discounted_score']
                
        ave_scores_df['ave_score'] = (ave_scores_df['ave_score'] * calculated_users + user_implicit_preds_df['score'])/(calculated_users + 1)
        ave_scores_df['ave_discounted_score'] = (ave_scores_df['ave_discounted_score'] * calculated_users + user_implicit_preds_df['discounted_score'])/(calculated_users + 1)
    
    print(ave_scores_df.head(20))
    print("\nIt took %.0f seconds to calculate the averaved item scores." % (time.time() - start))
    
    return ave_scores_df
    
if __name__ == "__main__":    
    

    ### Import implicit MF model, saved in an object
    f_import = open('model/implictMF.pkl', 'rb')
    algo = pickle.load(f_import)
    f_import.close()
    
    ### Import offline dataset, this was  also used as the transet in RSSA
    data_path = set_data_path()
    attri_name = ['user', 'item', 'rating', 'timestamp']
    
    # This is the training data being loaded
    ratings_train = MovieLens('data/ml-latest-small').ratings
    
    ### Import item popularity for discounting from the outout side
    item_popularity = pd.read_csv(data_path + 'item_popularity.csv')
    
    ave_item_score = averaged_item_score(algo, ratings_train, item_popularity)
        # ['item', 'ave_score', 'ave_discounted_score']
    ave_item_score.to_csv(data_path + 'averaged_item_score_implicitMF.csv', index = False)