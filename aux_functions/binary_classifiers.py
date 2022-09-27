from sklearn.model_selection import train_test_split
import numpy as np
import pickle
from aux_functions.sampling import bin_ObyO_sampling

def binary_data_sampling(X_train, y_train, X_test, y_test, class_, samp_strat, mult_factor, seed=None, feature_selection=False, features_index=None):        
    if feature_selection is True:
        X_train = X_train[:, features_index]
        X_test = X_test[:, features_index]
        
    X_train_pos = X_train[y_train == class_, :]
    y_train_pos = y_train[y_train == class_]
    X_train_neg = X_train[y_train != class_, :]
    y_train_neg = y_train[y_train != class_]
    X_test_pos = X_test[y_test == class_, :]
    y_test_pos = y_test[y_test == class_]
    X_test_neg = X_test[y_test != class_, :]
    y_test_neg = y_test[y_test != class_]
    train_pos_size = len(y_train_pos)
    test_pos_size = len(y_train_pos)*0.5 #split was 1/3 test & 2/3 train, test would be half of train
    
    if samp_strat is None:
        X_train_ = np.append(X_train_pos, X_train_neg, axis=0)
        y_train_ = [*[1]*len(y_train_pos), *[0]*len(y_train_neg)]
        y_train_ = np.array(y_train_)
        X_test_ = np.append(X_test_pos, X_test_neg, axis=0)
        y_test_ = [*[1]*len(y_test_pos), *[0]*len(y_test_neg)]
        y_test_ = np.array(y_test_)
        train_neg_size = len(y_train_neg)
        return X_train_, y_train_, X_test_, y_test_, train_pos_size, train_neg_size
    
    elif mult_factor*train_pos_size < mult_factor*50:
        if samp_strat == 'stratf':
            X_train_neg, _, y_train_neg, __ = train_test_split(X_train_neg, y_train_neg, stratify = y_train_neg, 
                                                                       train_size=int(mult_factor*50), random_state = seed)
            X_test_neg, _, y_test_neg, __ = train_test_split(X_test_neg, y_test_neg, stratify = y_test_neg, 
                                                                       train_size=int(mult_factor*25), random_state = seed)
        elif samp_strat == 'ObyO':
            X_train_neg, y_train_neg = bin_ObyO_sampling(X_train_neg, y_train_neg, int(mult_factor*50))
            X_test_neg, y_test_neg = bin_ObyO_sampling(X_test_neg, y_test_neg, int(mult_factor*25))

    elif mult_factor*train_pos_size<len(y_train_neg):
        if samp_strat == 'stratf':
            X_train_neg, _, y_train_neg, __ = train_test_split(X_train_neg, y_train_neg, stratify = y_train_neg, 
                                                                       train_size=int(mult_factor*train_pos_size), random_state = seed)
            X_test_neg, _, y_test_neg, __ = train_test_split(X_test_neg, y_test_neg, stratify = y_test_neg, 
                                                                       train_size=int(mult_factor*test_pos_size), random_state = seed)
            
        elif samp_strat == 'ObyO':
            X_train_neg, y_train_neg = bin_ObyO_sampling(X_train_neg, y_train_neg, int(mult_factor*train_pos_size), seed=seed)
            X_test_neg, y_test_neg = bin_ObyO_sampling(X_test_neg, y_test_neg, int(mult_factor*train_pos_size), seed=seed)


    X_train_ = np.append(X_train_pos, X_train_neg, axis=0)
    y_train_ = [*[1]*len(y_train_pos), *[0]*len(y_train_neg)]
    y_train_ = np.array(y_train_)
    X_test_ = np.append(X_test_pos, X_test_neg, axis=0)
    y_test_ = [*[1]*len(y_test_pos), *[0]*len(y_test_neg)]
    y_test_ = np.array(y_test_)
    
    train_neg_size = len(y_train_neg)
    return X_train_, y_train_, X_test_, y_test_, train_pos_size, train_neg_size