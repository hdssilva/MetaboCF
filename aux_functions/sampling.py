import numpy as np
import pandas as pd
from sklearn.utils.random import sample_without_replacement

def bin_ObyO_sampling(X, y, neg_size, seed=None):
    #Set class sizes
    class_, c_size = np.unique(y, return_counts=True)
    class_not_sampled = pd.Series(dict(zip(class_, c_size)))
    class_sampled = pd.Series()
    remaining = neg_size
    while True:
        to_sample = class_not_sampled[class_not_sampled < int(remaining/len(class_not_sampled))]
        if len(to_sample) != 0:
            class_sampled = pd.concat([class_sampled, to_sample])
            class_not_sampled = class_not_sampled[class_not_sampled > int(remaining/len(class_not_sampled))]
            remaining = neg_size - class_sampled.sum()
        else:
            break
    class_not_sampled = class_not_sampled.sort_values()
    rest = int(remaining/len(class_not_sampled))
    class_not_sampled = class_not_sampled.sort_values(ascending=False)
    for class_ in class_not_sampled.index:
        if class_ in list(class_not_sampled.iloc[:remaining%len(class_not_sampled)].index):
            class_sampled = pd.concat([class_sampled, pd.Series({class_:rest+1})])
        else:
            class_sampled = pd.concat([class_sampled, pd.Series({class_:rest})])
    class_sampled = class_sampled.sort_index()
    #Make sampling
    X_sampled = []
    y_sampled = np.array([])
    for class_, sample_size in class_sampled.iteritems():
        X_class = X[y==class_]
        X_sampled.extend([i for i in X_class[sample_without_replacement(len(X_class), sample_size, 
                                                                                             random_state=seed)]])
        y_sampled = np.append(y_sampled, np.array([class_]*sample_size))
    return np.array(X_sampled), y_sampled