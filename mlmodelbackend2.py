#%%
from database import executeSQL
from mlmodel import accident_rate_df, weather_list, week_list, month_list
import pandas as pd
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import ShuffleSplit
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
import datetime
import pickle
from sklearn import metrics
from sklearn.metrics import confusion_matrix
import numpy as np
from sklearn.metrics import plot_confusion_matrix
from sklearn.utils import resample
from sklearn.decomposition import PCA
from sklearn.model_selection import KFold
from sklearn.ensemble import GradientBoostingClassifier
import matplotlib.pyplot as plt
from util import plot_two, plot_learning_curve, plot_optimized_result
from sklearn.model_selection import GridSearchCV

def balanced_data():
    df_sql = f"""
    SELECT trim(Severity) severity, strftime('%H', trim(Start_Time)) as hour_of_day, strftime('%m', trim(Start_Time)) as month,
    strftime('%w', trim(Start_Time)) as day_of_wk, trim(State) as state, trim(Weather_Condition) as weather
    from accidents 
    where Severity <>'' and Severity NOT NULL and
    State <>'' and State NOT NULL and
    Start_Time <>'' and Start_Time NOT NULL and
    trim(Weather_Condition) in {weather_list};"""

    model_df = executeSQL(df_sql)

    model_df = model_df.astype({'severity': 'int32', 'hour_of_day': 'int32', 'day_of_wk':'int32', 'month':'int32'})
    features = ['hour_of_day', 'state', 'month', 'day_of_wk', 'weather']
    features_df = pd.get_dummies(model_df[features], columns=['hour_of_day', 'state', 'month', 'day_of_wk', 'weather'])
    print(features_df.head())
    model_df = pd.concat([features_df, model_df['severity']], axis=1)

    #%%
    # balance data, Separate majority and minority classes
    model_df1 = model_df[model_df['severity']==1]
    model_df2 = model_df[model_df['severity']==2]
    model_df3 = model_df[model_df['severity']==3]
    model_df4 = model_df[model_df['severity']==4]
    print("Number of Severity 1:", model_df1.shape[0])
    print("Number of Severity 2:", model_df2.shape[0])
    print("Number of Severity 3:", model_df3.shape[0])
    print("Number of Severity 4:", model_df4.shape[0])

    # balance minority / majority class, 
    df_1_train, df_1_val = train_test_split(model_df1, train_size=0.8, random_state=42)
    num_of_samples = df_1_train.shape[0]
    df_1_train = resample(df_1_train, replace=True, n_samples=num_of_samples*20, random_state=42)
    df_2_train, df_2_val = train_test_split(model_df2, train_size=num_of_samples*20, random_state=42)
    df_3_train, df_3_val = train_test_split(model_df3, train_size=num_of_samples*20, random_state=42)
    df_4_train, df_4_val = train_test_split(model_df4, train_size=num_of_samples*20, random_state=42)
    model_df_train = pd.concat([df_1_train, df_2_train, df_3_train, df_4_train])
    model_df_val = pd.concat([df_1_val, df_2_val, df_3_val, df_4_val])

    # generate x and y
    x_train = model_df_train.iloc[:,:-1]
    y_train = model_df_train.iloc[:,-1]
    x_val = model_df_val.iloc[:,:-1]
    y_val = model_df_val.iloc[:,-1]
    return x_train, y_train, x_val, y_val

def balanced_code():
    x_train, y_train, x_val, y_val = balanced_data()
    clf = RandomForestClassifier(random_state=42, n_estimators=500, max_depth=20)
    clf = clf.fit(x_train,y_train)
    clf.feature_names = list(x_train.columns.values)
    y_pred = clf.predict(x_val)
    print("Validation accuracy:", metrics.accuracy_score(y_val, y_pred))

    # # Draw the confusion matrix
    # disp = plot_confusion_matrix(clf, x_val, y_val, cmap=plt.cm.Blues, normalize='true')
    # print(disp.confusion_matrix)
    # fig = plt.gcf()
    # fig.set_size_inches(9, 9)
    # plt.savefig('balanced_confusion_matrix_2.png')

    # Save model to file in the current working directory
    pkl_filename = "rf_model.pkl"
    with open(pkl_filename, 'wb') as file:
        pickle.dump(clf, file)

if __name__ == "__main__":
    balanced_code()