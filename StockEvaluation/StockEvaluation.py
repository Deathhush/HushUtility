import pandas
import os
import numpy as np
import pandas as pd

from pandas import Series, DataFrame
from StockDataFetcher import StockDataFetcher

def cross(data, val1, val2): 
    if (data[val1].values[1] > data[val1].values[0]  and data[val2].values[1]  > data[val2].values[0] 
       and data[val1].values[0]  < data[val2].values[0]  and data[val1].values[1]  >data[val2].values[1] ):        
        return 1
    elif (data[val1].values[0] > data[val1].values[1]  and data[val2].values[0]  > data[val2].values[1] 
            and data[val1].values[0] > data[val2].values[0] and data[val1].values[1] < data[val2].values[1]):        
        return -1
    else:        
        return 0

def cross_current_only(data, val1, val2): 
    if (data[val1].values[1] > data[val1].values[0]  
       and data[val1].values[0]  < data[val2].values[0]  and data[val1].values[1]  >data[val2].values[1] ):        
        return 1
    elif (data[val1].values[0] > data[val1].values[1]
            and data[val1].values[0] > data[val2].values[0] and data[val1].values[1] < data[val2].values[1]):        
        return -1
    else:        
        return 0
    
def window_apply(df, columnName, windowSize, func):
    result = []
    for i in range(windowSize-1):
        result.append(np.NaN)    
    for i in range(df.index.size-windowSize+1):
        result.append(func(df[i:i+windowSize]))      
    df[columnName] = result

def generate_daily_df(symbol, year='', file_path = 'D:\\Testland\\stock_data\\'):
    if (year != ''):
        year_part = '\\%s\\' % year        
    result_df = pandas.read_csv('%s%s%s.csv' % (file_path, year_part, symbol), header=None, names=[u'date', u'time', u'open', u'high', u'low', u'close', u'volume',u'amount'])    
    result_df = result_df.groupby('date').agg({'high':np.max, 'low':np.min, 'volume':np.sum, 'amount':np.sum, 'open':'first', 'close':'last'})        
    result_df['ma5']=pd.rolling_mean(result_df['close'] , 5)
    result_df['ma10']=pd.rolling_mean(result_df['close'] , 10)
    analyzed_path = '%s\\analyzed\\%s.%s.daily.analyzed.csv' % (file_path, symbol, year)
    result_df.to_csv(analyzed_path)
    result_df = pandas.read_csv(analyzed_path)      
    return result_df

def load_daily_df(symbol, year='', file_path = 'D:\\Testland\\stock_data\\'):
    if (year != ''):
        year_part = '\\%s\\' % year
    analyzed_path = '%s\\analyzed\\%s.%s.daily.analyzed.csv' % (file_path, symbol, year)
    if (os.path.isfile(analyzed_path)!=True):
        StockDataFetcher().fetch_daily_bar(symbol, year, file_path)
    result_df = pandas.read_csv('%s%sdaily.%s.csv' % (file_path, year_part, symbol))
    result_df['ma5']=pd.rolling_mean(result_df['close'] , 5)
    result_df['ma10']=pd.rolling_mean(result_df['close'] , 10)    
    result_df.to_csv(analyzed_path)
    result_df = pandas.read_csv(analyzed_path)      
    return result_df

class TradeCommand(object):
    def __init__(self, share, price, trade_type):
        self.share = share
        self.price = price
        self.trade_type = trade_type
        
class Account(object):
    def __init__(self, fund, share):
        self.fund = fund
        self.share = share
        self.average_price = 0.0
    
def evaluate_strategy(df, strategy, verbose=False):    
    print '[Start] Evaluating strategy=%s verbose=%s' % (strategy.__class__.__name__, verbose)
    account = Account(1000000,0)
    strategy.prepare(df, account)
    for i in range(df.index.size-1):
        command = strategy.evaluate(df[:i+1], i, account)
        if (command == None):            
            continue
        if (command.trade_type == 'buy'):
            buy_price = command.price
            if (buy_price == -1):
                buy_price = df['high'].values[i+1] * 100
            buy_share = command.share
            if (buy_share == -1):
                buy_share = np.floor(account.fund / buy_price)
            actual_buy_share = min(account.fund / buy_price, buy_share)
            total_share = actual_buy_share + account.share
            new_average_price = (account.share * account.average_price + actual_buy_share*buy_price) / total_share
            account.share = total_share
            account.fund = account.fund - actual_buy_share*buy_price
            account.average_price = new_average_price
            if (verbose):
                print("[%d,%s] Try to buy %d shares at price %f. %d shares bought" % (i, df['date'].values[i], buy_share, buy_price, actual_buy_share))
                print("[%d,%s] fund: %f share: %f value: %f" % (i, df['date'].values[i], account.fund, account.share, account.fund+account.share*df['close'].values[i]*100))
        elif (command.trade_type == 'sell'):
            sell_price = command.price
            if (sell_price == -1):
                sell_price = df['low'].values[i+1] *100            
            sell_share = command.share
            if (sell_share == -1):
                sell_share = account.share
            actual_sell_share = min(account.share, sell_share)          
            account.fund = account.fund + actual_sell_share*sell_price
            account.share = account.share - actual_sell_share
            if (verbose):
                print("[%d,%s] Try to sell %d shares at price %f. %d shares sold" % (i, df['date'].values[i], sell_share, sell_price, actual_sell_share))
                print("[%d,%s] fund: %f share: %f value: %f" % (i, df['date'].values[i], account.fund, account.share, account.fund+account.share*df['close'].values[i]*100))
            share = 0
    close_price = df['close'].values[df.index.size-1]*100
    print('[Result] fund: %f share: %f value: %f' % (account.fund, account.share, account.fund+account.share*close_price) )
    
def isUp(df, index, column_name, window=5):
    isUp = True
    if (index <= window):
        return False
    for i in range(window):
        if (np.isnan(df[column_name].values[index]) or np.isnan(df[column_name].values[index-i-1])):
            #print '  ', i, 'nan detected'
            isUp = False
        if (df[column_name].values[index] <= df[column_name].values[index-i-1]):
            isUp = False
            #print '  ', i, 'larger detected'
    return isUp

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

class CrossStrategy(object):
    def __init__(self):
        self.column_name = 'cross'
    def prepare(self, df, account):
        window_apply(df, self.column_name, 2, lambda x: cross(x, 'ma5', 'ma10')) 
    def evaluate(self, df, index, account):
        if (df[self.column_name].values[index] == 1 and account.fund > 0):
            return TradeCommand(-1, -1, 'buy')
        elif (df[self.column_name].values[index] == -1 and account.share > 0):
            return TradeCommand(-1, -1, 'sell')
        else:
            return None

class MacdCrossStrategy(object):
    def __init__(self):
        self.column_name = 'macd_cross'
    def prepare(self, df, account):
        MacdIndicator().populate(df)
        window_apply(df, self.column_name, 2, lambda x: cross(x, 'MACD_DIF', 'MACD_DEA')) 
    def evaluate(self, df, index, account):
        if (df[self.column_name].values[index] == 1 and account.fund > 0 and df['MACD_DIF'][index] < 0 and df['MACD_DEA'][index] < 0):
            return TradeCommand(-1, -1, 'buy')
        elif (df[self.column_name].values[index] == -1 and account.share > 0 and df['MACD_DIF'][index] > 0 and df['MACD_DEA'][index] > 0):
            return TradeCommand(-1, -1, 'sell')
        else:
            return None

class KdjCrossStrategy(object):
    def __init__(self):
        self.column_name = 'kdj_cross'
    def prepare(self, df, account):
        KdjIndicator().populate(df)
        window_apply(df, self.column_name, 2, lambda x: cross(x, 'KDJ_K', 'KDJ_D')) 
    def evaluate(self, df, index, account):
        if (df[self.column_name].values[index] == 1 ):
            return TradeCommand(-1, -1, 'buy')
        elif (df[self.column_name].values[index] == -1):
            return TradeCommand(-1, -1, 'sell')
        else:
            return None
     
class CrossCurrentOnlyStrategy(object):
    def __init__(self):
        self.column_name = 'cross_current_only'
    def prepare(self, df, account):        
        window_apply(df, self.column_name, 2, lambda x: cross_current_only(x, 'ma5', 'ma10')) 
    def evaluate(self, df, index, account): 
        if (df[self.column_name].values[index] == 1 and account.fund > 0):
            return TradeCommand(-1, -1, 'buy')
        elif (df[self.column_name].values[index] == -1):
            return TradeCommand(-1, -1, 'sell')
        else:
            return None
            
class SphinxStrategy(object):
    def __init__(self):
        self.window = 5
        self.sell_all_threshold = 0.95
        self.share_size = 10
        self.buy_threshold = 1
        self.sell_threshold = 1
    def prepare(self, df, account):
        buy_price = df['high'].values[0]*100
        self.buy_share = account.fund / buy_price / self.share_size        
    def evaluate(self, df, index, account):
        if (index % self.window == 0):
            if (account.share == 0):                
                if (isUp(df, index, 'ma10')):
                    buy_price = df['high'].values[index]*100                    
                    return TradeCommand(share=self.buy_share, price=-1, trade_type='buy')
            if (account.share > 0 and index > self.window):                
                if (df['close'].values[index] > df['close'].values[index-self.window] * self.buy_threshold):
                    return TradeCommand(share=self.buy_share, price=-1, trade_type='buy')
                if (df['close'].values[index] < df['close'].values[index-self.window] * self.sell_threshold):
                    return TradeCommand(share=self.buy_share, price=-1, trade_type='sell')                    
                if (df['close'].values[index] / df['close'].values[index-self.window] < self.sell_all_threshold):
                    return TradeCommand(-1, -1, trade_type='sell')
            if (account.share > 0 and index > 2*self.window):
                if (df['close'].values[index] < df['close'].values[index-self.window] * self.sell_threshold and df['close'].values[index] < df['close'].values[index-2*self.window] * self.sell_threshold):
                    return TradeCommand(-1, -1, trade_type='sell')
            if (account.share > 0 and account.average_price > df['close'][index]):
                return TradeCommand(-1, -1, trade_type='sell') 
        return None

class CombinedStrategy(object):
    def __init__(self):
        self.macd = MacdCrossStrategy()
        self.sphinx = SphinxStrategy()
        self.cross = CrossStrategy()
    def prepare(self, df, account):
        self.macd.prepare(df, account)
        self.sphinx.prepare(df, account)
        self.cross.prepare(df, account)
    def evaluate(self, df, index, account):
        crossResult = self.cross.evaluate(df, index, account)
        sphinxResult = self.sphinx.evaluate(df, index, account)
        if (sphinxResult != None and sphinxResult.trade_type == 'sell'):
            return sphinxResult
        #elif (macdResult != None and sphinxResult.trade_type == 'sell'):
        #    return macdResult
        elif (crossResult != None and crossResult.trade_type == 'buy'):
            return crossResult
        elif (sphinxResult != None and sphinxResult.trade_type == 'buy'):
            return sphinxResult
        return None