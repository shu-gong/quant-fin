# import talib     
import numpy as np 
# import psycopg2 as pg 
import pandas as pd 
import matplotlib.pyplot as plt 
import matplotlib.gridspec as gridspec#分割子图 
import mplfinance as mpf 
np.seterr(divide='ignore',invalid='ignore') # 忽略warning
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签 
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号 
# fig = plt.figure(figsize=(20,12), dpi=100,facecolor="white") #创建fig对象

data_name = "TQQQ-state"
data = pd.read_csv("./data/"+data_name+".csv", index_col=0)
# data.open = data["Open"]
data.index = pd.to_datetime(data["Date"])

# gs = gridspec.GridSpec(4, 1, left=0.08, bottom=0.15, right=0.99, top=0.96, wspace=None, hspace=0, height_ratios=[3.5,1,1,1])
# graph_KAV = fig.add_subplot(gs[0,:])
# graph_VOL = fig.add_subplot(gs[1,:])
# graph_MACD = fig.add_subplot(gs[2,:])
# graph_KDJ = fig.add_subplot(gs[3,:])

#绘制K线图
# mpf.candlestick_ohlc(graph_KAV, data["Open"], data["Close"], data["High"], data["Low"], width=0.5,
#                       colorup='r', colordown='g')  # 绘制K线走势


df = data

# 设定上、下、中通道线初始值
upboundDC = pd.Series(0.0, index=df.Close.index)
downboundDC = pd.Series(0.0, index=df.Close.index)
midboundDC = pd.Series(0.0, index=df.Close.index)

# 求唐奇安上、中、下通道
for i in range(20, len(df.Close)):
    upboundDC[i] = max(df.High[(i-20):i])
    downboundDC[i] = min(df.Low[(i-20):i])
    midboundDC[i] = 0.5 * (upboundDC[i] + downboundDC[i])


df['upboundDC'] = upboundDC
df['downboundDC'] = downboundDC
df['midboundDC'] = midboundDC
data = df.loc['2018-1':'2018-12']


my_color = mpf.make_marketcolors(
    up="green",  # 上涨K线的颜色
    down="red",  # 下跌K线的颜色
    edge="black",  # 蜡烛图箱体的颜色
    wick="black",  # 蜡烛图影线的颜色
    volume="inherit"  # 继承up和down的颜色
)

# 设置图表的背景色 
my_style = mpf.make_mpf_style(
    base_mpl_style='seaborn',
    marketcolors=my_color,
    rc={'font.family': 'SimHei', 'axes.unicode_minus': 'False'}
)


add_plot = [
            # mpf.make_addplot(data['upboundDC']),
            # mpf.make_addplot(data['midboundDC']),
            # mpf.make_addplot(data['downboundDC']),
            # mpf.make_addplot(data['MA5'], type='line', color='y'),
            # mpf.make_addplot(exp26, type='line', color='r'),
            # mpf.make_addplot(histogram, type='bar', width=0.7, panel=2, color='dimgray', alpha=1, secondary_y=False),
            mpf.make_addplot(data['RSI'], panel=2, color='fuchsia', secondary_y=True,ylabel = 'RSI'),
            mpf.make_addplot(data['PCR'], panel=4, color='r', secondary_y=True, ylabel='PCR'),
            
            mpf.make_addplot(data['MACD'], panel=3, color='fuchsia', secondary_y=True,ylabel = 'MACD'),
            mpf.make_addplot(data['DIF'], panel=3, color='r', secondary_y=True, ylabel='DIF'),

            # mpf.make_addplot(data['MACD'], panel=2, color='b', secondary_y=True),
            # mpf.make_addplot(data['PercentB'], panel=1, color='g', secondary_y='auto'),
            ]


mpf.plot(data,
         type='candle',
         ylabel="price",
         style=my_style,
         title='TQQQ',
         addplot=add_plot,
         mav=(5, 10),
         volume=True,
         figratio=(5, 3),
         ylabel_lower="Volume")

plt.legend()

# plt.show()
