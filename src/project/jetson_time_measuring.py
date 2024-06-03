import os
import random
import time
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import pandas as pd
import pickle as pkl
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
import tensorflow as tf
import toml
# from xgboost import XGBClassifier
# NOTE: No se puede implementar porque requiere versión de pip>=21.3


# Lectura de fichero
data_dict = {}
DATA_DIR = '../../data/'

for data_folder in os.listdir(DATA_DIR):
    *data_files, config_file = os.listdir(f'{DATA_DIR}/{data_folder}')

    leak_value = toml.load(f'{DATA_DIR}/{data_folder}/{config_file}')['tanks']['flow_value']

    train_dataframe, test_data = random.sample(data_files, 2)

    data_dict[data_folder] = {
        'leak_value': leak_value,
        'train_dataframe': pd.read_csv(f'{DATA_DIR}/{data_folder}/{train_dataframe}').drop(columns=['Unnamed: 0']),
        'test_dataframe': pd.read_csv(f'{DATA_DIR}/{data_folder}/{test_data}').drop(columns=['Unnamed: 0'])
    }


# Limpieza de datos
bad_formatted_fields = [
    'Volumen dep. almacenam. ini. (L)',
    'Llenado dep. almacenam. (L)',
    'Volumen dep. almacenam. fin. teor. (L)',
    'Volumen dep. almacenam. fin. (L)',
    'Variacion',
    'Variacion Acum.',
]

for case in data_dict:
    for dataset in ['train_dataframe', 'test_dataframe']:
        for field in bad_formatted_fields:
            data_dict[case][dataset][field] = data_dict[case][dataset][field].str.replace(',', '.')
            data_dict[case][dataset][field] = pd.to_numeric(data_dict[case][dataset][field])


# Selección de características
for case in data_dict:
    for dataset in ['train_dataframe', 'test_dataframe']:
        data_dict[case][dataset] = data_dict[case][dataset].filter(items=['Variacion', 'Fugando combustible'])


# Unificación de conjunto de datos
complete_train_data = pd.concat([element['train_dataframe'] for element in data_dict.values()])

X_train, y_train = (
    complete_train_data.drop(columns='Fugando combustible'), 
    complete_train_data['Fugando combustible']
)


# Param_grids
param_grids_path = '../../pkl/param_grids'


# RandomForest
rf_param_grid = pkl.load(open(f'{param_grids_path}/RandomForestClassifier.pkl', 'rb'))
rf_model = RandomForestClassifier(**rf_param_grid)

start = time.time()
rf_model.fit(X_train, y_train)
end = time.time()

print(f'{"Random Forest:":<15} {(end - start):.4f} s\n')


# Gaussian NB
gnb_param_grid = pkl.load(open(f'{param_grids_path}/GaussianNB.pkl', 'rb'))
gnb_model = GaussianNB(**gnb_param_grid)

start = time.time()
gnb_model.fit(X_train, y_train)
end = time.time()

print(f'{"Gaussian NB:":<15} {(end - start):.4f} s\n')


# KNN
knn_param_grid = pkl.load(open(f'{param_grids_path}/KNeighborsClassifier.pkl', 'rb'))
knn_model = KNeighborsClassifier(**knn_param_grid)

start = time.time()
knn_model.fit(X_train, y_train)
end = time.time()

print(f'{"KNN:":<15} {(end - start):.4f} s\n')


# XGBoost
# xgb_param_grid = pkl.load(open(f'{param_grids_path}/XGBClassifier.pkl', 'rb'))
# xgb_model = XGBClassifier(**xgb_param_grid)

# start = time.time()
# xgb_model.fit(X_train, y_train)
# end = time.time()

# print(f'{"XGBoost:":<15} {(end - start):.4f} s\n')


# Ensemble
vot_model = VotingClassifier(
    estimators=[
        ('rf', RandomForestClassifier()),
        ('nb', GaussianNB()),
        ('knn', KNeighborsClassifier()),
        # ('XGB', XGBClassifier())
    ],
    voting='hard'
)

start = time.time()
vot_model.fit(X_train, y_train)
end = time.time()

print(f'{"Ensemble:":<15} {(end - start):.4f} s\n')


# DL unilayer
unil_model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(X_train.shape[1], 1)),
    tf.keras.layers.LSTM(15, dropout=0.2),
    tf.keras.layers.Dense(1, activation='sigmoid')
])

unil_model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

start = time.time()
unil_model.fit(
    x = X_train,
    y = y_train,
    epochs = 50,
    batch_size = 8192,
    verbose = 0
)
end = time.time()

print(f'{"DL unilayer:":<15} {(end - start):.4f} s\n')


# DL multilayer
multil_model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(X_train.shape[1], 1)),
    tf.keras.layers.LSTM(25, return_sequences=True, dropout=0.2),
    tf.keras.layers.LSTM(40, return_sequences=True, dropout=0.2),
    tf.keras.layers.LSTM(60, dropout=0.2),
    tf.keras.layers.Dense(1, activation='sigmoid')
])

multil_model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

start = time.time()
multil_model.fit(
    x = X_train,
    y = y_train,
    epochs = 50,
    batch_size = 8192,
    verbose = 0
)
end = time.time()

print(f'{"DL multilayer:":<15} {(end - start):.4f} s\n')


# DL ensemble
print('DL ensemble:')
dl_ensemble_total = 0
for case in data_dict:
    X_train = data_dict[case]['train_dataframe'].drop(columns='Fugando combustible')
    y_train = data_dict[case]['train_dataframe']['Fugando combustible']
    
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(X_train.shape[1], 1)),
        tf.keras.layers.LSTM(15, dropout=0.2),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='binary_crossentropy',
        metrics=['accuracy']
    )

    start = time.time()
    model.fit(
        x = X_train,
        y = y_train,
        epochs = 50,
        batch_size = 8192,
        verbose = 0
    )
    end = time.time()
    dl_ensemble_total += (end - start)
    print(f'\t{data_dict[case]["leak_value"]:.4f}  {(end - start):.4f} s')

print(f'\tTOTAL   {dl_ensemble_total:.4f} s')