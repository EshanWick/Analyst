#!/usr/bin/env python
# coding: utf-8

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Load the data using pandas
data = pd.read_csv('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/historical_automobile_sales.csv')

# Initialize the Dash app
app = dash.Dash(__name__)

# Create the layout of the app
app.layout = html.Div([
    html.H1("Automobile Sales Statistics Dashboard", style={'textAlign': 'center', 'color': '#503D36', 'font-size': 24}),
    html.Div([
        html.Label("Select Statistics:"),
        dcc.Dropdown(
            id='dropdown_statistics',
            options=[
                {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
                {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'}
            ],
            value='Yearly Statistics',
            placeholder='Select a report type',
            style={'width': '80%', 'font-size': 24, 'textAlign': 'center', 'padding': '3px'}
        )
    ]),
    html.Div(dcc.Dropdown(
        id='select_year',
        options=[{'label': i, 'value': i} for i in range(1980, 2024)],
        value=1980
    )),
    html.Div(id='output_container', className='chart-grid', style={'display': 'flex'})
])

# Disable year selection dropdown based on statistics selection
@app.callback(
    Output('select_year', 'disabled'),
    Input('dropdown_statistics', 'value')
)
def update_year_dropdown(selected_statistics):
    return selected_statistics != 'Yearly Statistics'

# Update graphs based on selected statistics and year
@app.callback(
    Output('output_container', 'children'),
    [Input('select_year', 'value'), Input('dropdown_statistics', 'value')]
)
def update_output(selected_year, selected_statistics):
    if selected_statistics == 'Recession Period Statistics':
        recession_data = data[data['Recession'] == 1]

        # Plot 1: Automobile sales fluctuate over Recession Period
        yearly_rec = recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        R_chart1 = dcc.Graph(figure=px.line(yearly_rec, x='Year', y='Automobile_Sales', title="Average Automobile Sales fluctuation over Recession Period"))

        # Plot 2: Average number of vehicles sold by vehicle type during recession
        avg_sales_by_type = recession_data.groupby(['Year', 'Vehicle_Type'])['Automobile_Sales'].mean().reset_index()
        R_chart2 = dcc.Graph(figure=px.line(avg_sales_by_type, x='Year', y='Automobile_Sales', color='Vehicle_Type', title='Average number of vehicles sold by vehicle type during recession'))

        # Plot 3: Total expenditure share by vehicle type during recession
        total_exp_by_type = recession_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        R_chart3 = dcc.Graph(figure=px.pie(total_exp_by_type, values='Advertising_Expenditure', names='Vehicle_Type', title='Total expenditure share by vehicle type during recessions'))

        # Plot 4: Effect of unemployment rate on vehicle type and sales
        sales_by_ur_and_type = recession_data.groupby(['unemployment_rate', 'Vehicle_Type'])['Automobile_Sales'].mean().reset_index()
        R_chart4 = dcc.Graph(figure=px.bar(sales_by_ur_and_type, x='unemployment_rate', y='Automobile_Sales', color='Vehicle_Type', title='Effect of unemployment rate on vehicle type and sales'))

        return [
            html.Div(className='chart-item', children=[html.Div(children=R_chart1),html.Div(children=R_chart2)]),
            html.Div(className='chart-item', children=[html.Div(children=R_chart3),html.Div(children=R_chart4)])
        ]

    elif selected_statistics == 'Yearly Statistics':
        yearly_data = data[data['Year'] == selected_year]

        # Plot 1: Yearly Automobile sales
        yearly_sales = data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        Y_chart1 = dcc.Graph(figure=px.line(yearly_sales, x='Year', y='Automobile_Sales', title='Yearly Automobile sales'))

        # Plot 2: Total Monthly Automobile sales
        monthly_sales = yearly_data.groupby('Month')['Automobile_Sales'].mean().reset_index()
        Y_chart2 = dcc.Graph(figure=px.line(monthly_sales, x='Month', y='Automobile_Sales', title='Monthly Automobile sales'))

        # Plot 3: Average number of vehicles sold by vehicle type in the given year
        avg_sales_by_type_yearly = yearly_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        Y_chart3 = dcc.Graph(figure=px.bar(avg_sales_by_type_yearly, x='Vehicle_Type', y='Automobile_Sales', title=f'Average Vehicles Sold by Vehicle Type in {selected_year}'))

        # Plot 4: Total Advertisement Expenditure by vehicle type
        exp_by_type_yearly = yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        Y_chart4 = dcc.Graph(figure=px.pie(exp_by_type_yearly, values='Advertising_Expenditure', names='Vehicle_Type', title='Total expenditure share by vehicle type'))

        return [
            html.Div(className='chart-item', children=[html.Div(children=Y_chart1),html.Div(children=Y_chart2)]),
            html.Div(className='chart-item', children=[html.Div(children=Y_chart3),html.Div(children=Y_chart4)])
        ]

if __name__ == '__main__':
    app.run_server(debug=True)