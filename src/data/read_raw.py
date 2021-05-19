import pandas as pd
import os
from pathlib import Path

full_path = Path(__file__).parent.absolute()
directory = f'{Path(full_path).parent}/data/raw'
print(full_path)
print(directory)

def read_raw(file : str):
    
    path = ''
    
    for filename in os.listdir(directory):
        
        if filename.endswith('.csv') and filename.find(file) > 0:
            
            path = f'{directory}/{filename}'
            
    try:
        return pd.read_csv(path, sep = ';', encoding='latin-1')
    except:
        print(path)
        raise FileNotFoundError
        
