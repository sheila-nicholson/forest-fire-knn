import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_validate, cross_val_predict
import xgboost as xgb
import matplotlib.pyplot as plt

# read in df
df = pd.read_csv('fires_final_dataset.csv')
df['IGNITION_DATE'] = pd.to_datetime(df['IGNITION_DATE'], errors='coerce',)
df['fire_year'] = df['IGNITION_DATE'].dt.year
df['fire_month'] = df['IGNITION_DATE'].dt.month

# represent the months cyclically rather than 1-12
df['month_sin'] = np.sin(2 * np.pi * df['fire_month'] / 12)
df['month_cos'] = np.cos(2 * np.pi * df['fire_month'] / 12)


# add a bindary encoding for prediction classes
# 1 - fire size is >= 100 hectares
# 0 - fire size is <100 

features = ['avg_tmp_igd', 
            'avg_tmp_7d', 
            'avg_hmd_igd', 
            'avg_hmd_7d', 
            'avg_wind_igd', 
            'avg_wind_7d', 
            'precp_igd', 
            'total_precp_7d', 
            'total_precp_30d', 
            'fire_month',
            'weather_station_distance_km', 
            'municipality_distance_km', 
            'POPULATION',
            'fire_year',
            'month_sin',
            'month_cos',
            'FIRE_SIZE_HECTARES']

X = df[features]
# drop any samples with null features 
X = X.dropna()
# print(X.isna().sum())

target = pd.Series(0, index=X.index, name='fire_size_class')
moderate = X['FIRE_SIZE_HECTARES'] >= 100

# remove target from features 
X = X.drop(columns=['FIRE_SIZE_HECTARES'])

target.loc[moderate] = 1
y = target

# 70% training, 15% validation, 15% testing
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.30, stratify=y, random_state=982)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=982)

print('Training:', X_train.shape)
print('Validation:', X_val.shape)
print('Testing:', X_test.shape)

print('\nTraining classes:')
print(y_train.value_counts(normalize=True))

print('\nValidation classes:')
print(y_val.value_counts(normalize=True))

print('\nTesting classes:')
print(y_test.value_counts(normalize=True))

# fit xgboost model
# train_weights = compute_sample_weight(class_weight='balanced', y=y_train, )
negative_count = (y == 0).sum()
positive_count = (y == 1).sum()

class_ratio = negative_count / positive_count

xgboost_model = xgb.XGBClassifier(objective='binary:logistic',
                                  tree_method='hist',
                                  n_estimators=200,
                                  learning_rate=0.03,
                                  max_depth=2,
                                  min_child_weight=5,
                                  subsample=0.8,
                                  colsample_bytree=0.8,
                                  scale_pos_weight=class_ratio,
                                  eval_metric='logloss',
                                  random_state=982)



# fit random forest model
random_forest_model = RandomForestClassifier(n_estimators=500,
                                             max_depth=None,
                                             min_samples_leaf=3,
                                             max_features='sqrt',
                                             class_weight='balanced',
                                             random_state=42,
                                             n_jobs=-1,)

# make pipeline to fit knn model - must scale features first
knn_model = make_pipeline(StandardScaler(),KNeighborsClassifier(n_neighbors=11, weights='distance'))

models = {'XGBoost': xgboost_model,
          'Random Forest': random_forest_model,
          'KNN': knn_model}

# do cross validation on all of the models
results = []
scoring = {'balanced_accuracy': 'balanced_accuracy',
           'roc_auc': 'roc_auc',
           'f1_score': 'f1'}
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=982)

for name, model in models.items():
    scores = cross_validate(model, X, y, cv=cv, scoring=scoring, n_jobs=-1)
    y_pred = cross_val_predict(model, X, y, cv=cv, n_jobs=-1)

    results.append({'Model': name,
                    # balanced accuracy is an average of recall (true positive rate) obtained
                    # by each class - may be more telling when classes are imbalanced 
                    'Balanced accuracy': scores['test_balanced_accuracy'].max(),
                    # roc aug tells you how well a model can separate two different classes
                    # across all possible decision thresholds
                    'ROC AUC': scores['test_roc_auc'].max(),
                    # f1 score is a metric used to evaluate a classification model's accuracy. It combines precision 
                    # and recall into a single number by taking their harmonic mean.
                    'F1 score': scores['test_f1_score'].max()})
    print(f'\n{name} Classification Report:')
    print(classification_report(y, y_pred, target_names=['< 100 ha', '>= 100 ha']))

    print(f'{name} Confusion Matrix:')
    print(confusion_matrix(y, y_pred))


summary = pd.DataFrame(results)
summary = summary.set_index('Model')

print('\nModel comparison - values are from the max fold:')
print(summary)

ax = summary.plot(kind='bar', figsize=(9, 5))
plt.ylabel('Score')
plt.xlabel('Model')
plt.title('Cross-Validated Model Performance')
plt.xticks(rotation=0)
plt.ylim(0, 1.05)

# add percentage above each bar
for container in ax.containers:
    ax.bar_label(container, labels=[f'{value:.2f}' for value in container.datavalues], padding=3)

plt.legend()
plt.tight_layout()
plt.savefig('plots/model_performance.png')
# plt.show()
plt.close()



