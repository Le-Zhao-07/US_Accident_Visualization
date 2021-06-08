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
    df_1 = model_df1
    df_2 = resample(model_df2, replace=False, n_samples=938, random_state=42)
    df_3 = resample(model_df3, replace=False, n_samples=938, random_state=42)
    df_4 = resample(model_df4, replace=False, n_samples=938, random_state=42)
    model_df_resample = pd.concat([df_1, df_2, df_3, df_4])

    # generate x and y
    features = ['hour_of_day', 'state', 'month', 'day_of_wk', 'weather']
    x = pd.get_dummies(model_df_resample[features], columns=['hour_of_day', 'state', 'month', 'day_of_wk', 'weather'])
    print("x original shape: ", x.shape)
    y = model_df_resample['severity']
    return x,y

def original_data():
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

    # generate x and y
    features = ['hour_of_day', 'state', 'month', 'day_of_wk', 'weather']
    x = pd.get_dummies(model_df[features], columns=['hour_of_day', 'state', 'month', 'day_of_wk', 'weather'])
    print("x original shape: ", x.shape)
    y = model_df['severity']
    return x,y    

# The best number of components for balanced data is 42
def optimize_pca_balanced_data():
    x, y = balanced_data()

    learner = RandomForestClassifier(random_state=42, n_estimators=500, max_depth=20)
    kfold = KFold(n_splits=5)
    n_comp_max = 90
    n_comp_list = list(range(1, n_comp_max+1))

    CEV_list=[]
    cv_list=[]
    CEV=0
    for n_comp in n_comp_list:
        pca = PCA(n_components=n_comp, random_state=42)
        x_pca = pca.fit_transform(x)
        CEV += pca.explained_variance_ratio_[-1]
        CEV_list.append(CEV)
        cv_list.append(np.mean(cross_val_score(learner, x_pca, y, cv=kfold, scoring="accuracy")))
    plot_two(x=n_comp_list, y1=CEV_list, y2=cv_list, y1_label='CEV', y2_label='cv accuracy', \
                  xaxis_label='number of components', yaxis1_label='cumulative explained variance', \
                  yaxis2_label='cross-validation accuracy', title='optimize_PCA_balanced_data', file_name='optimize_PCA_balanced_data.png')

# The optimized n_estimators=500, max_depth=20
def optimize_randomforest():
    x, y = balanced_data()
    # Grid search n_estimators and max_depth
    i=[100, 500, 1000]
    j=[1, 5, 10, 15, 20, 25, 30]
    param_grid = dict(n_estimators=i, max_depth=j)
    grid = GridSearchCV(RandomForestClassifier(random_state=42), param_grid, cv=3, scoring='accuracy', return_train_score=True)
    grid.fit(x,y)
    # Plot optimized results
    plot_optimized_result(xaxis=j, grid=grid, title='Optimize n_estimators and max_depth in Random Forest', file_name='optimize_randomforest.png')

def balanced_code():
    x, y = balanced_data()
    # Train Decision Tree Model
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.7)
    # Create Decision Tree classifer object
    clf = RandomForestClassifier(random_state=42, n_estimators=500, max_depth=20)
    # Train Decision Tree Classifer
    clf = clf.fit(x_train,y_train)
    # Predict the response for test dataset
    y_pred = clf.predict(x_test)
    print("Accuracy:", metrics.accuracy_score(y_test, y_pred))

    #%%

    disp = plot_confusion_matrix(clf, x_test, y_test,
                                    cmap=plt.cm.Blues,
                                    normalize='true')

    print(disp.confusion_matrix)
    fig = plt.gcf()
    fig.set_size_inches(9, 9)
    plt.savefig('balanced_confusion_matrix.png')

    cv = ShuffleSplit(n_splits=5, test_size=0.2, random_state=0)
    title = "random forest classifier"
    estimator = RandomForestClassifier(random_state=42, n_estimators=500, max_depth=20)
    plot_learning_curve(estimator, title, x, y, cv=cv)
    plt.savefig("balanced_learning_curve.png")

def balanced_pca_code():    
    x, y = balanced_data()
    pca = PCA(n_components=60, random_state=42)
    x = pca.fit_transform(x)
    print("x dimensionality reduced shape: ", x.shape)
    # Train Decision Tree Model
    x_train, x_test, y_train, y_test = train_test_split(x, y, train_size=0.8)
    # Create Decision Tree classifer object
    clf = RandomForestClassifier(random_state=42, n_estimators=500, max_depth=20)
    # Train Decision Tree Classifer
    clf = clf.fit(x_train,y_train)
    # Predict the response for test dataset
    y_pred = clf.predict(x_test)
    print("Accuracy:", metrics.accuracy_score(y_test, y_pred))

    #%%

    disp = plot_confusion_matrix(clf, x_test, y_test,
                                    cmap=plt.cm.Blues,
                                    normalize='true')

    print(disp.confusion_matrix)
    fig = plt.gcf()
    fig.set_size_inches(9, 9)
    plt.savefig('balanced_pca_confusion_matrix.png')

    cv = ShuffleSplit(n_splits=5, test_size=0.2, random_state=0)
    title = "random forest classifier"
    estimator = RandomForestClassifier(random_state=42, n_estimators=500, max_depth=20)
    plot_learning_curve(estimator, title, x, y, cv=cv)
    plt.savefig("balanced_pca_learning_curve.png")

def original_pca_code():    
    x, y = original_data()
    pca = PCA(n_components=41, random_state=42)
    x = pca.fit_transform(x)
    print("x dimensionality reduced shape: ", x.shape)
    # Train Decision Tree Model
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.7)
    # Create Decision Tree classifer object
    clf = RandomForestClassifier(n_estimators=31, max_depth=15)
    # Train Decision Tree Classifer
    clf = clf.fit(x_train,y_train)
    # Predict the response for test dataset
    y_pred = clf.predict(x_test)
    print("Accuracy:", metrics.accuracy_score(y_test, y_pred))

    #%%

    disp = plot_confusion_matrix(clf, x_test, y_test,
                                    cmap=plt.cm.Blues,
                                    normalize='true')

    print(disp.confusion_matrix)
    fig = plt.gcf()
    fig.set_size_inches(9, 9)
    plt.savefig('original_pca_confusion_matrix.png')

    cv = ShuffleSplit(n_splits=5, test_size=0.2, random_state=0)
    title = "random forest classifier"
    estimator = RandomForestClassifier(random_state=0, n_estimators=31, max_depth=15)
    plot_learning_curve(estimator, title, x, y, cv=cv)
    plt.savefig("original_pca_learning_curve.png")

if __name__ == "__main__":
    # balanced_code() #Accuracy: 0.3510
    balanced_pca_code()
    # original_pca_code()
    # optimize_pca_balanced_data()
    # optimize_randomforest()