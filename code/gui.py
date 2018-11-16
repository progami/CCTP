import os
import json
from datetime import datetime
import zmq
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, State, Output
import pandas as pd
import pprint
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

        # if pathname == '/page-2':


            # return html.Div([
            #
            #     html.Div(id='fake_2',
            #              style={'display': 'none'}
            #              ),
            #
            #     html.Div([html.H2('Investment Supervision Page'),
            #               ], style={'text-align': 'center'}, className='row'),
            #
            #     html.Br(),
            #
            #     html.Div([html.Div([
            #
            #         dcc.Graph(id='my-graph'),
            #     ], className='six columns'),
            #         html.Div([
            #
            #             dcc.Dropdown(
            #                 id='my-dropdown',
            #                 options=[
            #                     {'label': symbol, 'value': symbol} for symbol in pd_df.index.values
            #
            #                 ],
            #                 value='Coins'
            #             ),
            #
            #         ], className='six columns')
            #     ], className='row'
            #     ),
            #
            #     # html.Div([
            #     #     html.Div(id='output-b',className='six columns'),
            #     #     html.Div(id='output-d',className='six columns'),
            #     # ],className='row'),
            #
            #     html.Div([
            #         html.Div(html.H3('Info of Selected Coin ',className='six columns')),
            #         html.Div(html.H3('Market Buy/Sell Orders of All Coins ',className='six columns'))
            #
            #     ], className='row'),
            #
            #     html.Div([
            #         html.Div([
            #             dcc.Textarea(
            #                 id='text_area',
            #                 readOnly=True,
            #                 placeholder='',
            #                 value='',
            #                 style={'font-size': '20px', 'height': 500, 'width': '100%'},
            #
            #             )
            #         ], className='six columns'),
            #
            #         html.Div([
            #             dcc.Textarea(
            #                 id='text_area_2',
            #                 readOnly=True,
            #                 placeholder='',
            #                 value='',
            #                 style={'font-size': '20px', 'height': 500, 'width': '100%'},
            #
            #             )
            #         ], className='six columns'),
            #     ], className='row'),
            #
            #
            #     dcc.Interval(
            #         id='interval-component',
            #         interval=1 * 4000,  # in milliseconds
            #         n_intervals=0
            #     ),
            #     dcc.Interval(
            #         id='interval-component_2',
            #         interval=1 * 4100,  # in milliseconds
            #         n_intervals=0
            #     ),
            #     html.Div(id='page-2-content'),
            #
            #     html.Br(),
            #
            #     html.Div([dcc.Link('Investments Page', href='/page-1'),
            #               ], className='row', style={'text-align': 'center'})
            #
            # ])

        if pathname == '/page-1':

            if binance_status_flag == True:
                frontend.send_pyobj('')
                pd_df = frontend.recv_pyobj()



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


                html.Div([html.Label('Trading Space Mode')]),
                html.Div([dcc.RadioItems(id = 'radio',
                    options=[
                        {'label': 'Fully Automatic', 'value': 1},
                        {'label': 'Semi Automatic', 'value': 0}
                    ],className='two columns',
                    value=''
                )],className='row'),

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
                        dcc.Input(id='Email', value='', type='text', className="two columns"),
                        html.H3(className='two columns'),
                        dcc.Input(id='Public-Key', value='', type='text', className="two columns"),
                        html.H3(className='two columns'),
                        dcc.Input(id='Private-Key', value='', type='text', className="two columns"),
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

                                       options=[
                                           {'label': c, 'value': c} for c in Time_Frame

                                       ], className="three columns",

                                       ),

                          html.H3(className="one column"),
                          dcc.Dropdown(id='time-frame-2',

                                       options=[
                                           {'label': c, 'value': c} for c in Time_Frame

                                       ], className="three columns",

                                       ),

                          html.H3(className="one column"),
                          dcc.Dropdown(id='time-frame-3',

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
                        dcc.Input(id='SMA-Fast', value='', type='text', className="two columns"),
                        html.H3(className='two columns'),
                        dcc.Input(id='SMA-Slow', value='', type='text', className="two columns"),
                        html.H3(className='two columns'),
                        dcc.Input(id='take-profit', value='', type='text', className="two columns"),
                    ],
                        className='ten columns offset-by-two'
                    )
                ], className="row"),

                html.Br(),

                html.Div([html.H3('Select Variable Quote Currency :', style={'text-align': 'center'}),
                          ], className="row"),

                html.Div([html.H3(className="two columns"),

                          dcc.Dropdown(id='Variable-Quote-Count',
                                       options=[
                                           {'label': c, 'value': c} for c in ['BNB', 'BTC', 'ETH']
                                       ], className='eight columns'

                                       ),

                          ], className="row"),

                html.Div([html.H3('Select No. of Coins:', style={'text-align': 'center'}),
                          ], className="row"),

                html.Div([html.H3(className="two columns"),

                          dcc.Dropdown(id='Coin-Count',
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

            return pprint.pformat(pd_dict, indent=1).replace('{','').replace('}','').replace("'","").replace(',','')

        else:
            amount = float(amount)
            if amount > int(pd_df.loc[coin, 'min_investment'] +(pd_df.loc[coin, 'min_investment']/3)):
                if  pd_df.loc[coin, 'quote_asset_balance'] > amount:
                    pd_df.loc[coin, 'investment'] = amount

                    temp_pd_df = pd_df.drop(['min_qty', 'min_step'], axis=1)

                    pd_dict = temp_pd_df.to_dict('index')

                    string = ''

                    return pprint.pformat(pd_dict, indent=1).replace('{','').replace('}','').replace("'","").replace(',','')
                else:
                    return 'Not enough quote asset balance for '+ str(coin)
            else:
                return str(coin)+' investment amount must be greater than ' + str(int(pd_df.loc[coin, 'min_investment'] +(pd_df.loc[coin, 'min_investment']/3)))


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
               State('take-profit','value')
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
                        frontend.send_pyobj(input_params_dict)
                        # Coins_ = \
                        if frontend.recv_pyobj() == 1:
                            binance_status_flag = False
                            return 'Binance Closed For Maintanence !'
                        # print(Coins_)

                        return 'Data Saved ! You may proceed to Investments Page. '
                    return 'SMA slow Must be Greater than SMA fast !'
                return 'Choose Trading Space Mode'
            return 'Enter a valid Email !'
        return 'Invalid Keys !'
    return 'Some Boxes are Not Filled !'
# button click response - second call

# @app.callback(Output('text_area', 'value'),
#               [Input('interval-component', 'n_intervals'),
#                Input('url', 'pathname')]
#                 ,[State('my-dropdown','value')])
# def auto_recommend_local(inp=None, pathname=None,coin_=None):
#     global global_trade
#     global sentiment_List
#     if inp and coin_ :
#         print('globalfun')
#         if flag == 1:
#             print('e-', datetime.now().strftime("%H:%M:%S.%f"))
#             try:
#                 frontend.send_pyobj('')
#                 D = frontend.recv_pyobj(zmq.DONTWAIT)
#             except:
#                 return ''
#             print(D)
#             pprint.pprint(D)
#
#             if 'trade' in D:
#                 global_trade = str(D['trade']) +'\n' + global_trade
#
#             temp_string = D['general'].split('\n')[1]
#
#             global_List = D['sentiment_list']
#
#             line = str(D['general'])
#             if temp_string[13:] == coin_:
#                 if 'data1' in D:
#                     line = line+ '\n'+ 'Sma-1 Status : ' +str(D['data1'])
#                 if 'data2' in D:
#                     line = line+ '\n'+ 'Sma-1 Status : ' +str(D['data2'])
#                 if 'data3' in D:
#                     line = line+ '\n'+ 'Sma-1 Status : ' +str(D['data3'])
#
#                 return str(line)
#
#                 # global_general = line + '\n\n' + global_general
#
#
#
# @app.callback(Output('text_area_2', 'value'),
#               [Input('interval-component_2', 'n_intervals'),
#               Input('url', 'pathname')]
#                 , [State('my-dropdown', 'value')])
# def auto_recommend_global(inp=None, pathname=None,coin_=None):
#     global global_trade
#     print('v')
#     if inp and coin_:
#         if flag == 1:
#             print('inside')
#             return str(global_trade)


# @app.callback(Output('my-graph', 'figure'),
#               [Input('interval-component', 'n_intervals'),
#               Input('url', 'pathname')]
#                 , [State('my-dropdown', 'value')])
# def auto_recommend_global(inp=None,pathname=None,coin_=None):
#     global sentiment_List
#     time.sleep(4)
#     print('t')
#     if inp and coin_:
#         if flag == 1:
#
#             fig = {
#                 'data':[
#                     {'x':list(range(len(sentiment_List))),'y':sentiment_List,'type':'line','name':'sentiment'}
#                 ]
#             }
#             print('end')
#             return fig

@app.callback(Output('final-text','children'),
              [Input('submit-all-button','n_clicks')])
def final_call(clicks):

    if clicks == 1:
        frontend.send_pyobj(pd_df)
        frontend.recv_pyobj()
        return 'Orders Submitted ! You may proceed to Command Prompt.'
    elif clicks > 1:
        return 'Orders Already Submitted'


app.run_server(debug=False)
