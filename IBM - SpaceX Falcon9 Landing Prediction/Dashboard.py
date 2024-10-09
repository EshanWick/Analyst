# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                #addding dropdown with launch site options
                                  dcc.Dropdown(id='site-dropdown',
                                     options=[
                                        {'label': 'All Sites', 'value': 'ALL'},
                                        {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                        {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                        {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                        {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}

                                     ],
                                     value='ALL',
                                     placeholder="Select a Launch Site here",
                                     searchable=True
                                     ),
                                 html.Br(),

                                #adding pie chart to app
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                #payload range slider
                                dcc.RangeSlider(id='payload-slider',
                                    min=0, max=10000, step=1000,
                                    marks={0: '0',
                                           1000: '1000',
                                           2000: '2000',
                                           3000: '3000',
                                           4000: '4000',
                                           5000: '5000',
                                           6000: '6000',
                                           7000: '7000',
                                           8000: '8000',
                                           9000: '9000',
                                           10000:'10000'},
                                    value=[min_payload, max_payload]),
                                #adding scatter chart to app
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
 ])

#Callback function for Piechart
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        fig = px.pie(spacex_df, values='class', 
        names='Launch Site', 
        title='Total Success Launches for all sites')
        return fig
    else:
        filtered_df=spacex_df[spacex_df['Launch Site']== entered_site]
        filtered_df=filtered_df.groupby(['Launch Site','class']).size().reset_index(name='class count')
        fig=px.pie(filtered_df,values='class count',names='class',title=f"Total Success Launches for site {entered_site}")
        return fig

#Callback function for scatter chart
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
                [Input(component_id='site-dropdown', component_property='value'),
                Input(component_id="payload-slider", component_property="value")])
def get_scatter_chart(entered_site,payload_slider):
    filtered_df1 = spacex_df[spacex_df['Payload Mass (kg)'].between(payload_slider[0],payload_slider[1])]
    if entered_site == 'ALL':
        fig1 = px.scatter(filtered_df1, x='Payload Mass (kg)',y='class',
        color='Booster Version Category',title='Success count on Payload mass for all sites', 
        )
        return fig1
    else:
        filtered_df2=filtered_df1[filtered_df1['Launch Site']== entered_site]
        fig1 = px.scatter(filtered_df2, x='Payload Mass (kg)',y='class',
        color='Booster Version Category',title=f'Success count on Payload mass for Launch site {entered_site}')
        return fig1

#running the app
if __name__ == '__main__':
    app.run_server()
