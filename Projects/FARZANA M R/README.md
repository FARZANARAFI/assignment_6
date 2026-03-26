                                    WATER POTABILITY PREDICTION



import the packages

- import numpy as np
- import pandas as pd
- import matplotlib.pyplot as plt
- import seaborn as sns
- from sklearn.model_selection import train_test_split

- Read the given CSV file(water_potability.csv)

To check the number of null values in each column

- df.isnull().sum() 



- ColumnTransformer: cleanly separates numeric and categorical preprocessing.
- Pipeline: ensures preprocessing happens automatically before training.
- OneHotEncoder: converts categorical strings into numeric dummy variables.
- StandardScaler: keeps numeric features on the same scale.
- RandomForestClassifier: now receives only numeric inputs, so no conversion errors.


