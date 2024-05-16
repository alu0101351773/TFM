#%%

#LIBRERIAS
from sklearn import svm
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import GridSearchCV
import pandas as pd

from sklearn.metrics import accuracy_score, recall_score, precision_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split

# Modificación del Jorge (a.k.a. la mickey-herramienta)
import os

script_dir = os.path.dirname(os.path.abspath(__file__))

csv_file_path = os.path.join(script_dir, 'inventario-1anio.csv')

# IMPORTAR DATOS
data = pd.read_csv(csv_file_path,decimal=',').iloc[:,1:]

# SEPARAMOS ENTRE ATRIBUTOS Y CLASES
X = data.drop(['Fugando combustible'],axis=1)
y = data['Fugando combustible']


# APLICANDO GRIDSEARCHCV OBTENEMOS EL MEJOR MODELO EN BASE A LA PUNTUNCACIÓN ROC_AUC
# Y APLICANDO CROSS VALIDATION DE 10.
model_params = {
    'svm': {
        'model': svm.SVC(gamma='auto'),
        'params' : {
            'C': [1,10,20],
            'kernel': ['rbf','linear']
        }  
    },
    'random_forest': {
        'model': RandomForestClassifier(),
        'params' : {
            'n_estimators': [1,5,10]
        }
    },

    'naive_bayes_gaussian': {
        'model': GaussianNB(),
        'params': {}
    },

    'logistic_regression' : {
        'model': LogisticRegression(solver='liblinear',multi_class='auto'),
        'params': {
            'C': [1,5,10]
        }
    },
}

scores = []

for model_name, mp in model_params.items():
    clf =  GridSearchCV(mp['model'], mp['params'], cv=10, scoring='roc_auc', return_train_score=False)
    clf.fit(X, y)
    scores.append({
        'model': model_name,
        'best_score': clf.best_score_,
        'best_params': clf.best_params_
    })

df = pd.DataFrame(scores, columns=['model', 'best_score', 'best_params'])
df.columns = ['MODELO', 'MEJOR PUNTUACIÓN', 'MEJORES PARAMETROS']
# print(df)
print(df.iloc[:,:2])

best_clf = df.loc[df['MEJOR PUNTUACIÓN'].idxmax()].MODELO
print('\nEL MEJOR ESTIMADOR ES : ' + best_clf)

print('\nPUNTUACIÓN DEL MODELO CON MUESTRAS DE PRUEBA:')

# SEPARAMOS UN SEGEMENTO DE ENTRENAMIENTO Y OTRO PARA EVALUAR EL TEST
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, shuffle=False, random_state=0)

clf =  GridSearchCV(model_params[best_clf]['model'], 
                    model_params[best_clf]['params'],
                    scoring='roc_auc', 
                    return_train_score=False)

clf.fit(X_train, y_train) 
y_pred = clf.predict(X_test)

print('scoring roc auc : ' + str(round(roc_auc_score(y_test, y_pred),3)))
print('Accuracy Score : ' + str(round(accuracy_score(y_test, y_pred),3)))
print('Precision Score : ' + str(round(precision_score(y_test, y_pred),3)))
print('Recoll Score :' + str(round(recall_score(y_test, y_pred),3)))
print('F1 Score : ' + str(round(f1_score(y_test, y_pred),3)))



#%%

#LIBRERIAS
from sklearn import svm
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import GridSearchCV
import pandas as pd

from sklearn.metrics import accuracy_score, recall_score, precision_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split


# IMPORTAR DATOS
data = pd.read_csv('inventario-1mes2.csv',decimal=',').iloc[:,1:]

# SEPARAMOS ENTRE ATRIBUTOS Y CLASES
X = data.drop(['Fugando combustible'],axis=1)
y = data['Fugando combustible']


# APLICANDO GRIDSEARCHCV OBTENEMOS EL MEJOR MODELO EN BASE A LA PUNTUNCACIÓN ROC_AUC
# Y APLICANDO CROSS VALIDATION DE 10.
model_params = {
    'svm': {
        'model': svm.SVC(gamma='auto'),
        'params' : {
            'C': [1,10,20],
            'kernel': ['rbf','linear']
        }  
    },
    'random_forest': {
        'model': RandomForestClassifier(),
        'params' : {
            'n_estimators': [1,5,10]
        }
    },

    'naive_bayes_gaussian': {
        'model': GaussianNB(),
        'params': {}
    },

    'logistic_regression' : {
        'model': LogisticRegression(solver='liblinear',multi_class='auto'),
        'params': {
            'C': [1,5,10]
        }
    },
}

scores = []

for model_name, mp in model_params.items():
    clf =  GridSearchCV(mp['model'], mp['params'], cv=10, scoring='roc_auc', return_train_score=False)
    clf.fit(X, y)
    scores.append({
        'model': model_name,
        'best_score': clf.best_score_,
        'best_params': clf.best_params_
    })

df = pd.DataFrame(scores, columns=['model', 'best_score', 'best_params'])
df.columns = ['MODELO', 'MEJOR PUNTUACIÓN', 'MEJORES PARAMETROS']
# print(df)
print(df.iloc[:,:2])

best_clf = df.loc[df['MEJOR PUNTUACIÓN'].idxmax()].MODELO
print('\nEL MEJOR ESTIMADOR ES : ' + best_clf)

print('\nPUNTUACIÓN DEL MODELO CON MUESTRAS DE PRUEBA:')

clf =  GridSearchCV(model_params[best_clf]['model'], 
                    model_params[best_clf]['params'],
                    scoring='roc_auc', 
                    return_train_score=False)

clf.fit(X, y) 
y_pred = clf.predict(X)

print('scoring roc auc : ' + str(round(roc_auc_score(y, y_pred),3)))
print('Accuracy Score : ' + str(round(accuracy_score(y, y_pred),3)))
print('Precision Score : ' + str(round(precision_score(y, y_pred),3)))
print('Recoll Score :' + str(round(recall_score(y, y_pred),3)))
print('F1 Score : ' + str(round(f1_score(y, y_pred),3)))


# %%
