import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
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
    html.H1('Portfolio Optimization Demo', style={'textAlign':'center'}),
    html.Br(),
    dbc.Row([
        dbc.Col(lg=2),
        dbc.Col([
            dcc.Markdown("""
                            Under modern portfolio theory, a portfolio is considered **efficient** if it maximizes the expected return for a given level of risk (measured as the variance of expected return). 
                            
                            Based on the assets selected below, this app calculates a set of portfolios (also known as the **efficient frontier**) that satisfies this condition across a range of expected return values. The underlying algorithm uses a **Lagrange multiplier** to determine the minimum variance asset allocation under multiple constraints. 
                            
                            The links at the bottom of this page include references, a simple example, as well as code for both the algorithm and this dashboard. Please reach out if you have any feedback!
                            """),
            html.Br(),
            html.Br(),
            html.H5('Select the assets you want to include in your portfolio', style={'textAlign':'center'}),
            dcc.Dropdown(
                options=[{'label':col, 'value':col} for col in C.columns.sort_values()],
                value=['AAPL','F','BAC', 'XOM'],
                id='assets',
                multi=True),
            html.Div(id='warning', style={'color':'red', 'textAlign':'center'}),
            html.Br(),
            html.Br(),
            dcc.Graph(id='expected_return_chart'),
            html.Br(),
            html.Br(),
            html.Br(),
            dcc.Graph(id='allocation_chart')
        ],lg=8)
    ]), 
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),

    dbc.Tabs([
        dbc.Tab([
            html.Br(),
            html.Ul([
                html.Li(['Github repo: ',
                     html.A('https://github.com/dhrunlauwers/plotly-experiment',
                            href='https://github.com/dhrunlauwers/plotly-experiment')
                ]),
                html.Li(['A simpler example: ',
                     html.A('https://github.com/dhrunlauwers/markowitz-portfolio-optimization',
                            href='https://github.com/dhrunlauwers/markowitz-portfolio-optimization')
                ]),
                html.Li(['Contact: ',
                     html.A('https://www.linkedin.com/in/dhrunlauwers/',
                            href='https://www.linkedin.com/in/dhrunlauwers/')
                ]),
            ])
        ], label='Project Info'),
        dbc.Tab([
            html.Br(),
            html.Ul(
                    [html.Li('Number of available assets: 20'),
                    html.Li('Time period for underlying data: 2005-present'),
                    html.Li('Both expected return values and covariance matrix are based on annualized weekly returns')]
            )
        ], label='Key Facts'),
        dbc.Tab([
            html.Br(),
            html.Ul([
                   html.Li(['Modern portfolio theory: ',
                     html.A('https://en.wikipedia.org/wiki/Modern_portfolio_theory',
                            href='https://en.wikipedia.org/wiki/Modern_portfolio_theory')
                ]),
                html.Li(['The efficient frontier: ',
                     html.A('https://en.wikipedia.org/wiki/Efficient_frontier',
                            href='https://en.wikipedia.org/wiki/Efficient_frontier')
                ]),
                html.Li(['Lagrange multiplier: ',
                     html.A('https://en.wikipedia.org/wiki/Lagrange_multiplier',
                            href='https://en.wikipedia.org/wiki/Lagrange_multiplier')
                ])]
            )
        ], label='References')
    ])
], style={'backgroundColor': '#E5ECF6'})

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
    fig.add_scatter(x=results['std_dev'],y=results['mu'])
    fig.layout.template = 'simple_white'
    fig.layout.title = 'Efficient Frontier'
    fig.layout.xaxis.title = 'Risk (Standard Deviation)'
    fig.layout.yaxis.title = 'Reward (Expected Return)'
    fig.layout.yaxis.tickformat = '%'
    fig.layout.yaxis.rangemode = 'tozero'
    fig.layout.paper_bgcolor = '#E5ECF6'
    fig.layout.plot_bgcolor = '#E5ECF6'
    fig.update_traces(hovertemplate='Expected Return: %{y:.1%} <br> Standard Deviation of Return: %{x:.3g}')
    fig.update_layout(title={'text':'Efficient Frontier', 'y':0.9, 'x':0.5, 'xanchor':'center', 'yanchor':'top'},
                        title_font_size=20, height=750)

    return fig

@app.callback(Output('allocation_chart', 'figure'),
              Input('assets', 'value'))
def plot_allocation(assets):
    results = optimize_portfolio(returns_vector, r, C, assets)
    fig = px.bar(results.rename({'w'+str(k): v for k,v in enumerate(assets)}, axis=1), 
                 x=assets,
                 y='mu',
                 height=600, 
                 orientation='h',
                 color_discrete_sequence=px.colors.qualitative.Light24)
    fig.layout.xaxis.title = '% of overall Portfolio'
    fig.layout.yaxis.title = 'Expected Return'
    fig.layout.xaxis.tickformat = '%'
    fig.layout.yaxis.tickformat = '%'
    fig.layout.template = 'simple_white'
    fig.layout.title.x = 0.5
    fig.update_layout(legend_title_text='Assets',title_font_size=20,
                        title={'text':'Ideal Allocation', 'y':1, 'x':0.5, 'xanchor':'center', 'yanchor':'top'},
                        height=750)
    fig.update_traces(hovertemplate='Expected Return: %{y:.1%} <br> Allocation: %{x:.1%}')
    fig.layout.paper_bgcolor = '#E5ECF6'
    fig.layout.plot_bgcolor = '#E5ECF6'

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
