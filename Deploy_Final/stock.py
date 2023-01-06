import yfinance as yf
import datetime
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots


class Stock:
    """
    This class enables data loading, plotting and statistical analysis of a given stock,
     upon initialization load a sample of data to check if stock exists. 
        
    """

    def __init__(self, symbol="AAPL"):
       
        self.end = datetime.datetime.today()
        self.start = self.end - datetime.timedelta(days=4)
        self.symbol = symbol
        self.data = self.load_data(self.start, self.end)

    @st.cache(show_spinner=False) #Using st.cache allows st to load the data once and cache it. 
    def load_data(self, start, end, inplace=False):
        """
        takes a start and end dates, download data do some processing and returns dataframe
        """

        data = yf.download(self.symbol, start, end + datetime.timedelta(days=1))
        #Check if there is data
        try:
            assert len(data) > 0
        except AssertionError:
            print("Cannot fetch data, check spelling or time window")
        data.reset_index(inplace=True)
        data.rename(columns={"Date": "datetime"}, inplace=True)
        data["Date"] = data.apply(lambda raw: raw["datetime"].date(), axis=1)

        data = data[['Date', 'Open', 'High', 'Low','Close', 'Adj Close', 'Volume', 'datetime']]
        data['Return'] = data['Close'].pct_change(periods=1).fillna(0)

        log_returns = np.log(data.Close/data.Close.shift(1)).fillna(0)
        data['log_returns'] = log_returns

        daily_std = log_returns.std()
        data['daily_std'] = daily_std

        annualized_vol = daily_std * np.sqrt(252)
        data['annualized_vol'] = annualized_vol*100

        data['MA50'] = data['Close'].rolling(window=50, min_periods=0).mean()
        data['MA200'] = data['Close'].rolling(window=200, min_periods=0).mean()
        if inplace:
            self.data = data
            self.start = start
            self.end = end
            return data
        return data
            
    def plot_raw_data_1(self, fig):
        df_date=self.data.Date.unique()
        returns=self.data.groupby('Date')['Return'].mean().mul(100).rename('Average Return')
        vol_avg=self.data.groupby('Date')['Volume'].mean()
        close_avg=self.data.groupby('Date')['Close'].mean().rename('Closing Price')
        open_avg=self.data.groupby('Date')['Open'].mean()
        high_avg=self.data.groupby('Date')['High'].mean()
        low_avg=self.data.groupby('Date')['Low'].mean()
        MA_50 = self.data.groupby('Date')['MA50'].mean()
        MA_200 = self.data.groupby('Date')['MA200'].mean()
        colors=px.colors.qualitative.Plotly
        temp = dict(layout=go.Layout(font=dict(family="Franklin Gothic", size=12)))
            
                
        fig.add_trace(go.Candlestick(x=df_date, open=open_avg, high=high_avg, low=low_avg, close=close_avg, name=self.symbol,showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_date, y=MA_50, marker_color='grey', name='MA50', showlegend=True), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_date, y=MA_200, marker_color='lightblue', name='MA200', showlegend=True), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_date, y=returns, mode='lines', name='Return', showlegend=False, marker_color=colors[3]), row=2, col=1)
                
        fig.update_xaxes(rangeslider_visible=False,
                        rangeselector=dict(
                            buttons=list([
                                dict(count=1, label="1M", step="month", stepmode="backward"),
                                dict(count=3, label="3M", step="month", stepmode="backward"),
                                dict(count=6, label="6M", step="month", stepmode="backward"),
                                dict(count=1, label="1Y", step="year", stepmode="backward"),
                                dict(count=2, label="2Y", step="year", stepmode="backward"),
                                dict(step="all")]), y=1, x=.01), row=1,col=1)
                
        fig.update_layout(template=temp, title='Apple Stock', hovermode='x unified', 
                            yaxis1=dict(title='Stock Price'), yaxis2=dict(title='Stock Return',ticksuffix='%')
                        )
        return fig


    def plot_raw_data_2(self, fig):
        df_date=self.data.Date.unique()
        returns=self.data.groupby('Date')['Return'].mean().mul(100).rename('Average Return')
        vol_avg=self.data.groupby('Date')['Volume'].mean()
        close_avg=self.data.groupby('Date')['Close'].mean().rename('Closing Price')
        open_avg=self.data.groupby('Date')['Open'].mean()
        high_avg=self.data.groupby('Date')['High'].mean()
        low_avg=self.data.groupby('Date')['Low'].mean()
        MA_50 = self.data.groupby('Date')['MA50'].mean()
        MA_200 = self.data.groupby('Date')['MA200'].mean()
        colors=px.colors.qualitative.Plotly
        temp = dict(layout=go.Layout(font=dict(family="Franklin Gothic", size=12)))
                
                    
        fig.add_trace(go.Candlestick(x=df_date, open=open_avg, high=high_avg, low=low_avg, close=close_avg, name=self.symbol,showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_date, y=MA_50, marker_color='grey', name='MA50', showlegend=True), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_date, y=MA_200, marker_color='lightblue', name='MA200', showlegend=True), row=1, col=1)        
        fig.add_trace(go.Scatter(x=df_date, y=vol_avg, mode='lines', name='Volume', showlegend=False, marker_color=colors[5]), row=2, col=1)
                
        fig.update_xaxes(rangeslider_visible=False,
                        rangeselector=dict(
                            buttons=list([
                                dict(count=1, label="1M", step="month", stepmode="backward"),
                                dict(count=3, label="3M", step="month", stepmode="backward"),
                                dict(count=6, label="6M", step="month", stepmode="backward"),
                                dict(count=1, label="1Y", step="year", stepmode="backward"),
                                dict(count=2, label="2Y", step="year", stepmode="backward"),
                                dict(step="all")]), y=1, x=.01), row=1,col=1)
                    
        fig.update_layout(template=temp, title='Apple Stock', hovermode='x unified', 
                                yaxis1=dict(title='Stock Price'), yaxis2_title='Shares Traded'
                            )
        return fig        
    
    @staticmethod
    def nearest_business_day(DATE: datetime.date):
        """
        Takes a Date and transform it to the nearest business day, 
        static because we would like to use it without a stock object.
        """
        if DATE.weekday() == 5:
            DATE = DATE - datetime.timedelta(days=1)

        if DATE.weekday() == 6:
            DATE = DATE + datetime.timedelta(days=1)
        return DATE