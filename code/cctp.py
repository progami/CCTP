import smtplib
import pandas as pd
import time
import logging
from datetime import datetime
import decimal
import zmq
from coinmarketcap import Market
from binance.client import Client
# noinspection PyUnresolvedReferences
from sentimentAnalyse import SentimentAnalyse
import warnings
from colorama import init, Fore, Back, Style

init(convert=True)


warnings.filterwarnings("ignore")
log_file = str(time.strftime('%Y %m %d %H')) + ' activity.log'
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')


# TODO: read korean jgl 101 tips
# TODO: explain why this code is so good to client write on pad

# TODO: binance.products()



class Coin:
    def __init__(self, symbol, mode, take_profit,
                 backend, client, sentiment_analyse,
                 interval_list, sma_fast_length, sma_slow_length, user_email, symbol_info):

        # symbol info
        self.symbolPair = symbol
        self.base_currency_symbol = symbol_info['base_asset']
        self.quote_currency_symbol = symbol_info['quote_asset']

        # price, qty and take profit info for trade buy/sell settings
        self.price = float()
        self.quantity = float()
        self.investment = float(symbol_info['investment'])
        self.entry_price = float()
        self.exit_price = float()
        self.min_step = float(symbol_info[8])
        self.round_factor = abs(decimal.Decimal(str(self.min_step)).as_tuple().exponent)
        self.take_profit = take_profit / 100
        self.in_trade = False
        # 1 for automatic - 0 for semi-auto
        self.mode = mode

        # binance client and sentiment class objects
        self.client = client
        self.sentiment_analyse = sentiment_analyse
        self.backend = backend
        self.gui_dict = dict()

        # settings for technical indicator
        self.interval_list = interval_list
        self.sma_fast_length = sma_fast_length
        self.sma_slow_length = sma_slow_length

        # base currency and quote currency balance for checking trades can be done
        try:
            self.base_currency_balance = float(self.client.get_asset_balance(asset=self.base_currency_symbol)['free'])
            self.quote_currency_balance = float(self.client.get_asset_balance(asset=self.quote_currency_symbol)['free'])
        except:
            self.base_currency_balance = 0.0
            self.quote_currency_balance = 0.0
        # sma market position to keep track of status of technical indicator for the coin
        self.sma_market_position = int()
        # track of market sentiment
        self.sentiment = float()
        self.sentiment_list = list()

        # email settings
        self.bot_email = 'patch721lol@gmail.com'
        self.bot_password = 'jarrarammar1'
        self.user_email = user_email

        # contains the time, close price for all the intervals of the coin data
        self.data = list(pd.DataFrame())

        self._init_historic_data()
        self._init_sma()

    def _init_historic_data(self):
        # create pandas data frame for each interval in the interval list and append it to self.data list
        for interval in self.interval_list:
            # convert the 12 element list from historical klines to a pandas data frame
            temp_df = pd.DataFrame(data=self.client.get_historical_klines(self.symbolPair,
                                                                          interval,
                                                                          self.__day_count_required(interval))
                                   )
            # pick only the time and close price columns
            temp_df = temp_df[[0, 4]]
            # rename the columns from numeric to strings
            temp_df.columns = ['Time', 'Close_price']
            temp_df.Time = temp_df.Time.apply(lambda x: self.__binance_time_to_pandas_time(x))
            self.data.append(temp_df)

    def _init_sma(self):

        """ mutates the data frame by adding/replacing the sma_fast and sma_slow columns"""
        for data_frame in self.data:
            data_frame['sma_fast'] = data_frame.Close_price.rolling(self.sma_fast_length).mean().astype('float64')
            data_frame['sma_slow'] = data_frame.Close_price.rolling(self.sma_slow_length).mean().astype('float64')

    def __day_count_required(self, interval):
        """
                Inputs : interval -> string which tells us about the interval i.e. minutes(m), hour(h)...
                         sma_slow, sma_fast -> tells us about how much data we need to look for

                This function computes the amount of days required in order to compute the latest sma_slow candle,
                this function operates in terms of X day ago UTC, we have to compute X such that it will give us
                enough candles for at least 1 data point of sma_slow
                update: it will work on the biggest interval from the interval list - because giving the time of biggest
                interval will always make sure, it works with the smaller time frames
            """
        day_time_minutes = 1440
        day_count = 1
        minutes_required = 1

        if interval[-1] == 'm':
            minutes_required = int(interval[:-1])
        elif interval[-1] == 'h':
            minutes_required = int(interval[:-1]) * 60
        elif interval[-1] == 'd':
            minutes_required = int(interval[:-1]) * 60 * 24
        elif interval[-1] == 'w':
            minutes_required = int(interval[:-1]) * 60 * 24 * 7
        elif interval[-1] == 'M':
            minutes_required = int(interval[:-1]) * 60 * 24 * 30

        while 1:
            time_required = day_count * day_time_minutes / minutes_required
            if time_required >= self.sma_slow_length:
                break
            day_count += 1

        return str(day_count) + " day ago UTC"

    @staticmethod
    def __binance_time_to_pandas_time(gt):
        """ Converts binance time from milliseconds in a datetime - time stamp
            Then converts from python time to pandas datetime
        """
        return pd.to_datetime(datetime.fromtimestamp(gt / 1000))

    def monitor(self):
        # print("round factor check: ", self.round_factor)
        # state variables

        self.local_time = time.strftime("%Y-%m-%d %H:%M:%S")
        if self.investment:
            print('{} - monitoring {}'.format(self.local_time, self.symbolPair))

            try:
                self.price = float([pair['price'] for pair in self.client.get_all_tickers() if pair['symbol'] == self.symbolPair][0])
                self.base_currency_balance = float(self.client.get_asset_balance(asset=self.base_currency_symbol)['free'])
                self.quote_currency_balance = float(self.client.get_asset_balance(asset=self.quote_currency_symbol)['free'])
            except:
                logging.critical('binance rate limit reached - could not retrieve quote, base, and current price balances')
                print('binance rate limit reached')
                self.base_currency_balance = 0.0
                self.quote_currency_balance = 0.0

            logging.info('\nSymbol name: ' + str(self.symbolPair)
                         + '\ncurrent price: ' + str(self.price)
                         + '\ncurrent budget allocation: ' + str(self.investment)
                         + '\nbase currency: ' + str(self.base_currency_symbol) + '- base currency balance: ' + str(self.base_currency_balance)
                         + '\nquote currency: ' + str(self.quote_currency_symbol) + '- quote currency balance: ' + str(self.quote_currency_balance))

            for idx, (interval, data_frame) in enumerate(zip(self.interval_list, self.data)):
                # acquire latest candle from binance api, append it is a row at the end of self.data
                try:
                    latest_candle = self.client.get_klines(symbol=self.symbolPair, interval=interval, limit=1)
                except:
                    print("Binance rate limit reached for the day.")
                    logging.critical('binance rate limit reached most probably - could not retrieve latest candle')
                    return
                latest_time = self.__binance_time_to_pandas_time(latest_candle[0][0])
                latest_price = latest_candle[0][4]
                latest_row = pd.Series(data=[latest_time, latest_price, 0, 0], index=data_frame.columns)

                # check to see if the latest candle is adding any new data
                if data_frame.Time.max() != latest_time:
                    # append latest row to existing data frame
                    self.data[idx] = data_frame.append(latest_row, ignore_index=True)

                    # recalculate sma for latest candle
                    self._init_sma()


            if self.investment and self.in_trade is False:
                self._get_sma_market_position()
                self.sentiment = self.sentiment_analyse.get_sentiment()
                self.sentiment_list.append(self.sentiment)

                logging.info('market position: {}'.format(self.sma_market_position))
                logging.info('market sentiment: {}'.format(self.sentiment))
                # change this to abs() when working with sell orders also

                if self.sma_market_position and self.sentiment > 0.15:
                    if self.quote_currency_balance > self.investment and self.quote_currency_balance > 0:
                        self._exec_trade()
                        self.sma_market_position = 0
                        return

            if self.investment and self.in_trade:

                logging.info('trade was placed earlier, waiting for take profit to sell...')
                logging.info('current market price: {} '.format(self.price))
                logging.info('entry price at trade: {}'.format(self.entry_price))
                logging.info('req to sell: {}'.format(self.exit_price))

                if self.price >= round(self.exit_price, 6):
                    print('placing sell order at market')
                    logging.critical('placing sell order at market for {}'.format(self.symbolPair))
                    logging.critical('base currency balance: {}'.format(self.base_currency_balance))
                    self.sma_market_position = -1
                    if self.mode:

                        try:
                            self.client.order_market_sell(symbol=self.symbolPair, quantity=round(self.base_currency_balance - self.min_step,
                                                                                                 abs(self.round_factor)))

                            self.in_trade = False

                            self.gui_dict['trade'] = 'placed sell order on binance for ' + str(self.symbolPair) \
                                                     + ' for entry price ' + str(self.entry_price) \
                                                     + ' exit value: ' + str(self.entry_price + self.entry_price * self.take_profit)

                            print(Back.WHITE + Fore.GREEN + '{} placed sell order on binance for symbol: {}\nentry price: {}\nexit price: {}\nprofit: {}'\
                                  .format(self.local_time,
                                  self.symbolPair,
                                  self.entry_price,
                                  self.exit_price,
                                  round(self.exit_price - self.entry_price, 6)))
                            self.__send_email_notification()

                            self.entry_price = 0
                        except Exception as e:
                            logging.critical('sell order {}'.format(e))
                            print(e)
                        print(Style.RESET_ALL)
                    else:
                        self.__send_email_notification()
                        self.in_trade = False
                        self.entry_price = 0

            self.gui_dict['sentiment_list'] = self.sentiment_list
            self.sma_market_position = 0
            # self.backend.recv_pyobj()
            # self.backend.send_pyobj(self.gui_dict)

    def _get_sma_market_position(self):

        """ function compares sma_fast and sma_slow across all intervals in the self.data and sets market position"""

        self.gui_dict['data1'] = (self.data[0].loc[self.data[0].index[-1], 'sma_fast']) \
                                 > (self.data[0].loc[self.data[0].index[-1], 'sma_slow'])

        self.gui_dict['data2'] = (self.data[1].loc[self.data[1].index[-1], 'sma_fast']) \
                                 > (self.data[1].loc[self.data[1].index[-1], 'sma_slow'])

        self.gui_dict['data3'] = (self.data[2].loc[self.data[2].index[-1], 'sma_fast']) \
                                 > (self.data[2].loc[self.data[2].index[-1], 'sma_slow'])

        logging.info('SMA-data 1 state: {} \n SMA-data 2 state: {} \n SMA-data 3 state: {}'.format(
            self.gui_dict['data1'], self.gui_dict['data2'], self.gui_dict['data3']
        ))

        if all(data_frame.loc[data_frame.index[-1], 'sma_fast'] > data_frame.loc[data_frame.index[-1], 'sma_slow']
               for data_frame in self.data):
            self.sma_market_position = 1

        elif all(data_frame.loc[data_frame.index[-1], 'sma_fast'] < data_frame.loc[data_frame.index[-1], 'sma_slow']
                 for data_frame in self.data):
            self.sma_market_position = -1

        else:
            self.sma_market_position = 0

    def _exec_trade(self):
        # checks the sma_market_position and if it is positive or negative - places a market order for buy/sell
        # resets the market position intended at the end of the cycle
        if self.sma_market_position == 1 and self.sentiment > 0.15:

            self.__calculate_qty()
            # consume all of the investment in 1 market order
            if self.mode:
                try:
                    self.client.order_market_buy(symbol=self.symbolPair, quantity=self.quantity)
                    self.in_trade = True
                    self.entry_price = self.price
                    self.exit_price = round(self.entry_price + (self.entry_price * self.take_profit), 6)
                    print(Back.WHITE + Fore.RED + '{} - placed buy order at market\nentry price: {}\nexit target: {}\ntake profit %: {}'.format(self.local_time, self.entry_price, self.exit_price, self.take_profit * 100))
                    self.__send_email_notification()
                    logging.critical('placing buy order at market for {}'.format(self.symbolPair))

                    self.gui_dict['trade'] = 'placed buy order on ' + str(self.symbolPair) + ' at entry price ' + str(
                        self.entry_price)
                except Exception as e:
                    logging.critical('buy order: {}'.format(e))
                    print(e)
            else:
                self.__send_email_notification()
                self.in_trade = True
                self.entry_price = self.price
                self.gui_dict['trade'] = 'detected buy order on ' + str(self.symbolPair) + ' at entry price ' + str(
                    self.entry_price)

        print(Style.RESET_ALL)

    def __calculate_qty(self):
        self.quantity = round(self.investment / self.price, self.round_factor)
        logging.critical('quantity calculated: {}'.format(self.quantity))

    def __send_email_notification(self, special_message=''):
        try:
            if not special_message:
                email_text = 'Placed order on binance \n' \
                             + 'Symbol: ' + str(self.symbolPair) + '\n' \
                             + 'market position ( 1 = Buy, -1 = Sell): ' + str(self.sma_market_position) + '\n' \
                             + 'Quantity: ' + str(self.quantity) + '\n' \
                             + 'Entry price: ' + str(self.entry_price) + '\n' \
                             + 'Exit price: ' + str(self.exit_price) + '\n'\
                             + 'Investment: ' + str(self.investment) + '\n' \
                             + 'market sentiment: ' + str(self.sentiment)
            else:
                email_text = special_message

            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            server.login(self.bot_email, self.bot_password)
            server.sendmail(self.bot_email, self.user_email, email_text)
            server.close()
            print('email sent')
            logging.critical('email sent')
        except Exception as e:
            logging.critical('{}'.format(e))


class CCTP:

    def __init__(self):
        """
        relative to quote currency:
        [-len(quote_currency):] will return quote currency
        [:-len(quote_currency)] will return base currency

        relative to base currency:
        [len(base_currency):] will return will return quote currency
        [:len(base_currency)] will return will return base currency
        """

        # zmq for communication with frontend
        self.zmq_context = zmq.Context()
        self.backend = self.zmq_context.socket(zmq.REP)
        self.backend.bind('tcp://*:17000')

        # initialization parameters from input
        self.input_dict = self.backend.recv_pyobj()

        # binance for communication with binance website
        self.public_key = self.input_dict['public']
        self.private_key = self.input_dict['private']
        self.binance_client = Client(self.public_key, self.private_key)
        # sma lengths and intervals for technical indicators
        self.sma_fast_len = self.input_dict['sma_fast_len']
        self.sma_slow_len = self.input_dict['sma_slow_len']
        self.interval_list = self.input_dict['interval_list']
        # user email id for informing about trade details
        self.user_email_id = self.input_dict['email']
        # 1 for automatic - 0 for semi auto
        self.mode = self.input_dict['mode']
        self.take_profit = self.input_dict['take_profit']

        # all USDT pairs - 20 - symbol_count_1 is for internal use only - to speedup load times
        self.symbol_count_1 = int()
        self.quote_currency_1 = 'USDT'
        self.base_currency_1 = str()

        self.symbol_count_2 = int(self.input_dict['symbol_count'])
        self.quote_currency_2 = self.input_dict['variable_quote']
        self.base_currency_2 = str()

        # all TUSD/XXX pairs 3 markets - symbol_count_3 is for internal use only
        self.symbol_count_3 = int()
        self.quote_currency_3 = str()
        self.base_currency_3 = 'TUSD'

        self.init_dataframe = pd.DataFrame()
        # contains the symbol to full name mappings
        self.symbol_to_fullname_dict = {}
        # contains symbol details from binance
        self.symbol_info_dict = {}
        self.coin_list = []
        print('getting data from binance and coinbase... (one time loading) (apox 60 seconds - 140 seconds)')
        logging.info('getting data from binance and coinbase... (one time loading) (apox 60 seconds - 140 seconds)')
        self._get_full_name_data()
        self._get_binance_data()

        if self.binance_client.get_system_status()['status'] == 0:
            self.backend.send_pyobj(0)
        else:
            self.backend.send_pyobj(1)
            logging.critical('Binance down - 1')
            exit()

        # send this dict through zmq to the GUI - the GUI will update the keys and resend back
        self.backend.recv_pyobj()
        # # iterate this dict on the GUI to get the names of all pairs involved
        self.backend.send_pyobj(self.init_dataframe)

        # get back updated dataframe with investments
        self.init_dataframe = self.backend.recv_pyobj()

        print('Total currencies we will be dealing with')
        logging.info('Total currencies we will be dealing with')
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(Back.BLUE)
            print(self.init_dataframe.reset_index())
            print(Style.RESET_ALL)

        print('getting historical data from binance for technical analysis... (one time loading) (apox 100 seconds)')
        logging.info('getting historical data from binance for technical analysis... (one time loading) (apox 100 seconds)')
        for symbol, row in self.init_dataframe.iterrows():
            logging.info(str(symbol))
            try:
                coin_object = Coin(symbol=symbol,
                                   backend=self.backend, client=self.binance_client,
                                   mode=self.mode, take_profit=self.take_profit,
                                   sentiment_analyse=SentimentAnalyse(row[0]),
                                   interval_list=self.interval_list,
                                   sma_fast_length=self.sma_fast_len, sma_slow_length=self.sma_slow_len,
                                   user_email=self.user_email_id, symbol_info=row
                                   )

                self.coin_list.append(coin_object)
            except:
                print(symbol, ' not available currently.')
                logging.debug('something wrong with {}'.format(symbol))

        # send back reply once the data collection is complete
        self.backend.send_pyobj('')

        while 1:
            start_time = time.time()

            for coin_object in self.coin_list:
                coin_object.monitor()
                
            end_time = time.time() - start_time
            print('\n')
            time.sleep(max(0, 60 - end_time))
            
    def _get_binance_data(self):

        self.init_dataframe = pd.DataFrame(self.binance_client.get_ticker(), columns=['symbol', 'quoteVolume'])
        self.init_dataframe.quoteVolume = pd.to_numeric(self.init_dataframe.quoteVolume)

        # Adding name and investment columns
        self.init_dataframe['name'] = ''
        self.init_dataframe['investment'] = float()
        self.init_dataframe['base_asset'] = ''
        self.init_dataframe['quote_asset'] = ''
        self.init_dataframe['base_asset_balance'] = float()
        self.init_dataframe['quote_asset_balance'] = float()
        self.init_dataframe['min_investment'] = float()
        self.init_dataframe['min_qty'] = float()
        self.init_dataframe['min_step'] = float()

        # filtering selected pairs for trade out of all 398 cryptocurrencies

        # filter for all USDT pairs
        condition1 = self.init_dataframe.symbol.str[-len(self.quote_currency_1):] == self.quote_currency_1
        condition1 = self.init_dataframe.loc[condition1, :]
        condition1 = condition1.loc[condition1.quoteVolume > 1, :]
        # condition1 = condition1.nlargest(self.symbol_count_1, 'quoteVolume')

        # filter all BNB pairs excluding TUSD as base currency and pick top 10 by 24H volume
        condition2 = (self.init_dataframe.symbol.str[-len(self.quote_currency_2):] == self.quote_currency_2) & \
                     (self.init_dataframe.symbol.str[:-len(self.quote_currency_2)] != self.base_currency_3)
        condition2 = self.init_dataframe.loc[condition2, :]
        condition2 = condition2.nlargest(self.symbol_count_2, 'quoteVolume')

        # pick all pairs with base currency as TUSD
        condition3 = (self.init_dataframe.symbol.str[:len(self.base_currency_3)] == self.base_currency_3) & \
                     (self.init_dataframe.symbol.str[len(self.base_currency_3):] != 'USDT')
        condition3 = self.init_dataframe.loc[condition3, :]
        # condition3 = condition3.nlargest(self.symbol_count_3, 'quoteVolume')

        self.init_dataframe = pd.concat([condition1, condition2, condition3])
        # make index as name of the symbol to make it behave like a dict-ish

        self.init_dataframe = self.init_dataframe[['symbol', 'name', 'investment', 'base_asset', 'base_asset_balance',
                                                   'quote_asset', 'quote_asset_balance',
                                                   'min_investment',
                                                   'min_qty', 'min_step']]
        self.init_dataframe = self.init_dataframe.drop_duplicates(subset=['symbol'], keep=False)

        self.__get_symbol_info_data()

        self.init_dataframe.base_asset = self.init_dataframe.symbol.apply(
            lambda x: self.symbol_info_dict[x]['base_asset']
        )
        self.init_dataframe.base_asset_balance = self.init_dataframe.symbol.apply(
            lambda x: self.symbol_info_dict[x]['base_asset_balance']
        )
        self.init_dataframe.name = self.init_dataframe.base_asset.apply(
            lambda x: self._get_symbol_to_full_name(x)
        )
        self.init_dataframe.min_investment = self.init_dataframe.symbol.apply(
            lambda x: self.symbol_info_dict[x]['min_investment']
        )
        self.init_dataframe.min_qty = self.init_dataframe.symbol.apply(
            lambda x: self.symbol_info_dict[x]['min_qty']
        )
        self.init_dataframe.quote_asset = self.init_dataframe.symbol.apply(
            lambda x: self.symbol_info_dict[x]['quote_asset']
        )
        self.init_dataframe.quote_asset_balance = self.init_dataframe.symbol.apply(
            lambda x: self.symbol_info_dict[x]['quote_asset_balance']
        )
        self.init_dataframe.min_step = self.init_dataframe.symbol.apply(
            lambda x: self.symbol_info_dict[x]['min_step']
        )

        self.init_dataframe.set_index('symbol', inplace=True)

    def _get_full_name_data(self):
        """ returns a dict which converts crypto symbol to full name from coin market cap """
        cmp = Market()
        cmp_data = cmp.listings()

        for details in cmp_data['data']:
            self.symbol_to_fullname_dict[details['symbol']] = details['website_slug']

        self.symbol_to_fullname_dict['BCC'] = 'Bitcoin Cash'
        self.symbol_to_fullname_dict['IOTA'] = 'IOTA'

    def _get_symbol_to_full_name(self, symbol):
        try:
            return self.symbol_to_fullname_dict[symbol]
        except:
            return symbol

    def __get_symbol_info_data(self):

        for index, row in self.init_dataframe.iterrows():
            pair = row[0]
            symbol_info = self.binance_client.get_symbol_info(pair)
            base_asset = symbol_info['baseAsset']
            quote_asset = symbol_info['quoteAsset']
            min_investment = float(symbol_info['filters'][2]['minNotional'])
            min_qty = float(symbol_info['filters'][1]['minQty'])
            min_step = float(symbol_info['filters'][1]['stepSize'])
            base_asset_balance = float(self.binance_client.get_asset_balance(asset=base_asset)['free'])
            quote_asset_balance = float(self.binance_client.get_asset_balance(asset=quote_asset)['free'])
            self.symbol_info_dict[pair] = {'base_asset': base_asset, 'quote_asset': quote_asset,
                                           'min_investment': min_investment, 'min_qty': min_qty, 'min_step': min_step,
                                           'base_asset_balance': base_asset_balance,
                                           'quote_asset_balance': quote_asset_balance}


try:
    CCTP()
except Exception as bigE:
    logging.exception('program crashed {}'.format(bigE))
