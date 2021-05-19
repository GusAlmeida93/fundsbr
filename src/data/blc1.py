import pandas as pd
import os
from read_raw import read_raw

directory = '../data/raw'

columns = {
    'CD_ISIN' : 'ID',
    'TP_TITPUB' : 'DESC'
}

df = read_raw('BLC_1')

print(df.head())
