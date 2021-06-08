import matplotlib.pyplot as plt
from sklearn.model_selection import learning_curve
import numpy as np


def plot_two(x, y1, y2, y1_label, y2_label, xaxis_label, yaxis1_label, yaxis2_label, title, file_name):
    fig, ax1 = plt.subplots(dpi=300)
    ax2 = ax1.twinx()
    ax1.plot(x, y1, 'o-', color='blue', label=y1_label)
    ax2.plot(x, y2, 'o-', color= 'orange', label=y2_label)
    
    ax1.set_xlabel(xaxis_label)
    ax1.set_ylabel(yaxis1_label)
    ax2.set_ylabel(yaxis2_label)
    
    ax1.set_title(title)
    ax1.legend(loc=2, prop={'size':8})
    ax2.legend(loc=4, prop={'size':8})
    fig.tight_layout()
    fig.savefig(file_name)

def plot_learning_curve(estimator, title, X, y, ylim=(0.1, 1.01), cv=None, n_jobs=None, train_sizes=np.linspace(0.2,1.0,5)):
    plt.figure(dpi=300)
    plt.title(title)
    if ylim is not None:
        plt.ylim(*ylim)
    plt.xlabel("Training examples")
    plt.ylabel("Score")
    train_sizes,train_scores,test_scores = learning_curve(estimator, X, y, cv=cv, n_jobs=n_jobs, train_sizes=train_sizes)
    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)
    plt.fill_between(train_sizes, train_scores_mean - train_scores_std,
                     train_scores_mean + train_scores_std, alpha=0.1,
                     color="r")
    plt.fill_between(train_sizes, test_scores_mean - test_scores_std,
                     test_scores_mean + test_scores_std, alpha=0.1, color="g")
    plt.plot(train_sizes, train_scores_mean, 'o-', color="r",
             label="Training score")
    plt.plot(train_sizes, test_scores_mean, 'o-', color="g",
             label="Cross-validation score")

    plt.legend(loc="best")
    return plt

def plot_optimized_result(xaxis, grid, title, file_name):
    testArr = grid.cv_results_['mean_test_score']
    plt.figure(dpi=300)
    plt.plot(xaxis, testArr[0:7], 'o-',label="n_estimators=100")
    plt.plot(xaxis, testArr[7:14], 'o-', label="n_estimators=500")
    plt.plot(xaxis, testArr[14:], 'o-', label="n_estimators=1000")
    plt.xlabel('max_depth')
    plt.ylabel('Cross-validation score')
    plt.title(title)
    plt.legend()    
    plt.savefig(file_name)

state_abbr = {
    "Alabama":"AL",
    #"Alaska":"AK",
    "Arizona":"AZ",
    "Arkansas":"AR",
    "California":"CA",
    "Colorado":"CO",
    "Connecticut":"CT",
    "Delaware":"DE",
    "Florida":"FL",
    "Georgia":"GA",
    #"Hawaii":"HI",
    "Idaho":"ID",
    "Illinois":"IL",
    "Indiana":"IN",
    "Iowa":"IA",
    "Kansas":"KS",
    "Kentucky":"KY",
    "Louisiana":"LA",
    "Maine":"ME",
    "Maryland":"MD",
    "Massachusetts":"MA",
    "Michigan":"MI",
    "Minnesota":"MN",
    "Mississippi":"MS",
    "Missouri":"MO",
    "Montana":"MT",
    "Nebraska":"NE",
    "Nevada":"NV",
    "New Hampshire":"NH",
    "New Jersey":"NJ",
    "New Mexico":"NM",
    "New York":"NY",
    "North Carolina":"NC",
    "North Dakota":"ND",
    "Ohio":"OH",
    "Oklahoma":"OK",
    "Oregon":"OR",
    "Pennsylvania":"PA",
    "Rhode Island":"RI",
    "South Carolina":"SC",
    "South Dakota":"SD",
    "Tennessee":"TN",
    "Texas":"TX",
    "Utah":"UT",
    "Vermont":"VT",
    "Virginia":"VA",
    "Washington":"WA",
    "West Virginia":"WV",
    "Wisconsin":"WI",
    "Wyoming":"WY",
    "District of Columbia":"DC",
    #"Puerto Rico":"PR"
}