import matplotlib.pyplot as plt
import json
import numpy as np
import datetime as dt
import requests
import pickle
import matplotlib.ticker
import csv

class OOMFormatter(matplotlib.ticker.ScalarFormatter):
    def __init__(self, order=0, fformat="%1.1f", offset=True, mathText=True):
        self.oom = order
        self.fformat = fformat
        matplotlib.ticker.ScalarFormatter.__init__(self,useOffset=offset,useMathText=mathText)
    def _set_order_of_magnitude(self):
        self.orderOfMagnitude = self.oom
    def _set_format(self, vmin=None, vmax=None):
        self.format = self.fformat
        if self._useMathText:
            self.format = r'$\mathdefault{%s}$' % self.format

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

# time,blocknumber,reward,stake,reward(usd), stake(usd),diff reward,diff reward (USD),,MATIC(USD)
data = []
head = ['time', 'blocknumber', 'reward', 'reward (USD)', 'MATIC(USD)']

for [blockNumber, timestamp, reward, totalReward] in all_rewards:
    date = dt.datetime.fromtimestamp(timestamp)

    price = getPrice(date)
    totalReward = toFloat(totalReward)
    data.append([date, blockNumber, totalReward, totalReward * price, price])

data = np.array(data)
x = data.T[0]
y1 = data.T[2]
y2 = data.T[3]

fig, ax = plt.subplots()
ax.plot(x, y1)
ax.set_ylabel('Matic')
ax.yaxis.set_major_formatter(OOMFormatter(6, "%1.1f"))
ax.ticklabel_format(axis='y', style='sci', scilimits=(-4,-4))
plt.grid()
plt.savefig('matic-stake.png')
plt.show()

fig, ax = plt.subplots()
ax.plot(x, y2)
ax.set_ylabel('USD')
ax.yaxis.set_major_formatter(OOMFormatter(6, "%1.1f"))
ax.ticklabel_format(axis='y', style='sci', scilimits=(-4,-4))
plt.grid()
plt.savefig('usd-stake.png')
plt.show()


with open('full-data.csv', 'w') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(head)
    writer.writerows(data)