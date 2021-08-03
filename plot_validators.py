import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker
from web3 import Web3
import datetime as dt
import requests
from time import sleep


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



def toFloat(wei):
    if wei == '0':
        return 0
    return float(wei[:-18] + '.' + wei[-18:-1])

with open('./validators-populated.json') as f:
    validators = json.load(f)


sumReward = dict()
sumStake = dict()
for validator in validators:
    data = np.array([[block, float(stake), float(reward)] for [block, stake, reward] in validator['totalRewards']])
    data2 = np.array([[block, toFloat(stake), toFloat(reward)] for [block, stake, reward] in validator['rewards']])
    if len(data) > 0:
        blocks, stake, reward = data.T
        _, _, reward2 = data2.T

        plt.plot(blocks, stake, label='stake')
        plt.plot(blocks, reward ,label='fix reward')
        plt.plot(blocks, reward2,label='reward')
        for block, stake, reward in data:
            if block in sumReward:
                sumReward[block] += reward
            else:
                sumReward[block] = reward

            if block in sumStake:
                sumStake[block] += stake
            else:
                sumStake[block] = stake
        plt.title("Validator id: %s" % validator['id'])
plt.show()


fig, ax = plt.subplots()
sumReward = np.array(list(sumReward.items()))
sumStake = np.array(list(sumStake.items()))
blocks, reward = sumReward.T
w3 = Web3(Web3.HTTPProvider('https://eth-mainnet.alchemyapi.io/v2/xxx'))
time = [dt.datetime.fromtimestamp(w3.eth.getBlock(int(block)).timestamp) for block in blocks]
ax.plot(time, reward)
blocks, stake = sumStake.T
ax.plot(time, stake)
ax.set_ylabel('Matic')
ax.yaxis.set_major_formatter(OOMFormatter(6, "%1.1f"))
ax.ticklabel_format(axis='y', style='sci', scilimits=(-4,-4))
plt.show()

for i in range(len(time)):
    response = requests.get("https://api.coingecko.com/api/v3/coins/matic-network/history?date="+time[i].strftime('%d-%m-%Y'))
    price = float(response.json()['market_data']['current_price']['usd'])
    sleep(0.5)
    print(str(time[i]) + ',' + str(int(blocks[i])) + ',' + str(reward[i]) + ',' + str(stake[i]) + ',' + str(price * reward[i]) + ',' + str(price * stake[i]))
