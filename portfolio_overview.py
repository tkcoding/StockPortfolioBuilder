# Passes sequence clustering.
from datetime import datetime,timedelta
import numpy as np
import pandas as pd
from pandas_datareader import data as pdr
import matplotlib.pyplot as plt
import yfinance as yf
yf.pdr_override()
import seaborn as sns
import streamlit as st
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
import warnings
warnings.filterwarnings('ignore')
# st.set_option('deprecation.showPyplotGlobalUse', False)
# st.set_page_config(layout="wide")

st.markdown("""
<style>

[data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
    width: 450px;
}
[data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
    width: 500px;
    margin-left: -450px;
}
.big-font {
    font-size:30px !important;
    .sidebar-text {
    font-size:4px;}
}
</style>
""", unsafe_allow_html=True)
st.set_option('deprecation.showPyplotGlobalUse', False)

# file_path = r'./data/ajax_collected_data_all.csv'
# event_path = './data/event_data_v1/events/game_id={}'
        
# full_data_collected = pd.read_csv(file_path)


class stock_calculation(object):
    def __init__(self,foreign_stock_list,local_stock_list,crypto_stock_list=None):
        self.foreign_stock = foreign_stock_list
        self.local_stock = local_stock_list
        self.crypto_stock = crypto_stock_list
        self.date_execution = (datetime.today()-timedelta(days = 30)).strftime('%Y-%m-%d')
        self.yf_pull_list = self.local_stock+self.foreign_stock
        self.consolidated_price = pd.DataFrame()
        
    def yf_pull(self,stock_name,date):
        stock_dataframe= pdr.get_data_yahoo(stock_name,start=self.date_execution)
        return stock_dataframe.reset_index()
    
    def data_pulling(self,share_dict):
        for ticker in self.yf_pull_list:
            stock_dataframe = self.yf_pull(ticker,date=self.date_execution)
            
            stock_dataframe['Name'] = share_dict[ticker]['Name']
            stock_dataframe['Currency'] = share_dict[ticker]['currency']
            stock_dataframe['Holding'] = share_dict[ticker]['Unit']
            self.consolidated_price = pd.concat([self.consolidated_price,pd.DataFrame(stock_dataframe)],axis=0)
        # self.consolidated_price = self.consolidated_price.drop_duplicates(subset=['Name'],keep='last')
        print(self.consolidated_price)

    def stock_graph_plotting(self):
        for stock_n in self.consolidated_price['Name'].unique():
            stock_data= self.consolidated_price[self.consolidated_price['Name'] == stock_n]
            plt.figure(figsize=(20,12))
            plt.xticks(rotation=90)
            plt.title('Trendline for {}'.format(stock_n))
            sns.lineplot(x='Date',y='Close',data=stock_data)
            plt.show()
            st.pyplot()



    def share_worth(self):
        self.consolidated_price['worth'] = self.consolidated_price['Holding']*self.consolidated_price['Close']*self.consolidated_price['Currency']
        return self.consolidated_price

dictionary = {'3182.KL':{'Name':'Genting','Unit':800,'currency':1},\
              '0176.KL':{'Name':'Krono','Unit':6600,'currency':1},\
              '5236.KL':{'Name':'Matrix','Unit':2500,'currency':1},\
              '7160.KL':{'Name':'Penta','Unit':300,'currency':1},\
              '0200.KL':{'Name':'Revenue','Unit':9000,'currency':1},\
              '5279.KL':{'Name':'Serbadk','Unit':2200,'currency':1},\
              '7113.KL':{'Name':'TopGlove','Unit':400,'currency':1},
             'INTC':{'Name':'Intel','Unit':88,'currency':4.1}}



def app():

    foreign_stock_list = ['INTC']
    local_stock_list = ['3182.KL','0176.KL','5236.KL','7160.KL','0200.KL','5279.KL','7113.KL']
    stock_calc = stock_calculation(foreign_stock_list=foreign_stock_list,\
                                local_stock_list=local_stock_list)
    stock_calc.data_pulling(share_dict=dictionary)
    stock_calc.stock_graph_plotting()
    stock_df = stock_calc.share_worth()
app()
