import matplotlib.pyplot as plt
import json
import numpy as np
import datetime as dt
import requests
import pickle
import pandas as pd

def getPrice(datetime):

    try:
        prices = pickle.load(open("prices.pickle", "rb"))
    except (OSError, IOError) as e:
        prices = dict()


    date = datetime.strftime('%d-%m-%Y')

    if date in prices:
        return prices[date]
    
    response = requests.get("https://api.coingecko.com/api/v3/coins/matic-network/history?date="+date)
    price = float(response.json()['market_data']['current_price']['usd'])
    prices[date] = price

    pickle.dump(prices, open("prices.pickle", "wb"))
    return price

def toFloat(wei):
    if wei == '0':
        return 0.
    return float(wei[:-18] + '.' + wei[-18:-1])


with open('./all-rewards.json') as f:
    all_rewards = json.load(f)

data = []
head = ['date', 'blocknumber', 'reward', 'reward(USD)', 'MATIC(USD)']

for [blockNumber, timestamp, reward, totalReward] in all_rewards:
    date = dt.datetime.fromtimestamp(timestamp)

    price = getPrice(date)
    totalReward = toFloat(totalReward)
    data.append([date, blockNumber, totalReward, totalReward * price, price])

data = np.array(data)
df = pd.DataFrame(data, columns=head).apply(pd.to_numeric)
df.columns = df.columns.str.strip()


df['date'] = pd.to_datetime(df['date'])
df['diff'] = df['reward'].diff()
df.drop('blocknumber', axis=1)
df = df.groupby(df['date'].dt.date).agg({'reward': np.max, 'reward(USD)': np.max, 'MATIC(USD)': np.mean, 'diff': np.sum})
df['diff(USD)'] = df['MATIC(USD)'] * df['diff']
print(df)
df.to_csv('matic-full-history-daily.csv')
