import os
import json
from pprint import pprint, pformat
import zmq
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, State, Output
import pandas as pd
import time

print(dcc.__version__)  # 0.6.0 or above is required
app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True

# Boostrap CSS.
app.css.append_css({'external_url': 'https://cdn.rawgit.com/plotly/dash-app-stylesheets'
                                    '/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css'})

# app.css.append_css({
#     'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
# })

context = zmq.Context()
frontend = context.socket(zmq.REQ)
frontend.connect('tcp://localhost:17000')

# PAGE1_INVESTMENT_PATH = os.path.join('com', 'page1_investments_data.json')
# PAGE1_INPUTS_PATH = os.path.join('com', 'page1_inputs.txt')

# with open(PAGE1_INVESTMENT_PATH, 'w') as f:
#     pass
#
# with open(PAGE1_INPUTS_PATH, 'w') as f:
#     pass

flag = 0
# inputs from GUI
input_params_dict = dict()
if os.path.exists('default.json'):
    with open(os.path.join(os.getcwd(), 'default.json'), 'r') as f:
        input_params_dict = json.load(f)
    with open(os.path.join(os.getcwd(), 'default.json'), 'w') as f:
        json.dump(input_params_dict, f, indent=4)
else:
    input_params_dict = dict()

print(input_params_dict['mode'])
investment_dict = dict()
Coins_ = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'BCCUSDT', 'NEOUSDT', 'LTCUSDT', 'QTUMUSDT', 'ADAUSDT', 'XRPUSDT', 'EOSUSDT',
          'TUSDUSDT', 'IOTAUSDT', 'XLMUSDT', 'ONTUSDT', 'TRXUSDT', 'ETCUSDT', 'ICXUSDT', 'NULSUSDT', 'VETUSDT',
          'PAXUSDT', 'RVNBNB', 'XRPBNB', 'TRXBNB', 'BATBNB', 'PAXBNB', 'XZCBNB', 'XLMBNB', 'LTCBNB', 'EOSBNB',
          'LOOMBNB', 'TUSDBTC', 'TUSDETH', 'TUSDBNB']
Coin_No = ['Top-10', 'Top-25', 'Top-50']
Time_Frame = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']
binance_status_flag = True
pd_df = pd.DataFrame()
sentiment_List = []
global_trade = ''


# DF_SIMPLE = {
#     'x': ['A', 'B', 'C', 'D', 'E', 'F'],
#     'y': [4, 3, 1, 2, 3, 6],
#     'z': ['a', 'b', 'c', 'a', 'b', 'c']
# }



app.layout = html.Div([
    # represents the URL bar, doesn't render anything
    dcc.Location(id='url', refresh=False),

    # content will be rendered in this element
    html.Div(id='page-content')
])


# main page - first call
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    global flag
    global binance_status_flag
    global pd_df

    if pathname:

        if pathname == '/page-1':

            if binance_status_flag:
                frontend.send_pyobj('')
                pd_df = frontend.recv_pyobj()

                pd_df = pd.read_csv('default_investments.csv')
                pd_df.set_index('symbol', inplace=True)

                return html.Div([
                    # From Page 2 ---------------------------------------------------------------------------------------

                    html.Div([html.H2('Investments Page'),
                              ], style={'text-align': 'center'}, className='row'),

                    html.Div([html.H3('Choose a Coin to Invest In:', style={'text-align': 'center'}),
                              ], className="row"),

                    html.Div([html.H3(className='two columns'),
                              dcc.Dropdown(
                                  id='coin-dropdown',
                                  options=[
                                      {'label': symbol, 'value': symbol} for symbol in pd_df.index.values
                                  ], className='eight columns',
                              ),
                              ], className="row"),

                    html.Div([html.H3('Max Budget Allocated per Coin:', style={'text-align': 'center'})
                              ], className='row'),

                    html.Div([
                        html.H3(className='five columns'),
                        dcc.Input(id='coin_invest', value='', type='text', className="three columns"),
                    ], className='row'),

                    html.Br(),

                    html.Div([
                        html.H3(className='four columns'),
                        html.Button(id='submit-button', n_clicks=0, children='Submit Order', className="two columns"),
                        html.Button(id='reset-button', n_clicks_timestamp=0, n_clicks=0, children='Clear Orders',
                                    className="two columns"),
                    ], className='row'),

                    html.Br(),

                    html.Div([
                        html.Div(id='output-e', style={'text-align': 'center', 'font-size': '20px'}),
                    ], className='row'),

                    html.Div([
                        dcc.Textarea(
                            id='text_area_1',
                            readOnly=True,
                            placeholder='',
                            value='',
                            style={'font-size': '20px','height': 500, 'width': '50%'},

                        )
                    ]),

                    # Links ------------------------------------------------------------------------------------------------

                    html.Div(id='output-a'),

                    html.Div(id='fake_1', style={'display': 'none'}),

                    html.Div([
                        html.H3(className='four columns'),
                        html.Button(id='submit-all-button', n_clicks=0, children='Submit All Orders', className="two columns"),
                    ], className='row'),

                    html.Div([html.Div(id='final-text', style={'font-size': '25px', 'text-align': 'center'}),
                              ], className="row"),

                    #





                ])

        elif pathname == '/':

            return html.Div([

                html.Div([html.H1('Crypto Currency Trading Platform-CCTP', style={'text-align': 'center'}),
                          ], className="row"),

                html.Div([html.H2('Configuration Page', style={'text-align': 'center'}),
                          ], className="row"),


                html.Div([html.Label('Trading Mode')]),
                html.Div([dcc.RadioItems(id='radio',
                    options=[
                        {'label': 'Fully Automatic', 'value': 1},
                        {'label': 'Semi Automatic', 'value': 0}
                    ],
                    className='two columns',
                    value=input_params_dict['mode']
                )], className='row'),

                html.Div([

                ],className='row'),


                html.Div([
                    html.Div([

                        html.H3('Enter Email:', className='two columns'),
                        html.H3(className='two columns'),
                        html.H3('Enter Public Key:', className='two columns'),
                        html.H3(className='two columns'),
                        html.H3('Enter Private Key:', className='two columns'),

                    ],
                        className='ten columns offset-by-two'
                    )
                ], className="row"),

                html.Div([
                    html.Div([
                        dcc.Input(id='Email', value=input_params_dict['email'], type='text', className="two columns"),
                        html.H3(className='two columns'),
                        dcc.Input(id='Public-Key', value=input_params_dict['public'], type='text', className="two columns"),
                        html.H3(className='two columns'),
                        dcc.Input(id='Private-Key', value=input_params_dict['private'], type='text', className="two columns"),
                    ],
                        className='ten columns offset-by-two'
                    )
                ], className="row"),

                html.Br(),


                html.Div([html.H3(id='output-h', style={'text-align': 'center'}),
                          ], className="row"),

                html.Div([html.H3('Select 3 Time Frames:', style={'text-align': 'center'}),
                          ], className="row"),

                html.Div([html.H3(className="one column"),

                          dcc.Dropdown(id='time-frame-1',
                                       value=input_params_dict['interval_list'][0],
                                       options=[
                                           {'label': c, 'value': c} for c in Time_Frame

                                       ], className="three columns",

                                       ),

                          html.H3(className="one column"),
                          dcc.Dropdown(id='time-frame-2',
                                       value=input_params_dict['interval_list'][1],
                                       options=[
                                           {'label': c, 'value': c} for c in Time_Frame

                                       ], className="three columns",

                                       ),

                          html.H3(className="one column"),
                          dcc.Dropdown(id='time-frame-3',
                                       value=input_params_dict['interval_list'][2],
                                       options=[
                                           {'label': c, 'value': c} for c in Time_Frame

                                       ], className="three columns",

                                       ),
                          ], className="row"),

                html.Div([
                    html.Div([
                        html.H3('Enter SMA-Fast Length:', className='two columns'),
                        html.H3(className='two columns'),
                        html.H3('Enter SMA-Slow Length:', className='two columns'),
                        html.H3(className='two columns'),
                        html.H3('Enter Take-Profit:', className='two columns'),

                    ],
                        className='ten columns offset-by-two'
                    )
                ], className="row"),

                html.Div([
                    html.Div([
                        dcc.Input(id='SMA-Fast', value=input_params_dict['sma_fast_len'], type='text', className="two columns"),
                        html.H3(className='two columns'),
                        dcc.Input(id='SMA-Slow', value=input_params_dict['sma_slow_len'], type='text', className="two columns"),
                        html.H3(className='two columns'),
                        dcc.Input(id='take-profit', value=input_params_dict['take_profit'], type='text', className="two columns"),
                    ],
                        className='ten columns offset-by-two'
                    )
                ], className="row"),

                html.Br(),

                html.Div([html.H3('Select Variable Quote Currency :', style={'text-align': 'center'}),
                          ], className="row"),

                html.Div([html.H3(className="two columns"),

                          dcc.Dropdown(id='Variable-Quote-Count',
                                       value=input_params_dict['variable_quote'],
                                       options=[
                                           {'label': c, 'value': c} for c in ['BNB', 'BTC', 'ETH']
                                       ], className='eight columns'

                                       ),

                          ], className="row"),

                html.Div([html.H3('Select No. of Coins:', style={'text-align': 'center'}),
                          ], className="row"),

                html.Div([html.H3(className="two columns"),

                          dcc.Dropdown(id='Coin-Count',
                                       value='Top-10',
                                       options=[
                                           {'label': c, 'value': c} for c in Coin_No
                                       ], className='eight columns'

                                       ),

                          ], className="row"),

                html.Br(),

                html.Div([
                    html.H3(className='five columns'),
                    html.Button(id='Save-Data-button', n_clicks=0, children='Save Data', className="three columns"),
                ], className="row"),

                html.Br(),

                html.Div([html.Div(id='output-g', style={'font-size': '25px', 'text-align': 'center'}),
                          ], className="row"),

                html.Br(),

                html.Div([dcc.Link('Investments Page', href='/page-1'),
                          ], className='row', style={'text-align': 'center'})

            ])

        # You could also return a 404 "URL not found" page here










# Page-1 Key inputs ----------------------------------------------------------------------------------------------
# @app.callback(Output('output-h', 'children'),
#               [Input('Save-Key-button', 'n_clicks')],
#               [])
# def page_1_inputs(save_key_count=None, email=None,radio=None):
#     if save_key_count  :
#
#                 if save_key_count >= 1:
#
#                         print('Keyfun')
#
#
#                         print(input_params_dict)
#                         return 'Keys Received!'
#
#



# all inputs from page 1 - third call usually-----------------------------------------------------------------------
@app.callback(Output('text_area_1', 'value'),
              [Input('submit-button', 'n_clicks_timestamp'), Input('reset-button', 'n_clicks_timestamp')],
              [State('coin-dropdown', 'value'), State('coin_invest', 'value')])
def clear_page_1_coins_investment(submit_time=None, reset_time=None, coin=None, amount=None):
    global pd_df
    if submit_time:

        if reset_time > submit_time:

            pd_df.investment = 0

            pd_dict = pd_df['name','base_asset','base_asset_balance','investment','min_investment','quote_asset','quote_asset_balance'].to_dict('index')

            temp_pd_df = pd_df.drop(['min_qty', 'min_step'], axis=1)

            pd_dict = temp_pd_df.to_dict('index')

            return pformat(pd_dict, indent=1).replace('{','').replace('}','').replace("'","").replace(',','')

        else:
            amount = float(amount)
            if amount > int(pd_df.loc[coin, 'min_investment'] +(pd_df.loc[coin, 'min_investment']/3)):
                if  pd_df.loc[coin, 'quote_asset_balance'] > amount:
                    pd_df.loc[coin, 'investment'] = amount

                    temp_pd_df = pd_df.drop(['min_qty', 'min_step'], axis=1)

                    pd_dict = temp_pd_df.to_dict('index')

                    return pformat(pd_dict, indent=1).replace('{','').replace('}','').replace("'","").replace(',','')
                else:
                    return 'Not enough quote asset balance for ' + str(coin)
            else:
                return str(coin)+' investment amount must be greater than ' + str(int(pd_df.loc[coin, 'min_investment'] + (pd_df.loc[coin, 'min_investment']/3)))


@app.callback(Output('output-g', 'children'),
              [Input('Save-Data-button', 'n_clicks')],
              [State('time-frame-1', 'value'),
               State('time-frame-2', 'value'),
               State('time-frame-3', 'value'),
               State('SMA-Fast', 'value'),
               State('SMA-Slow', 'value'),
               State('Variable-Quote-Count', 'value'),
               State('Coin-Count', 'value'),
               State('Public-Key', 'value'),
               State('Private-Key', 'value'),
               State('Email', 'value'),
               State('radio','value'),
               State('take-profit', 'value')
               ])
def page_1_inputs(save_count=None, time_frame_1=None, time_frame_2=None,
                  time_frame_3=None, sma_fast_len=None, sma_slow_len=None,
                  variable_quote_count=None, symbol_count=None,
                  public_key=None,private_key=None,email=None,radio=None,take_profit=None):
    global Coins_
    if save_count and time_frame_1 and time_frame_2 and time_frame_3 and \
            sma_fast_len and sma_slow_len and variable_quote_count and symbol_count \
            and public_key and private_key and take_profit :
        if len(public_key) >= 64 and len(private_key) >= 64:
            if email and email[-4:] == '.com' and email.find('@') != -1:
                if radio == 1 or radio == 0:
                    if int(sma_slow_len) > int(sma_fast_len):

                        input_params_dict['mode'] = int(radio)
                        input_params_dict['email'] = email
                        input_params_dict['public'] = public_key
                        input_params_dict['private'] = private_key
                        input_params_dict['take_profit'] = float(take_profit)

                        input_params_dict['interval_list'] = [time_frame_1, time_frame_2, time_frame_3]
                        input_params_dict['sma_fast_len'] = int(sma_fast_len)
                        input_params_dict['sma_slow_len'] = int(sma_slow_len)
                        input_params_dict['variable_quote'] = variable_quote_count
                        input_params_dict['symbol_count'] = int(symbol_count.split('-')[1])
                        with open(os.path.join(os.getcwd(), 'default.json'), 'w') as f:
                            json.dump(input_params_dict, f, indent=4)

                        frontend.send_pyobj(input_params_dict)
                        # Coins_ = \
                        if frontend.recv_pyobj() == 1:
                            binance_status_flag = False
                            return 'Binance Closed For maintenance !'

                        return 'Data Saved ! You may proceed to Investments Page. '
                    return 'SMA slow Must be Greater than SMA fast !'
                return 'Choose Trading Mode'
            return 'Enter a valid Email !'
        return 'Invalid Keys !'
    return 'Some inputs may be empty'


@app.callback(Output('final-text','children'),
              [Input('submit-all-button','n_clicks')])
def final_call(clicks):

    if clicks == 1:
        frontend.send_pyobj(pd_df)
        frontend.recv_pyobj()
        pd_df.to_csv('default_investments.csv')
        return 'Settings saved, you may proceed to command prompt window to monitor your trade activity.'
    elif clicks > 1:
        return 'Orders Already Submitted'


app.run_server(debug=False)
