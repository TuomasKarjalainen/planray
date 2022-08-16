import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import date
from pickle import load

import tensorflow as tf 
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
config = tf.compat.v1.ConfigProto()
config.gpu_options.allow_growth = True
session = tf.compat.v1.Session(config=config)
from sklearn.model_selection import train_test_split

from Moduulit.data_preprocess import *
from Moduulit.features import tunnusluvut

"""Author: tuomas karjalainen"""

"""
-----------------------
VERSION: 2022-05-11
-----------------------
"""


def define_model(path,model_name,show_model):
    '''Load pretrained model
    ------------------------------------
    
    Parameters
    ----------
    model : STRING, model's filename i.e. "ADAMModel.h5"  
    path : STRING, path where's saved model can be found
    
    Returns
    ----------
    keras.engine.sequential.Sequential model
    '''   
    loaded_model = tf.keras.models.load_model(path+model_name)       
    if show_model==True: loaded_model.summary()    
    return loaded_model

def define_scaler(path,pickled_scaler):
    '''Load saved data scaler
    -----------------------------------
    
    Parameters
    ----------
    model : STRING, picke file's name"  
    path : STRING, path where's saved pickle file can be found
    
    Returns
    ----------
    sklearn.preprocessing._data.Scaler
    '''
    scaler = load(open(pickled_scaler, 'rb'))
    return scaler

def results(pred,test_targets,test_mse_score,test_mae_score,visualize_results,save_results,csv_path,data): 
    '''Neural Network's accuracy '''
    
    targets=[]
    for target in test_targets:
        targets.append(target) 
      
    difference = np.array(np.array(test_targets) - np.array(pred))
    multiplied_array = pred + difference.mean()
    
    if test_mae_score >= 0.19:
        print("\n------------------------------")
        print(f"Piirissä häikkää\nMean absolute error: {test_mae_score}")
        print("------------------------------\n")
        
    if visualize_results==True:
        visualize(pred,targets,difference,multiplied_array,save_results,csv_path,data)
        
    return difference

def results_to_csv(stats,test_mse_score,test_mae_score,model_name,pickled_scaler,csv_path,data,show_results):
    '''Saving results
    -------------------------------------
    Creates directory for the results.
    Saves results in CSV-format.
    Moves the result file to the directory.
    '''
    
    os.makedirs(f"{csv_path}/", exist_ok=True)
    model_name = model_name.split('/')[-1]   
         
    model_stats = {'model' : model_name,
                   'pickled_scaler' : pickled_scaler,
                   'test_data' : data.split('./')[-1],
                   'test_mse_score' : test_mse_score,
                   'test_mae_score' : test_mae_score}
    
    today = str(date.today()).replace('-','')
    df = pd.DataFrame.from_dict(model_stats, orient='index')
    df.rename(columns={0: "Model Info"}, inplace=True, errors='raise')
    df.to_csv(csv_path+f"/{today}_{data.split('./')[-1].replace('/','-')}_stats.csv")
    if show_results==True:
        try:
            print(f"\n{df.to_markdown()}\n") 
        except:
            display(df)
    
    
def visualize(pred,targets,difference,multiplied_array,save_results,csv_path,data):
    '''Visualization of results'''
    print()
    plt.figure(figsize=(12,8))
    sns.set(style="darkgrid")
    plt.plot(targets,label="Targets")
    plt.title("Predictions vs. real values")
    plt.plot(pred, label="Predictions")
    if save_results==True:
        imdir = f"{csv_path}/images/{data.split('./')[-1].replace('/','-')}/"
        os.makedirs(f"{csv_path}/images/{data.split('./')[-1].replace('/','-')}", exist_ok=True)
        plt.savefig(imdir+f"{data.split('./')[-1].replace('/','-')}_1.png")
    plt.legend()

    plt.figure(figsize=(12,8))
    sns.set(style="darkgrid")
    plt.plot(targets,label="Targets")
    plt.plot(multiplied_array, label="Predictions")
    plt.title("Predictions + abs vs. real values")
    if save_results==True:
        plt.savefig(imdir+f"{data.split('./')[-1].replace('/','-')}_2.png")
    plt.legend()
    plt.show()    
    
def NN_main(path,model_name,data,pickled_scaler,csv_path,print_data,show_results,show_model,visualize_results,save_results):
    '''The Main Function
    
    - Defines the data
    - Process it for the neural network model
    - Uses defined NN and defines the accuracy
    '''
    features = tunnusluvut(main_path=data, to_csv=False)
    
    if print_data==True:display(features.head(10))
    
    train_data, test_data, train_targets, test_targets = train_test_split(features.drop(["Name",
                                                                                         "kW",
                                                                                         "Max_L1",
                                                                                         "Min_TL",
                                                                                         "Max_TL",
                                                                                         "Min_TC",
                                                                                         "Max_TC",
                                                                                         "Max_TH",
                                                                                         "Max_L1",
                                                                                         "Valid_SetPoint",
                                                                                         "Mean_TC-Valid_SetPoint",
                                                                                         "Variation"],
                                                                                         axis=1), features["kW"], test_size=0.85, random_state=42)
    scaler = define_scaler(path,pickled_scaler)
    model = define_model(path,model_name,show_model)
    transformed_test_data = scaler.transform(test_data)  
    pred = model.predict(transformed_test_data)
    test_mse_score, test_mae_score = model.evaluate(transformed_test_data, test_targets)
    
    stats = results(pred,test_targets,test_mse_score,test_mae_score,visualize_results,save_results,csv_path,data)
    
    if save_results==True:
        results_to_csv(stats,test_mse_score,test_mae_score,model_name,pickled_scaler,csv_path,data,show_results)
