import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash.dependencies import Output, Input
import numpy as np
import pandas as pd
from src.optimization import optimize_portfolio

#-------------------------------------------------------------
#-------------------------------------------------------------
input_df = pd.read_csv('./data/cov-matrix-and-returns.csv', index_col=0)

r = input_df['mu']

C = input_df.drop(['mu'], axis=1)

returns_vector = np.arange(0.05, 0.2, 0.005)

results = optimize_portfolio(returns_vector, r, C, ['AAPL', 'F', 'BAC', 'XOM'])
    
#-------------------------------------------------------------
#-------------------------------------------------------------

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

app.layout = html.Div([
    html.H1('Portfolio Optimization Demo'),
    html.Br(),
    html.H5('Select the assets you want to include in your portfolio'),
    dcc.Dropdown(
        options=[{'label':col, 'value':col} for col in C.columns.sort_values()],
        value=['AAPL','F','BAC', 'XOM'],
        id='assets',
        multi=True
    ),
    html.Br(),
    html.Div(id='warning', style={'color':'red'}),
    html.Br(),
    dbc.Row([
        dbc.Col(
            dcc.Graph(id='expected_return_chart')
        ),
        dbc.Col(
            dcc.Graph(id='allocation_chart')
        )
    ]),

    html.Br(),
    html.Br(),

    dbc.Tabs([
        dbc.Tab([
            html.Br(),
            html.Ul([
                html.Li('Page Title: Markowitz Portfolio Optimization Demo - now in Dash!'),
                html.Li(['Github repo: ',
                     html.A('https://github.com/dhrunlauwers/markowitz-portfolio-optimization',
                            href='https://github.com/dhrunlauwers/markowitz-portfolio-optimization')
                    ])
            ])
        ], label='Project Info'),
        dbc.Tab([
            html.Br(),
            html.Ul(
                    [html.Li('Number of available assets: 20'),
                    html.Li('Time period for underlying data: 2005-present'),
                    html.Li('Based on annualized weekly returns')]
            )
        ], label='Key Facts')
    ])
])

@app.callback(Output('warning', 'children'),
              Input('assets', 'value'))
def check_selection(assets):
    if len(assets) >= 3:
        return ''
    else:
        return [html.H6(f'Please select at least three assets.\nYou currently have {len(assets)} selected.')]


@app.callback(Output('expected_return_chart', 'figure'),
              Input('assets', 'value'))
def plot_expected_return(assets):
    results = optimize_portfolio(returns_vector, r, C, assets)
    fig = go.Figure()
    fig.add_scatter(x=results['mu'],y=results['std_dev'])
    fig.layout.title = 'Standard deviation of portfolio returns'
    fig.layout.xaxis.title = 'Expected Return'
    fig.layout.yaxis.title = 'Standard Deviation'

    return fig

@app.callback(Output('allocation_chart', 'figure'),
              Input('assets', 'value'))
def plot_allocation(assets):
    results = optimize_portfolio(returns_vector, r, C, assets)
    fig = go.Figure()

    lowest_risk_portfolio = results.iloc[np.argmin(results['std_dev'])]

    for k, v in enumerate(assets):
        fig.add_scatter(x=results['mu'], y=results['w'+str(k)], name=v)

    fig.add_scatter(x=[lowest_risk_portfolio['mu'] for _ in range(len(results))], y=np.arange(-0.2, 1.4, 0.2),
                    line=go.scatter.Line(dash='longdash', 
                    color='rgb(255,0,0)'), 
                    marker=go.scatter.Marker(opacity=0),
                    name='MVP')

    fig.layout.title = 'Lowest risk asset allocation for a range of expected return values'
    fig.layout.xaxis.title = 'Expected Return'
    fig.layout.yaxis.title = 'Percent Allocation'

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
