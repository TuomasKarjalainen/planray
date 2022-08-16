import glob
import matplotlib.pyplot as plt
import pandas as pd

"""Author: tuomas karjalainen"""

def plot_circuits(circuit,main_path = '../Datat/', value='L1'):
    """
    -------------------
    VERSION: 2022-04-01
    -------------------
    
    A function for plotting all the CSV files of the circuit.
    
    Parameters
    -----------
    circuit: STRING, The circuit that you want to visualize.
    main_path: STRING, The path for the circuits. DEFAULT is the same as in GitLab repo.
    value: STRING, 
    
    Returns
    --------
    Nothing
    
    """
       
    all_csv = glob.glob(f"{main_path}{circuit}/*.csv")

    plt.figure(figsize=(20,40))
    try:
        for i,csv in enumerate(all_csv):
            df = pd.read_csv(csv)  
            plt.subplot(10,3, i+1)
            plt.plot(df[value], label=value)
            plt.legend(loc="upper right")
            plt.title(csv)
        plt.show()
    except:
        pass