import os
import sys
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import random
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC, LinearSVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.externals import joblib

if (len(sys.argv) != 4) :
	print('\nUsage: python3 sklearn-train.py datasets_path models_path svm_kernel\n\nsvm_kernel: one of linear, poly, rbf, sigmoid, or linearsvc "which trains an OVA linear model".');
	sys.exit()

dataset_path = sys.argv[1]
models_path = sys.argv[2]
svm_kernel = sys.argv[3].casefold()

files = {}
# r=root, d=directories, f=files
for r, d, f in os.walk(dataset_path):
  for file in f:
    files[file]=os.path.join(r, file)

if not os.path.exists(models_path):
  os.makedirs(models_path)


for file in files:
  file_no_ext = file
  if (file_no_ext.find('.') != -1) :
    file_no_ext = file_no_ext[:file_no_ext.find('.')]

  # These are the classifiers that permit training data with sample weights!
  models_names = [svm_kernel]
  
  if svm_kernel == 'linearsvc' :
    classifiers = [LinearSVC()]
  else :
    classifiers = [SVC(kernel=svm_kernel)]

  print("file name :", file)
  data = pd.read_csv(files[file], delimiter=r"\s+").dropna().iloc[:200000]
  
  # if records equals to classes number, duplicates the data
  if data.shape[0] == data.iloc[:,0].nunique():
    data = data.append(data)

  # words (features) encoding
  from sklearn.preprocessing import OrdinalEncoder
  enc = OrdinalEncoder(dtype=np.int32)
  features = enc.fit_transform(data.iloc[:,2:])

  # save the encoder 
  enc_name = os.path.join(models_path, 'encoder'+'-'+file_no_ext)[:256]
  if os.path.exists(enc_name):
    continue  
  joblib.dump(enc, enc_name)

  # target and weights
  target = data.iloc[:,0]
  weights = data.iloc[:,1].values
  
  print("Rules(classes) number :",target.nunique())
  print("Words(features) number :",features.shape[1])
  print("Records number :",features.shape[0])
  print(data.iloc[:target.nunique(),:] , '\n')

  # split to train and test
  X_train, X_test, y_train, y_test, w_train, w_test = \
      train_test_split(features, target, weights, test_size=.5, random_state=0, stratify=target)

  # train models and print their scores
  for name, model in zip(models_names, classifiers):
    print("model :", name, ",", end = '')
    model.fit(X=X_train, y=y_train, sample_weight=w_train)
    score = model.score(X=X_test, y=y_test, sample_weight=w_test)
    print(" score =", score)
    
    # save models
    model_name = os.path.join(models_path, name+'-'+file_no_ext)[:256]
    joblib.dump(model, model_name)
  print("----------------------------------------------\n")
