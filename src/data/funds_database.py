import pandas as pd
import os
from pathlib import Path

class FundsDataBase:
    
    full_path = Path(__file__).parent.absolute()
    directory = f'{Path(full_path).parent}/data/raw'
    
    def read_raw(self, file : str, directory : str) -> pd.DataFrame: 
        
        path = ''
    
        for filename in os.listdir(directory):
            
            if filename.endswith('.csv') and filename.find(file) > 0:
                
                path = f'{directory}/{filename}'
                
        try:
            return pd.read_csv(path, sep = ';', encoding='latin-1')
        except:
            print(path)
            raise FileNotFoundError
        
    def blc1(self):
        
        default_columns = {
            'CD_ISIN' : 'CD_ATIVO',
            'TP_TITPUB' : 'DESC_ATIVO'
        }
        
        df = self.read_raw('BLC_1', self.directory)
        df = df.rename(columns=default_columns)
    
    