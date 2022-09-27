import pandas as pd
import numpy as np
from sklearnex import patch_sklearn #Improves sklearn alghoritms performance
patch_sklearn()
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression

# This function makes predict_proba and stores for each sample only the class predicted with the respective prob
def get_class_w_prob(cf, level_name, X_test, X_test_scal, index=None):
    #Check which algorithm is
    for alg_name, alg_class in {'RF': RandomForestClassifier, 'KNN': KNeighborsClassifier, 
                                'LR': LogisticRegression}.items():
        if cf.__class__ is alg_class:
            break
    #scaled features when is not RF (for KNN and LR)
    if alg_name == 'RF':
        X_test = X_test
    else:
        X_test = X_test_scal
    proba = cf.predict_proba(X_test)
    n_samples = proba.shape[0]
    pred = np.empty((n_samples, 2), dtype='object')
    for i in range(n_samples):
        pred[i, 0] = cf.classes_[np.argmax(proba[i])]
        pred[i, 1] = proba[i][np.argmax(proba[i])]
    return pd.DataFrame(pred, columns=[f'{level_name} pred', f'{level_name} prob'], index=index)