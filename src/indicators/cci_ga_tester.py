from cci import genetic_algo_cci_golden_cross,one_year_golden_cross_tester, read_ga_result, golden_cross_tester_for_permit
from log_get_data import read_dataset_csv, get_symbols
from datetime import datetime
from random import randint
import MetaTrader5 as mt5
from random import seed
import pandas as pd
import numpy as np
import threading
import logging
import sys
import os


#ga_runner()
#dataset_spliter()
#ga_optimizer_buy()
#ga_tester_buy()
#learning_buy()
#ga_optimizer_sell()
#ga_tester_sell()
#learning_sell()

#**************************************** Logger *****************
now = datetime.now()
log_path = 'log/cci/golden_cross_zero/optimizer-{}-{}-{}-{}-{}-{}.log'.format(now.year, now.month, now.day, now.hour, now.minute, now.second)
log_level = 'info'
logger = logging.getLogger()

if not os.path.exists(os.path.dirname(log_path)):
    os.makedirs(os.path.dirname(log_path))

if log_level == 'info':
    logger.setLevel(logging.INFO)
elif log_level == 'warning':
    logger.setLevel(logging.WARNING)
elif log_level == 'debug':
    logger.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
formatter = logging.Formatter('%(asctime)s | %(message)s')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

file_handler = logging.FileHandler(log_path)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)


logger.addHandler(file_handler)
logger.addHandler(stdout_handler)


def logs(message):
    logger.info(message)

#/////////////////////////////////////////////////////////////////////////////////////////////////////////


def dataset_spliter(
					symbol,
					dataset_5M,
					dataset_1H,
					spliter_5M_end,
					spliter_5M_first
					):
	symbol_data_5M = pd.DataFrame()
	symbol_data_1H = pd.DataFrame()

	symbol_data_5M = {
						symbol: dataset_5M[symbol].copy()
						}

	symbol_data_5M[symbol]['low'] = dataset_5M[symbol]['low'][spliter_5M_first:spliter_5M_end].reset_index(drop=True)
	symbol_data_5M[symbol]['high'] = dataset_5M[symbol]['high'][spliter_5M_first:spliter_5M_end].reset_index(drop=True)
	symbol_data_5M[symbol]['close'] = dataset_5M[symbol]['close'][spliter_5M_first:spliter_5M_end].reset_index(drop=True)
	symbol_data_5M[symbol]['open'] = dataset_5M[symbol]['open'][spliter_5M_first:spliter_5M_end].reset_index(drop=True)
	symbol_data_5M[symbol]['HL/2'] = dataset_5M[symbol]['HL/2'][spliter_5M_first:spliter_5M_end].reset_index(drop=True)
	symbol_data_5M[symbol]['HLC/3'] = dataset_5M[symbol]['HLC/3'][spliter_5M_first:spliter_5M_end].reset_index(drop=True)
	symbol_data_5M[symbol]['HLCC/4'] = dataset_5M[symbol]['HLCC/4'][spliter_5M_first:spliter_5M_end].reset_index(drop=True)
	symbol_data_5M[symbol]['OHLC/4'] = dataset_5M[symbol]['OHLC/4'][spliter_5M_first:spliter_5M_end].reset_index(drop=True)
	symbol_data_5M[symbol]['volume'] = dataset_5M[symbol]['volume'][spliter_5M_first:spliter_5M_end].reset_index(drop=True)
	symbol_data_5M[symbol]['time'] = dataset_5M[symbol]['time'][spliter_5M_first:spliter_5M_end].reset_index(drop=True)

	loc_1H = 0
	location_1H = -1
	for ti in dataset_1H[symbol]['time']:
		#print('1H===> ',ti.year)
		if (
			ti.year == symbol_data_5M[symbol]['time'].iloc[-1].year and
			ti.month == symbol_data_5M[symbol]['time'].iloc[-1].month and
			ti.day == symbol_data_5M[symbol]['time'].iloc[-1].day and
			ti.hour == symbol_data_5M[symbol]['time'].iloc[-1].hour
			):
			location_1H = loc_1H

		loc_1H += 1

	symbol_data_1H = {
						symbol: dataset_1H[symbol].copy()
						}

	symbol_data_1H[symbol]['low'] = dataset_1H[symbol]['low'][0:location_1H].reset_index(drop=True)
	symbol_data_1H[symbol]['high'] = dataset_1H[symbol]['high'][0:location_1H].reset_index(drop=True)
	symbol_data_1H[symbol]['close'] = dataset_1H[symbol]['close'][0:location_1H].reset_index(drop=True)
	symbol_data_1H[symbol]['open'] = dataset_1H[symbol]['open'][0:location_1H].reset_index(drop=True)
	symbol_data_1H[symbol]['HL/2'] = dataset_1H[symbol]['HL/2'][0:location_1H].reset_index(drop=True)
	symbol_data_1H[symbol]['HLC/3'] = dataset_1H[symbol]['HLC/3'][0:location_1H].reset_index(drop=True)
	symbol_data_1H[symbol]['HLCC/4'] = dataset_1H[symbol]['HLCC/4'][0:location_1H].reset_index(drop=True)
	symbol_data_1H[symbol]['OHLC/4'] = dataset_1H[symbol]['OHLC/4'][0:location_1H].reset_index(drop=True)
	symbol_data_1H[symbol]['volume'] = dataset_1H[symbol]['volume'][0:location_1H].reset_index(drop=True)
	symbol_data_1H[symbol]['time'] = dataset_1H[symbol]['time'][0:location_1H].reset_index(drop=True)

	return symbol_data_5M, symbol_data_1H

def ga_runner(
				symbol_data_5M,
				symbol_data_15M,
				symbol_data_1H,
				symbol_data_4H,
				symbol,
				num_turn,
				max_score_ga_buy,
				max_score_ga_sell,
				flag_trade='buy'
				):

	try:
		genetic_algo_cci_golden_cross(
									symbol_data_5M=symbol_data_5M,
									symbol_data_15M=symbol_data_15M,
									dataset_1H=symbol_data_1H,
									dataset_4H=symbol_data_4H,
									symbol=symbol,
									num_turn=num_turn,
									max_score_ga_buy=max_score_ga_buy,
									max_score_ga_sell=max_score_ga_sell,
									flag_trade=flag_trade
									)
		pass
	except Exception as ex:
		print('getting error GA Runner: ', ex)


def ga_optimizer_buy():

	logs('=========> ga optimizer buy')

	symbols,my_money = get_symbols(mt5.TIMEFRAME_M1)

	for sym in symbols:

		if not (
			#sym.name == 'AUDCAD_i' or
			#sym.name == 'AUDCHF_i' or
			sym.name == my_sym or
			#sym.name == 'CADJPY_i' or
			#sym.name == 'EURAUD_i' or
			#sym.name == 'EURCAD_i' or
			#sym.name == 'EURCHF_i' or
			#sym.name == 'EURGBP_i' or
			#sym.name == 'EURUSD_i' or
			#sym.name == 'EURJPY_i' or
			#sym.name == 'GBPAUD_i' or
			#sym.name == 'GBPCAD_i' or
			#sym.name == 'GBPJPY_i' or
			#sym.name == 'GBPUSD_i' or
			#sym.name == 'USDJPY_i' or
			#sym.name == 'USDCAD_i' or
			sym.name == 'XAUUSD_i'
			): continue

		if sym.name != my_sym: continue



		learn_counter = 0
		while learn_counter < 1:


			low_distance = randint((learn_counter*12850), ((learn_counter*12850) + 12850))
			high_distance = randint((learn_counter*12850), ((learn_counter*12850) + 12850))
			if high_distance < low_distance: continue
			if high_distance - low_distance != 10000: continue
			logs('high_distance buy = {}'.format(high_distance))
			logs('low_distance buy = {}'.format(low_distance))

			logs('====== my_sym optimizer buy ====> {}'.format(my_sym))

			logs('************** ============= AI Buy ==========> {}'.format(learn_counter))

			dataset_5M, symbol_data_15M, dataset_1H, symbol_data_4H, symbol = read_dataset_csv(
																								sym=sym.name,
																								num_5M=99000,
																								num_15M=1,
																								num_1H=8250,
																								num_4H=1
																								)
			symbol_data_5M,symbol_data_1H = dataset_spliter(
														symbol=sym.name,
														dataset_5M=dataset_5M,
														dataset_1H=dataset_1H,
														spliter_5M_end=high_distance,
														spliter_5M_first=low_distance
														)

			buy_path = "Genetic_cci_output_buy/" + sym.name + '.csv'
			
			logs('*************> {}'.format(sym.name))

			if not os.path.exists(buy_path):
				ga_runner(
						symbol_data_5M=symbol_data_5M,
						symbol_data_15M=symbol_data_15M,
						symbol_data_1H=symbol_data_1H,
						symbol_data_4H=symbol_data_4H,
						symbol=sym.name,
						num_turn=8000,
						max_score_ga_buy=70,
						max_score_ga_sell=70,
						flag_trade='buy'
						)
			else:
				if learn_counter > 1: 
					num_turn = 40
				else:
					num_turn = 200
				ga_runner(
						symbol_data_5M=symbol_data_5M,
						symbol_data_15M=symbol_data_15M,
						symbol_data_1H=symbol_data_1H,
						symbol_data_4H=symbol_data_4H,
						symbol=sym.name,
						num_turn=num_turn,
						max_score_ga_buy=10,
						max_score_ga_sell=10,
						flag_trade='buy'
						)

			#print('======= learn_counter buy ====> ',learn_counter)

			learn_counter += 1

def ga_tester_buy():

	logs('===========> ga tester buy')

	symbols,my_money = get_symbols(mt5.TIMEFRAME_M1)

	for sym in symbols:

		if not (
			#sym.name == 'AUDCAD_i' or
			#sym.name == 'AUDCHF_i' or
			sym.name == my_sym or
			#sym.name == 'CADJPY_i' or
			#sym.name == 'EURAUD_i' or
			#sym.name == 'EURCAD_i' or
			#sym.name == 'EURCHF_i' or
			#sym.name == 'EURGBP_i' or
			#sym.name == 'EURUSD_i' or
			#sym.name == 'EURJPY_i' or
			#sym.name == 'GBPAUD_i' or
			#sym.name == 'GBPCAD_i' or
			#sym.name == 'GBPJPY_i' or
			#sym.name == 'GBPUSD_i' or
			#sym.name == 'USDJPY_i' or
			#sym.name == 'USDCAD_i' or
			sym.name == 'XAUUSD_i'
			): continue

		if sym.name != my_sym: continue
		logs('====== my_sym tester buy ====> {}'.format(my_sym))

		buy_path = "Genetic_cci_output_buy/" + sym.name + '.csv'

		if os.path.exists(buy_path):
			logs('*********** Tester Buy *')

			ga_result_buy, _ = read_ga_result(symbol=sym.name)

			if 'permit' not in ga_result_buy.columns:


				symbol_data_5M, symbol_data_15M, symbol_data_1H, symbol_data_4H, symbol = read_dataset_csv(
																										sym=sym.name,
																										num_5M=9000,
																										num_15M=1,
																										num_1H=8000,
																										num_4H=1
																										)
				golden_cross_tester_for_permit(
												dataset=symbol_data_5M,
												dataset_15M=symbol_data_15M,
												symbol_data_1H=symbol_data_1H,
												symbol_data_4H=symbol_data_4H,
												symbol=sym.name,
												flag_trade='buy'
												)

			ga_result_buy, _ = read_ga_result(symbol=sym.name)
			if 'permit' in ga_result_buy.columns:
				while ga_result_buy['permit'][0] != True:
					ga_optimizer_buy()
					ga_tester_buy()


def ga_optimizer_sell():

	logs('===========> ga optimizer sell')

	symbols,my_money = get_symbols(mt5.TIMEFRAME_M1)

	for sym in symbols:

		if not (
			#sym.name == 'AUDCAD_i' or
			#sym.name == 'AUDCHF_i' or
			sym.name == my_sym or
			#sym.name == 'CADJPY_i' or
			#sym.name == 'EURAUD_i' or
			#sym.name == 'EURCAD_i' or
			#sym.name == 'EURCHF_i' or
			#sym.name == 'EURGBP_i' or
			#sym.name == 'EURUSD_i' or
			#sym.name == 'EURJPY_i' or
			#sym.name == 'GBPAUD_i' or
			#sym.name == 'GBPCAD_i' or
			#sym.name == 'GBPJPY_i' or
			#sym.name == 'GBPUSD_i' or
			#sym.name == 'USDJPY_i' or
			#sym.name == 'USDCAD_i' or
			sym.name == 'XAUUSD_i'
			): continue

		if sym.name != my_sym: continue

		learn_counter = 0
		while learn_counter < 1:

			low_distance = randint((learn_counter*12850), ((learn_counter*12850) + 12850))
			high_distance = randint((learn_counter*12850), ((learn_counter*12850) + 12850))
			if high_distance < low_distance: continue
			if high_distance - low_distance != 10000: continue
			logs('high_distance sell = {}'.format(high_distance))
			print('low_distance sell = {}'.format(low_distance))

			logs('====== my_sym optimizer sell ====> {}'.format(my_sym))

			logs('************** ============= AI Sell ==========> {}'.format(learn_counter))

			dataset_5M, symbol_data_15M, dataset_1H, symbol_data_4H, symbol = read_dataset_csv(
																								sym=sym.name,
																								num_5M=99000,
																								num_15M=1,
																								num_1H=8250,
																								num_4H=1
																								)
			symbol_data_5M,symbol_data_1H = dataset_spliter(
														symbol=sym.name,
														dataset_5M=dataset_5M,
														dataset_1H=dataset_1H,
														spliter_5M_end=high_distance,
														spliter_5M_first=low_distance
														)

			sell_path = "Genetic_cci_output_sell/" + sym.name + '.csv'
			
			logs('*************> {}'.format(sym.name))

			if not os.path.exists(sell_path):
				ga_runner(
						symbol_data_5M=symbol_data_5M,
						symbol_data_15M=symbol_data_15M,
						symbol_data_1H=symbol_data_1H,
						symbol_data_4H=symbol_data_4H,
						symbol=sym.name,
						num_turn=8000,
						max_score_ga_buy=70,
						max_score_ga_sell=70,
						flag_trade='sell'
						)
			else:
				if learn_counter > 1: 
					num_turn = 40
				else:
					num_turn = 200
				ga_runner(
						symbol_data_5M=symbol_data_5M,
						symbol_data_15M=symbol_data_15M,
						symbol_data_1H=symbol_data_1H,
						symbol_data_4H=symbol_data_4H,
						symbol=sym.name,
						num_turn=num_turn,
						max_score_ga_buy=10,
						max_score_ga_sell=10,
						flag_trade='sell'
						)


			learn_counter += 1

def ga_tester_sell():

	logs('===========> ga tester sell')

	symbols,my_money = get_symbols(mt5.TIMEFRAME_M1)

	for sym in symbols:

		if not (
			#sym.name == 'AUDCAD_i' or
			#sym.name == 'AUDCHF_i' or
			sym.name == my_sym or
			#sym.name == 'CADJPY_i' or
			#sym.name == 'EURAUD_i' or
			#sym.name == 'EURCAD_i' or
			#sym.name == 'EURCHF_i' or
			#sym.name == 'EURGBP_i' or
			#sym.name == 'EURUSD_i' or
			#sym.name == 'EURJPY_i' or
			#sym.name == 'GBPAUD_i' or
			#sym.name == 'GBPCAD_i' or
			#sym.name == 'GBPJPY_i' or
			#sym.name == 'GBPUSD_i' or
			#sym.name == 'USDJPY_i' or
			#sym.name == 'USDCAD_i' or
			sym.name == 'XAUUSD_i'
			): continue

		if sym.name != my_sym: continue

		logs('====== my_sym tester sell ====> {}'.format(my_sym))

		sell_path = "Genetic_cci_output_sell/" + sym.name + '.csv'

		if os.path.exists(sell_path):
			logs('*********** tester Permit Sell *')

			_, ga_result_sell = read_ga_result(symbol=sym.name)

			if 'permit' not in ga_result_sell.columns:


				symbol_data_5M, symbol_data_15M, symbol_data_1H, symbol_data_4H, symbol = read_dataset_csv(
																										sym=sym.name,
																										num_5M=9000,
																										num_15M=1,
																										num_1H=8000,
																										num_4H=1
																										)
				golden_cross_tester_for_permit(
												dataset=symbol_data_5M,
												dataset_15M=symbol_data_15M,
												symbol_data_1H=symbol_data_1H,
												symbol_data_4H=symbol_data_4H,
												symbol=sym.name,
												flag_trade='sell'
												)

			_, ga_result_sell = read_ga_result(symbol=sym.name)
			if 'permit' in ga_result_sell.columns:
				while ga_result_sell['permit'][0] != True:
					ga_optimizer_sell()
					ga_tester_sell()

def learning_buy():

	symbols,my_money = get_symbols(mt5.TIMEFRAME_M1)

	for sym in symbols:

		if not (
			#sym.name == 'AUDCAD_i' or
			#sym.name == 'AUDCHF_i' or
			sym.name == my_sym or
			#sym.name == 'CADJPY_i' or
			#sym.name == 'EURAUD_i' or
			#sym.name == 'EURCAD_i' or
			#sym.name == 'EURCHF_i' or
			#sym.name == 'EURGBP_i' or
			#sym.name == 'EURUSD_i' or
			#sym.name == 'EURJPY_i' or
			#sym.name == 'GBPAUD_i' or
			#sym.name == 'GBPCAD_i' or
			#sym.name == 'GBPJPY_i' or
			#sym.name == 'GBPUSD_i' or
			#sym.name == 'USDJPY_i' or
			#sym.name == 'USDCAD_i' or
			sym.name == 'XAUUSD_i'
			): continue

		if sym.name != my_sym: continue
		dataset_5M, symbol_data_15M, dataset_1H, symbol_data_4H, symbol = read_dataset_csv(
																									sym=sym.name,
																									num_5M=99000,
																									num_15M=1,
																									num_1H=8250,
																									num_4H=1
																									)

		symbol_data_5M,symbol_data_1H = dataset_spliter(
														symbol=sym.name,
														dataset_5M=dataset_5M,
														dataset_1H=dataset_1H,
														spliter_5M_end=90000,
														spliter_5M_first=0
														)


		max_learning_turn = 50
		learn_out = pd.DataFrame(np.zeros(max_learning_turn))
		learn_out['score'] = np.nan
		learn_out['value_min_upper_cci_pr'] = np.nan
		learn_out['power_pr_high'] = np.nan
		learn_out['power_pr_low'] = np.nan
		learn_out['max_st'] = np.nan
		learn_out['max_tp'] = np.nan

		out_buy,_ = one_year_golden_cross_tester(
									dataset=symbol_data_5M,
									dataset_15M=symbol_data_15M,
									symbol_data_1H=symbol_data_1H,
									symbol_data_4H=symbol_data_4H,
									symbol=sym.name,
									flag_trade='buy',
									max_st=1,
									max_tp=1,
									permit_flag=False
									)
		learn_out['score'][0] = out_buy['score_pr'][0]
		learn_out['value_min_upper_cci_pr'][0] = out_buy['value_min_upper_cci_pr'][0]
		learn_out['power_pr_high'][0] = out_buy['power_pr_high'][0]
		learn_out['power_pr_low'][0] = out_buy['power_pr_low'][0]
		learn_out['max_st'][0] = out_buy['max_st'][0]
		learn_out['max_tp'][0] = out_buy['max_tp'][0]

		learning_turn = 1
		alfa = 0.1
		while learning_turn < max_learning_turn:
			logs('========== Leraning Turn ======> {}'.format(learning_turn))
			out_buy,_ = one_year_golden_cross_tester(
									dataset=symbol_data_5M,
									dataset_15M=symbol_data_15M,
									symbol_data_1H=symbol_data_1H,
									symbol_data_4H=symbol_data_4H,
									symbol=sym.name,
									flag_trade='buy',
									alfa=alfa,
									max_st=learn_out['max_st'][learning_turn-1],
									max_tp=learn_out['max_tp'][learning_turn-1],
									permit_flag=False
									)
			if out_buy['score_pr'][0] > learn_out['score'][learning_turn-1]:
				learn_out['score'][learning_turn] = out_buy['score_pr'][0]
				learn_out['value_min_upper_cci_pr'][learning_turn] = out_buy['value_min_upper_cci_pr'][0]
				learn_out['power_pr_high'][learning_turn] = out_buy['power_pr_high'][0]
				learn_out['power_pr_low'][learning_turn] = out_buy['power_pr_low'][0]
				learn_out['max_st'][learning_turn] = out_buy['max_st'][0]
				learn_out['max_tp'][learning_turn] = out_buy['max_tp'][0]
			else:
				alfa = randint(0, 50)/100
				learning_turn += 1
				continue

			learning_turn += 1

		max_score_learn = np.max(learn_out['score'].dropna())
		max_score_learn_index = np.where((learn_out['score']==max_score_learn))[0]

		print('max_score_learn = ',max_score_learn)
		print('max_score_learn_index = ',max_score_learn_index)
		print('learn_out = ',learn_out)

		buy_path = "Genetic_cci_output_buy/" + 'AUDUSD_i' + '.csv'

		if os.path.exists(buy_path):
			ga_result_buy, _ = read_ga_result(symbol=sym.name)

		ga_result_buy['score_learn'] = learn_out['score'][max_score_learn_index]
		ga_result_buy['value_min_upper_cci_pr'] = learn_out['value_min_upper_cci_pr'][max_score_learn_index]
		ga_result_buy['power_pr_high'] = learn_out['power_pr_high'][max_score_learn_index]
		ga_result_buy['power_pr_low'] = learn_out['power_pr_low'][max_score_learn_index]
		ga_result_buy['max_st'] = learn_out['max_st'][max_score_learn_index]
		ga_result_buy['max_tp'] = learn_out['max_tp'][max_score_learn_index]

		if os.path.exists(buy_path):
			os.remove(buy_path)

		ga_result_buy.to_csv(buy_path)

def learning_sell():

	symbols,my_money = get_symbols(mt5.TIMEFRAME_M1)

	for sym in symbols:

		if not (
			#sym.name == 'AUDCAD_i' or
			#sym.name == 'AUDCHF_i' or
			sym.name == my_sym or
			#sym.name == 'CADJPY_i' or
			#sym.name == 'EURAUD_i' or
			#sym.name == 'EURCAD_i' or
			#sym.name == 'EURCHF_i' or
			#sym.name == 'EURGBP_i' or
			#sym.name == 'EURUSD_i' or
			#sym.name == 'EURJPY_i' or
			#sym.name == 'GBPAUD_i' or
			#sym.name == 'GBPCAD_i' or
			#sym.name == 'GBPJPY_i' or
			#sym.name == 'GBPUSD_i' or
			#sym.name == 'USDJPY_i' or
			#sym.name == 'USDCAD_i' or
			sym.name == 'XAUUSD_i'
			): continue

		if sym.name != my_sym: continue
		dataset_5M, symbol_data_15M, dataset_1H, symbol_data_4H, symbol = read_dataset_csv(
																									sym=sym.name,
																									num_5M=99000,
																									num_15M=1,
																									num_1H=8250,
																									num_4H=1
																									)

		symbol_data_5M,symbol_data_1H = dataset_spliter(
														symbol=sym.name,
														dataset_5M=dataset_5M,
														dataset_1H=dataset_1H,
														spliter_5M_end=90000,
														spliter_5M_first=0
														)


		max_learning_turn = 50
		learn_out = pd.DataFrame(np.zeros(max_learning_turn))
		learn_out['score'] = np.nan
		learn_out['value_max_lower_cci_pr'] = np.nan
		learn_out['power_pr_high'] = np.nan
		learn_out['power_pr_low'] = np.nan
		learn_out['max_st'] = np.nan
		learn_out['max_tp'] = np.nan

		_, out_sell = one_year_golden_cross_tester(
									dataset=symbol_data_5M,
									dataset_15M=symbol_data_15M,
									symbol_data_1H=symbol_data_1H,
									symbol_data_4H=symbol_data_4H,
									symbol=sym.name,
									flag_trade='sell',
									max_st=1,
									max_tp=1,
									permit_flag=False
									)
		learn_out['score'][0] = out_sell['score_pr'][0]
		learn_out['value_max_lower_cci_pr'][0] = out_sell['value_max_lower_cci_pr'][0]
		learn_out['power_pr_high'][0] = out_sell['power_pr_high'][0]
		learn_out['power_pr_low'][0] = out_sell['power_pr_low'][0]
		learn_out['max_st'][0] = out_sell['max_st'][0]
		learn_out['max_tp'][0] = out_sell['max_tp'][0]

		learning_turn = 1
		alfa = 0.1
		while learning_turn < max_learning_turn:
			logs('========== Leraning Turn ======> {}'.format(learning_turn))
			_, out_sell = one_year_golden_cross_tester(
									dataset=symbol_data_5M,
									dataset_15M=symbol_data_15M,
									symbol_data_1H=symbol_data_1H,
									symbol_data_4H=symbol_data_4H,
									symbol=sym.name,
									flag_trade='sell',
									alfa=alfa,
									max_st=learn_out['max_st'][learning_turn-1],
									max_tp=learn_out['max_tp'][learning_turn-1],
									permit_flag=False
									)
			if out_sell['score_pr'][0] > learn_out['score'][learning_turn-1]:
				learn_out['score'][learning_turn] = out_sell['score_pr'][0]
				learn_out['value_max_lower_cci_pr'][learning_turn] = out_sell['value_max_lower_cci_pr'][0]
				learn_out['power_pr_high'][learning_turn] = out_sell['power_pr_high'][0]
				learn_out['power_pr_low'][learning_turn] = out_sell['power_pr_low'][0]
				learn_out['max_st'][learning_turn] = out_sell['max_st'][0]
				learn_out['max_tp'][learning_turn] = out_sell['max_tp'][0]
			else:
				alfa = randint(0, 50)/100
				learning_turn += 1
				continue

			learning_turn += 1

		max_score_learn = np.max(learn_out['score'].dropna())
		max_score_learn_index = np.where((learn_out['score']==max_score_learn))[0]

		print('max_score_learn = ',max_score_learn)
		print('max_score_learn_index = ',max_score_learn_index)
		print('learn_out = ',learn_out)

		sell_path = "Genetic_cci_output_sell/" + sym.name + '.csv'

		if os.path.exists(sell_path):
			_, ga_result_sell = read_ga_result(symbol=sym.name)

		ga_result_sell['score_learn'] = learn_out['score'][max_score_learn_index]
		ga_result_sell['value_max_lower_cci_pr'] = learn_out['value_max_lower_cci_pr'][max_score_learn_index]
		ga_result_sell['power_pr_high'] = learn_out['power_pr_high'][max_score_learn_index]
		ga_result_sell['power_pr_low'] = learn_out['power_pr_low'][max_score_learn_index]
		ga_result_sell['max_st'] = learn_out['max_st'][max_score_learn_index]
		ga_result_sell['max_tp'] = learn_out['max_tp'][max_score_learn_index]

		if os.path.exists(sell_path):
			os.remove(sell_path)

		ga_result_sell.to_csv(sell_path)

def Task_optimizer():
	job_thread_buy = threading.Thread(target=ga_optimizer_buy)
	job_thread_buy.start()
	print()
	logs('optimizer job_thread_buy ===> optimizer job_thread_buy runed')

	job_thread_sell = threading.Thread(target=ga_optimizer_sell)
	job_thread_sell.start()
	print()
	logs('optimizer job_thread_sell ===> optimizer job_thread_sell runed')

	
	job_thread_buy.join()
	job_thread_sell.join()

def Task_tester():
	job_thread_buy = threading.Thread(target=ga_tester_buy)
	job_thread_buy.start()
	print()
	logs('tester job_thread_buy ===> tester job_thread_buy runed')

	job_thread_sell = threading.Thread(target=ga_tester_sell)
	job_thread_sell.start()
	print()
	logs('tester job_thread_sell ===> tester job_thread_sell runed')

	
	job_thread_buy.join()
	job_thread_sell.join()


my_sym = 'AUDUSD_i'
#learning_buy()
#ga_tester_buy()

ga_optimizer_buy()
learning_buy()
#ga_tester_buy()

ga_optimizer_sell()
learning_sell()
#ga_tester_sell()


#Task_optimizer()

#Task_tester()
#ga_optimizer_buy()