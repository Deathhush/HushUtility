from gmsdk import md
from datetime import date, datetime
import time
import csv
import ConfigParser

class StockDataFetcher(object):
    def __init__(self, configFilePath="D:\\Testland\\stock_data\\gm\\gm.ini"):
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
        return symbol
    
    def fetch_daily_bar(self, symbol, year=2015, outputFolder='D:\\Testland\\stock_data\\'):
        dayBars = self.get_daily_bar(symbol=symbol, year=year)
        if(len(dayBars)>0):
            outputFile = '%s\\%s\\daily.%s.csv' % (outputFolder, year, symbol)
            self.save_daily_bar_to_file(dayBars=dayBars, outputFile=outputFile)
            print 'Daily bar data is loaded.'
        else:
            outputFile = '%s\\%s\\no.daily.%s.csv' % (outputFolder, year, symbol)
            self.save_daily_bar_to_file(dayBars=dayBars, outputFile=outputFile)
            print 'No data is loaded.'

def dayBarToRow(dayBar):
    return [datetime.fromtimestamp(dayBar.utc_time).strftime('%Y/%m/%d'), dayBar.open, dayBar.high, dayBar.low, dayBar.close, dayBar.volume, dayBar.amount]