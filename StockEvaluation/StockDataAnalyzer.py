import time
import csv
import ConfigParser
import os
import numpy as np
import pandas as pd

from datetime import date, datetime, timedelta
from StockDataFetcher import StockDataFetcher

class StockDataAnalyzer(object):
    def __init__(self, workingDir='D:\\Testland\\stock_data'):
        self.workingDir = workingDir
        self.fetcher = StockDataFetcher(workingDir)
        
    def analyze(self, df, analyzedPath):        
        df['ma5']=pd.rolling_mean(df['close'] , 5)
        df['ma10']=pd.rolling_mean(df['close'] , 10)    
        df['ma20']=pd.rolling_mean(df['close'] , 20)
        df['ma30']=pd.rolling_mean(df['close'] , 30)
        MacdIndicator().populate(df)
        KdjIndicator().populate(df)        
        return df         
    
    def load_daily_df_by_year(self, symbol, start_year=2015, end_year=None):
        if end_year == None:
            end_year = start_year
        df = self.fetcher.load_daily_df_by_year(symbol, start_year)
        start = datetime(int(start_year), 1, 1).strftime('%Y/%m/%d')
        end = datetime(int(end_year), 12, 31).strftime('%Y/%m/%d')

        return self.load_daily_df(symbol, start, end)

    def load_daily_df(self, symbol, start, end):
        start_date = datetime.strptime(start, '%Y/%m/%d')
        end_date = datetime.strptime(end, '%Y/%m/%d')
        prefetch_date = start_date - timedelta(days=45)
        df = self.fetcher.load_daily_df(symbol, prefetch_date.strftime('%Y/%m/%d'), end)        

        analyzedFileName = '%s.%s.to.%s.analyzed.csv' % (symbol, start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d'))
        analyzedPath = os.path.join(self.workingDir, 'analyzed', analyzedFileName)        
        df = self.analyze(df, analyzedPath)

        df = df[df['date'] >=start]
        resultDf = remove_index(df, analyzedPath)
        return resultDf

class KdjIndicator(object):
    def __init__(self, windowSize=9):
        self.windowSize = 9
    def populate(self, df):
        result_rsv = []
        result_k = []
        result_d = []
        result_j = []
        for i in range(self.windowSize-1):
            result_rsv.append(np.NaN) 
            result_k.append(50)
            result_d.append(50)
            result_j.append(50)
        for i in range(df.index.size-self.windowSize+1):
            current_index = i+self.windowSize-1
            current_rsv = self.calculate_rsv(df, current_index)
            result_rsv.append(current_rsv)
            last_k = result_k[current_index-1]
            last_d = result_d[current_index-1]
            current_k = last_k*2/3 + current_rsv/3
            result_k.append(current_k)
            current_d = last_d*2/3 + current_k/3
            result_d.append(current_d)
            current_j = 3*current_k - 2*current_d
            result_j.append(current_j)            
        df['KDJ_rsv'] = result_rsv
        df['KDJ_K'] = result_k
        df['KDJ_D'] = result_d
        df['KDJ_J'] = result_j
        return
    def calculate_rsv(self, df, index):
        current_min_low = df['low'].values[index]
        for i in range(1, self.windowSize):
            current_min_low = min(current_min_low, df['low'].values[index-i])
        current_max_high = df['high'].values[index]
        for i in range(1, self.windowSize):
            current_max_high = max(current_max_high, df['high'].values[index-i])
        current_close = df['close'].values[index]
        #print 'current_close', current_close
        #print 'max', current_max_high
        #print 'min', current_min_low
        return (current_close - current_min_low) / (current_max_high - current_min_low) * 100

class MacdIndicator(object):
    def __init__(self):
        self.fast = 12        
        self.slow = 26        
        self.average = 9
    def populate(self, df):  
        ema_fast = self.calculate_ema(df, 'close', self.fast)        
        df['MACD_EMA_FAST'] = ema_fast
        ema_slow = self.calculate_ema(df, 'close', self.slow)
        df['MACD_EMA_SLOW'] = ema_slow
        dif = [np.NaN for i in range(self.slow-1)]        
        dif = dif + [ema_fast[i + self.slow-1] - ema_slow[i + self.slow-1] for i in range(df.index.size-self.slow+1)]        
        df['MACD_DIF'] = dif
        dea = [np.NaN for i in range(self.slow-1)]        
        dea = dea + self.calculate_ema(df[self.slow-1:], 'MACD_DIF', self.average, self.slow-1)        
        df['MACD_DEA'] = dea        
    def calculate_ema(self, df, columnName, windowSize, base=0):        
        factor = 2.0/(windowSize+1)        
        ema = [np.NaN for i in range(windowSize-1)]        
        ema.append(df[base:windowSize+base][columnName].mean())                
        total_count = df.index.size        
        for i in range (total_count-windowSize):
            current_index = i + windowSize 
            current_adjusted_index = current_index + base           
            ema.append(factor*df[columnName][current_adjusted_index] + (1.0-factor)*ema[current_index-1])        
        return ema

def remove_index(df, path):
    df.to_csv(path, index=False)
    df = pd.read_csv(path)
    return df