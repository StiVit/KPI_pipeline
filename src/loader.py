import pandas as pd
import os

def get_path():
    data_dir = "../data"
    if os.path.exists(data_dir):
        for file in os.listdir(data_dir):
            if file.endswith(('.xlsx', '.xls')):
                return os.path.join(data_dir, file)
    raise FileNotFoundError("No Excel file found in the data folder")
        

def load_data(path, sheet_name = None, header = 0):
    return pd.read_excel(path, sheet_name=sheet_name, header=header)