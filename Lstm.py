# -*- coding: utf-8 -*-
"""DS_lab_hw1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1NxB7uVydp89VmLoLC9b8C-58ym-UB-BI

# Lstm
"""

# !pip install pytorch
#! pip install torchmetrics
import pandas as pd
import numpy as np
import torch 
import torch.nn as nn
import torchvision.transforms as transforms
import torch.optim as optim
from matplotlib import pyplot as plt
import pickle
from torchmetrics.classification import BinaryF1Score
# metric(preds, target)
from sklearn.metrics import f1_score, precision_score

transform = transforms.Compose([
    transforms.ToTensor()
])

def prepare_dataset_using_pandas(df, patient):
  """
  Create tensor dataset and label from pandas df
  """

  df_patient = df[df['id']== patient].copy(deep=True)
  df_patient.fillna(method="ffill", inplace=True)
  df_patient.fillna(method = "backfill", inplace=True)
  df_patient.fillna(0, inplace=True)
  if df_patient.shape[0]>1:
    label = df_patient['SepsisLabel'].to_list()[-1]
    # y = np.array([0]*(df_patient.shape[0]-1)+[label]).astype('float32')
  else: 
    y = np.array(df_patient['SepsisLabel'].to_list()[0]).astype('float32')
    print("strange")
  X = df_patient.drop(['id', 'SepsisLabel'], axis=1).to_numpy().astype('float32')
  return torch.tensor(X), torch.tensor(label).float()

# Build train and test dfs:

# TRAIN:
all_data_for_training = pd.read_parquet("/content/all_data.parquet")
df_train = all_data_for_training



# TEST:
all_data_for_testing = pd.read_parquet("/content/all_data_for_testing.parquet")
df_test = all_data_for_testing



# PICKLE TRAIN:
def build_pickle_train():
  for i, patient in enumerate(df_train["id"].unique()):
    X, y_train = prepare_dataset_using_pandas(df_train, patient)
    train_list.append((X, y_train))

  with open('train_list.pkl', 'wb') as f:
    pickle.dump(train_list, f)
    
# PICKLE TEST:
def build_pickle_test():
  for i, patient in enumerate(df_test["id"].unique()):
    X, y_train = prepare_dataset_using_pandas(df_test, patient)
    test_list.append((X, y_train))

  with open('test_list.pkl', 'wb') as f:
    pickle.dump(test_list, f)

train_list = []
# test_list = []
build_pickle_train()
# build_pickle_test()

len(train_list)

# TRAIN UNPICKLE:
with open('/content/train_list.pkl', 'rb') as fp:
    train_list = pickle.load(fp)
    print("train_list loaded successfully")

# TEST UNPICKLE:

with open('/content/test_list.pkl', 'rb') as fp:
    test_list = pickle.load(fp)
    print("test_list loaded successfully")

class Model(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(input_size=40, hidden_size=250, num_layers=1, batch_first=True)
        self.linear = nn.Linear(250, 1)
        self.sigmoid = nn.Sigmoid()
        # self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        x, _ = self.lstm(x)
        x = self.linear(x)
        # x = self.dropout(x)
        x = self.sigmoid(x)

        return x

class Model150(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(input_size=40, hidden_size=150, num_layers=1, batch_first=True)
        self.linear = nn.Linear(150, 1)
        self.sigmoid = nn.Sigmoid()
        # self.dropout = nn.Dropout(0.5)

 
    def forward(self, x):
        x, _ = self.lstm(x)
        x = self.linear(x)
        # x = self.dropout(x)
        x = self.sigmoid(x)
        return x

class Model300(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(input_size=40, hidden_size=300, num_layers=1, batch_first=True)
        self.linear = nn.Linear(300, 1)
        self.sigmoid = nn.Sigmoid()
        # self.dropout = nn.Dropout(0.5)
 
    def forward(self, x):
        x, _ = self.lstm(x)
        x = self.linear(x)
        # x = self.dropout(x)
        x = self.sigmoid(x)
        return x

class Model_2layers(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(input_size=40, hidden_size=250, num_layers=2, batch_first=True)
        self.linear = nn.Linear(250, 1)
        self.sigmoid = nn.Sigmoid()
        # self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        x, _ = self.lstm(x)
        x = self.linear(x)
        # x = self.dropout(x)
        x = self.sigmoid(x)
        return x


class Model_3layers(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(input_size=40, hidden_size=250, num_layers=3, batch_first=True)
        self.linear = nn.Linear(250, 1)
        self.sigmoid = nn.Sigmoid()
        # self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        x, _ = self.lstm(x)
        x = self.linear(x)
        # x = self.dropout(x)
        x = self.sigmoid(x)
        return x

# #Load Model
# model = Model()
# model.load_state_dict(torch.load('/content/model.pt'), strict=False)

def run_training(model):

  learning_rate = 1e-3
  optimizer = optim.Adam(model.parameters(),lr=learning_rate)   
  train_stats = []
  test_stats = []

  for epoch in range(n_epochs):
      print("Epoch :",epoch)
      # Train model: -------------------------------------------------------------
      counter =1
      model.train()
      for i, patient in enumerate(train_list):
        X, y_train = train_list[i]
        # Run on model:-----------------------------------------------------------
        if torch.cuda.is_available():
          X = X.cuda()
          y_train = y_train.cuda()
        y_pred = model(X)
        y_pred = y_pred.view(-1)

        loss = loss_fn(y_pred[-1], y_train)
        loss_item = loss.item()

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if counter%2000==0:
          print(f"counter at {counter}/ {len(train_list)}")
        counter+=1
      train_stats.append(loss_item)

      # Validation----------------------------------------------------------------
      # if epoch % 2 != 0:
      #     continue

      model.eval()
      test_predictions = []
      test_labels = []
      with torch.no_grad():
          y_pred = model(X).view(-1)
          test_results = []
          for i, patient in enumerate(test_list):

            X, y_test = test_list[i]
            if torch.cuda.is_available():
              X = X.cuda()
              y_test = y_test.cuda()

            y_pred = model(X)
            y_pred = y_pred.view(-1)
            test_predictions.append(round(y_pred[-1].cpu().item()))
            test_labels.append(y_test.cpu().item())
          
      test_stats.append(f1_score(test_predictions, test_labels))

      print("Epoch %d: train loss %.4f" % (epoch, np.mean(train_stats)))
      print("Epoch %d: test F1 %.4f" % (epoch, f1_score(test_predictions, test_labels)))
      if epoch%5 and epoch > 0:
        learning_rate = learning_rate*0.88
        optimizer = optim.Adam(model.parameters(),lr=learning_rate)

  return train_stats, test_stats

# Prepare for run:

F1 = BinaryF1Score()

learning_rate = 1e-3

loss_fn = nn.BCELoss()

n_epochs = 100

# Run models:

model_generic = Model()
model150 = Model150()
model300 = Model300()
model_2layers = Model_2layers()
model_3layers = Model_3layers()
model_list = [model_3layers]
stats = []
for x in model_list:
  print(f"---------------------------------------- Running {str(x)}-----------------------------------")
  optimizer = optim.Adam(x.parameters(),lr=learning_rate)

  if torch.cuda.is_available():
    x = x.cuda()
    F1 = F1.cuda()
  stats.append(run_training(x))

# Plot F1 & Losses:

f1s = [x[1] for x in stats]
losses = [x[0] for x in stats]

for s, label in zip(f1s, ["Model_3layers","model_2layers"]):
  plt.plot([x for x in range(1, len(s)+1)], s, label= label)
  plt.ylabel("F1")
  plt.xlabel("Epoch")
  plt.title(" Test F1 Score Per Epoch")
plt.legend()
plt.show()

for loss, label in zip(losses, [ "Model_3layers","model_2layers"]):
  plt.plot([x for x in range(len(loss))], [x for x in loss], label= label)
  plt.title("Train loss")
  plt.ylabel("Loss")
  plt.xlabel("Epochs")
plt.legend()
plt.show()

torch.save(model_3layers.state_dict(),'model_3layers.pt')  #<----- pickle model for future use

def create_frame(t):
    fig = plt.figure(figsize=(6, 6))
    # plt.plot(x[:(t+1)], y[:(t+1)], color = 'grey' )
    plt.plot(x[:(t+1)], y[:(t+1)], label= "3 layers LSTM")
    plt.ylabel("F1")
    plt.xlabel("Epoch")
    plt.title(" Test F1 Score Per Epoch")
    plt.legend()
    plt.title(f'Relation Between F1 & Epoch',
              fontsize=14)
    plt.savefig(f'./img_{t}.png', 
                transparent = False,  
                facecolor = 'white'
               )
    plt.close()
# import imageio
for i in time:
    create_frame(i)
frames = []
for t in time:
    image = imageio.v2.imread(f'./img_{t}.png')
    frames.append(image)

imageio.mimsave('./LSTM.gif', # output gif
                frames,          # array of input frames
                fps = 5)         # optional: frames per second

"""
# Examine on sub-sets:"""

#Load Model
model = Model_3layers()
model.load_state_dict(torch.load('/content/model_3layers.pt'), strict=False)

# Get patients by age:

young_patients = df_test[df_test['Age'].isin([x for x in range(30,60)])]
young_male_patients = young_patients[young_patients['Gender']==1]['id'].unique()
young_female_patients = young_patients[young_patients['Gender']==0]['id'].unique()

old_patients = df_test[df_test['Age']>=60]
old_male_patients = old_patients[old_patients['Gender']==1]['id'].unique()
old_female_patients = old_patients[old_patients['Gender']==0]['id'].unique()

F1 = BinaryF1Score()

learning_rate = 1e-3

loss_fn = nn.BCELoss()
optimizer = optim.Adam(model.parameters(),lr=learning_rate)

if torch.cuda.is_available():
  model = model.cuda()
  F1 = F1.cuda()

def calc_f1(predictions, y_test):
    f1 = f1_score(y_test, predictions)
    print(f"F1 score: {round(f1, 3)}")
    return f1


def calc_precision(predictions, y_test):
    precision = precision_score(y_test, predictions)
    print(f"Precision score: {round(precision, 3)}")
    return precision


def calc_recall(predictions, y_test):
    recall = recall_score(y_test, predictions)
    print(f"Recall score: {round(recall, 3)}")
    return recall
from sklearn.metrics import f1_score, precision_score, recall_score

def eval_patients(patient_list, list_name):
  model.eval()
  test_predictions = []
  test_labels = []
  with torch.no_grad():
      test_results = []
      for i, patient in enumerate(patient_list):

        X, y_test = prepare_dataset_using_pandas(df_test, patient)
        if torch.cuda.is_available():
          X = X.cuda()
          y_test = y_test.cuda()

        y_pred = model(X)
        y_pred = y_pred.view(-1)
        test_predictions.append(round(y_pred[-1].cpu().item()))
        test_labels.append(y_test.cpu().item())
  print(f"Group {list_name}:")
  calc_f1(test_predictions, test_labels)
  calc_precision(test_predictions, test_labels)
  calc_recall(test_predictions, test_labels)

eval_patients(young_male_patients,"young_male_patients")

eval_patients(young_female_patients,"young_female_patients")

eval_patients(old_male_patients,"old_male_patients")

eval_patients(old_female_patients,"old_female_patients")

# Get patient by temp:
median_temp = df_test['Temp'].median()
map_median = df_test['MAP'].median()

#low temp:
low_temp = df_test[df_test['Temp']<median_temp]

low_temp_low_map = low_temp[low_temp["MAP"]<map_median]["id"].unique()
low_temp_high_map = low_temp[low_temp["MAP"]>=map_median]["id"].unique()

#high temp:
high_temp = df_test[df_test['Temp']>= median_temp]

high_temp_low_map = high_temp[high_temp["MAP"]<map_median]["id"].unique()
high_temp_high_map = high_temp[high_temp["MAP"]>=map_median]["id"].unique()

eval_patients(low_temp_low_map,"low_temp_low_map")
eval_patients(low_temp_high_map,"low_temp_high_map")
eval_patients(high_temp_low_map,"high_temp_low_map")
eval_patients(high_temp_high_map,"high_temp_high_map")