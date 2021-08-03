import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import matplotlib.ticker

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

df = pd.read_csv('matic-history.csv', sep=',', dtype=np.float128)
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

print(df)
df = df.drop('blocknumber', axis=1)
df.columns = ['Date', 'totalStaked', 'totalReward']
fig, ax = plt.subplots()
df.plot(x='Date', ax=ax)

ax.set_ylabel('Matic')
ax.yaxis.set_major_formatter(OOMFormatter(6, "%1.1f"))
ax.ticklabel_format(axis='y', style='sci', scilimits=(-4,-4))
ax.set_title("Matic historical rewards")
ax.set_xlim(df['Date'].min(),)
ax.set_ylim(0,2.5e8)

plt.grid()
plt.show(block=True)
