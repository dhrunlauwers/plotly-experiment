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

    dbc.Container([
        dbc.Row([
            dbc.Col(width=2),
            dbc.Col(
                html.H1('Portfolio Optimization Demo', style={'color':'white'}), width=8
            ),
            dbc.Col([
                html.A(html.Img(src="https://github.com/dhrunlauwers/plotly-experiment/raw/dev/images/linkedin.png", height='30px'),
                href="https://www.linkedin.com/in/dhrunlauwers/"),
                ], width=1, align='right'
            ),
            dbc.Col([
                html.A(html.Img(src="https://github.com/dhrunlauwers/plotly-experiment/raw/dev/images/GitHub-Mark-Light-32px.png", height="30px"),
                href='https://github.com/dhrunlauwers/plotly-experiment')
                ], width=1, 
            )
        ], style={'backgroundColor': '#013752'}, align='center'),

        html.Br(),
        dbc.Row([
            dbc.Col(lg=2),
            dbc.Col([
                dcc.Markdown("""
                                ### Introduction
                                Under **[modern portfolio theory](https://en.wikipedia.org/wiki/Modern_portfolio_theory)**, a portfolio is considered **efficient** if it maximizes the expected return for a given level of risk (measured as the variance of expected return). 
                                
                                #### What does the app do?
                                Based on the assets selected below, the tool below calculates a set of portfolios (also known as **[the efficient frontier](https://en.wikipedia.org/wiki/Efficient_frontier)**) that satisfies the above condition across a range of expected return values. 
                                
                                #### How does it work?
                                The underlying algorithm uses a **[Lagrange multiplier](https://en.wikipedia.org/wiki/Lagrange_multiplier)** to determine the minimum variance asset allocation under multiple constraints.
                                - Expected return must meet the target value.
                                - Portfolio weights must add up to 100%.
                                
                                #### What data was used?
                                Split-adjusted price [data](https://github.com/dhrunlauwers/plotly-experiment/blob/main/data/finances.csv) for different organizations was gathered using Yahoo Finance API.
                                - Number of available assets: 20
                                - Time period covered: 2005 - 2021
                                - Frequency of observations: Weekly 

                                #### How was it processed?
                                - Covariance matrix calculated based on weekly returns data.
                                - Expected returns calculated by annualizing weekly returns.
                                """),
            ]),
            dbc.Col(lg=2)
        ]),
        dbc.Row([
            dbc.Col(lg=2),
            dbc.Col([
                html.Br(),
                    dcc.Markdown("""
                                ### Demo
                                #### Select the assets you want to include in your portfolio
                                """),
                    dcc.Dropdown(
                        options=[{'label':col, 'value':col} for col in C.columns.sort_values()],
                        value=['AAPL','F','BAC', 'XOM'],
                        id='assets',
                        multi=True),
                    html.Div(id='warning', style={'color':'red'}),
                html.Br(),
                ]),
            dbc.Col(lg=6)
        ]),
        dbc.Row([
            dbc.Col(lg=2),
            dbc.Col([
                dcc.Graph(id='expected_return_chart', config={'displayModeBar':False}),
                html.Br(),
                html.Br(),
                html.Br(),
                dcc.Graph(id='allocation_chart', config={'displayModeBar':False})
            ],lg=8)
        ]), 
    ], fluid=True)
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
    fig.add_scatter(x=results['std_dev'],y=results['mu'], name='Efficient Frontier')
    fig.layout.template = 'simple_white'
    fig.layout.title = 'Efficient Frontier'
    fig.layout.xaxis.title = 'Risk (Standard Deviation)'
    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.title = 'Reward (Expected Return)'
    fig.layout.yaxis.tickformat = '%'
    fig.layout.yaxis.rangemode = 'tozero'
    fig.layout.yaxis.fixedrange = True
    fig.layout.paper_bgcolor = '#E5ECF6'
    fig.layout.plot_bgcolor = '#E5ECF6'
    fig.update_traces(hovertemplate='Expected Return: %{y:.1%} <br> Standard Deviation of Return: %{x:.3g}')
    fig.update_layout(title={'text':'Efficient Frontier', 'y':0.95, 'x':0},
                        title_font_size=24, height=750)

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
    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.fixedrange = True
    fig.layout.template = 'simple_white'
    fig.update_layout(legend_title_text='Assets',title_font_size=24,
                        title={'text':'Ideal Allocation', 'y':0.99, 'x':0},
                        height=750)
    fig.update_traces(hovertemplate='Expected Return: %{y:.1%} <br> Allocation: %{x:.1%}')
    fig.layout.paper_bgcolor = '#E5ECF6'
    fig.layout.plot_bgcolor = '#E5ECF6'

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
