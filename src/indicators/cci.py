import pandas as pd
import pandas_ta as ind
from log_get_data import *
from shapely.geometry import LineString
import matplotlib.pyplot as plt
import time
from F_I_RESIST_PROTECT import protect_resist
from sklearn.cluster import KMeans
import math
from scipy import stats
from fitter import Fitter, get_common_distributions, get_distributions
import fitter
from scipy.stats import foldnorm, dweibull, rayleigh, expon, nakagami, norm
from scipy.optimize import fsolve
#For Genetic:
from random import seed
from random import randint
import csv
import os
from tqdm import tqdm
import logging
from datetime import datetime


# Create a DataFrame so 'ta' can be used.
#df = pd.DataFrame()
# Help about this, 'ta', extension
#help(df.ta)

# List of all indicators
#df.ind.indicators()

# Help about an indicator such as bbands
#help(ta.sma)
#help(ind.cci)

#**************************************************** High Low Toucehd *******************************************************

#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


#**************************************************** Ramp Lines Toucehd *******************************************************

#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


#**************************************************** Divergence *******************************************************

#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#**************************************************** Golden Cross Zero *******************************************************
def golden_cross_zero(dataset,dataset_15M,symbol,Low_Period=25,High_Period=50,distance_lines=2,mode='online',name_stp_minmax=True,name_stp_pr=False,plot=False):
	x = np.arange(0,len(dataset[symbol]['HLC/3']),1)

	High_Period = int(High_Period)
	Low_Period = int(Low_Period)

	CCI_Low = ind.cci(high=dataset[symbol]['high'], low=dataset[symbol]['low'], close=dataset[symbol]['close'], length = Low_Period)
	CCI_High = ind.cci(high=dataset[symbol]['high'], low=dataset[symbol]['low'], close=dataset[symbol]['close'], length = High_Period)

	zero_line = pd.DataFrame(np.zeros(len(x)))

	#****************** Finding Low Period Cross With Zero Line ************************
	first_line = LineString(np.column_stack((x[(High_Period-1):], CCI_Low[(High_Period-1):])))
	second_line = LineString(np.column_stack((x[(High_Period-1):], zero_line[(High_Period-1):])))

	intersection_low = first_line.intersection(second_line)

	if intersection_low.geom_type == 'MultiPoint':
		cross = pd.DataFrame(*LineString(intersection_low).xy)
		cross_index = cross.index.to_numpy()
		cross_low = pd.DataFrame(cross.values.astype(int),columns=['index'])
		cross_low['index'] = cross.values.astype(int)
		cross_low['values'] = cross_index

		if (plot == True):
			plt.plot(cross_low['index'],cross_low['values'], 'o',c='g')
    
	elif intersection_low.geom_type == 'Point':
		cross = pd.DataFrame(*intersection_low.xy)
		cross_index = cross.index.to_numpy()
		cross_low = pd.DataFrame(cross.values.astype(int),columns=['index'])
		cross_low['index'] = cross.values.astype(int)
		cross_low['values'] = cross_index

		if (plot == True):
			plt.plot(cross_low['index'],cross_low['values'], 'o',c='g')

	#///////////////////////////////////////////////////////////////////////////////////

	#****************** Finding High Period Cross With Zero Line ************************
	first_line = LineString(np.column_stack((x[(High_Period-1):], CCI_High.dropna())))
	second_line = LineString(np.column_stack((x[(High_Period-1):], zero_line[(High_Period-1):])))

	intersection_high = first_line.intersection(second_line)

	if intersection_high.geom_type == 'MultiPoint':
		cross = pd.DataFrame(*LineString(intersection_high).xy)
		cross_index = cross.index.to_numpy()
		cross_high = pd.DataFrame(cross.values.astype(int),columns=['index'])
		cross_high['index'] = cross.values.astype(int)
		cross_high['values'] = cross_index

		if (plot == True):
			plt.plot(cross_high['index'],cross_high['values'], 'o',c='g')
    
	elif intersection_high.geom_type == 'Point':
		cross = pd.DataFrame(*intersection_high.xy)
		cross_index = cross.index.to_numpy()
		cross_high = pd.DataFrame(cross.values.astype(int),columns=['index'])
		cross_high['index'] = cross.values.astype(int)
		cross_high['values'] = cross_index

		if (plot == True):
			plt.plot(cross_high['index'],cross_high['values'], 'o',c='g')

	#///////////////////////////////////////////////////////////////////////////////////

	#print('high = ',cross_high)
	#print('low = ',cross_low)

	i = 0
	finding_points = pd.DataFrame(np.zeros(len(CCI_Low)))
	finding_points['index'] = np.nan

	for elm in cross_high.index:
		points = cross_low['index'][np.where(abs(cross_low['index'] - cross_high['index'][elm]) <= distance_lines)[0]]
		for mle in points:
			finding_points['index'][i] = mle
			i += 1

	finding_points = finding_points.dropna(inplace = False)
	finding_points = finding_points.drop(columns = 0)
	finding_points = finding_points.sort_values(by = ['index'])
	finding_points = finding_points.drop_duplicates(keep = 'last', inplace = False)
	finding_points = finding_points.reset_index(drop=True)

	if ((mode == 'optimize') | (mode == 'online')):
		signal_buy = pd.DataFrame(np.zeros(len(finding_points)))
		signal_buy['signal'] = np.nan
		signal_buy['index'] = np.nan
		signal_buy['ramp_low'] = np.nan
		signal_buy['ramp_high'] = np.nan
		signal_buy['diff_min_max_cci'] = np.nan
		signal_buy['diff_min_max_candle'] = np.nan
		if (mode == 'optimize'):
			if (name_stp_minmax == True):
				signal_buy['tp_min_max_index'] = np.nan
				signal_buy['tp_min_max'] = np.nan
				signal_buy['st_min_max_index'] = np.nan
				signal_buy['st_min_max'] = np.nan
				signal_buy['flag_min_max'] = np.nan
			if (name_stp_pr == True):
				signal_buy['tp_pr_index'] = np.nan
				signal_buy['tp_pr'] = np.nan
				signal_buy['st_pr_index'] = np.nan
				signal_buy['st_pr'] = np.nan
				signal_buy['flag_pr'] = np.nan
				signal_buy['diff_pr_top'] = np.nan
				signal_buy['diff_pr_down'] = np.nan

		signal_sell = pd.DataFrame(np.zeros(len(finding_points)))
		signal_sell['signal'] = np.nan
		signal_sell['index'] = np.nan
		signal_sell['ramp_low'] = np.nan
		signal_sell['ramp_high'] = np.nan
		signal_sell['diff_min_max_cci'] = np.nan
		signal_sell['diff_min_max_candle'] = np.nan
		if (mode == 'optimize'):
			if (name_stp_minmax == True):
				signal_sell['tp_min_max_index'] = np.nan
				signal_sell['tp_min_max'] = np.nan
				signal_sell['st_min_max_index'] = np.nan
				signal_sell['st_min_max'] = np.nan
				signal_sell['flag_min_max'] = np.nan

			if (name_stp_pr == True):
				signal_sell['tp_pr_index'] = np.nan
				signal_sell['tp_pr'] = np.nan
				signal_sell['st_pr_index'] = np.nan
				signal_sell['st_pr'] = np.nan
				signal_sell['flag_pr'] = np.nan
				signal_sell['diff_pr_top'] = np.nan
				signal_sell['diff_pr_down'] = np.nan

	buy_counter = 0
	sell_counter = 0

	for elm in finding_points.index:

		if (plot == True):
			plt.axvline(x=finding_points['index'][elm],c='r')

		if (elm-2 < 0): continue
		#******************** Buy Signal Finding *********************************
		if ((CCI_Low[finding_points['index'][elm]] > CCI_Low[finding_points['index'][elm]-1]) &
			(CCI_High[finding_points['index'][elm]] > CCI_High[finding_points['index'][elm]-1])):

			signal_buy['signal'][buy_counter] = 'buy'
			signal_buy['index'][buy_counter] = finding_points['index'][elm]
			signal_buy['ramp_low'][buy_counter] = CCI_Low[finding_points['index'][elm]] - CCI_Low[finding_points['index'][elm]-1]
			signal_buy['ramp_high'][buy_counter] = CCI_High[finding_points['index'][elm]] - CCI_High[finding_points['index'][elm]-1]
			signal_buy['diff_min_max_cci'][buy_counter] = ((np.max(CCI_High[int(finding_points['index'][elm-2]):int(finding_points['index'][elm])]) - CCI_High[int(finding_points['index'][elm])])/CCI_High[int(finding_points['index'][elm])])*100
			signal_buy['diff_min_max_candle'][buy_counter] = ((np.max(dataset[symbol]['high'][int(finding_points['index'][elm-2]):int(finding_points['index'][elm])]) - dataset[symbol]['high'][int(finding_points['index'][elm])])/dataset[symbol]['high'][int(finding_points['index'][elm])])*100


			#Calculate porfits
			#must read protect and resist from protect resist function
			if (mode == 'optimize'):

				if (name_stp_minmax == True):
					#Calculate With Min Max Diff From MACD:
					if ((len(np.where((((dataset[symbol]['high'][int(finding_points['index'][elm]):-1]-dataset[symbol]['high'][int(finding_points['index'][elm])])/dataset[symbol]['high'][int(finding_points['index'][elm])]).values*100) >= signal_buy['diff_min_max_candle'][buy_counter])[0]) - 1) > 1):
						signal_buy['tp_min_max_index'][buy_counter] = int(finding_points['index'][elm]) + np.min(np.where((((dataset[symbol]['high'][int(finding_points['index'][elm]):-1]-dataset[symbol]['high'][int(finding_points['index'][elm])])/dataset[symbol]['high'][int(finding_points['index'][elm])]).values*100) >= signal_buy['diff_min_max_candle'][buy_counter])[0])
						signal_buy['tp_min_max'][buy_counter] = ((dataset[symbol]['high'][signal_buy['tp_min_max_index'][buy_counter]] - dataset[symbol]['high'][int(finding_points['index'][elm])])/dataset[symbol]['high'][int(finding_points['index'][elm])]) * 100
					else:
						signal_buy['tp_min_max_index'][buy_counter] = -1
						signal_buy['tp_min_max'][buy_counter] = 0

					if ((len(np.where((((dataset[symbol]['low'][int(finding_points['index'][elm]):-1]).values) <= (dataset[symbol]['low'][int(finding_points['index'][elm])] * 0.9994)))[0])-1) > 1):
						signal_buy['st_min_max_index'][buy_counter] = int(finding_points['index'][elm]) + np.min(np.where((((dataset[symbol]['low'][int(finding_points['index'][elm]):-1]).values) <= (dataset[symbol]['low'][int(finding_points['index'][elm])] * 0.9994)))[0])
						signal_buy['st_min_max'][buy_counter] = ((dataset[symbol]['low'][int(finding_points['index'][elm])] - dataset[symbol]['low'][signal_buy['st_min_max_index'][buy_counter]])/dataset[symbol]['low'][int(finding_points['index'][elm])]) * 100
					else:
						signal_buy['st_min_max_index'][buy_counter] = -1
						signal_buy['st_min_max'][buy_counter] = 0

					if (signal_buy['st_min_max_index'][buy_counter] < signal_buy['tp_min_max_index'][buy_counter])&(signal_buy['st_min_max_index'][buy_counter] != -1):
						signal_buy['flag_min_max'][buy_counter] = 'st'
						signal_buy['tp_min_max'][buy_counter] = ((np.max(dataset[symbol]['high'][int(finding_points['index'][elm]):int(signal_buy['st_min_max_index'][buy_counter])]) - dataset[symbol]['high'][int(finding_points['index'][elm])])/dataset[symbol]['high'][int(finding_points['index'][elm])]) * 100
					else:
						
						if (signal_buy['tp_min_max_index'][buy_counter] != -1):
							signal_buy['flag_min_max'][buy_counter] = 'tp'
							signal_buy['st_min_max'][buy_counter] = ((dataset[symbol]['low'][int(finding_points['index'][elm])] - np.min(dataset[symbol]['low'][int(finding_points['index'][elm]):int(signal_buy['tp_min_max_index'][buy_counter])]))/dataset[symbol]['low'][int(finding_points['index'][elm])]) * 100

						if (signal_buy['tp_min_max_index'][buy_counter] == -1) & (signal_buy['st_min_max_index'][buy_counter] != -1):
							signal_buy['flag_min_max'][buy_counter] = 'st'
							signal_buy['tp_min_max'][buy_counter] = ((np.max(dataset[symbol]['high'][int(finding_points['index'][elm]):int(signal_buy['st_min_max_index'][buy_counter])]) - dataset[symbol]['high'][int(finding_points['index'][elm])])/dataset[symbol]['high'][int(finding_points['index'][elm])]) * 100
					#///////////////////////////////////////////////////
				if (name_stp_pr == True):
					#Calculate ST and TP With Protect Resist Function
					dataset_pr_5M = pd.DataFrame()
					dataset_pr_15M = pd.DataFrame()
					cut_first = 0
					if (int(finding_points['index'][elm]) > 2000):
						cut_first = int(finding_points['index'][elm]) - 2000
					dataset_pr_5M['low'] = dataset[symbol]['low'][cut_first:int(finding_points['index'][elm])].reset_index(drop=True)
					dataset_pr_5M['high'] = dataset[symbol]['high'][cut_first:int(finding_points['index'][elm])].reset_index(drop=True)
					dataset_pr_5M['close'] = dataset[symbol]['close'][cut_first:int(finding_points['index'][elm])].reset_index(drop=True)
					dataset_pr_5M['open'] = dataset[symbol]['open'][cut_first:int(finding_points['index'][elm])].reset_index(drop=True)

					dataset_pr_15M['low'] = dataset_15M[symbol]['low'][int(cut_first/3):int(int(finding_points['index'][elm])/3)].reset_index(drop=True)
					dataset_pr_15M['high'] = dataset_15M[symbol]['high'][int(cut_first/3):int(int(finding_points['index'][elm])/3)].reset_index(drop=True)
					dataset_pr_15M['close'] = dataset_15M[symbol]['close'][int(cut_first/3):int(int(finding_points['index'][elm])/3)].reset_index(drop=True)
					dataset_pr_15M['open'] = dataset_15M[symbol]['open'][int(cut_first/3):int(int(finding_points['index'][elm])/3)].reset_index(drop=True)

					res_pro = pd.DataFrame()
					
					try:
						res_pro = protect_resist(T_5M=True,T_15M=True,T_1H=False,T_4H=False,T_1D=False,dataset_5M=dataset_pr_5M,dataset_15M=dataset_pr_15M,dataset_1H=dataset_pr_15M,dataset_4H=dataset_pr_5M,dataset_1D=dataset_pr_5M,plot=False)
					except:
						res_pro['high'] = 'nan'
						res_pro['low'] = 'nan'

					if (res_pro.empty == False):
						signal_buy['diff_pr_top'][buy_counter] = (((res_pro['high'][0] * 0.9994) - dataset[symbol]['high'][int(finding_points['index'][elm])])/dataset[symbol]['high'][int(finding_points['index'][elm])]) * 100
						signal_buy['diff_pr_down'][buy_counter] = ((dataset[symbol]['low'][int(finding_points['index'][elm])] - (res_pro['low'][2] * 0.9994))/dataset[symbol]['low'][int(finding_points['index'][elm])]) * 100

						if ((len(np.where(((dataset[symbol]['high'][int(finding_points['index'][elm]):-1].values) >= (res_pro['high'][0] * 0.9994)))[0]) - 1) > 1):
							signal_buy['tp_pr_index'][buy_counter] = int(finding_points['index'][elm]) + np.min(np.where(((dataset[symbol]['high'][int(finding_points['index'][elm]):-1].values) >= (res_pro['high'][0] * 0.9994)))[0])
							signal_buy['tp_pr'][buy_counter] = ((dataset[symbol]['high'][signal_buy['tp_pr_index'][buy_counter]] - dataset[symbol]['high'][int(finding_points['index'][elm])])/dataset[symbol]['high'][int(finding_points['index'][elm])]) * 100
						else:
							signal_buy['tp_pr_index'][buy_counter] = -1
							signal_buy['tp_pr'][buy_counter] = 0

						if ((len(np.where((((dataset[symbol]['low'][int(finding_points['index'][elm]):-1]).values) <= (res_pro['low'][2] * 0.9994)))[0])-1) > 1):
							signal_buy['st_pr_index'][buy_counter] = int(finding_points['index'][elm]) + np.min(np.where((((dataset[symbol]['low'][int(finding_points['index'][elm]):-1]).values) <= (res_pro['low'][2] * 0.9994)))[0])
							signal_buy['st_pr'][buy_counter] = ((dataset[symbol]['low'][int(finding_points['index'][elm])] - dataset[symbol]['low'][signal_buy['st_pr_index'][buy_counter]])/dataset[symbol]['low'][int(finding_points['index'][elm])]) * 100
						else:
							signal_buy['st_pr_index'][buy_counter] = -1
							signal_buy['st_pr'][buy_counter] = 0

						if ((signal_buy['st_pr_index'][buy_counter] < signal_buy['tp_pr_index'][buy_counter]) & (signal_buy['st_pr_index'][buy_counter] != -1)):
							signal_buy['flag_pr'][buy_counter] = 'st'
							signal_buy['tp_pr'][buy_counter] = ((np.max(dataset[symbol]['high'][int(finding_points['index'][elm]):int(signal_buy['st_pr_index'][buy_counter])]) - dataset[symbol]['high'][int(finding_points['index'][elm])])/dataset[symbol]['high'][int(finding_points['index'][elm])]) * 100
						else:
							if (signal_buy['tp_pr_index'][buy_counter] != -1):
								signal_buy['flag_pr'][buy_counter] = 'tp'
								signal_buy['st_pr'][buy_counter] = ((dataset[symbol]['low'][int(finding_points['index'][elm])] - np.min(dataset[symbol]['low'][int(finding_points['index'][elm]):int(signal_buy['tp_pr_index'][buy_counter])]))/dataset[symbol]['low'][int(finding_points['index'][elm])]) * 100

							if (signal_buy['tp_pr_index'][buy_counter] == -1) & (signal_buy['st_pr_index'][buy_counter] != -1):
								signal_buy['flag_pr'][buy_counter] = 'st'
								signal_buy['tp_pr'][buy_counter] = ((np.max(dataset[symbol]['high'][int(finding_points['index'][elm]):int(signal_buy['st_pr_index'][buy_counter])]) - dataset[symbol]['high'][int(finding_points['index'][elm])])/dataset[symbol]['high'][int(finding_points['index'][elm])]) * 100
					else:
						signal_buy['tp_pr_index'][buy_counter] = -1
						signal_buy['tp_pr'][buy_counter] = 0
						signal_buy['st_pr_index'][buy_counter] = -1
						signal_buy['st_pr'][buy_counter] = 0
						signal_buy['flag_pr'][buy_counter] = 'no_flag'
					#///////////////////////////////////////////////////

			buy_counter += 1
		#///////////////////////////////////////////////////////////////////////

		#************************ Sell Signal Finding *****************************
		if ((CCI_Low[finding_points['index'][elm]] < CCI_Low[finding_points['index'][elm]-1]) &
			(CCI_High[finding_points['index'][elm]] < CCI_High[finding_points['index'][elm]-1])):

			signal_sell['signal'][sell_counter] = 'sell'
			signal_sell['index'][sell_counter] = finding_points['index'][elm]
			signal_sell['ramp_low'][sell_counter] = CCI_Low[finding_points['index'][elm]] - CCI_Low[finding_points['index'][elm]-1]
			signal_sell['ramp_high'][sell_counter] = CCI_High[finding_points['index'][elm]] - CCI_High[finding_points['index'][elm]-1]
			signal_sell['diff_min_max_cci'][sell_counter] = ((CCI_High[int(finding_points['index'][elm])] - np.min(CCI_High[int(finding_points['index'][elm-2]):int(finding_points['index'][elm])]))/CCI_High[int(finding_points['index'][elm])]) * 100
			signal_sell['diff_min_max_candle'][sell_counter] = ((dataset[symbol]['low'][int(finding_points['index'][elm])] - np.min(dataset[symbol]['low'][int(finding_points['index'][elm-2]):int(finding_points['index'][elm])]))/dataset[symbol]['low'][int(finding_points['index'][elm])]) * 100

			#Calculate porfits
			#must read protect and resist from protect resist function
			if (mode == 'optimize'):

				if (name_stp_minmax == True):
					#Calculate With Min Max Diff From MACD:

					if ((len(np.where((((((dataset[symbol]['low'][int(finding_points['index'][elm])] - dataset[symbol]['low'][int(finding_points['index'][elm]):-1])/dataset[symbol]['low'][int(finding_points['index'][elm])]).values) * 100) >= (signal_sell['diff_min_max_candle'][sell_counter])))[0]) - 1) > 1):
						signal_sell['tp_min_max_index'][sell_counter] = int(finding_points['index'][elm]) + np.min(np.where((((((dataset[symbol]['low'][int(finding_points['index'][elm])] - dataset[symbol]['low'][int(finding_points['index'][elm]):-1])/dataset[symbol]['low'][int(finding_points['index'][elm])]).values) * 100) >= (signal_sell['diff_min_max_candle'][sell_counter])))[0])
						signal_sell['tp_min_max'][sell_counter] = ((dataset[symbol]['low'][int(finding_points['index'][elm])] - dataset[symbol]['low'][signal_sell['tp_min_max_index'][sell_counter]])/dataset[symbol]['low'][int(finding_points['index'][elm])]) * 100
					else:
						signal_sell['tp_min_max_index'][sell_counter] = -1
						signal_sell['tp_min_max'][sell_counter] = 0

					if ((len(np.where((((dataset[symbol]['high'][int(finding_points['index'][elm]):-1]).values) >= (dataset[symbol]['high'][int(finding_points['index'][elm])] * 1.0006)))[0])-1) > 1):
						signal_sell['st_min_max_index'][sell_counter] = int(finding_points['index'][elm]) + np.min(np.where((((dataset[symbol]['high'][int(finding_points['index'][elm]):-1]).values) >= (dataset[symbol]['high'][int(finding_points['index'][elm])] * 1.0006)))[0])
						signal_sell['st_min_max'][sell_counter] = ((dataset[symbol]['high'][signal_sell['st_min_max_index'][sell_counter]] - dataset[symbol]['high'][int(finding_points['index'][elm])])/dataset[symbol]['high'][int(finding_points['index'][elm])]) * 100
					else:
						signal_sell['st_min_max_index'][sell_counter] = -1
						signal_sell['st_min_max'][sell_counter] = 0

					if ((signal_sell['st_min_max_index'][sell_counter] < signal_sell['tp_min_max_index'][sell_counter]) & (signal_sell['st_min_max_index'][sell_counter] != -1)):
						signal_sell['flag_min_max'][sell_counter] = 'st'
						signal_sell['tp_min_max'][sell_counter] = ((dataset[symbol]['low'][int(finding_points['index'][elm])] - np.min(dataset[symbol]['low'][int(finding_points['index'][elm]):int(signal_sell['st_min_max_index'][sell_counter])]))/dataset[symbol]['low'][int(finding_points['index'][elm])]) * 100
					else:
						
						if (signal_sell['tp_min_max_index'][sell_counter] != -1):
							signal_sell['flag_min_max'][sell_counter] = 'tp'
							signal_sell['st_min_max'][sell_counter] = ((np.max(dataset[symbol]['high'][int(finding_points['index'][elm]):int(signal_sell['tp_min_max_index'][sell_counter])]) - dataset[symbol]['high'][int(finding_points['index'][elm])])/dataset[symbol]['high'][int(finding_points['index'][elm])]) * 100

						if (signal_sell['tp_min_max_index'][sell_counter] == -1) & (signal_sell['st_min_max_index'][sell_counter] != -1):
							signal_sell['flag_min_max'][sell_counter] = 'st'
							signal_sell['tp_min_max'][sell_counter] = ((dataset[symbol]['low'][int(finding_points['index'][elm])] - np.min(dataset[symbol]['low'][int(finding_points['index'][elm]):int(signal_sell['st_min_max_index'][sell_counter])]))/dataset[symbol]['low'][int(finding_points['index'][elm])]) * 100
					#///////////////////////////////////////////////////
				if (name_stp_pr == True):
					#Calculate ST and TP With Protect Resist Function
					dataset_pr_5M = pd.DataFrame()
					dataset_pr_15M = pd.DataFrame()
					cut_first = 0
					if (int(finding_points['index'][elm]) > 2000):
						cut_first = int(finding_points['index'][elm]) - 2000
					dataset_pr_5M['low'] = dataset[symbol]['low'][cut_first:int(finding_points['index'][elm])].reset_index(drop=True)
					dataset_pr_5M['high'] = dataset[symbol]['high'][cut_first:int(finding_points['index'][elm])].reset_index(drop=True)
					dataset_pr_5M['close'] = dataset[symbol]['close'][cut_first:int(finding_points['index'][elm])].reset_index(drop=True)
					dataset_pr_5M['open'] = dataset[symbol]['open'][cut_first:int(finding_points['index'][elm])].reset_index(drop=True)

					dataset_pr_15M['low'] = dataset_15M[symbol]['low'][int(cut_first/3):int(int(finding_points['index'][elm])/3)].reset_index(drop=True)
					dataset_pr_15M['high'] = dataset_15M[symbol]['high'][int(cut_first/3):int(int(finding_points['index'][elm])/3)].reset_index(drop=True)
					dataset_pr_15M['close'] = dataset_15M[symbol]['close'][int(cut_first/3):int(int(finding_points['index'][elm])/3)].reset_index(drop=True)
					dataset_pr_15M['open'] = dataset_15M[symbol]['open'][int(cut_first/3):int(int(finding_points['index'][elm])/3)].reset_index(drop=True)

					res_pro = pd.DataFrame()
					
					try:
						res_pro = protect_resist(T_5M=True,T_15M=True,T_1H=False,T_4H=False,T_1D=False,dataset_5M=dataset_pr_5M,dataset_15M=dataset_pr_15M,dataset_1H=dataset_pr_15M,dataset_4H=dataset_pr_5M,dataset_1D=dataset_pr_5M,plot=False)
					except:
						res_pro['high'] = 'nan'
						res_pro['low'] = 'nan'

					if (res_pro.empty == False):
						signal_sell['diff_pr_top'][sell_counter] = (((res_pro['high'][0] * 1.0006) - dataset[symbol]['high'][int(finding_points['index'][elm])])/dataset[symbol]['high'][int(finding_points['index'][elm])]) * 100
						signal_sell['diff_pr_down'][sell_counter] = ((dataset[symbol]['low'][int(finding_points['index'][elm])] - (res_pro['low'][0] * 1.0006))/dataset[symbol]['low'][int(finding_points['index'][elm])]) * 100

						if ((len(np.where(((dataset[symbol]['low'][int(finding_points['index'][elm]):-1].values) <= (res_pro['low'][0] * 1.0006)))[0]) - 1) > 1):
							signal_sell['tp_pr_index'][sell_counter] = int(finding_points['index'][elm]) + np.min(np.where(((dataset[symbol]['low'][int(finding_points['index'][elm]):-1].values) <= (res_pro['low'][0] * 1.0006)))[0])
							signal_sell['tp_pr'][sell_counter] = ((dataset[symbol]['low'][int(finding_points['index'][elm])] - dataset[symbol]['low'][signal_sell['tp_pr_index'][sell_counter]])/dataset[symbol]['low'][int(finding_points['index'][elm])]) * 100
						else:
							signal_sell['tp_pr_index'][sell_counter] = -1
							signal_sell['tp_pr'][sell_counter] = 0

						if ((len(np.where((((dataset[symbol]['high'][int(finding_points['index'][elm]):-1]).values) >= (res_pro['high'][0] * 1.0006)))[0])-1) > 1):
							signal_sell['st_pr_index'][sell_counter] = int(finding_points['index'][elm]) + np.min(np.where((((dataset[symbol]['high'][int(finding_points['index'][elm]):-1]).values) >= (res_pro['high'][0] * 1.0006)))[0])
							signal_sell['st_pr'][sell_counter] = ((dataset[symbol]['high'][signal_sell['st_pr_index'][sell_counter]] - dataset[symbol]['high'][int(finding_points['index'][elm])])/dataset[symbol]['high'][int(finding_points['index'][elm])]) * 100
						else:
							signal_sell['st_pr_index'][sell_counter] = -1
							signal_sell['st_pr'][sell_counter] = 0

						if (signal_sell['st_pr_index'][sell_counter] < signal_sell['tp_pr_index'][sell_counter])&(signal_sell['st_pr_index'][sell_counter] != -1):
							signal_sell['flag_pr'][sell_counter] = 'st'
							signal_sell['tp_pr'][sell_counter] = ((dataset[symbol]['low'][int(finding_points['index'][elm])] - np.min(dataset[symbol]['low'][int(finding_points['index'][elm]):int(signal_sell['st_pr_index'][sell_counter])]))/dataset[symbol]['low'][int(finding_points['index'][elm])]) * 100
						else:
							
							if (signal_sell['tp_pr_index'][sell_counter] != -1):
								signal_sell['flag_pr'][sell_counter] = 'tp'
								signal_sell['st_pr'][sell_counter] = ((np.max(dataset[symbol]['high'][int(finding_points['index'][elm]):int(signal_sell['tp_pr_index'][sell_counter])]) - dataset[symbol]['high'][int(finding_points['index'][elm])])/dataset[symbol]['high'][int(finding_points['index'][elm])]) * 100
							
							if (signal_sell['tp_pr_index'][sell_counter] == -1) & (signal_sell['st_pr_index'][sell_counter] != -1):
								signal_sell['flag_pr'][sell_counter] = 'st'
								signal_sell['tp_pr'][sell_counter] = ((dataset[symbol]['low'][int(finding_points['index'][elm])] - np.min(dataset[symbol]['low'][int(finding_points['index'][elm]):int(signal_sell['st_pr_index'][sell_counter])]))/dataset[symbol]['low'][int(finding_points['index'][elm])]) * 100
					else:
						signal_sell['tp_pr_index'][sell_counter] = -1
						signal_sell['tp_pr'][sell_counter] = 0
						signal_sell['st_pr_index'][sell_counter] = -1
						signal_sell['st_pr'][sell_counter] = 0
						signal_sell['flag_pr'][sell_counter] = 'no_flag'
					#///////////////////////////////////////////////////
					#print('tp = ',signal_sell['tp_pr'][sell_counter])
					#print('tp index = ',signal_sell['tp_pr_index'][sell_counter])
					#print('st = ',signal_sell['st_pr'][sell_counter])
					#print('st index = ',signal_sell['st_pr_index'][sell_counter])
					#print('flag_pr = ',signal_sell['flag_pr'][sell_counter])

			sell_counter += 1

		#////////////////////////////////////////////////////////////////////////////
	
	signal_buy = signal_buy.drop(columns=0)
	signal_buy = signal_buy.dropna()
	signal_buy = signal_buy.sort_values(by = ['index'])
	signal_buy = signal_buy.reset_index(drop=True)

	signal_sell = signal_sell.drop(columns=0)
	signal_sell = signal_sell.dropna()
	signal_sell = signal_sell.sort_values(by = ['index'])
	signal_sell = signal_sell.reset_index(drop=True)


	if (plot == True):
		plt.plot(CCI_Low.index, CCI_Low,c='b')
		plt.plot(CCI_High.index, CCI_High,c='r')
		plt.show()

	return signal_buy, signal_sell
#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#**************************************************** Find Best Intervals *******************************************************
def Find_Best_intervals(signals,apply_to, min_tp=0.1, max_st=0.1, name_stp='flag_min_max', alpha=0.1):

	if (name_stp == 'flag_min_max'):
		signal_good = signals.drop(np.where((signals[name_stp]=='st')|
			(signals['st_min_max']>max_st)|
			(signals['tp_min_max']<min_tp))[0])

		if (signal_good.empty == True): 
			best_signals_interval = pd.DataFrame()
			best_signals_interval['interval'] = [0,0,0]
			best_signals_interval['power'] = [0,0,0]
			best_signals_interval['alpha'] = [alpha,alpha,alpha]
			best_signals_interval[name_stp] = [name_stp,name_stp,name_stp]
			return best_signals_interval

	if (name_stp == 'flag_pr'):
		signal_good = signals.drop(np.where((signals[name_stp]=='st')|
			(signals['st_pr']>max_st)|
			(signals['tp_pr']<min_tp))[0])
			#(signals['diff_pr_down']>max_st)

		if (signal_good.empty == True): 
			best_signals_interval = pd.DataFrame()
			best_signals_interval['interval'] = [0,0,0]
			best_signals_interval['power'] = [0,0,0]
			best_signals_interval['alpha'] = [alpha,alpha,alpha]
			best_signals_interval[name_stp] = [name_stp,name_stp,name_stp]
			return best_signals_interval

	signal_good = signal_good.sort_values(by = ['index'])
	signal_good = signal_good.reset_index(drop=True)

	#timeout = time.time() + 20  # timeout_break Sec from now
	while True:

		if (len(signal_good[apply_to].to_numpy()) - 1) >= 10:
			n_clusters = 5
		else:
			n_clusters = len(signal_good[apply_to].to_numpy()) - 1
			if (n_clusters <= 0):
				best_signals_interval = pd.DataFrame()
				best_signals_interval['interval'] = [0,0,0]
				best_signals_interval['power'] = [0,0,0]
				best_signals_interval['alpha'] = [alpha,alpha,alpha]
				best_signals_interval[name_stp] = [name_stp,name_stp,name_stp]
				return best_signals_interval

		kmeans = KMeans(n_clusters=n_clusters, random_state=0,init='k-means++',n_init=5,max_iter=5)
		#Model Fitting
		kmeans = kmeans.fit(signal_good[apply_to].to_numpy().reshape(-1,1))

		Y = kmeans.cluster_centers_
		Power = kmeans.labels_
		Power = np.bincount(Power)

		if ((len(Y) != len(Power))):
			timeout = time.time() + timeout_break
			continue
		if ((len(Y) == len(Power))): break

	signal_final = pd.DataFrame(Y, columns=['Y'])
	signal_final['power'] = Power
	signal_final = signal_final.sort_values(by = ['Y'])

	#Fitting Model Finding ****************************
	data_X = np.zeros(np.sum(signal_final['power']))

	j = 0
	z = 0
	for elm in signal_final['Y']:
		k = 0
		while k < signal_final['power'].to_numpy()[j]:
			data_X[z] = elm
			k += 1
			z += 1
		j += 1

	data_X = np.sort(data_X)

	distributions = ['foldnorm','dweibull','expon','nakagami','norm']

	#************************************ Finding Sell's ****************************

	while True:
		
		try:
			f = Fitter(data = data_X, xmin=np.min(data_X), xmax=np.max(data_X), bins = len(signal_final['Y']), distributions = distributions, timeout=30, density=True)
	
			f.fit(amp=1, progress=False, n_jobs=-1)
	
			#distributions=['foldnorm','dweibull','rayleigh','expon','nakagami','norm']
			#f.summary(Nbest=5, lw=2, plot=True, method='sumsquare_error', clf=True)
			#print(f.get_best(method = 'sumsquare_error').items())
	
			items = list(f.get_best(method = 'sumsquare_error').items())
			dist_name = items[0][0]
			dist_parameters = items[0][1]
		except:
			best_signals_interval = pd.DataFrame()
			best_signals_interval['interval'] = [0,0,0]
			best_signals_interval['power'] = [0,0,0]
			best_signals_interval['alpha'] = [alpha,alpha,alpha]
			best_signals_interval[name_stp] = [name_stp,name_stp,name_stp]
			return best_signals_interval

		if dist_name == 'foldnorm':
			Y = f.fitted_pdf['foldnorm']
			Y = foldnorm.pdf(x=data_X, c=dist_parameters['c'], loc=dist_parameters['loc'], scale=dist_parameters['scale'])
			Extereme = foldnorm.interval(alpha=alpha, c=dist_parameters['c'], loc=dist_parameters['loc'], scale=dist_parameters['scale'])
			Upper_Line = Extereme[1]
			Lower_Line = Extereme[0]
			Mid_Line = np.array(dist_parameters['loc'])
			Power_Upper_Line = (signal_final['power'][kmeans.predict(Mid_Line.reshape(1,-1))].to_numpy())/np.max(signal_final['power'])
			Power_Lower_Line =(signal_final['power'][kmeans.predict(Mid_Line.reshape(1,-1))].to_numpy())/np.max(signal_final['power'])
			Power_Mid_Line = (signal_final['power'][kmeans.predict(Mid_Line.reshape(1,-1))].to_numpy())/np.max(signal_final['power'])
	
		elif dist_name == 'dweibull':
			Y = f.fitted_pdf['dweibull']
			Y = dweibull.pdf(x=data_X, c=dist_parameters['c'], loc=dist_parameters['loc'], scale=dist_parameters['scale'])
			Extereme = dweibull.interval(alpha=alpha, c=dist_parameters['c'], loc=dist_parameters['loc'], scale=dist_parameters['scale'])
			Upper_Line = Extereme[1]
			Lower_Line = Extereme[0]
			Mid_Line = np.array(dist_parameters['loc'])
			Power_Upper_Line = (signal_final['power'][kmeans.predict(Mid_Line.reshape(1,-1))].to_numpy())/np.max(signal_final['power'])
			Power_Lower_Line =(signal_final['power'][kmeans.predict(Mid_Line.reshape(1,-1))].to_numpy())/np.max(signal_final['power'])
			Power_Mid_Line = (signal_final['power'][kmeans.predict(Mid_Line.reshape(1,-1))].to_numpy())/np.max(signal_final['power'])
		
		elif dist_name == 'rayleigh':
			Y = f.fitted_pdf['rayleigh']
			Y = rayleigh.pdf(x=data_X, loc=dist_parameters['loc'], scale=dist_parameters['scale'])
			Extereme = rayleigh.interval(alpha=alpha, loc=dist_parameters['loc'], scale=dist_parameters['scale'])
			Upper_Line = Extereme[1]
			Lower_Line = Extereme[0]
			Mid_Line = np.array(dist_parameters['loc'])
			Power_Upper_Line = (signal_final['power'][kmeans.predict(Mid_Line.reshape(1,-1))].to_numpy())/np.max(signal_final['power'])
			Power_Lower_Line =(signal_final['power'][kmeans.predict(Mid_Line.reshape(1,-1))].to_numpy())/np.max(signal_final['power'])
			Power_Mid_Line = (signal_final['power'][kmeans.predict(Mid_Line.reshape(1,-1))].to_numpy())/np.max(signal_final['power'])
	
		elif dist_name == 'expon':
			Y = f.fitted_pdf['expon']
			Y = expon.pdf(x=data_X, loc=dist_parameters['loc'], scale=dist_parameters['scale'])
			Extereme = expon.interval(alpha=alpha, loc=dist_parameters['loc'], scale=dist_parameters['scale'])
			Upper_Line = Extereme[1]
			Lower_Line = Extereme[0]
			Mid_Line = np.array(dist_parameters['loc'])
			Power_Upper_Line = (signal_final['power'][kmeans.predict(Mid_Line.reshape(1,-1))].to_numpy())/np.max(signal_final['power'])
			Power_Lower_Line =(signal_final['power'][kmeans.predict(Mid_Line.reshape(1,-1))].to_numpy())/np.max(signal_final['power'])
			Power_Mid_Line = (signal_final['power'][kmeans.predict(Mid_Line.reshape(1,-1))].to_numpy())/np.max(signal_final['power'])
	
		elif dist_name == 'nakagami':
			Y = f.fitted_pdf['nakagami']
			Y = nakagami.pdf(x=data_X, nu=dist_parameters['nu'], loc=dist_parameters['loc'], scale=dist_parameters['scale'])
			Extereme = nakagami.interval(alpha=alpha, nu=dist_parameters['nu'], loc=dist_parameters['loc'], scale=dist_parameters['scale'])
			Upper_Line = Extereme[1]
			Lower_Line = Extereme[0]
			Mid_Line = np.array(dist_parameters['loc'])
			Power_Upper_Line = (signal_final['power'][kmeans.predict(Mid_Line.reshape(1,-1))].to_numpy())/np.max(signal_final['power'])
			Power_Lower_Line =(signal_final['power'][kmeans.predict(Mid_Line.reshape(1,-1))].to_numpy())/np.max(signal_final['power'])
			Power_Mid_Line = (signal_final['power'][kmeans.predict(Mid_Line.reshape(1,-1))].to_numpy())/np.max(signal_final['power'])
	
		elif dist_name == 'norm':
			Y = f.fitted_pdf['norm']
			Y = norm.pdf(x=data_X, loc=dist_parameters['loc'], scale=dist_parameters['scale'])
			Extereme = norm.interval(alpha=alpha, loc=dist_parameters['loc'], scale=dist_parameters['scale'])
			Upper_Line = Extereme[1]
			Lower_Line = Extereme[0]
			Mid_Line = np.array(dist_parameters['loc'])
			Power_Upper_Line = (signal_final['power'][kmeans.predict(Mid_Line.reshape(1,-1))].to_numpy())/np.max(signal_final['power'])
			Power_Lower_Line =(signal_final['power'][kmeans.predict(Mid_Line.reshape(1,-1))].to_numpy())/np.max(signal_final['power'])
			Power_Mid_Line = (signal_final['power'][kmeans.predict(Mid_Line.reshape(1,-1))].to_numpy())/np.max(signal_final['power'])

		#if (time.time() > timeout):
		#	if (distributions_sell == None):
				#return 'timeout.error'
		#		pass

		if ((Mid_Line <= Upper_Line)&(Mid_Line >= Lower_Line)&(Upper_Line>Lower_Line)): 
			break
		else:
			distributions.remove(dist_name)
			if (distributions == None):
				#return 'timeout.error'
				pass

	#//////////////////////////////////////////////////////////////////////////////////////

	best_signals_interval = pd.DataFrame()
	best_signals_interval['interval'] = [Upper_Line,Mid_Line,Lower_Line]
	best_signals_interval['power'] = [Power_Upper_Line,Power_Mid_Line,Power_Lower_Line]
	best_signals_interval['alpha'] = [alpha,alpha,alpha]
	best_signals_interval[name_stp] = [name_stp,name_stp,name_stp]

	return best_signals_interval

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#**************************************************** Tester Golden Cross Zero *******************************************************
def tester_golden_cross_zero(signal_buy,signal_sell,min_tp,max_st,alpha):

	upper = 0
	mid = 1
	lower = 2

	#*********** Methode 1 Profits With MinMax Buy:
	ramp_high_intervals_minmax_buy = Find_Best_intervals(signals=signal_buy,apply_to='ramp_high',
	 min_tp=min_tp, max_st=max_st, name_stp='flag_min_max',alpha=alpha)

	ramp_low_intervals_minmax_buy = Find_Best_intervals(signals=signal_buy,apply_to='ramp_low',
	 min_tp=min_tp, max_st=max_st, name_stp='flag_min_max',alpha=alpha)

	diff_min_max_cci_intervals_minmax_buy = Find_Best_intervals(signals=signal_buy,apply_to='diff_min_max_cci',
	 min_tp=min_tp, max_st=max_st, name_stp='flag_min_max',alpha=alpha)

	diff_min_max_candle_intervals_minmax_buy = Find_Best_intervals(signals=signal_buy,apply_to='diff_min_max_candle',
	 min_tp=min_tp, max_st=max_st, name_stp='flag_min_max',alpha=alpha)

	list_index_ok = np.where(((signal_buy['ramp_high'].to_numpy()>=ramp_high_intervals_minmax_buy['interval'][lower]))&
		((signal_buy['ramp_low'].to_numpy()>=ramp_low_intervals_minmax_buy['interval'][lower]))&
		((signal_buy['diff_min_max_cci'].to_numpy()<=diff_min_max_cci_intervals_minmax_buy['interval'][upper]))&
		((signal_buy['diff_min_max_candle'].to_numpy()<=diff_min_max_candle_intervals_minmax_buy['interval'][upper]))
		)[0]

	output_buy = pd.DataFrame()
	output_buy['mean_tp_min_max'] = [np.mean(signal_buy['tp_min_max'][list_index_ok])]
	output_buy['mean_st_min_max'] = [np.mean(signal_buy['st_min_max'][list_index_ok])]
	output_buy['max_tp_min_max'] = [np.max(signal_buy['tp_min_max'][list_index_ok])]
	output_buy['max_st_min_max'] = [np.max(signal_buy['st_min_max'][list_index_ok])]
	output_buy['sum_st_min_max'] = [np.sum(signal_buy['st_min_max'][np.where(signal_buy['flag_min_max'][list_index_ok] == 'st')[0]].to_numpy())]
	output_buy['sum_tp_min_max'] = [np.sum(signal_buy['tp_min_max'][np.where(signal_buy['flag_min_max'][list_index_ok] == 'tp')[0]].to_numpy())]

	tp_counter = 0
	st_counter = 0
	for elm in signal_buy['flag_min_max'][list_index_ok]:
		if (elm == 'tp'):
			tp_counter += 1
		if (elm == 'st'):
			st_counter += 1
	output_buy['num_tp_min_max'] = [tp_counter]
	output_buy['num_st_min_max'] = [st_counter]
	output_buy['num_trade_min_max'] = [st_counter + tp_counter]
	output_buy['ramp_low_upper_min_max'] = [ramp_low_intervals_minmax_buy['interval'][upper]]
	output_buy['ramp_low_lower_min_max'] = [ramp_low_intervals_minmax_buy['interval'][lower]]
	output_buy['ramp_high_upper_min_max'] = [ramp_high_intervals_minmax_buy['interval'][upper]]
	output_buy['ramp_high_lower_min_max'] = [ramp_high_intervals_minmax_buy['interval'][lower]]
	output_buy['diff_min_max_cci_upper_min_max'] = [diff_min_max_cci_intervals_minmax_buy['interval'][upper]]
	output_buy['diff_min_max_cci_lower_min_max'] = [diff_min_max_cci_intervals_minmax_buy['interval'][lower]]
	output_buy['diff_min_max_candle_upper_min_max'] = [diff_min_max_candle_intervals_minmax_buy['interval'][upper]]
	output_buy['diff_min_max_candle_lower_min_max'] = [diff_min_max_candle_intervals_minmax_buy['interval'][lower]]

	if output_buy['num_trade_min_max'][0] != 0:
		score_num_tp = (tp_counter/output_buy['num_trade_min_max'][0])
	else:
		score_num_tp = 0

	if output_buy['max_st_min_max'][0] != 0:
		score_max_tp = (output_buy['max_tp_min_max'][0]/output_buy['max_st_min_max'][0])
	else:
		score_max_tp = output_buy['max_tp_min_max'][0]
		if (output_buy['max_tp_min_max'][0] != 0):
			score_max_tp = output_buy['max_tp_min_max'][0] * 10

	if (output_buy['mean_st_min_max'][0] != 0):
		score_mean_tp = (output_buy['mean_tp_min_max'][0]/output_buy['mean_st_min_max'][0])
	else:
		score_mean_tp = output_buy['mean_tp_min_max'][0]
		if (output_buy['mean_tp_min_max'][0] != 0):
			score_mean_tp = output_buy['mean_tp_min_max'][0] * 10

	if (output_buy['sum_st_min_max'][0] != 0):
		score_sum_tp = (output_buy['sum_tp_min_max'][0]/output_buy['sum_st_min_max'][0])
	else:
		score_sum_tp = output_buy['sum_tp_min_max'][0]
		if (output_buy['sum_tp_min_max'][0] != 0):
			score_sum_tp = output_buy['sum_tp_min_max'][0] * 10

	output_buy['score_min_max'] = [(score_num_tp*score_max_tp*score_mean_tp*score_sum_tp)]

	#///////////////////////////////////////////////

	#*********** Methode 1 Profits With MinMax Sell:
	ramp_high_intervals_minmax_sell = Find_Best_intervals(signals=signal_sell,apply_to='ramp_high',
	 min_tp=min_tp, max_st=max_st, name_stp='flag_min_max',alpha=alpha)

	ramp_low_intervals_minmax_sell = Find_Best_intervals(signals=signal_sell,apply_to='ramp_low',
	 min_tp=min_tp, max_st=max_st, name_stp='flag_min_max',alpha=alpha)

	diff_min_max_cci_intervals_minmax_sell = Find_Best_intervals(signals=signal_sell,apply_to='diff_min_max_cci',
	 min_tp=min_tp, max_st=max_st, name_stp='flag_min_max',alpha=alpha)

	diff_min_max_candle_intervals_minmax_sell = Find_Best_intervals(signals=signal_sell,apply_to='diff_min_max_candle',
	 min_tp=min_tp, max_st=max_st, name_stp='flag_min_max',alpha=alpha)

	list_index_ok = np.where(((signal_sell['ramp_high'].to_numpy()<=ramp_high_intervals_minmax_sell['interval'][upper]))&
		((signal_sell['ramp_low'].to_numpy()<=ramp_low_intervals_minmax_sell['interval'][upper]))&
		((signal_sell['diff_min_max_cci'].to_numpy()<=diff_min_max_cci_intervals_minmax_sell['interval'][upper]))&
		((signal_sell['diff_min_max_candle'].to_numpy()<=diff_min_max_candle_intervals_minmax_sell['interval'][upper]))
		)[0]

	output_sell = pd.DataFrame()
	output_sell['mean_tp_min_max'] = [np.mean(signal_sell['tp_min_max'][list_index_ok])]
	output_sell['mean_st_min_max'] = [np.mean(signal_sell['st_min_max'][list_index_ok])]
	output_sell['max_tp_min_max'] = [np.max(signal_sell['tp_min_max'][list_index_ok])]
	output_sell['max_st_min_max'] = [np.max(signal_sell['st_min_max'][list_index_ok])]
	output_sell['sum_st_min_max'] = [np.sum(signal_sell['st_min_max'][np.where(signal_sell['flag_min_max'][list_index_ok] == 'st')[0]].to_numpy())]
	output_sell['sum_tp_min_max'] = [np.sum(signal_sell['tp_min_max'][np.where(signal_sell['flag_min_max'][list_index_ok] == 'tp')[0]].to_numpy())]
	
	tp_counter = 0
	st_counter = 0
	for elm in signal_sell['flag_min_max'][list_index_ok]:
		if (elm == 'tp'):
			tp_counter += 1
		if (elm == 'st'):
			st_counter += 1
	output_sell['num_tp_min_max'] = [tp_counter]
	output_sell['num_st_min_max'] = [st_counter]
	output_sell['num_trade_min_max'] = [st_counter + tp_counter]
	output_sell['ramp_low_upper_min_max'] = [ramp_low_intervals_minmax_sell['interval'][upper]]
	output_sell['ramp_low_lower_min_max'] = [ramp_low_intervals_minmax_sell['interval'][lower]]
	output_sell['ramp_high_upper_min_max'] = [ramp_high_intervals_minmax_sell['interval'][upper]]
	output_sell['ramp_high_lower_min_max'] = [ramp_high_intervals_minmax_sell['interval'][lower]]
	output_sell['diff_min_max_cci_upper_min_max'] = [diff_min_max_cci_intervals_minmax_sell['interval'][upper]]
	output_sell['diff_min_max_cci_lower_min_max'] = [diff_min_max_cci_intervals_minmax_sell['interval'][lower]]
	output_sell['diff_min_max_candle_upper_min_max'] = [diff_min_max_candle_intervals_minmax_sell['interval'][upper]]
	output_sell['diff_min_max_candle_lower_min_max'] = [diff_min_max_candle_intervals_minmax_sell['interval'][lower]]

	if output_sell['num_trade_min_max'][0] != 0:
		score_num_tp = (tp_counter/output_sell['num_trade_min_max'][0])
	else:
		score_num_tp = 0

	if output_sell['max_st_min_max'][0] != 0:
		score_max_tp = (output_sell['max_tp_min_max'][0]/output_sell['max_st_min_max'][0])
	else:
		score_max_tp = output_sell['max_tp_min_max'][0]
		if (output_sell['max_tp_min_max'][0] != 0):
			score_max_tp = output_sell['max_tp_min_max'][0] * 10

	if (output_sell['mean_st_min_max'][0] != 0):
		score_mean_tp = (output_sell['mean_tp_min_max'][0]/output_sell['mean_st_min_max'][0])
	else:
		score_mean_tp = output_sell['mean_tp_min_max'][0]
		if (output_sell['mean_tp_min_max'][0] != 0):
			score_mean_tp = output_sell['mean_tp_min_max'][0] * 10

	if (output_sell['sum_st_min_max'][0] != 0):
		score_sum_tp = (output_sell['sum_tp_min_max'][0]/output_sell['sum_st_min_max'][0])
	else:
		score_sum_tp = output_sell['sum_tp_min_max'][0]
		if (output_sell['sum_tp_min_max'][0] != 0):
			score_sum_tp = output_sell['sum_tp_min_max'][0] * 10

	output_sell['score_min_max'] = [(score_num_tp*score_max_tp*score_mean_tp*score_sum_tp)]

	#///////////////////////////////////////////////
	
	#*********** Methode 2 Profits With PR Buy:
	ramp_low_intervals_pr_buy = Find_Best_intervals(signals=signal_buy,apply_to='ramp_low',
	 min_tp=min_tp, max_st=max_st, name_stp='flag_pr',alpha=alpha)

	ramp_high_intervals_pr_buy = Find_Best_intervals(signals=signal_buy,apply_to='ramp_high',
	 min_tp=min_tp, max_st=max_st, name_stp='flag_pr',alpha=alpha)

	diff_min_max_cci_intervals_pr_buy = Find_Best_intervals(signals=signal_buy,apply_to='diff_min_max_cci',
	 min_tp=min_tp, max_st=max_st, name_stp='flag_pr',alpha=alpha)

	diff_min_max_candle_intervals_pr_buy = Find_Best_intervals(signals=signal_buy,apply_to='diff_min_max_candle',
	 min_tp=min_tp, max_st=max_st, name_stp='flag_pr',alpha=alpha)

	diff_top_intervals_pr_buy = Find_Best_intervals(signals=signal_buy,apply_to='diff_pr_top',
	 min_tp=min_tp, max_st=max_st, name_stp='flag_pr',alpha=alpha)

	diff_down_intervals_pr_buy = Find_Best_intervals(signals=signal_buy,apply_to='diff_pr_down',
	 min_tp=min_tp, max_st=max_st, name_stp='flag_pr',alpha=alpha)

	list_index_ok = np.where(((signal_buy['ramp_low'].to_numpy()>=ramp_low_intervals_pr_buy['interval'][lower]))&
		((signal_buy['ramp_high'].to_numpy()>=ramp_high_intervals_pr_buy['interval'][lower]))&
		((signal_buy['diff_pr_top'].to_numpy()<=diff_top_intervals_pr_buy['interval'][upper]))&
		((signal_buy['diff_pr_down'].to_numpy()<=diff_down_intervals_pr_buy['interval'][upper]))&
		((signal_buy['diff_min_max_cci'].to_numpy()<=diff_min_max_cci_intervals_pr_buy['interval'][upper]))&
		((signal_buy['diff_min_max_candle'].to_numpy()<=diff_min_max_candle_intervals_pr_buy['interval'][upper]))
		)[0]

	output_buy['mean_tp_pr'] = [np.mean(signal_buy['tp_pr'][list_index_ok])]
	output_buy['mean_st_pr'] = [np.mean(signal_buy['st_pr'][list_index_ok])]
	output_buy['max_tp_pr'] = [np.max(signal_buy['tp_pr'][list_index_ok])]
	output_buy['max_st_pr'] = [np.max(signal_buy['st_pr'][list_index_ok])]
	output_buy['sum_st_pr'] = [np.sum(signal_buy['st_pr'][np.where(signal_buy['flag_pr'][list_index_ok] == 'st')[0]].to_numpy())]
	output_buy['sum_tp_pr'] = [np.sum(signal_buy['tp_pr'][np.where(signal_buy['flag_pr'][list_index_ok] == 'tp')[0]].to_numpy())]
	
	tp_counter = 0
	st_counter = 0
	for elm in signal_buy['flag_pr'][list_index_ok]:
		if (elm == 'tp'):
			tp_counter += 1
		if (elm == 'st'):
			st_counter += 1
	output_buy['num_tp_pr'] = [tp_counter]
	output_buy['num_st_pr'] = [st_counter]
	output_buy['num_trade_pr'] = [st_counter + tp_counter]
	output_buy['ramp_low_upper_pr'] = [ramp_low_intervals_pr_buy['interval'][upper]]
	output_buy['ramp_low_lower_pr'] = [ramp_low_intervals_pr_buy['interval'][lower]]
	output_buy['ramp_high_upper_pr'] = [ramp_high_intervals_pr_buy['interval'][upper]]
	output_buy['ramp_high_lower_pr'] = [ramp_high_intervals_pr_buy['interval'][lower]]
	output_buy['diff_min_max_cci_upper_pr'] = [diff_min_max_cci_intervals_pr_buy['interval'][upper]]
	output_buy['diff_min_max_cci_lower_pr'] = [diff_min_max_cci_intervals_pr_buy['interval'][lower]]
	output_buy['diff_min_max_candle_upper_pr'] = [diff_min_max_candle_intervals_pr_buy['interval'][upper]]
	output_buy['diff_min_max_candle_lower_pr'] = [diff_min_max_candle_intervals_pr_buy['interval'][lower]]
	output_buy['diff_top_upper_pr'] = [diff_top_intervals_pr_buy['interval'][upper]]
	output_buy['diff_top_lower_pr'] = [diff_top_intervals_pr_buy['interval'][lower]]
	output_buy['diff_down_upper_pr'] = [diff_down_intervals_pr_buy['interval'][upper]]
	output_buy['diff_down_lower_pr'] = [diff_down_intervals_pr_buy['interval'][lower]]

	if output_buy['num_trade_pr'][0] != 0:
		score_num_tp = (tp_counter/output_buy['num_trade_pr'][0])
	else:
		score_num_tp = 0

	if output_buy['max_st_pr'][0] != 0:
		score_max_tp = (output_buy['max_tp_pr'][0]/output_buy['max_st_pr'][0])
	else:
		score_max_tp = output_buy['max_tp_pr'][0]
		if (output_buy['max_tp_pr'][0] != 0):
			score_max_tp = output_buy['max_tp_pr'][0] * 10

	if (output_buy['mean_st_pr'][0] != 0):
		score_mean_tp = (output_buy['mean_tp_pr'][0]/output_buy['mean_st_pr'][0])
	else:
		score_mean_tp = output_buy['mean_tp_pr'][0]
		if (output_buy['mean_tp_pr'][0] != 0):
			score_mean_tp = output_buy['mean_tp_pr'][0] * 10

	if (output_buy['sum_st_pr'][0] != 0):
		score_sum_tp = (output_buy['sum_tp_pr'][0]/output_buy['sum_st_pr'][0])
	else:
		score_sum_tp = output_buy['sum_tp_pr'][0]
		if (output_buy['sum_tp_pr'][0] != 0):
			score_sum_tp = output_buy['sum_tp_pr'][0] * 10

	output_buy['score_pr'] = [(score_num_tp*score_max_tp*score_mean_tp*score_sum_tp)]

	if np.isnan(output_buy['score_pr'][0]) : output_buy['score_pr'][0] = 0
	if np.isnan(output_buy['score_min_max'][0]) : output_buy['score_min_max'][0] = 0

	if (output_buy['score_pr'][0] > output_buy['score_min_max'][0]):
		output_buy['methode'] = ['pr']

	if (output_buy['score_min_max'][0] >= output_buy['score_pr'][0]):
		output_buy['methode'] = ['min_max']

	if (output_buy['score_pr'][0] is 0) and (output_buy['score_min_max'][0] is 0):
		output_buy['methode'] = ['no_trade']

	#///////////////////////////////////////////////
	
	#*********** Methode 2 Profits With PR Sell:
	ramp_low_intervals_pr_sell = Find_Best_intervals(signals=signal_sell,apply_to='ramp_low',
	 min_tp=min_tp, max_st=max_st, name_stp='flag_pr',alpha=alpha)

	ramp_high_intervals_pr_sell = Find_Best_intervals(signals=signal_sell,apply_to='ramp_high',
	 min_tp=min_tp, max_st=max_st, name_stp='flag_pr',alpha=alpha)

	diff_min_max_cci_intervals_pr_sell = Find_Best_intervals(signals=signal_sell,apply_to='diff_min_max_cci',
	 min_tp=min_tp, max_st=max_st, name_stp='flag_pr',alpha=alpha)

	diff_min_max_candle_intervals_pr_sell = Find_Best_intervals(signals=signal_sell,apply_to='diff_min_max_candle',
	 min_tp=min_tp, max_st=max_st, name_stp='flag_pr',alpha=alpha)

	diff_top_intervals_pr_sell = Find_Best_intervals(signals=signal_sell,apply_to='diff_pr_top',
	 min_tp=min_tp, max_st=max_st, name_stp='flag_pr',alpha=alpha)

	diff_down_intervals_pr_sell = Find_Best_intervals(signals=signal_sell,apply_to='diff_pr_down',
	 min_tp=min_tp, max_st=max_st, name_stp='flag_pr',alpha=alpha)

	list_index_ok = np.where(((signal_sell['ramp_low'].to_numpy()<=ramp_low_intervals_pr_sell['interval'][upper]))&
		((signal_sell['ramp_high'].to_numpy()<=ramp_high_intervals_pr_sell['interval'][upper]))&
		((signal_sell['diff_pr_top'].to_numpy()<=diff_top_intervals_pr_sell['interval'][upper]))&
		((signal_sell['diff_pr_down'].to_numpy()<=diff_down_intervals_pr_sell['interval'][upper]))&
		((signal_sell['diff_min_max_cci'].to_numpy()<=diff_min_max_cci_intervals_pr_sell['interval'][upper]))&
		((signal_sell['diff_min_max_candle'].to_numpy()<=diff_min_max_candle_intervals_pr_sell['interval'][upper]))
		)[0]

	output_sell['mean_tp_pr'] = [np.mean(signal_sell['tp_pr'][list_index_ok])]
	output_sell['mean_st_pr'] = [np.mean(signal_sell['st_pr'][list_index_ok])]
	output_sell['max_tp_pr'] = [np.max(signal_sell['tp_pr'][list_index_ok])]
	output_sell['max_st_pr'] = [np.max(signal_sell['st_pr'][list_index_ok])]
	output_sell['sum_st_pr'] = [np.sum(signal_sell['st_pr'][np.where(signal_sell['flag_pr'][list_index_ok] == 'st')[0]].to_numpy())]
	output_sell['sum_tp_pr'] = [np.sum(signal_sell['tp_pr'][np.where(signal_sell['flag_pr'][list_index_ok] == 'tp')[0]].to_numpy())]
	
	tp_counter = 0
	st_counter = 0
	for elm in signal_sell['flag_pr'][list_index_ok]:
		if (elm == 'tp'):
			tp_counter += 1
		if (elm == 'st'):
			st_counter += 1
	output_sell['num_tp_pr'] = [tp_counter]
	output_sell['num_st_pr'] = [st_counter]
	output_sell['num_trade_pr'] = [st_counter + tp_counter]
	output_sell['ramp_low_upper_pr'] = [ramp_low_intervals_pr_sell['interval'][upper]]
	output_sell['ramp_low_lower_pr'] = [ramp_low_intervals_pr_sell['interval'][lower]]
	output_sell['ramp_high_upper_pr'] = [ramp_high_intervals_pr_sell['interval'][upper]]
	output_sell['ramp_high_lower_pr'] = [ramp_high_intervals_pr_sell['interval'][lower]]
	output_sell['diff_min_max_cci_upper_pr'] = [diff_min_max_cci_intervals_pr_sell['interval'][upper]]
	output_sell['diff_min_max_cci_lower_pr'] = [diff_min_max_cci_intervals_pr_sell['interval'][lower]]
	output_sell['diff_min_max_candle_upper_pr'] = [diff_min_max_candle_intervals_pr_sell['interval'][upper]]
	output_sell['diff_min_max_candle_lower_pr'] = [diff_min_max_candle_intervals_pr_sell['interval'][lower]]
	output_sell['diff_top_upper_pr'] = [diff_top_intervals_pr_sell['interval'][upper]]
	output_sell['diff_top_lower_pr'] = [diff_top_intervals_pr_sell['interval'][lower]]
	output_sell['diff_down_upper_pr'] = [diff_down_intervals_pr_sell['interval'][upper]]
	output_sell['diff_down_lower_pr'] = [diff_down_intervals_pr_sell['interval'][lower]]

	if output_sell['num_trade_pr'][0] != 0:
		score_num_tp = (tp_counter/output_sell['num_trade_pr'][0])
	else:
		score_num_tp = 0

	if output_sell['max_st_pr'][0] != 0:
		score_max_tp = (output_sell['max_tp_pr'][0]/output_sell['max_st_pr'][0])
	else:
		score_max_tp = output_sell['max_tp_pr'][0]
		if (output_sell['max_tp_pr'][0] != 0):
			score_max_tp = output_sell['max_tp_pr'][0] * 10

	if (output_sell['mean_st_pr'][0] != 0):
		score_mean_tp = (output_sell['mean_tp_pr'][0]/output_sell['mean_st_pr'][0])
	else:
		score_mean_tp = output_sell['mean_tp_pr'][0]
		if (output_sell['mean_tp_pr'][0] != 0):
			score_mean_tp = output_sell['mean_tp_pr'][0] * 10

	if (output_sell['sum_st_pr'][0] != 0):
		score_sum_tp = (output_sell['sum_tp_pr'][0]/output_sell['sum_st_pr'][0])
	else:
		score_sum_tp = output_sell['sum_tp_pr'][0]
		if (output_sell['sum_tp_pr'][0] != 0):
			score_sum_tp = output_sell['sum_tp_pr'][0] * 10

	output_sell['score_pr'] = [(score_num_tp*score_max_tp*score_mean_tp*score_sum_tp)]

	if np.isnan(output_sell['score_pr'][0]) : output_sell['score_pr'][0] = 0
	if np.isnan(output_sell['score_min_max'][0]) : output_sell['score_min_max'][0] = 0

	if (output_sell['score_pr'][0] > output_sell['score_min_max'][0]):
		output_sell['methode'] = ['pr']

	if (output_sell['score_min_max'][0] >= output_sell['score_pr'][0]):
		output_sell['methode'] = ['min_max']

	if (output_sell['score_pr'][0] is 0) and (output_sell['score_min_max'][0] is 0):
		output_sell['methode'] = ['no_trade']

	#///////////////////////////////////////////////

	return output_buy,output_sell
#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#**************************************************** Create First Cromosomes *******************************************************
def initilize_values_genetic():
	#************************** initialize Values ******************************************************
	Chromosome = {}
	range(1)
	value = randint(50, 100)

	Chromosome[0] = {
	'high_period': 50,
	'low_period': 25,
	'distance_lines': 2,
	'min_tp': 0.1,
	'max_st': 0.2,
	'alfa': 0.02,
	'signal': None,
	'score_buy': 0,
	'score_sell': 0
	}

	Chromosome[1] = {
	'high_period': 100,
	'low_period': 50,
	'distance_lines': 4,
	'min_tp': 0.2,
	'max_st': 0.1,
	'alfa': 0.2,
	'signal': None,
	'score_buy': 0,
	'score_sell': 0
	}
	i = 2
	while i < 20:
		Chromosome[i] = {
			'high_period': randint(5, 120),
			'low_period': randint(5, 60),
			'distance_lines': randint(0, 10),
			'min_tp': randint(0, 60)/100,
			'max_st': randint(0, 40)/100,
			'alfa': randint(1, 500)/1000,
			'signal': None,
			'score_buy': 0,
			'score_sell': 0
		}
		if (Chromosome[i]['high_period'] <= Chromosome[i]['low_period']): continue
		res = list(Chromosome[i].keys()) 
		#print(res[1])
		#print(Chromosome[i][res[1]])
		i += 1
	#***********************************************************************************
	return Chromosome
#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#************************************************ Gen Creator ****************************************************************
def takeSecond(elem):
    return elem[1]

def gen_creator(Chromosome):

	Chromosome_Cutter = randint(0, 5)

	Chromosome_selector = randint(0, 19)

	baby = {}

	#print('Generate Baby')
	chrom_creator_counter = 0
	baby_counter = 0

	baby_counter_create = 0

	while (baby_counter_create < (len(Chromosome) * 2)):
		baby[baby_counter_create] = {
			'high_period': randint(5, 120),
			'low_period': randint(5, 60),
			'distance_lines': randint(0, 10),
			'min_tp': randint(0, 60)/100,
			'max_st': randint(0, 40)/100,
			'alfa': randint(1, 500)/1000,
			'signal': None,
			'score_buy': 0,
			'score_sell': 0
		}

		baby_counter_create += 1

	scr = []
	for k,v in zip(Chromosome.keys(), Chromosome.values()):
		scr.append([k, (v.get('score_buy') + v.get('score_sell'))/2])

	scr_idx = sorted(scr, key=takeSecond, reverse=True)[:int(len(Chromosome)/2)]

	while chrom_creator_counter < len(Chromosome):

		#********************************************* Baby ***********************************************************
		
		
		Chromosome_selector_1 = np.random.choice(len(scr_idx), size=1)[0]
		Chromosome_selector_2 = np.random.choice(len(scr_idx), size=1)[0]

		res_1 = list(Chromosome[Chromosome_selector_1].keys())
		res_2 = list(Chromosome[Chromosome_selector_2].keys())

		Chromosome_Cutter = randint(0, 5)
		change_chrom_counter = 0

		while change_chrom_counter < Chromosome_Cutter:
						#print(change_chrom_counter)
			baby[baby_counter].update({res_1[change_chrom_counter]: Chromosome[Chromosome_selector_1][res_1[change_chrom_counter]]})
			baby[baby_counter + 1].update({res_2[change_chrom_counter]: Chromosome[Chromosome_selector_2][res_2[change_chrom_counter]]})

			change_chrom_counter += 1

		change_chrom_counter = Chromosome_Cutter

		while change_chrom_counter < 6:
			baby[baby_counter].update({res_2[change_chrom_counter]: Chromosome[Chromosome_selector_2][res_2[change_chrom_counter]]})
			baby[baby_counter + 1].update({res_1[change_chrom_counter]: Chromosome[Chromosome_selector_1][res_1[change_chrom_counter]]})
			change_chrom_counter += 1

		baby_counter = baby_counter + 2

					#********************************************///////***************************************************************************
		chrom_creator_counter += 1

	i = 0
	limit_counter = len(Chromosome) * 2 
	while i < (limit_counter):
		Chromosome[i] = {
			'high_period': randint(5, 120),
			'low_period': randint(5, 60),
			'distance_lines': randint(0, 10),
			'min_tp': randint(0, 60)/100,
			'max_st': randint(0, 40)/100,
			'alfa': randint(1, 500)/1000,
			'signal': None,
			'score_buy': 0,
			'score_sell': 0
		}

		if (Chromosome[i]['high_period'] <= Chromosome[i]['low_period']): continue
		i += 1

	re_counter = 0
	while (re_counter < limit_counter):
		Chromosome[re_counter]['high_period'] = baby[re_counter]['high_period']
		Chromosome[re_counter]['low_period'] = baby[re_counter]['low_period']
		Chromosome[re_counter]['distance_lines'] = baby[re_counter]['distance_lines']
		Chromosome[re_counter]['min_tp'] = baby[re_counter]['min_tp']
		Chromosome[re_counter]['max_st'] = baby[re_counter]['max_st']
		Chromosome[re_counter]['alfa'] = baby[re_counter]['alfa']
		Chromosome[re_counter]['signal'] = baby[re_counter]['signal']
		Chromosome[re_counter]['score_buy'] = baby[re_counter]['score_buy']
		Chromosome[re_counter]['score_sell'] = baby[re_counter]['score_sell']
		re_counter += 1
		#print(Chromosome_5M[6])

	return Chromosome

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#***************************************** Genetic Algorithm **************************************************************

def genetic_buy_algo(symbol_data_5M,symbol_data_15M,symbol,num_turn,max_score):

	#*************************** Algorithm *************************************************//
	Chromosome = initilize_values_genetic()

	print('**************************** START Genetic BUY ',symbol,'****************************')
	print('\n')

	if os.path.exists("Genetic_cci_output_buy/"+symbol+'.csv'):
		with open("Genetic_cci_output_buy/"+symbol+'.csv', 'r', newline='') as myfile:
			for line in csv.DictReader(myfile):
				Chromosome[19] = line
				Chromosome[19]['high_period'] = float(Chromosome[19]['high_period'])
				Chromosome[19]['low_period'] = float(Chromosome[19]['low_period'])
				Chromosome[19]['distance_lines'] = float(Chromosome[19]['distance_lines'])
				Chromosome[19]['min_tp'] = float(Chromosome[19]['min_tp'])
				Chromosome[19]['max_st'] = float(Chromosome[19]['max_st'])
				Chromosome[19]['alfa'] = float(Chromosome[19]['alfa'])
				Chromosome[19]['signal'] = Chromosome[19]['signal']
				Chromosome[19]['score_buy'] = float(Chromosome[19]['score_buy'])
				Chromosome[19]['score_sell'] = float(Chromosome[19]['score_sell'])

	if os.path.exists("Genetic_cci_output_sell/"+symbol+'.csv'):
		with open("Genetic_cci_output_sell/"+symbol+'.csv', 'r', newline='') as myfile:
			for line in csv.DictReader(myfile):
				Chromosome[18] = line
				Chromosome[18]['high_period'] = float(Chromosome[18]['high_period'])
				Chromosome[18]['low_period'] = float(Chromosome[18]['low_period'])
				Chromosome[18]['distance_lines'] = float(Chromosome[18]['distance_lines'])
				Chromosome[18]['min_tp'] = float(Chromosome[18]['min_tp'])
				Chromosome[18]['max_st'] = float(Chromosome[18]['max_st'])
				Chromosome[18]['alfa'] = float(Chromosome[18]['alfa'])
				Chromosome[18]['signal'] = Chromosome[18]['signal']
				Chromosome[18]['score_buy'] = float(Chromosome[18]['score_buy'])
				Chromosome[18]['score_sell'] = float(Chromosome[18]['score_sell'])

	result_buy = pd.DataFrame()
	chromosome_buy = pd.DataFrame()

	result_sell = pd.DataFrame()
	chromosome_sell = pd.DataFrame()

	chrom_counter = 0

	with tqdm(total=num_turn) as pbar:
		while chrom_counter < len(Chromosome):

			buy_data,sell_data = golden_cross_zero(dataset=symbol_data_5M,dataset_15M=symbol_data_15M,symbol=symbol,
				Low_Period=Chromosome[chrom_counter]['low_period'],High_Period=Chromosome[chrom_counter]['high_period'],
				distance_lines=Chromosome[chrom_counter]['distance_lines'],mode='optimize',
				name_stp_minmax=True,name_stp_pr=True,plot=False)

			output_buy,output_sell = tester_golden_cross_zero(signal_buy=buy_data,signal_sell=sell_data,
				min_tp=Chromosome[chrom_counter]['min_tp'],max_st=Chromosome[chrom_counter]['max_st'],
				alpha=Chromosome[chrom_counter]['alfa'])

			if not np.isnan(output_buy['score_pr'][0]) or not np.isnan(output_buy['score_min_max'][0]):
				if (
					output_buy['score_pr'][0] < max_score and
					not np.isnan(output_buy['score_pr'][0]) and
					output_buy['score_min_max'][0] < max_score and
					not np.isnan(output_buy['score_min_max'][0])
					):
					Chromosome.pop(chrom_counter)
					high_period = randint(5, 120)
					low_period = randint(5, 60)
					while high_period <= low_period:
						high_period = randint(5, 120)
						low_period = randint(5, 60)

					Chromosome[chrom_counter] = {
						'high_period': high_period,
						'low_period': low_period,
						'distance_lines': randint(0, 10),
						'min_tp': randint(0, 60)/100,
						'max_st': randint(0, 40)/100,
						'alfa': randint(1, 500)/1000,
						'signal': None,
						'score_buy': 0,
						'score_sell': 0
						}
				else:
					Chromosome[chrom_counter]['signal'] = ('buy' if Chromosome[chrom_counter].get('signal') else 'buy,sell')
					result_buy = result_buy.append(output_buy, ignore_index=True)
					chromosome_buy = chromosome_buy.append(Chromosome[chrom_counter], ignore_index=True)
					score = (output_buy['score_pr'][0]+output_buy['score_min_max'][0])/2
					Chromosome[chrom_counter].update({'score_buy': score })

			if not np.isnan(output_sell['score_pr'][0]) or not np.isnan(output_sell['score_min_max'][0]):
				if (
					output_sell['score_pr'][0] < max_score and
					not np.isnan(output_sell['score_pr'][0]) and
					output_sell['score_min_max'][0] < max_score and
					not np.isnan(output_sell['score_min_max'][0])
					):
					Chromosome.pop(chrom_counter)
					high_period = randint(5, 120)
					low_period = randint(5, 60)
					while high_period <= low_period:
						high_period = randint(5, 120)
						low_period = randint(5, 60)

					Chromosome[chrom_counter] = {
						'high_period': high_period,
						'low_period': low_period,
						'distance_lines': randint(0, 10),
						'min_tp': randint(0, 60)/100,
						'max_st': randint(0, 40)/100,
						'alfa': randint(1, 500)/1000,
						'signal': None,
						'score_buy': 0,
						'score_sell': 0
						}
				else:
					Chromosome[chrom_counter]['signal'] = ('sell' if Chromosome[chrom_counter].get('signal') else 'buy,sell')
					result_sell = result_sell.append(output_sell, ignore_index=True)
					chromosome_sell = chromosome_sell.append(Chromosome[chrom_counter], ignore_index=True)
					score = (output_sell['score_pr'][0]+output_sell['score_min_max'][0])/2
					Chromosome[chrom_counter].update({'score_sell': score })

			pbar.update(int((len(chromosome_buy) + len(chromosome_sell))/2))

			if Chromosome[chrom_counter]['signal'] is None: continue

			if len(chromosome_buy) > num_turn and len(chromosome_sell) > num_turn: break
			chrom_counter += 1
			if (chrom_counter >= ((len(Chromosome)))):
				chrom_counter = 0
				Chromosome = gen_creator(Chromosome)
				continue

			
	
	#**************************** Best Find *********************************************************

	#************ Buy Find:
	best_buy = pd.DataFrame()
	max_score_buy_pr = np.max(result_buy['score_pr'].dropna())
	max_score_buy_min_max = np.max(result_buy['score_min_max'].dropna())
	max_score_buy = max(max_score_buy_pr,max_score_buy_min_max)
	best_buy_score_index = np.where((result_buy['score_pr']==max_score_buy) | (result_buy['score_min_max'] == max_score_buy))[0]
	best_dict = dict()
	for idx in best_buy_score_index:
		for clm in result_buy.columns:
			best_dict.update(
				{
				clm: result_buy[clm][idx]
				})
		for clm in chromosome_buy.columns:
			best_dict.update(
				{
				clm: chromosome_buy[clm][idx]
				})

		best_buy = best_buy.append(best_dict, ignore_index=True)
	#//////////////////////
	#********** Sell Find:
	best_sell = pd.DataFrame()
	max_score_sell_pr = np.max(result_sell['score_pr'].dropna())
	max_score_sell_min_max = np.max(result_sell['score_min_max'].dropna())
	max_score_sell = max(max_score_sell_pr,max_score_sell_min_max)
	best_sell_score_index = np.where((result_sell['score_pr']==max_score_sell) | (result_sell['score_min_max'] == max_score_sell))[0]
	best_dict = dict()
	for idx in best_sell_score_index:
		for clm in result_sell.columns:
			best_dict.update(
				{
				clm: result_sell[clm][idx]
				})
		for clm in chromosome_sell.columns:
			best_dict.update(
				{
				clm: chromosome_sell[clm][idx]
				})

		best_sell = best_sell.append(best_dict, ignore_index=True)
	#//////////////////////

	#********************************///////////////****************************************************************

	#*************************** Save to TXT File ***************************************************************

	try:
		if os.path.exists("Genetic_cci_output_buy/"+symbol+'.csv'):
			os.remove("Genetic_cci_output_buy/"+symbol+'.csv')

		with open("Genetic_cci_output_buy/"+symbol+'.csv', 'w', newline='') as myfile:
			fields = best_buy.columns.to_list()
			writer = csv.DictWriter(myfile, fieldnames=fields)
			writer.writeheader()
	
			for idx in range(len(best_buy)):
				rows = dict()
				for clm in best_buy.columns:
					rows.update({clm: best_buy[clm][idx]})
				writer.writerow(rows)
					
	except Exception as ex:
		print('some thing wrong: ', ex)


	try:
		if os.path.exists("Genetic_cci_output_sell/"+symbol+'.csv'):
			os.remove("Genetic_cci_output_sell/"+symbol+'.csv')

		with open("Genetic_cci_output_sell/"+symbol+'.csv', 'w', newline='') as myfile:
			fields = best_sell.columns.to_list()
			writer = csv.DictWriter(myfile, fieldnames=fields)
			writer.writeheader()
	
			for idx in range(len(best_sell)):
				rows = dict()
				for clm in best_sell.columns:
					rows.update({clm: best_sell[clm][idx]})
				writer.writerow(rows)
					
	except Exception as ex:
		print('some thing wrong: ', ex)

	print('/////////////////////// Finish Genetic BUY ',symbol,'///////////////////////////////////')

#/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#********************** read GA result ****************************************************************************

def read_ga_result(symbol):
	buy_path = "Genetic_cci_output_buy/" + symbol + '.csv'
	sell_path = "Genetic_cci_output_sell/" + symbol + '.csv'
	if os.path.exists(buy_path):
		ga_result_buy = pd.read_csv(buy_path)

	if os.path.exists(sell_path):
		ga_result_sell = pd.read_csv(sell_path)

	return ga_result_buy, ga_result_sell
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#************************************ one year golden cross tester ***********************************************

def one_year_golden_cross_tester(dataset,dataset_15M,symbol):

	now = datetime.now()

	log_name = 'log/cci/golden_cross_zero/'+str(now.year)+'-'+str(now.month)+'-'+str(now.day)+'-'+str(now.hour)+'-'+str(now.minute)+'-'+str(now.second)+'.log'
	
	logging.basicConfig(filename=log_name, level=logging.DEBUG)
	logging.debug('=======================> %s' %symbol)

	buy_path = "Genetic_cci_output_buy/" + symbol + '.csv'
	sell_path = "Genetic_cci_output_sell/" + symbol + '.csv'

	if os.path.exists(buy_path):
		ga_result_buy, ga_result_sell = read_ga_result(symbol=symbol)
	else:
		return 0
	#********************************************** Buy Test:
	logging.info('****** Buy:')
	if ga_result_buy['methode'][0] is not 'no_trade':
		if ga_result_buy['methode'][0] == 'pr':
			name_stp_pr = True
			name_stp_minmax = False
		elif ga_result_buy['methode'][0] == 'min_max':
			name_stp_pr = False
			name_stp_minmax = True

		buy_data,sell_data = golden_cross_zero(dataset=dataset,dataset_15M=dataset_15M,symbol=symbol,
			Low_Period=ga_result_buy['low_period'][0],High_Period=ga_result_buy['high_period'][0],
			distance_lines=ga_result_buy['distance_lines'][0],mode='optimize',
			name_stp_minmax=name_stp_minmax,name_stp_pr=name_stp_pr,plot=False)

		#*********************** Min Max Methode:

		if ga_result_buy['methode'][0] == 'min_max':
			list_index_ok = np.where(((buy_data['ramp_high'].to_numpy()>=ga_result_buy['ramp_high_lower_min_max'][0]))&
				((buy_data['ramp_low'].to_numpy()>=ga_result_buy['ramp_low_lower_min_max'][0]))&
				((buy_data['diff_min_max_cci'].to_numpy()<ga_result_buy['diff_min_max_cci_upper_min_max'][0]))&
				((buy_data['diff_min_max_candle'].to_numpy()<=ga_result_buy['diff_min_max_candle_upper_min_max'][0]))
				)[0]

			output_buy = pd.DataFrame()
			output_buy['mean_tp_min_max'] = [np.mean(buy_data['tp_min_max'][list_index_ok])]
			output_buy['mean_st_min_max'] = [np.mean(buy_data['st_min_max'][list_index_ok])]
			output_buy['max_tp_min_max'] = [np.max(buy_data['tp_min_max'][list_index_ok])]
			output_buy['max_st_min_max'] = [np.max(buy_data['st_min_max'][list_index_ok])]
			output_buy['sum_st_min_max'] = [np.sum(buy_data['st_min_max'][np.where(buy_data['flag_min_max'][list_index_ok] == 'st')[0]].to_numpy())]
			output_buy['sum_tp_min_max'] = [np.sum(buy_data['tp_min_max'][np.where(buy_data['flag_min_max'][list_index_ok] == 'tp')[0]].to_numpy())]

			tp_counter = 0
			st_counter = 0
			for elm in buy_data['flag_min_max'][list_index_ok]:
				if (elm == 'tp'):
					tp_counter += 1
				if (elm == 'st'):
					st_counter += 1
			output_buy['num_tp_min_max'] = [tp_counter]
			output_buy['num_st_min_max'] = [st_counter]
			output_buy['num_trade_min_max'] = [st_counter + tp_counter]

			if output_buy['num_trade_min_max'][0] != 0:
				score_num_tp = (tp_counter/output_buy['num_trade_min_max'][0])
			else:
				score_num_tp = 0

			if output_buy['max_st_min_max'][0] != 0:
				score_max_tp = (output_buy['max_tp_min_max'][0]/output_buy['max_st_min_max'][0])
			else:
				score_max_tp = output_buy['max_tp_min_max'][0]
				if (output_buy['max_tp_min_max'][0] != 0):
					score_max_tp = output_buy['max_tp_min_max'][0] * 10

			if (output_buy['mean_st_min_max'][0] != 0):
				score_mean_tp = (output_buy['mean_tp_min_max'][0]/output_buy['mean_st_min_max'][0])
			else:
				score_mean_tp = output_buy['mean_tp_min_max'][0]
				if (output_buy['mean_tp_min_max'][0] != 0):
					score_mean_tp = output_buy['mean_tp_min_max'][0] * 10

			if (output_buy['sum_st_min_max'][0] != 0):
				score_sum_tp = (output_buy['sum_tp_min_max'][0]/output_buy['sum_st_min_max'][0])
			else:
				score_sum_tp = output_buy['sum_tp_min_max'][0]
				if (output_buy['sum_tp_min_max'][0] != 0):
					score_sum_tp = output_buy['sum_tp_min_max'][0] * 10

			output_buy['score_min_max'] = [(score_num_tp*score_max_tp*score_mean_tp*score_sum_tp)]

			if np.isnan(output_buy['score_min_max'][0]) : output_buy['score_min_max'][0] = 0

			logging.info('mean_tp_min_max= {}'.format(output_buy['mean_tp_min_max'][0]))
			logging.info('mean_st_min_max= {}'.format(output_buy['mean_st_min_max'][0]))
			logging.info('max_tp_min_max= {}'.format(output_buy['max_tp_min_max'][0]))
			logging.info('max_st_min_max= {}'.format(output_buy['max_st_min_max'][0]))
			logging.info('sum_st_min_max= {}'.format(output_buy['sum_st_min_max'][0]))
			logging.info('sum_tp_min_max= {}'.format(output_buy['sum_tp_min_max'][0]))
			logging.info('num_tp_min_max= {}'.format(output_buy['num_tp_min_max'][0]))
			logging.info('num_st_min_max= {}'.format(output_buy['num_st_min_max'][0]))
			logging.info('num_trade_min_max= {}'.format(output_buy['num_trade_min_max'][0]))
			logging.info('score_min_max= {}'.format(output_buy['score_min_max'][0]))
			logging.info('score_min_max ga= {}'.format(ga_result_buy['score_min_max'][0]))

			if output_buy['score_min_max'][0] >= ga_result_buy['score_min_max'][0]:
				ga_result_buy['permit'] = True
				ga_result_buy.to_csv(buy_path)
			else:
				ga_result_buy['permit'] = False
				ga_result_buy.to_csv(buy_path)

		#////////////////////////////////////////////////////////////////

		#*********************** PR Methode:
		if ga_result_buy['methode'][0] == 'pr':
			list_index_ok = np.where(((buy_data['ramp_low'].to_numpy()>=ga_result_buy['ramp_low_lower_pr'][0]))&
				((buy_data['ramp_high'].to_numpy()>=ga_result_buy['ramp_high_lower_pr'][0]))&
				((buy_data['diff_pr_top'].to_numpy()<=ga_result_buy['diff_top_upper_pr'][0]))&
				((buy_data['diff_pr_down'].to_numpy()<=ga_result_buy['diff_down_upper_pr'][0]))&
				((buy_data['diff_min_max_cci'].to_numpy()<=ga_result_buy['diff_min_max_cci_upper_pr'][0]))&
				((buy_data['diff_min_max_candle'].to_numpy()<=ga_result_buy['diff_min_max_candle_upper_pr'][0]))
				)[0]

			output_buy = pd.DataFrame()
			output_buy['mean_tp_pr'] = [np.mean(buy_data['tp_pr'][list_index_ok])]
			output_buy['mean_st_pr'] = [np.mean(buy_data['st_pr'][list_index_ok])]
			output_buy['max_tp_pr'] = [np.max(buy_data['tp_pr'][list_index_ok])]
			output_buy['max_st_pr'] = [np.max(buy_data['st_pr'][list_index_ok])]
			output_buy['sum_st_pr'] = [np.sum(buy_data['st_pr'][np.where(buy_data['flag_pr'][list_index_ok] == 'st')[0]].to_numpy())]
			output_buy['sum_tp_pr'] = [np.sum(buy_data['tp_pr'][np.where(buy_data['flag_pr'][list_index_ok] == 'tp')[0]].to_numpy())]
	
			tp_counter = 0
			st_counter = 0
			for elm in buy_data['flag_pr'][list_index_ok]:
				if (elm == 'tp'):
					tp_counter += 1
				if (elm == 'st'):
					st_counter += 1
			output_buy['num_tp_pr'] = [tp_counter]
			output_buy['num_st_pr'] = [st_counter]
			output_buy['num_trade_pr'] = [st_counter + tp_counter]
			

			if output_buy['num_trade_pr'][0] != 0:
				score_num_tp = (tp_counter/output_buy['num_trade_pr'][0])
			else:
				score_num_tp = 0

			if output_buy['max_st_pr'][0] != 0:
				score_max_tp = (output_buy['max_tp_pr'][0]/output_buy['max_st_pr'][0])
			else:
				score_max_tp = output_buy['max_tp_pr'][0]
				if (output_buy['max_tp_pr'][0] != 0):
					score_max_tp = output_buy['max_tp_pr'][0] * 10

			if (output_buy['mean_st_pr'][0] != 0):
				score_mean_tp = (output_buy['mean_tp_pr'][0]/output_buy['mean_st_pr'][0])
			else:
				score_mean_tp = output_buy['mean_tp_pr'][0]
				if (output_buy['mean_tp_pr'][0] != 0):
					score_mean_tp = output_buy['mean_tp_pr'][0] * 10

			if (output_buy['sum_st_pr'][0] != 0):
				score_sum_tp = (output_buy['sum_tp_pr'][0]/output_buy['sum_st_pr'][0])
			else:
				score_sum_tp = output_buy['sum_tp_pr'][0]
				if (output_buy['sum_tp_pr'][0] != 0):
					score_sum_tp = output_buy['sum_tp_pr'][0] * 10

			output_buy['score_pr'] = [(score_num_tp*score_max_tp*score_mean_tp*score_sum_tp)]

			if np.isnan(output_buy['score_pr'][0]) : output_buy['score_pr'][0] = 0

			logging.info('mean_tp_pr= {}'.format(output_buy['mean_tp_pr'][0]))
			logging.info('mean_st_pr= {}'.format(output_buy['mean_st_pr'][0]))
			logging.info('max_tp_pr= {}'.format(output_buy['max_tp_pr'][0]))
			logging.info('max_st_pr= {}'.format(output_buy['max_st_pr'][0]))
			logging.info('sum_st_pr= {}'.format(output_buy['sum_st_pr'][0]))
			logging.info('sum_tp_pr= {}'.format(output_buy['sum_tp_pr'][0]))
			logging.info('num_tp_pr= {}'.format(output_buy['num_tp_pr'][0]))
			logging.info('num_st_pr= {}'.format(output_buy['num_st_pr'][0]))
			logging.info('num_trade_pr= {}'.format(output_buy['num_trade_pr'][0]))
			logging.info('score_pr= {}'.format(output_buy['score_pr'][0]))
			logging.info('score_pr ga= {}'.format(ga_result_buy['score_pr'][0]))

			if output_buy['score_pr'][0] >= ga_result_buy['score_pr'][0]: 
				ga_result_buy['permit'] = True
				ga_result_buy.to_csv(buy_path)
			else:
				ga_result_buy['permit'] = False
				ga_result_buy.to_csv(buy_path)

	#///////////////////////////////////////////////////////////////////////////////////////////////

	#********************************************** Sell Test:
	logging.info('****** Sell:')
	if ga_result_sell['methode'][0] is not 'no_trade':
		if ga_result_sell['methode'][0] == 'pr':
			name_stp_pr = True
			name_stp_minmax = False
		elif ga_result_sell['methode'][0] == 'min_max':
			name_stp_pr = False
			name_stp_minmax = True

		buy_data,sell_data = golden_cross_zero(dataset=dataset,dataset_15M=dataset_15M,symbol=symbol,
			Low_Period=ga_result_sell['low_period'][0],High_Period=ga_result_sell['high_period'][0],
			distance_lines=ga_result_sell['distance_lines'][0],mode='optimize',
			name_stp_minmax=name_stp_minmax,name_stp_pr=name_stp_pr,plot=False)

		#*********************** Min Max Methode:
		if ga_result_sell['methode'][0] == 'min_max':
			list_index_ok = np.where(((sell_data['ramp_high'].to_numpy()<=ga_result_sell['ramp_high_upper_min_max'][0]))&
				((sell_data['ramp_low'].to_numpy()<=ga_result_sell['ramp_low_upper_min_max'][0]))&
				((sell_data['diff_min_max_cci'].to_numpy()<=ga_result_sell['diff_min_max_cci_upper_min_max'][0]))&
				((sell_data['diff_min_max_candle'].to_numpy()<=ga_result_sell['diff_min_max_candle_upper_min_max'][0]))
				)[0]

			output_sell = pd.DataFrame()
			output_sell['mean_tp_min_max'] = [np.mean(sell_data['tp_min_max'][list_index_ok])]
			output_sell['mean_st_min_max'] = [np.mean(sell_data['st_min_max'][list_index_ok])]
			output_sell['max_tp_min_max'] = [np.max(sell_data['tp_min_max'][list_index_ok])]
			output_sell['max_st_min_max'] = [np.max(sell_data['st_min_max'][list_index_ok])]
			output_sell['sum_st_min_max'] = [np.sum(sell_data['st_min_max'][np.where(sell_data['flag_min_max'][list_index_ok] == 'st')[0]].to_numpy())]
			output_sell['sum_tp_min_max'] = [np.sum(sell_data['tp_min_max'][np.where(sell_data['flag_min_max'][list_index_ok] == 'tp')[0]].to_numpy())]
	
			tp_counter = 0
			st_counter = 0
			for elm in sell_data['flag_min_max'][list_index_ok]:
				if (elm == 'tp'):
					tp_counter += 1
				if (elm == 'st'):
					st_counter += 1
			output_sell['num_tp_min_max'] = [tp_counter]
			output_sell['num_st_min_max'] = [st_counter]
			output_sell['num_trade_min_max'] = [st_counter + tp_counter]

			if output_sell['num_trade_min_max'][0] != 0:
				score_num_tp = (tp_counter/output_sell['num_trade_min_max'][0])
			else:
				score_num_tp = 0

			if output_sell['max_st_min_max'][0] != 0:
				score_max_tp = (output_sell['max_tp_min_max'][0]/output_sell['max_st_min_max'][0])
			else:
				score_max_tp = output_sell['max_tp_min_max'][0]
				if (output_sell['max_tp_min_max'][0] != 0):
					score_max_tp = output_sell['max_tp_min_max'][0] * 10

			if (output_sell['mean_st_min_max'][0] != 0):
				score_mean_tp = (output_sell['mean_tp_min_max'][0]/output_sell['mean_st_min_max'][0])
			else:
				score_mean_tp = output_sell['mean_tp_min_max'][0]
				if (output_sell['mean_tp_min_max'][0] != 0):
					score_mean_tp = output_sell['mean_tp_min_max'][0] * 10

			if (output_sell['sum_st_min_max'][0] != 0):
				score_sum_tp = (output_sell['sum_tp_min_max'][0]/output_sell['sum_st_min_max'][0])
			else:
				score_sum_tp = output_sell['sum_tp_min_max'][0]
				if (output_sell['sum_tp_min_max'][0] != 0):
					score_sum_tp = output_sell['sum_tp_min_max'][0] * 10

			output_sell['score_min_max'] = [(score_num_tp*score_max_tp*score_mean_tp*score_sum_tp)]

			if np.isnan(output_sell['score_min_max'][0]) : output_sell['score_min_max'][0] = 0

			logging.info('mean_tp_min_max= {}'.format(output_sell['mean_tp_min_max'][0]))
			logging.info('mean_st_min_max= {}'.format(output_sell['mean_st_min_max'][0]))
			logging.info('max_tp_min_max= {}'.format(output_sell['max_tp_min_max'][0]))
			logging.info('max_st_min_max= {}'.format(output_sell['max_st_min_max'][0]))
			logging.info('sum_st_min_max= {}'.format(output_sell['sum_st_min_max'][0]))
			logging.info('sum_tp_min_max= {}'.format(output_sell['sum_tp_min_max'][0]))
			logging.info('num_tp_min_max= {}'.format(output_sell['num_tp_min_max'][0]))
			logging.info('num_st_min_max= {}'.format(output_sell['num_st_min_max'][0]))
			logging.info('num_trade_min_max= {}'.format(output_sell['num_trade_min_max'][0]))
			logging.info('score_min_max= {}'.format(output_sell['score_min_max'][0]))
			logging.info('score_min_max ga= {}'.format(ga_result_sell['score_min_max'][0]))

			if output_sell['score_min_max'][0] >= ga_result_sell['score_min_max'][0]: 
				ga_result_sell['permit'] = True
				ga_result_sell.to_csv(sell_path)
			else:
				ga_result_sell['permit'] = False
				ga_result_sell.to_csv(sell_path)

		#/////////////////////////////////////////

		#*********************** PR Methode:
		if ga_result_sell['methode'][0] == 'pr':
			list_index_ok = np.where(((sell_data['ramp_low'].to_numpy()<=ga_result_sell['ramp_low_upper_pr'][0]))&
				((sell_data['ramp_high'].to_numpy()<=ga_result_sell['ramp_high_upper_pr'][0]))&
				((sell_data['diff_pr_top'].to_numpy()<=ga_result_sell['diff_top_upper_pr'][0]))&
				((sell_data['diff_pr_down'].to_numpy()<=ga_result_sell['diff_down_upper_pr'][0]))&
				((sell_data['diff_min_max_cci'].to_numpy()<=ga_result_sell['diff_min_max_cci_upper_pr'][0]))&
				((sell_data['diff_min_max_candle'].to_numpy()<=ga_result_sell['diff_min_max_candle_upper_pr'][0]))
				)[0]

			output_sell = pd.DataFrame()
			output_sell['mean_tp_pr'] = [np.mean(sell_data['tp_pr'][list_index_ok])]
			output_sell['mean_st_pr'] = [np.mean(sell_data['st_pr'][list_index_ok])]
			output_sell['max_tp_pr'] = [np.max(sell_data['tp_pr'][list_index_ok])]
			output_sell['max_st_pr'] = [np.max(sell_data['st_pr'][list_index_ok])]
			output_sell['sum_st_pr'] = [np.sum(sell_data['st_pr'][np.where(sell_data['flag_pr'][list_index_ok] == 'st')[0]].to_numpy())]
			output_sell['sum_tp_pr'] = [np.sum(sell_data['tp_pr'][np.where(sell_data['flag_pr'][list_index_ok] == 'tp')[0]].to_numpy())]
	
			tp_counter = 0
			st_counter = 0
			for elm in sell_data['flag_pr'][list_index_ok]:
				if (elm == 'tp'):
					tp_counter += 1
				if (elm == 'st'):
					st_counter += 1
			output_sell['num_tp_pr'] = [tp_counter]
			output_sell['num_st_pr'] = [st_counter]
			output_sell['num_trade_pr'] = [st_counter + tp_counter]

			if output_sell['num_trade_pr'][0] != 0:
				score_num_tp = (tp_counter/output_sell['num_trade_pr'][0])
			else:
				score_num_tp = 0

			if output_sell['max_st_pr'][0] != 0:
				score_max_tp = (output_sell['max_tp_pr'][0]/output_sell['max_st_pr'][0])
			else:
				score_max_tp = output_sell['max_tp_pr'][0]
				if (output_sell['max_tp_pr'][0] != 0):
					score_max_tp = output_sell['max_tp_pr'][0] * 10

			if (output_sell['mean_st_pr'][0] != 0):
				score_mean_tp = (output_sell['mean_tp_pr'][0]/output_sell['mean_st_pr'][0])
			else:
				score_mean_tp = output_sell['mean_tp_pr'][0]
				if (output_sell['mean_tp_pr'][0] != 0):
					score_mean_tp = output_sell['mean_tp_pr'][0] * 10

			if (output_sell['sum_st_pr'][0] != 0):
				score_sum_tp = (output_sell['sum_tp_pr'][0]/output_sell['sum_st_pr'][0])
			else:
				score_sum_tp = output_sell['sum_tp_pr'][0]
				if (output_sell['sum_tp_pr'][0] != 0):
					score_sum_tp = output_sell['sum_tp_pr'][0] * 10

			output_sell['score_pr'] = [(score_num_tp*score_max_tp*score_mean_tp*score_sum_tp)]

			if np.isnan(output_sell['score_pr'][0]) : output_sell['score_pr'][0] = 0

			logging.info('mean_tp_pr= {}'.format(output_sell['mean_tp_pr'][0]))
			logging.info('mean_st_pr= {}'.format(output_sell['mean_st_pr'][0]))
			logging.info('max_tp_pr= {}'.format(output_sell['max_tp_pr'][0]))
			logging.info('max_st_pr= {}'.format(output_sell['max_st_pr'][0]))
			logging.info('sum_st_pr= {}'.format(output_sell['sum_st_pr'][0]))
			logging.info('sum_tp_pr= {}'.format(output_sell['sum_tp_pr'][0]))
			logging.info('num_tp_pr= {}'.format(output_sell['num_tp_pr'][0]))
			logging.info('num_st_pr= {}'.format(output_sell['num_st_pr'][0]))
			logging.info('num_trade_pr= {}'.format(output_sell['num_trade_pr'][0]))
			logging.info('score_pr= {}'.format(output_sell['score_pr'][0]))
			logging.info('score_pr ga= {}'.format(ga_result_sell['score_pr'][0]))

			if output_sell['score_pr'][0] >= ga_result_sell['score_pr'][0]:
				ga_result_sell['permit'] = True
				ga_result_sell.to_csv(sell_path)
			else:
				ga_result_sell['permit'] = False
				ga_result_sell.to_csv(sell_path)
		#////////////////////////////////////////
	logging.info('//////////////////////////////////////////')

#///////////////////////////////////////////////////////////////////////////////////////////////////////

#******************************** Last Signal Out ******************************************************

def last_signal(dataset,dataset_15M,symbol):
	""" Last signal out """
	buy_path = "Genetic_cci_output_buy/" + symbol + '.csv'
	sell_path = "Genetic_cci_output_sell/" + symbol + '.csv'

	signal = pd.DataFrame()

	if os.path.exists(buy_path):
		ga_result_buy = pd.read_csv(buy_path)
		ga_result_sell = pd.read_csv(sell_path)
	else:
		signal['signal'] = ['no_trade']
		return signal

	#**************** Buy Check:
	if ga_result_buy['permit'][0]:
		buy_data, _ = golden_cross_zero(dataset=dataset,dataset_15M=dataset,symbol=symbol,
			Low_Period=ga_result_buy['low_period'][0],High_Period=ga_result_buy['high_period'][0],
			distance_lines=ga_result_buy['distance_lines'][0],mode='online',
			name_stp_minmax=False,name_stp_pr=False,plot=False)
		lst_idx_buy = buy_data['index'].iloc[-1]
	else:
		lst_idx_buy = 0
	#**************** Sell Check:
	if ga_result_sell['permit'][0]:
		_, sell_data = golden_cross_zero(dataset=dataset,dataset_15M=dataset,symbol=symbol,
			Low_Period=ga_result_sell['low_period'][0],High_Period=ga_result_sell['high_period'][0],
			distance_lines=ga_result_sell['distance_lines'][0],mode='online',
			name_stp_minmax=False,name_stp_pr=False,plot=False)
		lst_idx_sell = sell_data['index'].iloc[-1]
	else:
		lst_idx_sell = 0

	#***************** Calculate PR:
	if ga_result_buy['methode'][0] == 'pr' and lst_idx_buy != 0:

		dataset_pr_5M = pd.DataFrame()
		dataset_pr_15M = pd.DataFrame()
		cut_first = 0
		if (lst_idx_buy > 2000):
			cut_first = lst_idx_buy - 2000
		dataset_pr_5M['low'] = dataset[symbol]['low'][cut_first:lst_idx_buy].reset_index(drop=True)
		dataset_pr_5M['high'] = dataset[symbol]['high'][cut_first:lst_idx_buy].reset_index(drop=True)
		dataset_pr_5M['close'] = dataset[symbol]['close'][cut_first:lst_idx_buy].reset_index(drop=True)
		dataset_pr_5M['open'] = dataset[symbol]['open'][cut_first:lst_idx_buy].reset_index(drop=True)

		dataset_pr_15M['low'] = dataset_15M[symbol]['low'][int(cut_first/3):int(lst_idx_buy/3)].reset_index(drop=True)
		dataset_pr_15M['high'] = dataset_15M[symbol]['high'][int(cut_first/3):int(lst_idx_buy/3)].reset_index(drop=True)
		dataset_pr_15M['close'] = dataset_15M[symbol]['close'][int(cut_first/3):int(lst_idx_buy/3)].reset_index(drop=True)
		dataset_pr_15M['open'] = dataset_15M[symbol]['open'][int(cut_first/3):int(lst_idx_buy/3)].reset_index(drop=True)

		res_pro = pd.DataFrame()
		try:
			res_pro = protect_resist(T_5M=True,T_15M=True,T_1H=False,T_4H=False,T_1D=False,dataset_5M=dataset_pr_5M,dataset_15M=dataset_pr_15M,dataset_1H=dataset,dataset_4H=dataset,dataset_1D=dataset,plot=False)
		except:
			res_pro['high'] = 'nan'
			res_pro['low'] = 'nan'
			res_pro['power_high'] = 0
			res_pro['power_low'] = 0

		if (res_pro.empty == False):
			diff_pr_top_buy = (((res_pro['high'][0] * 0.9994) - dataset[symbol]['high'][lst_idx_buy])/dataset[symbol]['high'][lst_idx_buy]) * 100
			diff_pr_down_buy = ((dataset[symbol]['low'][lst_idx_buy] - (res_pro['low'][2] * 0.9994))/dataset[symbol]['low'][lst_idx_buy]) * 100
			diff_pr_top_buy_power = np.mean(res_pro['power_high'])
			diff_pr_down_buy_power = np.mean(res_pro['power_low'])

	if ga_result_sell['methode'][0] == 'pr' and lst_idx_sell != 0:

		dataset_pr_5M = pd.DataFrame()
		dataset_pr_15M = pd.DataFrame()
		cut_first = 0
		if (lst_idx_sell > 2000):
			cut_first = lst_idx_sell - 2000
		dataset_pr_5M['low'] = dataset[symbol]['low'][cut_first:lst_idx_sell].reset_index(drop=True)
		dataset_pr_5M['high'] = dataset[symbol]['high'][cut_first:lst_idx_sell].reset_index(drop=True)
		dataset_pr_5M['close'] = dataset[symbol]['close'][cut_first:lst_idx_sell].reset_index(drop=True)
		dataset_pr_5M['open'] = dataset[symbol]['open'][cut_first:lst_idx_sell].reset_index(drop=True)

		dataset_pr_15M['low'] = dataset_15M[symbol]['low'][int(cut_first/3):int(lst_idx_sell/3)].reset_index(drop=True)
		dataset_pr_15M['high'] = dataset_15M[symbol]['high'][int(cut_first/3):int(lst_idx_sell/3)].reset_index(drop=True)
		dataset_pr_15M['close'] = dataset_15M[symbol]['close'][int(cut_first/3):int(lst_idx_sell/3)].reset_index(drop=True)
		dataset_pr_15M['open'] = dataset_15M[symbol]['open'][int(cut_first/3):int(lst_idx_sell/3)].reset_index(drop=True)

		res_pro = pd.DataFrame()
		try:
			res_pro = protect_resist(T_5M=True,T_15M=True,T_1H=False,T_4H=False,T_1D=False,dataset_5M=dataset_pr_5M,dataset_15M=dataset_pr_15M,dataset_1H=dataset,dataset_4H=dataset,dataset_1D=dataset,plot=False)
		except:
			res_pro['high'] = 'nan'
			res_pro['low'] = 'nan'
			res_pro['power_high'] = 0
			res_pro['power_low'] = 0

		if (res_pro.empty == False):
			diff_pr_top_sell = (((res_pro['high'][0] * 1.0006) - dataset[symbol]['high'][lst_idx_sell])/dataset[symbol]['high'][lst_idx_sell]) * 100
			diff_pr_down_sell = ((dataset[symbol]['low'][lst_idx_sell] - (res_pro['low'][0] * 1.0006))/dataset[symbol]['low'][lst_idx_sell]) * 100
			diff_pr_top_sell_power = np.mean(res_pro['power_high'])
			diff_pr_down_sell_power = np.mean(res_pro['power_low'])

	#***** Last Signal:

	if lst_idx_buy > lst_idx_sell and (lst_idx_buy - len(dataset[symbol]['close']) - 1) <= 1:

		if ga_result_buy['methode'][0] == 'pr':

			if (
				buy_data['ramp_low'].iloc[-1]>=ga_result_buy['ramp_low_lower_pr'][0] and
				buy_data['ramp_high'].iloc[-1]>=ga_result_buy['ramp_high_lower_pr'][0] and
				diff_pr_top_buy<=ga_result_buy['diff_top_upper_pr'][0] and
				diff_pr_down_buy<=ga_result_buy['diff_down_upper_pr'][0] and
				buy_data['diff_min_max_cci'].iloc[-1]<=ga_result_buy['diff_min_max_cci_upper_pr'][0] and
				buy_data['diff_min_max_candle'].iloc[-1]<=ga_result_buy['diff_min_max_candle_upper_pr'][0]
				):
				
				signal['signal'] = ['buy']

			else:
				signal['signal'] = ['no_trade']
				
		if ga_result_buy['methode'][0] == 'min_max':

			if (
				buy_data['ramp_high'].iloc[-1]>=ga_result_buy['ramp_high_lower_min_max'][0] and
				buy_data['ramp_low'].iloc[-1]>=ga_result_buy['ramp_low_lower_min_max'][0] and
				buy_data['diff_min_max_cci'].iloc[-1]<ga_result_buy['diff_min_max_cci_upper_min_max'][0] and
				buy_data['diff_min_max_candle'].iloc[-1]<=ga_result_buy['diff_min_max_candle_upper_min_max'][0]
				):

				signal['signal'] = ['buy']

			else:
				signal['signal'] = ['no_trade']

	elif lst_idx_buy < lst_idx_sell and (lst_idx_sell - len(dataset[symbol]['close']) - 1) <= 1:
		
		if ga_result_sell['methode'][0] == 'pr':
			if (
				sell_data['ramp_low'].iloc[-1]<=ga_result_sell['ramp_low_upper_pr'][0] and
				sell_data['ramp_high'].iloc[-1]<=ga_result_sell['ramp_high_upper_pr'][0] and
				diff_pr_top_sell<=ga_result_sell['diff_top_upper_pr'][0] and
				diff_pr_down_sell<=ga_result_sell['diff_down_upper_pr'][0] and
				sell_data['diff_min_max_cci'].iloc[-1]<=ga_result_sell['diff_min_max_cci_upper_pr'][0] and
				sell_data['diff_min_max_candle'].iloc[-1]<=ga_result_sell['diff_min_max_candle_upper_pr'][0]
				):

				signal['signal'] = ['sell']

			else:
				signal['signal'] = ['no_trade']
				

		if ga_result_sell['methode'][0] == 'min_max':
			if (
				sell_data['ramp_high'].iloc[-1]<=ga_result_sell['ramp_high_upper_min_max'][0] and
				sell_data['ramp_low'].iloc[-1]<=ga_result_sell['ramp_low_upper_min_max'][0] and
				sell_data['diff_min_max_cci'].iloc[-1]<=ga_result_sell['diff_min_max_cci_upper_min_max'][0] and
				sell_data['diff_min_max_candle'].iloc[-1]<=ga_result_sell['diff_min_max_candle_upper_min_max'][0]
				):

				signal['signal'] = ['sell']

			else:
				signal['signal'] = ['no_trade']

	else:
		signal['signal'] = ['no_trade']

	return signal

#//////////////////////////////////////////////////////////////////////////////////////////////////////

#*************************** How To Use Funcs *****************************************
symbol_data_5M,money,symbol = log_get_data_Genetic(mt5.TIMEFRAME_M5,0,6000)
symbol_data_15M,money,symbol = log_get_data_Genetic(mt5.TIMEFRAME_M15,0,2000)
print('data get')

symbol_black_list = np.array(
	[
		'WSt30_m_i','SPX500_m_i','NQ100_m_i','GER40_m_i',
		'GER40_i','USDRUR','USDRUR_i','USDRUB','USDRUB_i',
		'USDHKD','WTI_i','BRN_i','STOXX50_i','NQ100_i',
		'NG_i','HSI50_i','CAC40_i','ASX200_i','SPX500_i',
		'NIKK225_i','IBEX35_i','FTSE100_i','RUBRUR',
		'EURDKK_i','DAX30_i','XRPUSD_i','XBNUSD_i',
		'LTCUSD_i','ETHUSD_i','BTCUSD_i','_DXY','_DJI',
		'EURTRY_i','USDTRY_i','USDDKK_i'
	])

for sym in symbol:
	if np.where(sym.name == symbol_black_list)[0].size != 0: continue
	#genetic_buy_algo(symbol_data_5M=symbol_data_5M,symbol_data_15M=symbol_data_15M,symbol=sym.name,num_turn=400,max_score=5)

symbol_data_5M,money,symbol = log_get_data_Genetic(mt5.TIMEFRAME_M5,0,2100)
symbol_data_15M,money,symbol = log_get_data_Genetic(mt5.TIMEFRAME_M15,0,700)

for sym in symbol:
	if np.where(sym.name == symbol_black_list)[0].size != 0: continue
	#one_year_golden_cross_tester(dataset=symbol_data_5M,dataset_15M=symbol_data_15M,symbol=sym.name)
print(last_signal(dataset=symbol_data_5M,dataset_15M=symbol_data_15M,symbol='AUDCAD_i'))

