import dash
import plotly.graph_objects as go
from dash import dcc, dash_table
from dash import html
from dash.dependencies import Input, Output, State
from ibapi.contract import Contract
from ibapi.order import Order

from fintech_ibkr import *
import pandas as pd
import datetime

# Make a Dash app!
app = dash.Dash(__name__)

# ADD this!
server = app.server

# Read data file
df = pd.read_csv('submitted_orders.csv')

# Define the layout.
app.layout = html.Div([

    # Section title
    html.H1("Section 1: Fetch & Display exchange rate historical data"),

    # endDateTime parameter
    html.H4("Select value for endDateTime:"),
    html.Div(
        children=[
            html.P("You may select a specific endDateTime for the call to " + \
                   "fetch_historical_data. If any of the below is left empty, " + \
                   "the current present moment will be used.")
        ],
        style={'width': '365px'}
    ),
    html.Div(
        children=[
            html.Div(
                children=[
                    html.Label('Date:'),
                    dcc.DatePickerSingle(id='edt-date')
                ],
                style={
                    'display': 'inline-block',
                    'margin-right': '20px',
                }
            ),
            html.Div(
                children=[
                    html.Label('Hour:'),
                    dcc.Dropdown(list(range(24)), id='edt-hour'),
                ],
                style={
                    'display': 'inline-block',
                    'padding-right': '5px'
                }
            ),
            html.Div(
                children=[
                    html.Label('Minute:'),
                    dcc.Dropdown(list(range(60)), id='edt-minute'),
                ],
                style={
                    'display': 'inline-block',
                    'padding-right': '5px'
                }
            ),
            html.Div(
                children=[
                    html.Label('Second:'),
                    dcc.Dropdown(list(range(60)), id='edt-second'),
                ],
                style={'display': 'inline-block'}
            )
        ]
    ),
    html.Br(),

    # endDateTime parameter
    # html.H4("Type in the value for endDateTime:"),
    # html.Div(
    #     ["Type in the ending time with format yyyyMMdd HH:mm:ss {TMZ} and press Enter (default is empty and current present moment will be used): ",
    #      dcc.Input(
    #          id='end-date-time', value='', type='text', debounce=True
    #      )]
    # ),
    # html.Br(),

    # durationStr parameter
    html.H4("Choose the value for durationStr:"),
    html.Div(
        children=[
            html.P("Type in an integer and press Enter. " + \
                   "And select the amount of time for which the data needs to be retrieved: " + \
                   "S (seconds), D (days), W (weeks), M (months), Y (years).")
        ],
        style={'width': '365px'}
    ),
    html.Div(
        children=[
            html.Div(
                children=[
                    dcc.Input(id='duration-str-number', value='20', debounce=True)
                ],
                style={
                    'display': 'inline-block',
                    'margin-right': '20px',
                }
            ),
            html.Div(
                children=[
                    dcc.Dropdown(
                        ["S", "D", "W", "M", "Y"], "D", id='duration-str-unit'),
                ],
                style={
                    'display': 'inline-block',
                    'padding-right': '5px'
                }
            ),
        ]
    ),
    html.Br(),

    # barSizeSetting parameter
    html.H4("Choose the value for barSizeSetting:"),
    html.Div(
        ["Choose the size of the bar",
         dcc.Dropdown(
             ["1 sec", "5 secs", "15 secs", "30 secs", "1 min", "2 mins", "3 mins",
              "5 mins", '15 mins', "30 mins", "1 hour", "1 day"], value="1 day",
             id='bar-size-setting')],
        style={'width': '365px'},
    ),
    html.Br(),

    # whatToShow parameter
    html.H4("Choose the value for whatToShow:"),
    html.Div(
        ["Choose what kind of information to be retrieved",
         dcc.Dropdown(
             ["TRADES", "MIDPOINT", "BID", "ASK", "BID_ASK", "HISTORICAL_VOLATILITY",
              "OPTION_IMPLIED_VOLATILITY", 'REBATE_RATE', "FEE_RATE", "SCHEDULE"],
             "MIDPOINT", id='what-to-show')],
        style={'width': '365px'},
    ),
    html.Br(),

    # useRTH parameter
    html.H4("Select the value for useRTH:"),
    html.Div(
        ["Select whether to obtain the data generated outside of the Regular Trading Hours (1 for only the RTH data)",
         dcc.RadioItems(
             id='use-rth',
             options=['1', '0'],
             value='1'
         )]),
    html.Br(),

    html.H4("Enter a currency pair:"),
    html.P(
        children=[
            "See the various currency pairs here: ",
            html.A(
                "currency pairs",
                href='https://www.interactivebrokers.com/en/index.php?f=2222&exch=ibfxpro&showcategories=FX'
            )
        ]
    ),
    html.Br(),

    # Currency pair text input, within its own div.
    html.Div(
        # The input object itself
        ["Input Currency: ", dcc.Input(
            id='currency-input', value='AUD.CAD', type='text'
        )],
        # Style it so that the submit button appears beside the input.
        style={'display': 'inline-block', 'padding-top': '5px'}
    ),
    # Submit button
    html.Button('Submit', id='submit-button', n_clicks=0),
    # Line break
    html.Br(),
    # Div to hold the initial instructions and the updated info once submit is pressed
    html.Div(id='currency-output', children='Enter a currency code and press submit'),
    html.Br(),

    # Div to hold the candlestick graph
    html.Div(
        dcc.Loading(
            id="loading-1",
            type="default",
            children=dcc.Graph(id='candlestick-graph')
        )
    ),
    html.Br(),

    # Section title
    html.H1("Section 2: Make a Trade"),

    html.Div([
        html.H3("Contract Inputs:"),

        # Text input for the contract symbol to be traded
        html.Div(
            children=["Contract Symbol: ", dcc.Input(
                id='symbol-input', value='AUD', type='text'
            )],
            style={'display': 'inline-block', 'padding-top': '5px'}
        ),

        # Text input for the secType to be traded
        html.Div(
            children=["secType: ", dcc.Input(
                id='secType-input', value='CASH', type='text'
            )],
            style={'display': 'inline-block', 'padding-top': '5px'}
        ),

        # Text input for the currency to be traded
        html.Div(
            children=["Currency: ", dcc.Input(
                id='contract-currency-input', value='USD', type='text'
            )],
            style={'display': 'inline-block', 'padding-top': '5px'}
        ),

        # Text input for the exchange to be traded
        html.Div(
            children=["Exchange: ", dcc.Input(
                id='contract-exchange-input', value='IDEALPRO', type='text'
            )],
            style={'display': 'inline-block', 'padding-top': '5px'}
        ),

        # Text input for the primaryExchange to be traded
        html.Div(
            children=["Primary Exchange: ", dcc.Input(
                id='primary-exchange-input', type='text'
            )],
            style={'display': 'inline-block', 'padding-top': '5px'}
        ),
    ]),
    html.Br(),

    html.Div([
        html.H3("Order Inputs:"),
        html.Div(id='trade-output'),

        # Radio items to select buy or sell
        dcc.RadioItems(
            id='buy-or-sell',
            options=[
                {'label': 'BUY', 'value': 'BUY'},
                {'label': 'SELL', 'value': 'SELL'}
            ],
            value='BUY'
        ),
        html.Br(),

        # Numeric input for the trade amount
        html.Label("Total Quantity"),
        dcc.Input(id='trade-amt', value='200', type='number'),
        html.Br(),
        html.Br(),

        # Radio items to select orderType
        dcc.RadioItems(
            id='mkt-or-lmt',
            options=[
                {'label': 'Market', 'value': 'MKT'},
                {'label': 'Limit', 'value': 'LMT'}
            ],
            value='MKT'
        ),
        html.Br(),

        # Numeric input for the lmtPrice
        html.Label("Limit Price"),
        dcc.Input(id='lmt-price-input', type='number', step=0.01),
        html.Br(),
    ]),
    html.Br(),

    # Submit button for the trade
    html.Button('Trade', id='trade-button', n_clicks=0),
    dcc.ConfirmDialog(
        id='confirm-alert',
        message='',
    ),
    dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns], id='table')
])


@app.callback(
    [  # there's more than one output here, so you have to use square brackets to pass it in as an array.
        Output(component_id='currency-output', component_property='children'),
        Output(component_id='candlestick-graph', component_property='figure'),
        Output(component_id='confirm-alert', component_property='displayed'),
        Output(component_id='confirm-alert', component_property='message')
    ],
    Input('submit-button', 'n_clicks'),
    # The callback function will
    # fire when the submit button's n_clicks changes
    # The currency input's value is passed in as a "State" because if the user is typing and the value changes, then
    #   the callback function won't run. But the callback does run because the submit button was pressed, then the value
    #   of 'currency-input' at the time the button was pressed DOES get passed in.
    [State('currency-input', 'value'), State('what-to-show', 'value'),
     State('bar-size-setting', 'value'), State('use-rth', 'value'),
     State('edt-date', 'date'), State('edt-hour', 'value'),
     State('edt-minute', 'value'), State('edt-second', 'value'),
     State('duration-str-number', 'value'), State('duration-str-unit', 'value')]
)
def update_candlestick_graph(n_clicks, currency_string, what_to_show, bar_size_setting, use_rth, edt_date, edt_hour,
                             edt_minute, edt_second, duration_str_number, duration_str_unit):
    # n_clicks doesn't get used, we only include it for the dependency.

    # First things first -- what currency pair history do you want to fetch?
    # Define it as a contract object!
    contract = Contract()
    contract.symbol = currency_string.split(".")[0]  # set this to the FIRST currency (before the ".")
    contract.secType = 'CASH'
    contract.exchange = 'IDEALPRO'  # 'IDEALPRO' is the currency exchange.
    contract.currency = currency_string.split(".")[1]  # set this to the FIRST currency (before the ".")

    # Verify that you've got the right contract
    errmsg = None
    contract_details, errmsg = fetch_contract_details(contract=contract)

    # if type(contract_details) == str:
    #     message = f"Error: {contract_details}! Please check your input!"
    #     # If input is wrong, return blank figure
    #     return message, go.Figure()
    # else:
    #     s = str(contract_details).split(",")[10]
    #     if s == currency_string:
    #         message = "We've found the right contract! Submitted query for " + currency_string
    #     else:
    #         message = f"Contract symbol {s} does not match with the input {currency_string}"
    #         # If input is wrong, return blank figure
    #         return message, go.Figure()

    if any([i is None for i in [edt_date, edt_hour, edt_minute, edt_second]]):
        end_date_time = ''
    else:
        edt_date = edt_date.split('-')
        end_date_time = edt_date[0] + edt_date[1] + edt_date[2] + " " \
                        + str(edt_hour) + ":" + str(edt_minute) + ":" \
                        + str(edt_second) + " EST"

    duration_str = duration_str_number + " " + duration_str_unit

    ############################################################################
    ############################################################################
    # This block is the one you'll need to work on. UN-comment the code in this
    #   section and alter it to fetch & display your currency data!
    # Make the historical data request.
    # Where indicated below, you need to make a REACTIVE INPUT for each one of
    #   the required inputs for req_historical_data().
    # This resource should help a lot: https://dash.plotly.com/dash-core-components

    # Some default values are provided below to help with your testing.
    # Don't forget -- you'll need to update the signature in this callback
    #   function to include your new vars!
    if errmsg is None:
        cph = fetch_historical_data(
            contract=contract,
            endDateTime=end_date_time,
            durationStr=duration_str,
            barSizeSetting=bar_size_setting,
            whatToShow=what_to_show,
            useRTH=use_rth
        )
        # # Make the candlestick figure
        fig = go.Figure(
            data=[
                go.Candlestick(
                    x=cph['date'],
                    open=cph['open'],
                    high=cph['high'],
                    low=cph['low'],
                    close=cph['close']
                )
            ]
        )
    # # Give the candlestick figure a title
        fig.update_layout(title=('Exchange Rate: ' + currency_string))
    else:
        fig = go.Figure(
            data=[
                go.Candlestick(
                )
            ]
        )
        fig.update_layout(title=('Exchange Rate: ' + currency_string))
        print(errmsg)
        return ('Submitted query for ' + currency_string), fig, True, 'Error: ' + errmsg
    ############################################################################
    ############################################################################

    ############################################################################
    ############################################################################
    # This block returns a candlestick plot of apple stock prices. You'll need
    # to delete or comment out this block and use your currency prices instead.
    # df = pd.read_csv(
    #     'https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv'
    # )
    # fig = go.Figure(
    #     data=[
    #         go.Candlestick(
    #             x=df['Date'],
    #             open=df['AAPL.Open'],
    #             high=df['AAPL.High'],
    #             low=df['AAPL.Low'],
    #             close=df['AAPL.Close']
    #         )
    #     ]
    # )
    #
    # currency_string = 'default Apple price data fetch'
    ############################################################################
    ############################################################################

    # Return your updated text to currency-output, and the figure to candlestick-graph outputs
    return ('Submitted query for ' + currency_string), fig, False, ''


# Callback for what to do when trade-button is pressed
@app.callback(
    # We're going to output the result to trade-output
    Output(component_id='trade-output', component_property='children'),
    Output(component_id='table', component_property='data'),
    # We only want to run this callback function when the trade-button is pressed
    Input('trade-button', 'n_clicks'),
    # We DON'T want to run this function whenever buy-or-sell, trade-currency, or trade-amt is updated, so we pass those in as States, not Inputs:
    [State('buy-or-sell', 'value'), State('contract-currency-input', 'value'),
     State('trade-amt', 'value'), State('mkt-or-lmt', 'value'),
     State('secType-input', 'value'), State('symbol-input', 'value'),
     State('contract-exchange-input', 'value'),
     State('primary-exchange-input', 'value'),
     State('lmt-price-input', 'value')],
    # We DON'T want to start executing trades just because n_clicks was initialized to 0!!!
    prevent_initial_call=True
)
def trade(n_clicks, action, trade_currency, trade_amt, order_type,
          sec_type, symbol, exchange, primary_exchange, limit_price):
    # Still don't use n_clicks, but we need the dependency

    # Make the message that we want to send back to trade-output
    msg = action + ' ' + str(trade_amt) + ' ' + trade_currency
    contract = Contract()
    contract.symbol = symbol
    contract.secType = sec_type
    contract.exchange = exchange  # 'IDEALPRO' is the currency exchange.
    # contract.currency = value.split(".")[1]
    contract.currency = trade_currency
    if primary_exchange is not None:
        contract.primaryExchange = primary_exchange

    order = Order()
    order.action = action
    order.orderType = order_type
    order.totalQuantity = trade_amt
    if order_type == 'LMT':
        if limit_price is None:
            return 'Limit price must have a value!'
        order.lmtPrice = limit_price

    fetch_contract_details_new(contract)
    file_path = 'submitted_orders.csv'
    info = place_order(contract, order)
    print(info)

    order_id = info['order_id'][0]
    client_id = info['client_id'][0]
    perm_id = info['perm_id'][0]
    con_id = contract.conId
    timestamp = fetch_current_time()
    new_data = {'timestamp': [timestamp],
                'order_id': [order_id],
                'client_id': [client_id],
                'perm_id': [perm_id],
                'con_id': [con_id],
                'symbol': [symbol],
                'action': [action],
                'size': [trade_amt],
                'order_type': [order_type],
                'lmt_price': [limit_price]}
    new_line = pd.DataFrame(new_data)
    new_line.to_csv(file_path, mode='a', header=False, index=False)
    df = pd.read_csv(file_path)

    return msg, df.to_dict('records')


# Run it!
if __name__ == '__main__':
    app.run_server(debug=True)