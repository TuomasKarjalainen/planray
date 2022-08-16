import pandas as pd
import requests
import os
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from os import getenv

"""Author: tuomas karjalainen"""

def fetch_data(circuits,start,end,forward):
    """
    from modules.fetch_data import *
    
    A function for data acquisition from REST-API. 
    At the moment, the function is designed and implemented for fetching Forchem's data.
    At first there have to define the URL path for REST and datanodes of which you want data.
    
    The function creater folders for every circuit and pushes csv files into them.
    The function also converts timestamps to right format.
    
    Parameters
    ----------
    circuits = dict, datanodes to extract
    start = INT, start time in microseconds
    end = INT, end time in microseconds
    forward = INT, interval for fetching data for example if you want data from every day, then you have to define one day in microseconds
    batch = INT, count of the batches

    Returns
    -------
    Nothing
    
    """
    usr = getenv("username")
    pwd = getenv("password")
    rounds_total= 1
    start_init = start
    end_init = end
    for k, l in circuits.items():
        start = start_init
        end = end_init
        for day in range(1,20+1):
            L1 = requests.get(f"https://iotflex.caverion.net/rest/v1/datanodes/{l[0]}/processdata?begin={start}&end={end}",
                            auth=HTTPBasicAuth(f"{usr}", f"{pwd}"))

            TC = requests.get(f"https://iotflex.caverion.net/rest/v1/datanodes/{l[1]}/processdata?begin={start}&end={end}",
                            auth=HTTPBasicAuth(f"{usr}", f"{pwd}"))

            TH = requests.get(f"https://iotflex.caverion.net/rest/v1/datanodes/{l[2]}/processdata?begin={start}&end={end}",
                            auth=HTTPBasicAuth(f"{usr}", f"{pwd}"))

            TL = requests.get(f"https://iotflex.caverion.net/rest/v1/datanodes/{l[3]}/processdata?begin={start}&end={end}",
                            auth=HTTPBasicAuth(f"{usr}", f"{pwd}"))

            VSP = requests.get(f"https://iotflex.caverion.net/rest/v1/datanodes/{l[4]}/processdata?begin={start}&end={end}",
                            auth=HTTPBasicAuth(f"{usr}", f"{pwd}"))
            
            CL = requests.get(f"https://iotflex.caverion.net/rest/v1/datanodes/{l[5]}/processdata?begin={start}&end={end}",
                            auth=HTTPBasicAuth(f"{usr}", f"{pwd}"))
            
            CR = requests.get(f"https://iotflex.caverion.net/rest/v1/datanodes/{l[6]}/processdata?begin={start}&end={end}",
                            auth=HTTPBasicAuth(f"{usr}", f"{pwd}"))
            
            PP = requests.get(f"https://iotflex.caverion.net/rest/v1/datanodes/{l[7]}/processdata?begin={start}&end={end}",
                            auth=HTTPBasicAuth(f"{usr}", f"{pwd}"))
            
            PWM = requests.get(f"https://iotflex.caverion.net/rest/v1/datanodes/{l[8]}/processdata?begin={start}&end={end}",
                            auth=HTTPBasicAuth(f"{usr}", f"{pwd}"))
            
            
            start = start + forward
            end = end + forward       
            
            L1_df = pd.DataFrame(L1.json()['items'])
            L1_df.rename(columns={"ts" : "timestamp",
                                  "v" : "L1"}, inplace=True, errors='raise')

            TC_df = pd.DataFrame(TC.json()['items'])
            TC_df.rename(columns={"v" : "TC"}, inplace=True, errors='raise')

            TH_df = pd.DataFrame(TH.json()['items'])
            TH_df.rename(columns={"v" : "TH"}, inplace=True, errors='raise')

            TL_df = pd.DataFrame(TL.json()['items'])
            TL_df.rename(columns={"v" : "TL"}, inplace=True, errors='raise')

            VSP_df = pd.DataFrame(VSP.json()['items'])
            VSP_df.rename(columns={"v" : "Valid_SetPoint"}, inplace=True, errors='raise')

            CL_df = pd.DataFrame(CL.json()['items'])
            CL_df.rename(columns={"v" : "Cable_length"}, inplace=True, errors='raise')
            
            CR_df = pd.DataFrame(CR.json()['items'])
            CR_df.rename(columns={"v" : "Cable_resistance"}, inplace=True, errors='raise')
            
            PP_df = pd.DataFrame(PP.json()['items'])
            PP_df.rename(columns={"v" : "Power_percentage"}, inplace=True, errors='raise')
            
            PWM_df = pd.DataFrame(PWM.json()['items'])
            PWM_df.rename(columns={"v" : "Power_W/m"}, inplace=True, errors='raise')
            
            
            df = pd.concat([L1_df,TC_df,TH_df,TL_df,VSP_df, CL_df, CR_df, PP_df, PWM_df] ,axis=1)        
            df = df.loc[:,~df.columns.str.startswith('type')]
            df = df.loc[:,~df.columns.str.startswith('ts')]

            FIN = tz.gettz('Europe/Helsinki')  
            epoch = datetime(1970, 1, 1, tzinfo=FIN)

            for i,e in enumerate(df.timestamp):
                FIN = tz.gettz('Europe/Helsinki')  
                cookie_microseconds_since_epoch = e
                try:
                    cookie_datetime = epoch + timedelta(microseconds=cookie_microseconds_since_epoch)
                except ValueError:
                    print(k,l,day,rounds_total)
                    pass
                df.loc[i,'timestamp'] = cookie_datetime

            os.makedirs(f'./Uudet_piirit/{k}', exist_ok = True) 
            df.to_csv(f'./Uudet_piirit/{k}/{k}_{day}.csv', index=False)
            print(f"In progress: {k} - {day}/{20} \t -  {round(((rounds_total/(len(circuits)*20))*100),2)}% ",end="\r")
            rounds_total += 1