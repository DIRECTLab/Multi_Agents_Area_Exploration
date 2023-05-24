import os
import pandas as pd

# 

def merg_two_csv(path1,path2):
    return pd.concat([pd.read_csv(path1),
                      pd.read_csv(path2)],ignore_index=True)

if __name__ == "__main__":
    path1 = "/home/direct-lab/Documents/christopher/Multi_Agents_Area_Exploration/data_save/Agent_run_only(5/22/23)/all_data.csv"
    path2 = "/home/direct-lab/Documents/christopher/Multi_Agents_Area_Exploration/data_copy/MT_all_data.csv"

    df = merg_two_csv(path1,path2)
    df.to_csv("data_copy/all_data.csv")