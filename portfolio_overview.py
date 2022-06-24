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
from plotly.subplots import make_subplots
import plotly.graph_objects as go

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
        print(share_dict)
        for ticker in self.yf_pull_list:
            stock_dataframe = self.yf_pull(ticker,date=self.date_execution)
            
            stock_dataframe['Name'] = share_dict[ticker]['Name']
            stock_dataframe['Currency'] = share_dict[ticker]['currency']
            stock_dataframe['Holding'] = share_dict[ticker]['Unit']
            stock_dataframe['PurchasePrice'] = share_dict[ticker]['buy_price']
            self.consolidated_price = pd.concat([self.consolidated_price,pd.DataFrame(stock_dataframe)],axis=0)
        # self.consolidated_price = self.consolidated_price.drop_duplicates(subset=['Name'],keep='last')
        print(self.consolidated_price)

    def trending(self,df):
        if (df['Close'] - df['Open']) > 0:
            return 'green'
        else:
            return 'red'


    def stock_graph_plotting(self):
        for stock_n in self.consolidated_price['Name'].unique():
            stock_data = self.consolidated_price[self.consolidated_price['Name'] == stock_n]
            # stock_data = stock_data.set_index('Date')

            stock_data['tag'] = stock_data.apply(self.trending,axis=1)
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(
                        go.Candlestick(
                            x=stock_data.index,
                            low=stock_data.Low,
                            high=stock_data.High,
                            close=stock_data.Close,
                            open=stock_data.Open,
                            increasing_line_color='green',
                            decreasing_line_color='red'
                        )
            )
            # fig.add_trace(go.Bar(x=analysis_df.index, y=analysis_df['Volume'],marker={'color': analysis_df['tag']}),secondary_y=True)


            fig.update_layout(
                title = f'{stock_n}',
                yaxis_title = f'Candle stick graph {stock_n} Price (Ringgit Malaysia)',
                xaxis_title = 'Date'
            )
            st.plotly_chart(fig,use_container_width=True)



    def share_worth(self):
        self.consolidated_price['worth'] = self.consolidated_price['Holding']*self.consolidated_price['Close']*self.consolidated_price['Currency']
        self.consolidated_price['purchasePrice'] = self.consolidated_price['Holding']*self.consolidated_price['PurchasePrice']*self.consolidated_price['Currency']
        self.consolidated_price['PNL'] = self.consolidated_price['worth'] - self.consolidated_price['purchasePrice']
        self.consolidated_price = self.consolidated_price.reset_index()
        portfolio_nettworth = self.consolidated_price.groupby('Date').agg('sum')
        self.consolidated_price = self.consolidated_price.set_index('Date')

        return self.consolidated_price,portfolio_nettworth

#TODO: Need to turn this into json file or input
share_dictionary = {'3182.KL':{'Name':'Genting','Unit':200,'currency':1,'buy_price':4.58},\
              '0176.KL':{'Name':'Krono','Unit':6600,'currency':1,'buy_price':0.649},\
              '7160.KL':{'Name':'Penta','Unit':300,'currency':1,'buy_price':6.18},\
              '0200.KL':{'Name':'Revenue','Unit':12400,'currency':1,'buy_price':1.86},\
              '5279.KL':{'Name':'Serbadk','Unit':2200,'currency':1,'buy_price':0.94},\
              '7113.KL':{'Name':'TopGlove','Unit':400,'currency':1,'buy_price':3.49}}


def app():

    # Issue with nettworth on foreign investment on public holiday.

    foreign_stock_list = []
    local_stock_list = ['3182.KL','0176.KL','7160.KL','0200.KL','5279.KL','7113.KL']
    stock_calc = stock_calculation(foreign_stock_list=foreign_stock_list,\
                                local_stock_list=local_stock_list)
    stock_calc.data_pulling(share_dict=share_dictionary)
    stock_df,portfolio_nettw = stock_calc.share_worth()
    # Nettworth plotting
    plt.figure(figsize=(20,12))
    plt.xticks(rotation=90)
    plt.title('Trendline for portfolio nettworth')
    sns.lineplot(x='Date',y='worth',data=portfolio_nettw)
    sns.lineplot(x='Date',y='PNL',data=portfolio_nettw)
    plt.show()
    st.pyplot()
    stock_calc.stock_graph_plotting()

app()
