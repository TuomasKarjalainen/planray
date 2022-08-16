import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# from scipy.signal import find_peaks

"""Author: tuomas karjalainen"""

def L1_times(csv):
    """
    -----------------------
    VERSION: 2022-04-20
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
    
    indexit_listaan = []
    new_df = pd.DataFrame()
    on_times = []
    off_times = []
    variation = 0
    x = df.L1
#     peaks, _ = find_peaks(x, height=0)
#     spikes = len(peaks)

    # Kuinka paljon virrassa tapahtuu muutoksia
    for value in df.value_difference_L1:
        if value != 0:
            variation += 1

    for index, row in enumerate(df.itertuples()):
        if (abs(row.value_difference_L1) / df.value_difference_L1.max()) > 0.5:
            indexit_listaan.append(index)

    for i in indexit_listaan:
        new_df = new_df.append(df.loc[[i]])

    new_df['timestamp'] = pd.to_datetime(new_df['timestamp'])
    new_df['time_diff'] = new_df.timestamp.diff()
    new_df['time_diff'] = new_df['time_diff'] / np.timedelta64(1,'s')

    for index, row in enumerate(new_df.itertuples()):  
        if (row.value_difference_L1 < 0) & (np.isnan(row.time_diff)==False):
            on_times.append(row.time_diff)

        if (row.value_difference_L1 > 0) & (np.isnan(row.time_diff)==False):
            off_times.append(row.time_diff)

    on_time_avg = np.mean(on_times)
    off_time_avg = np.mean(off_times)
    
    return on_time_avg, off_time_avg, variation