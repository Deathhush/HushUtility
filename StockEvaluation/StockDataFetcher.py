from gmsdk import md
from datetime import date, datetime
import time
import csv
import ConfigParser
import os
import numpy as np
import pandas as pd


class StockDataFetcher(object):
    def __init__(self, workingDir='D:\\Testland\\stock_data'):
        print 'WorkingDir is %s' % workingDir
        self.workingDir = workingDir
        configFilePath= os.path.join(workingDir, 'gm\\gm.ini')
        cf = ConfigParser.ConfigParser()
        cf.read(configFilePath)
        user = cf.get('account', 'user')
        password = cf.get('account','password')
        print 'Initializing MD with user "%s"' % user
        md.init(user, password)
    
    def get_daily_bar(self, symbol, year=2015):
        start_date= '%s-01-01' % year
        end_date = '%s-12-31' % year
        gmSymbol = self.generate_gm_symbol(symbol)
        print "'%s','%s','%s'" % (gmSymbol, start_date, end_date)
        return md.get_dailybars(gmSymbol, start_date, end_date)
    
    def save_daily_bar_to_file(self, dayBars, outputFile):
        resultFile = file(outputFile, 'wb')
        writer = csv.writer(resultFile)
        writer.writerow(['date', 'open', 'high','low','close','volume','amount'])
        writer.writerows([dayBarToRow(b) for b in dayBars])
        resultFile.close()
    
    def generate_gm_symbol(self, symbol):
        symbol=str(symbol)
        if symbol[0]=='6':
            return "SHSE.%s" % symbol
        if symbol[0]=='0':
            return "SZSE.%s" % symbol
        return symbol
    
    def fetch_daily_bar_by_year(self, symbol, year=2015):        
        outputFolder = os.path.join(self.workingDir, str(year))        
        if (os.path.isdir(outputFolder) != True):
            print "Making dir '%s'" % outputFolder
            os.mkdir(outputFolder)
        outputFile = os.path.join(outputFolder, 'daily.%s.csv' %(symbol))
        if os.path.isfile(outputFile):
            print 'Data cache exists. Daily bar data is loaded from cache.'
            return
        noOutputFile = os.path.join(outputFolder, 'no.daily.%s.csv' %(symbol))        
        if os.path.isfile(noOutputFile):
            print 'Data cache exists. No data is loaded from cache.'
            return
        dayBars = self.get_daily_bar(symbol=symbol, year=year)
        if(len(dayBars)>0):           
            self.save_daily_bar_to_file(dayBars=dayBars, outputFile=outputFile)
            print 'Daily bar data is loaded.'
        else:            
            self.save_daily_bar_to_file(dayBars=dayBars, outputFile=noOutputFile)
            print 'No data is loaded.'

    def load_daily_df_by_year(self, symbol, year=2015):
        analyzedFileName = '%s.%s.daily.analyzed.csv' % (symbol, year)
        analyzedPath = os.path.join(self.workingDir, 'analyzed', analyzedFileName)
        if (os.path.isfile(analyzedPath)!=True):
            self.fetch_daily_bar_by_year(symbol, year)
            analyzedDataFrame = pd.read_csv(os.path.join(self.workingDir, str(year), 'daily.%s.csv' %(symbol)))
            analyzedDataFrame['ma5']=pd.rolling_mean(analyzedDataFrame['close'] , 5)
            analyzedDataFrame['ma10']=pd.rolling_mean(analyzedDataFrame['close'] , 10)    
            analyzedDataFrame.to_csv(analyzedPath)
        resultDf = pd.read_csv(analyzedPath)      
        return resultDf

def dayBarToRow(dayBar):
    return [datetime.fromtimestamp(dayBar.utc_time).strftime('%Y/%m/%d'), dayBar.open, dayBar.high, dayBar.low, dayBar.close, dayBar.volume, dayBar.amount]