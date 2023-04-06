import pandas as pd
import yfinance as yf
import time
import numpy as np
import talib

def get_mdev(price, t=5):
    mdev = price.copy()
    for v in range(mdev.shape[0]):
        if v >= t:
            mdev[v] = np.std(price[v-t:v])
        else:
            mdev[v] = np.std(price[:v+1])
    return mdev


def get_mat(price, t=5):
    mat = price.copy()
    for v in range(mat.shape[0]):
        if v >= t:
            mat[v] = np.mean(price[v-t:v])
        else:
            mat[v] = np.mean(price[:v+1])
    return mat


def judge_nan(x):
    return 0 if x == float("nan") else x

class Stock():
    def __init__(self, stock, stock_name=None):
        self.stock = stock
        self.stock_name = stock_name
            
    # calculate the Moving average during a particular period
    def cal_mat(self, t=5):
        price = self.stock["Close"]
        mat = self.stock["Close"].copy()
        for v in range(mat.shape[0]):
            if v >= t:
                mat[v] = np.mean(price[v-t:v])
            else:
                mat[v] = np.mean(price[:v+1])
        return mat

    def cal_up_lower(self, r=0.1):
        price = self.stock["Close"]
        return price * (1+r), price * (1-r)

    def read_PCR(self, start_date, end_date):
        # read from history, the temporal interval is close
        put_call = pd.read_csv("./data/put-call.csv")
        DATE = put_call["Date"]
        PCR = put_call["Put Call"]
        value = []
        begin_flag = False
        for i in range(len(DATE)):
            if DATE[i] == start_date:
                begin_flag = True
            if begin_flag:
                value.append(PCR[i])
            if DATE[i] == end_date:
                begin_flag = False    
        return value


    # calculate the moving derivation during a particular period
    def cal_mdev(self, t=5):
        price = self.stock["Close"]
        mdev = price.copy()
        for v in range(mdev.shape[0]):
            if v >= t:
                mdev[v] = np.std(price[v-t:v])
            else:
                mdev[v] = np.std(price[:v+1])
        return mdev

    # calculate the upper and lower bound based on bollinger bands
    def cal_bollinger_bands(self, m=2, n=20):
        # high, low, close = np.array(self.stock["High"]), np.array(self.stock["Low"]), np.array(self.stock["Close"])
        # typical_price = (high+low+close)/3
        # ma_tp = get_mat(typical_price, n)
        # std_tp = get_mdev(typical_price, n)
        # upper_bound = ma_tp + 2*m*std_tp
        # lower_bound = ma_tp - 2*m*std_tp
        upper_bound, middle_bound, lower_bound = talib.BBANDS(self.stock["Close"].values, timeperiod=n)
        upper_bound, middle_bound, lower_bound = pd.Series(upper_bound).fillna(0), pd.Series(middle_bound).fillna(0), pd.Series(lower_bound).fillna(0)
        return upper_bound, middle_bound, lower_bound

    # input date, close, high, low, open, volume to calculate CHMF
    def cal_CHMF(self,tf=20):
        c, h = np.array(self.stock["Close"]), np.array(self.stock["High"]) 
        l, v = np.array(self.stock["Low"]), np.array(self.stock["Volume"])
        CHMF = np.zeros_like(c)
        MFMs = []
        MFVs = []
        x = tf
        while x < len(c):
            PeriodVolumn = 0
            volRange = v[x-tf:x]
            for eachVol in volRange:
                PeriodVolumn += eachVol
            MFM = ((c[x]-l[x])-(h[x]-c[x]))/(h[x]-l[x])
            MFV = MFM * (PeriodVolumn)
            MFMs.append(MFM)
            MFVs.append(MFV)
            x+=1
        y = tf
        while y < len(MFVs):
            PeriodVolumn = 0
            volRange = v[x-tf:x]
            for eachVol in volRange:
                PeriodVolumn += eachVol
            consider = MFVs[y-tf:y]
            tfsMFV = 0
            for eachMFV in consider:
                tfsMFV += eachMFV
            tfsCMF = tfsMFV / PeriodVolumn
            CHMF[tf+y] = tfsCMF
            y+=1
        return CHMF

    # calculate the on-balance volume
    def cal_OBV(self, start_date=0):
        OBV = talib.OBV(self.stock["Close"].values, self.stock["Volume"].values.astype(np.float64))
        return pd.Series(OBV).fillna(0)
        # open, close, volume = np.array(self.stock["Open"]), np.array(self.stock["Close"]), np.array(self.stock["Volume"])
        # OBV = np.zeros_like(open)
        # # OBV = talib.OBV()
        # cur_OBV = 0
        # for i in range(start_date, len(volume)):
        #     if open[i]>close[i]:
        #         cur_OBV += volume[i]
        #     elif open[i]<close[i]:
        #         cur_OBV -= volume[i]
        #     OBV[i] = cur_OBV
        # return OBV


    # calculate the trend (with accurate value of changing)
    def cal_trend(self, threshold=0.3, mode="Close"):
        close = np.array(self.stock[mode])
        trend = np.zeros_like(close)
        for i in range(1, len(close)):
            trend[i] = (close[i]/close[i-1] - 1.0) * 100.
            if np.abs(trend[i]) < threshold:
                trend[i] = 0
        return trend 

    # calculate the relative strength index
    def cal_RSI(self, period=14):
        # RSI = talib.RSI(self.stock["Close"].values, period)
        # print(RSI, type(RSI[0]))
        # RSI = pd.Series(pd).fillna(0).values
        # print(type(RSI[0]))
        # RSI = RSI.astype(np.float32)
        close = self.stock["Close"]
        RSI = np.zeros_like(close)
        for i in range(period + 1, len(RSI)):
            period_dif = np.zeros(period)
            for j in range(period):
                period_dif[j] = close[i-period+j] - close[i-period+j-1]
            pos_index = (period_dif > 0).astype(np.uint32)
            pos = np.mean(pos_index * period_dif)
            neg = -np.mean((1-pos_index) * period_dif)
            rs = pos/neg 
            RSI[i] = 100 - 100 / (1+rs)
        return RSI

    def cal_EMA(self, period=12, smooth=2):
        close = self.stock["Close"]
        ema = np.zeros_like(close)
        for i in range(1, len(close)):
            ema[i] = ema[i-1] * (1-smooth/(period+1)) + close[i] * (smooth/(period+1))
        return ema


    def cal_MACD(self, fast_period=12, slow_period=26, signal_period=9):
        # print(self.stock["Close"].values)
        dif, dea, bar = talib.MACD(self.stock["Close"].values, fastperiod=12, slowperiod=26, signalperiod=9)
        dif, dea, bar = pd.Series(dif).fillna(0), pd.Series(dea).fillna(0), pd.Series(bar).fillna(0)
        return dif, dea, bar
        # ema12, ema26 = self.cal_EMA(period=12), self.cal_EMA(period=26)
        # close = self.stock["Close"]
        # macd, dif = np.zeros_like(close), np.zeros_like(close)
        # for i in range(1, len(macd)):
        #     dif[i] = ema12[i] - ema26[i] # 快速线减去慢速线，如果股价上涨，则dif上升。如果股价下跌则DIF下降
        #     if i >= dif_period:
        #         macd[i] = np.mean(dif[i-dif_period:i])
        # if mode == "macd":
        #     return macd
        # elif mode == "all":
        #     return dif, macd, (dif-macd)*2 # 返回快线，慢线，MACD柱子

    # here we set the flag bit 0 as no pattern, 1 as evenstar, 2 as mornstar
    def judge_stars(self, threshold=0.1, updown=5):
        close, open = self.stock["Close"], self.stock["Open"]
        doji = ((np.abs(close/open-1))<threshold * 0.01).astype(np.int32)
        flag = np.zeros_like(close)
        for i in range(len(doji)):
            if i >= 2 and doji[i-1] == 1:
                if open[i-2] > close[i-2] * (1+updown * 0.01) and open[i] < close[i] * (1-updown * 0.01):
                    flag[i-1] = 2
                elif open[i-2] < close[i-2] * (1-updown * 0.01) and open[i] > close[i] * (1+updown * 0.01):
                    flag[i-1] = 1
        return flag

    # we define here starting at 2000 . 1
    def read_IR(self, start_year=2018, months=12):
        path = ".\\data\\IR.csv"
        ir = np.array(pd.read_csv(path)["FEDFUNDS"])
        ir_month = ir[(start_year-2000)*12:(start_year-2000)*12+months]
        date, close = self.stock["Date"],  self.stock["Close"]
        ir_date = np.zeros_like(close)
        for i in range(len(date)):
            ir_date[i] = ir_month[int(date[i][5:7])-1]

        return ir_date

    # read the VIX from csv
    def read_VIX(self, start_date="01/02/2018", end_date="01/02/2019"):
        # read from history, the temporal interval is close
        path = ".\\data\\VIX_History.csv"
        df = pd.read_csv(path)
        date, close = df["DATE"], df["CLOSE"]
        begin_flag = False
        vix_close = []
        for i in range(len(close)):
            if date[i] == start_date:
                begin_flag = True
            if begin_flag:
                vix_close.append(close[i])
            if date[i] == end_date:
                begin_flag = False

        return vix_close

    def cal_KDLines(self, fastk=9, slowk=3, slowd=3):
        close, high, low = self.stock["Close"], self.stock["High"], self.stock["Low"]
        # rsv = np.zeros_like(close)
        # kl, dl = np.zeros_like(close), np.zeros_like(close)
        # for i in range(len(close)):
        #     if i>=N:
        #         rsv[i] = 100 * (close[i-1] - np.min(close[i-N:i]))/(np.max(high[i-N:i])-np.min(low[i-N:i]))
        #     elif i>0:
        #         rsv[i] = 100 * (close[i-1] - np.min(close[:i]))/(np.max(high[:i])-np.min(low[:i]))
            
        # for i in range(len(rsv)):
        #     if i>=3:
        #         kl[i] = np.mean(rsv[i-3:i])
        #     elif i>0:
        #         kl[i] = np.mean(rsv[:i])
        #     else:
        #         kl[i] = rsv[0]
        # for i in range(len(rsv)):
        #     if i>=3:
        #         dl[i] = np.mean(kl[i-3:i])
        #     elif i>0:
        #         dl[i] = np.mean(kl[:i])
        #     else:
        #         dl[i] = kl[0]
        kl, dl = talib.STOCH(high.values, low.values, close.values, fastk, slowk, slowd)
        kl, dl = pd.Series(kl).fillna(0), pd.Series(dl).fillna(0)
        return kl, dl


    def determine_state(self):
        price = self.stock["Close"]
        # determine A state (The bolinger bound)
        state_a = np.zeros_like(price)
        bbh, bbl = self.stock["BBH"], self.stock["BBL"]
        # bound = [bbm - (bbm-bbl) * 0.1, bbm + (bbh-bbm) * 0.1, bbm - (bbm-bbl) * 0.5, bbm + (bbh-bbm) * 0.5]
        bbi = bbh - bbl 
        bound = [bbl + bbi * 0.2, bbl + bbi * 0.4, bbl + bbi * 0.6, bbl + bbi * 0.8, bbh]
        for i in range(len(price)):
            p = price[i]
            if p < bound[0][i]:
                state_a[i] = -2
            elif p < bound[1][i]:
                state_a[i] = -1
            elif p < bound[2][i]:
                state_a[i] = 0
            elif p < bound[3][i]:
                state_a[i] = 1
            else:
                state_a[i] = 2
        
        # determine B state (The DEA and DIF behavior)
        state_b = np.zeros_like(price) 
        # at this time, 0 repsents no state (0), if DIF>DEA is (1), else (2)
        DIF, DEA = self.stock["DIF"], self.stock["MACD"]
        for i in range(1,len(DIF)):
            if DIF[i-1] - DEA[i-1] >0 and DIF[i] - DEA[i] <0: # DEA 穿越 DIF
                state_b[i] = -1
            elif DIF[i-1] - DEA[i-1] <0 and DIF[i] - DEA[i] >0: # DIF 穿越 DEA
                state_b[i] = 1
        
        # determine C state (The candlestick pattern)
        state_c = np.zeros_like(price)
        open_price = self.stock["Open"]
        dif_open_close = np.abs(open_price-price)
        for i in range(1,len(state_c)-1):
            if dif_open_close[i] < 0.01 * price[i]:
                state_c[i] = 1
                if (price[i-1]-open_price[i-1]) > 0.05 * open_price[i-1] and (price[i+1]-open_price[i+1]) > 0.05 * open_price[i+1] and state_a[i] > 0:
                    state_c[i] = 2 # evening star
                elif (open_price[i-1]-price[i-1]) > 0.05 * open_price[i-1] and (open_price[i+1]-price[i+1]) > 0.05 * open_price[i+1] and state_a[i] < 0:
                    state_c[i] = 3 # morning star
        
        # determine D state (The K and D behavior)
        state_d = np.zeros_like(price)
        KL, DL = self.stock["KL"], self.stock["DL"]
        for i in range(1, len(price)):
            if KL[i-1] - DL[i-1] >0 and KL[i] - DL[i] <0: # D 穿 K
                state_d[i] = -1
            elif KL[i-1] - DL[i-1] <0 and KL[i] - DL[i] >0: # K 穿 D
                state_d[i] = 1

        # determine E state (The on-balance volumne)
        state_e = np.zeros_like(price)
        obv = self.stock["OBV"]
        obv_ma = get_mat(obv)
        dif_obv_mean_cur = obv - obv_ma
        for i in range(1, len(price)):
            if dif_obv_mean_cur[i-1] <0 and dif_obv_mean_cur[i] >0:
                state_e[i] = 1
            elif dif_obv_mean_cur[i-1] >0 and dif_obv_mean_cur[i] <0:
                state_e[i] = -1
            
        # determine the state F (The rsi behavior)
        rsi = self.stock["RSI"]
        state_f = np.zeros_like(price)
        for i in range(len(price)):
            cur_rsi = rsi[i]
            if cur_rsi <= 20:
                state_f[i] = -2
            elif cur_rsi <= 40:
                state_f[i] = -1
            elif cur_rsi <= 60:
                state_f[i] = 0
            elif cur_rsi <= 80:
                state_f[i] = 1
            else:
                state_f[i] = 2

        # determine the state G (The pcr behavior)
        state_g = np.zeros_like(price)
        lowest_pcr = 0.37
        highest_pcr = 1.28
        inter_pcr = highest_pcr - lowest_pcr
        pcr = self.stock["PCR"]
        bound = [lowest_pcr + 0.2*inter_pcr, lowest_pcr+0.4*inter_pcr, lowest_pcr+0.6*inter_pcr, lowest_pcr+0.8*inter_pcr, highest_pcr]
        for i in range(len(price)):
            if pcr[i] <= bound[0]:
                state_g[i] = -2
            elif pcr[i] <= bound[1]:
                state_g[i] = -1
            elif pcr[i] <= bound[2]:
                state_g[i] = 0
            elif pcr[i] <= bound[3]:
                state_g[i] = 1
            elif pcr[i] <= bound[4]:
                state_g[i] = 2

        # store the difference of PCR to show short-term trend
        state_h = np.zeros_like(price)
        pcr = self.stock["PCR"]
        for i in range(1, len(state_h)-1):
            ratio = 0.5 * ((pcr[i]-pcr[i-1]) + (pcr[i] - pcr[i+1]))
            state_h[i] = ratio if np.abs(ratio) > 1e-3 else 0
        
        # store the difference of RSI to show short-term trend
        state_i = np.zeros_like(price)
        rsi = self.stock["RSI"]
        for i in range(1, len(state_i)-1):
            ratio = 0.5 * ((rsi[i]-rsi[i-1]) + (rsi[i] - rsi[i+1]))
            state_i[i] = ratio if np.abs(ratio) > 1e-3 else 0






        return state_a, state_b, state_c, state_d, state_e, state_f, state_g, state_h, state_i
