import pandas as pd

def blc1(self):
        
        default_columns = {
            'CD_ISIN' : 'CD_ATIVO',
            'TP_TITPUB' : 'DESC_ATIVO'
        }
        
        df = self.read_raw('BLC_1', self.directory)
        df = df.rename(columns=default_columns)
        