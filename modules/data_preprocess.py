from timeit import default_timer as timer
import pandas as pd
import numpy as np
import glob
import os 

"""
Author: tuomas karjalainen
"""


def remove_outliers(df):
    """
    -----------------------
    VERSION: 2022-04-22
    -----------------------
    
    Function for removing outlier spikes from L1 and TC data.
    
    Parameters
    ----------
    df = STRING, CSV file path.
    
    Returns
    ----------
    Input dataframe without outliers.
    
    
    """
    
    Q1 = df.quantile(0.03)
    Q3 = df.quantile(0.97)
    IQR = Q3 - Q1
    alaraja = Q1 - 0.4 * IQR
    ylaraja = Q3 + 0.4 * IQR
    label = 'L1'
    df = df.loc[(df[label] >= alaraja[label]) & (df[label] <= ylaraja[label])]
    label = 'TC'
    df = df.loc[(df[label] >= alaraja[label]) & (df[label] <= ylaraja[label])]
    df = df.reset_index()
    return df



def fetch_hours(main_path='../Datat/*',
                name_folder='tunti_data',
                create_folder=True,
                clean_data=True,
                print_progress=True,
                csv_limiter=True):
    """
    -----------------------
    VERSION: 2022-05-05
    -----------------------
    
    A function that searches hourly periods when the trace heating circuit has been active. 
    The function also creates a folder for the found periods and moves them there in CSV format at the user's request. 
    
    
    USE EXAMPLE
    ------------
    NOTE: Check module import in your case
    
    from Moduulit.data_preprocess import *

    dataframes = fetch_hours(main_path='./Datat/*',
                             name_folder='tunti_data',
                             create_folder=True,
                             clean_data=True,
                             print_progress=True,
                             csv_limiter=True)
    
    
    Parameters
    ----------
    main_path = STRING, The path to the folder containing data about circuits. DEFAULT is the same as in GitLab repo.
    name_folder = STRING, The name of the folder that function creates.
    create_folder = BOOLEAN, If True (DEFAULT) the function creates folder for found files.
    clean_data = BOOLEAN, IF True (DEFAULT) the function removes outlier spikes from data. Intended for the original 10 hour data.
    print_progress = BOOLEAN, If True (DEFAULT) the function prints its process during execution.
    csv_limiter = BOOLEAN, - If True, (DEFAULT), function tends to find ~20 files for each circuit.
                           - If False, the function does not limit the creation of CSV files. Function creates as many valid CSV files as possible.
                            
    
    
    Returns
    ----------
    List of found valid dataframes.
    
    """
    start = timer()  
    if print_progress==True: print("Processing dataframes...\n")
    all_circuits = glob.glob(main_path)
    if len(all_circuits) == 0:
        print("\n------------------------")
        print("YOUR PATH IS EMPTY\n")
        print("Define correct datapath")
        print("------------------------\n")
    dataframes = []
    totalframes=[]
    
    # Looping all circuit folders
    for circuit in all_circuits:
        batch = 0
        L1_keskiarvot = []
        all_csv = glob.glob(f'{circuit}/*.csv')
        
        # Looping all CSV files in the going on circuit folder
        for i,csv in enumerate(all_csv):   
            
            # Creating folder for new CSV files
            if create_folder==True: 
                make_dir = (f"./{name_folder}/{csv.split('/')[-2]}/")
                os.makedirs(f"{make_dir}/", exist_ok = True)
                
            df = pd.read_csv(csv)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            L1_keskiarvot.append(df.L1.mean()) 
            limit = np.median(L1_keskiarvot)
            
            # Removing outliers (spikes) from TC and L1 values
            if clean_data==True:
                print("Removing spikes...",end="\r")
                df = remove_outliers(df)
                
            # Looping dataframe's unique hour values
            for z,j in enumerate(df.timestamp.dt.hour.unique().tolist()):
                
                # Defining the condition for one hour time frame
                condition = (df.timestamp >= df.timestamp[0] + pd.DateOffset(hours=z)) & (df.timestamp < (df.timestamp[0] + pd.DateOffset(hours=z) + pd.DateOffset(hours=1)))                 
                hour = df.loc[condition]
                
                x1 = 0
                zeros = []
                
                # Listing lengths of consecutive zeros
                for value in hour.L1:
                    if value != 0:
                        zeros.append(x1)
                        x1 = 0
                    x1 += 1
                zeros.append(x1)
                max_zeros = np.max(zeros)
                
                # Checking if there's too many zeros in a row in the time frame
                if max_zeros < 100:
                    
                    # Checking if power is on (average greater than 1) and length of the frame is enough
                    if hour.L1.mean() > 1 and len(hour) > 200:
                        try:
                            if len(dataframes) > z:
                                if limit <= hour.L1.mean():
                                    batch += 1
                                    dataframes.append(hour)
                                    if create_folder==True: hour.to_csv(f"{make_dir}/{csv.split('/')[-2]}_{batch}.csv",index=False)
                            else:
                                batch += 1
                                dataframes.append(hour)
                                if create_folder==True: hour.to_csv(f"{make_dir}/{csv.split('/')[-2]}_{batch}.csv",index=False)

                        except Exception as e:
                            print(f"ERROR : {e}") 
                        
            # CSV file limiter
            if csv_limiter==True:
                if batch > 20:
                    break

    if print_progress==True and create_folder==True:
        hour_files = glob.glob(f'./{name_folder}/*')
        if clean_data==True: print("\n")
        for file in hour_files:
            print(f"{file.split('/')[-1]}: {len(os.listdir(file))}")
            totalframes.append(len(os.listdir(file)))
            
    if print_progress==True: 
        end = timer()
        print(f"\nDataframes in total: {sum(totalframes)}\n-------------------------\n")
        print("Done in", round(end-start,2),"seconds\n")
    
    return dataframes