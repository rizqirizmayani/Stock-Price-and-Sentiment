import streamlit as st
import datetime
import yfinance as yf
import pandas as pd
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from plotly import graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
from stock import Stock
import numpy as np
import pickle
from PIL import Image


st.set_page_config(
    page_title="PIP Consultant", layout='centered'
)

image = Image.open('./PIP_consultant.png')
window1 = st.sidebar.container()
window1.image(image)

st.markdown("<h3 style='text-align: center;'>Apple Stock Analysis</h3>", unsafe_allow_html=True)

# ------ layout setting---------------------------
window_selection_c = st.sidebar.container() # create an empty container in the sidebar
window_selection_c.markdown("## Insights") # add a title to the sidebar container
sub_columns = window_selection_c.columns(2) #Split the container into two columns for start and end date

# ----------Time window selection-----------------
NOW=datetime.date.today()
NOW = Stock.nearest_business_day(NOW) #Round to business day

DEFAULT_START=NOW - datetime.timedelta(days=1816)
DEFAULT_START = Stock.nearest_business_day(DEFAULT_START)

START = sub_columns[0].date_input("From", value=DEFAULT_START, max_value=NOW - datetime.timedelta(days=1), min_value=DEFAULT_START)
END = sub_columns[1].date_input("To", value=NOW, max_value=NOW, min_value=START)

START = Stock.nearest_business_day(START)
END = Stock.nearest_business_day(END)
# ---------------stock selection------------------
STOCKS = np.array([ "AAPL"])  # TODO : include all stocks
SYMB = window_selection_c.selectbox("select stock", STOCKS)

stock = Stock(symbol=SYMB)
df = stock.load_data(START, END, inplace=True)
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_width=[0.3, 1])

option = st.sidebar.radio('Option', ['Stock Return', 'Shares Traded'])

if option=='Stock Return':
        
    stock.plot_raw_data_1(fig)
    st.plotly_chart(fig)

if option=='Shares Traded':
        
    stock.plot_raw_data_2(fig)
    st.plotly_chart(fig)


tab2, tab1 = st.columns(["Forcast Without Twitter Sentiment", "Forecast With Twitter Sentiment"])

with tab1:
    st.markdown("<h4 style='text-align: center;'>Forecast With Twitter Sentiment</h4>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        positive_sentiment = st.number_input('Positive Sentiment',0,10000)
    with col2:
        negative_sentiment = st.number_input('Negative Sentiment',0,10000)
    with col3:
        neutral_sentiment = st.number_input('Neutral Sentiment',0,10000)

    open_price = df['Open'].tail(1).values
    high_price = df['High'].tail(1).values
    volume_shares = df['Volume'].tail(1).values
    close_price = df['Close'].tail(1).values
    low_price = df['Low'].tail(1).values
    date_now = pd.to_datetime(df['datetime']).dt.strftime('%Y-%m-%d').tail(1).values
    adj_close_price = df['Adj Close'].tail(1).values
    
    df_predict = pd.DataFrame({'Open': [open_price], 'High': [high_price], 
                        'Low': [low_price], 'Close': [close_price],
                        'Volume': [volume_shares], 'pos': [positive_sentiment], 
                        'neg': [negative_sentiment], 'neutral': [neutral_sentiment]}, index=date_now)

    submit_2 = st.button('Predict')
    if submit_2:
        st.write("Today")
        st.write(df_predict.drop(columns=['pos', 'neg', 'neutral']))
        model_linreg = pickle.load(open('./preprocess.pkl', 'rb'))
        pred = float(np.round(model_linreg.predict(df_predict), 3))
        
        st.write(f"Tomorrow Close Price : $ {pred}")

    

with tab2:
    def data_upload():
        df_1 = pd.read_csv('./data_forecast_arima.csv')
        df_1 = df_1.drop(columns='Unnamed: 0')
        return df_1

    df_arima = data_upload()
    st.markdown("<h4 style='text-align: center;'>Forecast Without Twitter Sentiment</h4>", unsafe_allow_html=True)

    fig = go.Figure(
        data = go.Scatter(
            x = df_arima['date'],
            y = df_arima['forecast'],
            name = "Forecast ARIMA"))
    fig.layout.update(title_text="Forecast", xaxis_rangeslider_visible=True, yaxis_title='Close Adj')
    st.plotly_chart(fig)
    st.write("Forecast Result")
    gd = GridOptionsBuilder.from_dataframe(df_arima)
    gd.configure_pagination(enabled=True)
    gridoption = gd.build()
    AgGrid(df_arima, gridOptions=gridoption, height=250, reload_data=True)
    