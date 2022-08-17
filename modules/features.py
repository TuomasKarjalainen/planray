import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import statistics

# import ssh-connector for pushing data to database!
from modules import ssh_connector 

"""Author: tuomas karjalainen"""

def L1_times(csv):
    """
    -----------------------
    VERSION: 2022-05-11
    -----------------------
    This function is used in features.py function.
    
    The function determines the average times, how long the power is on and how long it is off.
    
    The function also determines the amount of L1 variation during time period.
    
    
    Parameters
    ----------
    csv = STRING, CSV file
    
    Returns
    ----------
    Average on/off times and variation
    
    """
    df = pd.read_csv(csv)
    df["value_difference_L1"] = df["L1"].diff()  
    

    variation = 0

    for value in df.value_difference_L1:
        if value != 0:
            variation += 1


    return variation


def tunnusluvut(main_path = '../Uudet_tunnit2/', to_csv=True, push_to_database=False, table_name=None):
    """
    -----------------------
    VERSION: 2022-05-12
    -----------------------
    
    The function which creates statistical indicators from given data. Returned feature matrix is used for Neural Networks.
    The function needs L1_times named function for determine some features.
    
    EXAMPLE USE FOR DATABASE POPULATION
    -------------------------------------
    tunnusluvut(main_path = "./big_hours/",
                to_csv=False,
                push_to_database=True,
                table_name="OK")    
    
    EXAMPLE USE FOR DATAFRAME
    --------------------------------------
    features =  tunnusluvut(main_path = "./big_hours/",
                to_csv=False,
                push_to_database=False,
                table_name="OK")
            
            
    Parameters
    ------------
    main_path = STRING, The path for CSV folder.
    to_csv = BOOLEAN, If True (DEFAULT), the function also returns the dataframe in CSV format. 
    push_to_database = BOOLEAN, If True, the function call's ssh_connector for pushing dataframe into blade's MariaDB.
    table_name = STRING, Name of the database table.
    
    Returns
    ------------
    Statistical indicators (features) in pandas dataframe -format.
    
    """

    if push_to_database==True:     
        query1 = f'''CREATE TABLE IF NOT EXISTS {table_name} (Name VARCHAR(255) UNIQUE, Mean_L1 FLOAT, Std_L1 FLOAT, Vaihtelu_L1 FLOAT, Max_L1 FLOAT, Mean_TL FLOAT, Std_TL FLOAT, Vaihtelu_TL FLOAT, Min_TL FLOAT, Max_TL FLOAT, Median_TL FLOAT, Mean_TC FLOAT, Std_TC FLOAT, Vaihtelu_TC FLOAT, Min_TC FLOAT, Max_TC FLOAT, Median_TC FLOAT, Mean_TH FLOAT, Std_TH FLOAT, Vaihtelu_TH FLOAT, Max_TH FLOAT, Median_TH FLOAT, Valid_SetPoint FLOAT, Mean_TC_vs_Valid_SetPoint FLOAT, kW FLOAT, virta_prosentit_maksimista FLOAT, Variation FLOAT);'''
        
        
    all_csv = glob.glob(f"{main_path}*/*.csv")
    lukuja = pd.DataFrame()
    print("Creating feature matrix...\n")
    for i,csv in enumerate(all_csv):
        df = pd.read_csv(csv)
        df_count = len(df['L1'].dropna())
        
        df_mean_L1 = df['L1'].mean()
        df_std_L1 = df['L1'].std()
        df_IQR_L1 = df['L1'].quantile(0.97)-df['L1'].quantile(0.03)
        df_min_L1 = min(df['L1'])
        df_max_L1 = max(df['L1'])
        df_median_L1 = statistics.median(df['L1'])
        
        percent_L1 = df_mean_L1/df['L1'].quantile(0.97)
        
        df_mean_TL = df['TL'].mean()
        df_std_TL = df['TL'].std()
        df_IQR_TL = df['TL'].quantile(0.97)-df['TL'].quantile(0.03)
        df_min_TL = min(df['TL'])
        df_max_TL = max(df['TL'])
        df_median_TL = statistics.median(df['TL'])
        
        df_mean_TC = df['TC'].mean()
        df_std_TC = df['TC'].std()
        df_IQR_TC = df['TC'].quantile(0.97)-df['TC'].quantile(0.03)
        df_min_TC = min(df['TC'])
        df_max_TC = max(df['TC'])
        df_median_TC = statistics.median(df['TC'])
        
        df_mean_TH = df['TH'].mean()
        df_std_TH = df['TH'].std()
        df_IQR_TH = df['TH'].quantile(0.97)-df['TH'].quantile(0.03)
        df_min_TH = min(df['TH'])
        df_max_TH = max(df['TH'])
        df_median_TH = statistics.median(df['TH'])
        
        Valid = df['Valid_SetPoint'].mean()            
        
        T = df_mean_TC-df['Valid_SetPoint'].mean()
        
        variation = L1_times(csv)
        
        P = (230 * df_mean_L1) / 1000
        
        # Commented features were original  
        data = {'Name': csv.split("/")[-1],
#                'Count': df_count,
                'Mean_L1': df_mean_L1,
                'Std_L1': df_std_L1,
                'Vaihtelu_L1': df_IQR_L1,
#                'Min_L1': df_min_L1,
                'Max_L1': df_max_L1,
#                'Median_L1': df_median_L1,
                'Mean_TL': df_mean_TL,
                'Std_TL': df_std_TL,
                'Vaihtelu_TL': df_IQR_TL,
                'Min_TL': df_min_TL,
                'Max_TL': df_max_TL,
                'Median_TL': df_median_TL,
                'Mean_TC': df_mean_TC,
                'Std_TC': df_std_TC,
                'Vaihtelu_TC': df_IQR_TC,
                'Min_TC': df_min_TC,
                'Max_TC': df_max_TC,
                'Median_TC': df_median_TC,
                'Mean_TH': df_mean_TH,
                'Std_TH': df_std_TH,
                'Vaihtelu_TH': df_IQR_TH,
#                'Min_TH': df_min_TH,
                'Max_TH': df_max_TH,
                'Median_TH': df_median_TH,
                'Valid_SetPoint':Valid,
                'Mean_TC-Valid_SetPoint':T,
#                 'OnTime_Avg': avg_on_time,
#                 'OffTime_Avg': avg_off_time,
                'kW':P,
                'virta_prosentit_maksimista':percent_L1,
                'Variation':variation}
        
        lukuja = lukuja.append(data, ignore_index=True)
    print("Done!")        
    if to_csv==True: lukuja.to_csv(f"{main_path.split('/')[1]}.csv",index=False)
    

    if push_to_database==True:    
        lukuja.rename(columns={"Mean_TC-Valid_SetPoint": "Mean_TC_vs_Valid_SetPoint"}, inplace=True, errors='raise') 
        ssh_connector.Connect(query1,lukuja,table_name)
    else:
        return lukuja
