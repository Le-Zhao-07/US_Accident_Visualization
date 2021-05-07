-----------
DESCRIPTION
-----------
This package is the final project of team 45 for CSE 6242 @ Georgia Tech Spring 2020. The project is about "Visualization and forecast of traffic accidents in US". The package mainly contains three different parts: map section, machine learning and different visualization charts.
The main function is in index.py.
Usmap.py belongs to the map section which contains map chart, filter and Search Dangerous Road Components.
Machine learning section has mlmodel.py which is the front-end of machine learning, and mlmodelbackend.py which is the back-end of machine learning.
Visulization chart section has three python files which are barchart.py, linechart.py and bubblechart.py.

------------
INSTALLATION
------------
Python 3.7 should be used. Also, internet connection is required. 

1. You can choose to download the entire zip file for this repository to your system or use terminal:
```
    git clone https://github.gatech.edu/cs6242/accidents.git
```

2. Download the database accidents.db from the following URL:  
https://drive.google.com/file/d/13Mcf00RBcvIgT75QMBOvp9l-AlHMxj0I/view?usp=sharing  
Put the accidents.db in the folder which you cloned accidents folder.

(Optional) if you are interested in getting the database by your own, please download the zip file in the following URL:  
https://drive.google.com/file/d/1lQGI5CM-A0dOCGgUoAETs3EHESzWPDB6/view?usp=sharing  
Then, unzip the file and put those under the accidents/data folder, execute the SQLite script in the sqlite_script.txt in cmd to get the accidents.db.

3. Install dependent packages:

  * Option 1 (recommended): use conda to create environment and install packages:
    ```
    conda env create -f environment.yml
    ```
  * Option 2: use pip
    ```
    pip install -r requirements.txt
    ```

---------
EXECUTION
---------
1. Open terminal inside the project folder. Run the program index.py in python:
      python index.py
2. After showing "* Running on http://127.0.0.1:8050/", copy and paste the link into a browser.
3. We already deployed the code to AWS, you can also go to http://ec2-100-27-28-45.compute-1.amazonaws.com:8050/ to check it.
Go to the above url within your favorite browser (please prefer Chrome or Firefox)


---------
DEMO VIDEO
---------
You can watch the demo video to know how to run our code:
https://youtu.be/Qej5PoCWaug


--------------------------------------------------------------------------------------

Explore on the website:

The first part of the visualization is the map. It will show the number of accidents per state when you hover the cursor on the state. You can apply various filters or reset them. When you zoom-in the map to street level, it will load and show the exact points where the accidents happened. 
The bottom-left part of the map will show the dangerous roads nearby. You can fill in your interested address, state, city or zip code to check top 5 most dangerous streets.

The second part is a machine learning prediction. It will predict the accident rate based on different conditions which you can choose in the left panel.

The third part is a series of analytical plots. It will show three kinds of charts: a bar chart, a line chart and a bubble chart which enable us to analyze the data from different aspects.

More details are included in the report. Please feel free to give us feedback.

Have fun!
