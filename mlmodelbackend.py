#%%
from database import executeSQL
from mlmodel import accident_rate_df, weather_list, week_list, month_list
import pandas as pd
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
import datetime
import pickle
from sklearn import metrics
from sklearn.metrics import confusion_matrix
import numpy as np
from sklearn.metrics import plot_confusion_matrix
import matplotlib.pyplot as plt
from sklearn.utils import resample


df_sql = f"""
SELECT trim(Severity) severity, strftime('%H', trim(Start_Time)) as hour_of_day, strftime('%m', trim(Start_Time)) as month,
strftime('%w', trim(Start_Time)) as day_of_wk,
trim(State) state, 

case when [Temperature(F)] < 0 then '<0'
 when [Temperature(F)] >= 0 and [Temperature(F)]<30 then '[0, 30)'
 when [Temperature(F)] >= 30 and [Temperature(F)]<50 then '[30, 50)'
 when [Temperature(F)] >= 50 and [Temperature(F)]<70 then '[50, 70)'
 when [Temperature(F)] >= 70 and [Temperature(F)]<90 then '[70, 90)'
 else '>=90'
end as temperature,

case when [Visibility(mi)] < 2 then 'Poor [0,2)'
 when [Visibility(mi)] >= 2 and [Visibility(mi)]<5 then 'Moderate [2,5)'
 when [Visibility(mi)] >= 5 and [Visibility(mi)]<10 then 'Good [5,10)'
 when [Visibility(mi)] >= 10 then 'Very Good >=10'
end as visibility,

trim(Weather_Condition) weather

from accidents 

where Severity <>'' and Severity NOT NULL and
State <>'' and State NOT NULL and
Start_Time <>'' and Start_Time NOT NULL and
[Temperature(F)] <>'' and [Temperature(F)] NOT NULL and 
[Visibility(mi)] <>'' and [Visibility(mi)] NOT NULL and
trim(Weather_Condition) in {weather_list};"""


model_df = executeSQL(df_sql)

# model_df = pd.merge(selected, accident_rate_df, how='left', on=['state'])

# print(model_df)
# print(model_df.info())

model_df = model_df.astype({'severity': 'int32', 'hour_of_day': 'int32', 'day_of_wk':'int32', 'month':'int32'})
# model_df['month'] = pd.to_datetime(model_df['date_time']).dt.month_name()

print(model_df.columns)
print(model_df.head(20))
# print(model_df)
# print(model_df.info())

#%%
# balance data, Separate majority and minority classes
#remove 15% of total data(too huge)
num_samples = len(model_df) * 0.85
model_df1 = model_df[model_df['severity']==1]
model_df2 = model_df[model_df['severity']==2]
model_df3 = model_df[model_df['severity']==3]
model_df4 = model_df[model_df['severity']==4]

# balance minority / majority class, 
df_1 = resample(model_df1, replace=True, n_samples=int(0.2*num_samples))
df_2 = resample(model_df2, replace=False, n_samples=int(0.3*num_samples))
df_3 = resample(model_df3, replace=False, n_samples=int(0.3*num_samples))
df_4 = resample(model_df4, replace=True, n_samples=int(0.2*num_samples))

model_df_resample = pd.concat([df_1, df_2, df_3, df_4])

print('df length', len(model_df_resample))
# print(model_df_resample)

#%%
# add day of week, month
features = ['hour_of_day', 'state', 'temperature', 'month', 'day_of_wk',
       'visibility', 'weather']
y_col = ['severity']


x = pd.get_dummies(model_df_resample[features], columns=['state', 'temperature', 'month', 'day_of_wk',
       'visibility', 'weather'])

print(x.head(5))

y = model_df_resample[y_col]

# print(x)
# print(x.info())

#%%

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.7)

# Create Decision Tree classifer object
clf = RandomForestClassifier(n_estimators=31, max_depth=15, n_jobs=-1, min_samples_split=100)

# Train Decision Tree Classifer
clf = clf.fit(x_train,y_train)

# Add feature names in the model
clf.feature_names = list(x_train.columns.values)

#Predict the response for test dataset
y_pred = clf.predict(x_test)

print("Accuracy:", metrics.accuracy_score(y_test, y_pred))
# result 45.37%

#%%

# Save model to file in the current working directory
pkl_filename = "rf_model.pkl"
with open(pkl_filename, 'wb') as file:
    pickle.dump(clf, file)


#%%

disp = plot_confusion_matrix(clf, x_test, y_test,
                                cmap=plt.cm.Blues,
                                normalize='true')

print(disp.confusion_matrix)
fig = plt.gcf()
fig.set_size_inches(9, 9)
plt.savefig('confusion_matrix.png')
# plt.show()

#%%
# load

# with open("rf_model.pkl", 'rb') as file:
#     clf = pickle.load(file)

from collections import defaultdict

distribution = defaultdict(int)
for index, row in model_df.iterrows():
    distribution[row['severity']] += 1

for i in distribution.keys():
    distribution[i] = distribution[i] / len(model_df)
print('original data distribution', distribution)

