import streamlit as st
import requests
import json
import pandas as pd
import numpy as np
from scipy.optimize import minimize
from scipy.stats import skew, kurtosis, jarque_bera, norm
import math

def getStockPrice(symbol) :
    success = False
    while success != True :
        try :
            data = json.loads(requests.get('https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY_ADJUSTED&symbol='+symbol+'&outputsize=compact&apikey=B1V5UKZC6MHRRLE0').text)
            data = pd.DataFrame(data["Monthly Adjusted Time Series"]).transpose().iloc[::-1]
            data = data.drop(['7. dividend amount', '6. volume', '5. adjusted close', '1. open', '2. high', '3. low'], axis=1)
            data = data.tail(61)
            success = True
            return data
        except :
            continue

def getReturns(data) :
    return data.astype(float).pct_change().dropna()

def getTotalReturns(returns) :
    return (returns + 1).prod() - 1 #np.expm1(np.log1p(r).sum())

def formatPCT(number) :
    return round(number*100, 2)

def stockAnalysis(symbol) :
    data = getStockPrice(symbol)
    tot_return = formatPCT(getTotalReturns(getReturns(data)))['4. close']
    ann_vol = formatPCT((getReturns(data).std()*np.sqrt(12)))['4. close']
    ann_vol = formatPCT((getReturns(data).std()*(12**0.5)))['4. close']
    ann_return = formatPCT(((getReturns(data) + 1).prod()**(12/getReturns(data).shape[0]) - 1))['4. close']

    riskfreePerPeriod = (1+riskfree)**(1/12)-1
    excess_rate =  getReturns(data)['4. close'] - riskfreePerPeriod
    ann_excess_rate = getTotalReturns(excess_rate)

    ratio = formatPCT((ann_return - riskfree) / ann_vol)
    ratio = formatPCT(ann_excess_rate/ann_vol)

    #s = skew(getReturns(data))[0]
    #k = kurtosis(getReturns(data), fisher = False)[0]

    z = norm.ppf(0.05)
    z = z + (z**2 - 1)*s/6 + (z**3 - 3*z)*(k-3)/24 - (2*z**3 - 5*z)*(s**2)/36
    VaR = -formatPCT((getReturns(data).mean() + z*getReturns(data).std()))['4. close']

    drawdown = formatPCT(drawDown(getReturns(data)))['4. close']


symbol = 'MSFT'
riskfree = 0.03
data = getStockPrice(symbol)

st.title("Finance - Stock Analysis")
st.write(data)

